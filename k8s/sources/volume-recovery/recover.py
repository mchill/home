import json
import os
import re
import ssl
import time
import urllib.request

API = "https://kubernetes.default.svc"
SA = "/var/run/secrets/kubernetes.io/serviceaccount"
MOUNTINFO = os.environ.get("MOUNTINFO", "/host/proc/1/mountinfo")
NODE_NAME = os.environ["NODE_NAME"]
INTERVAL = int(os.environ.get("INTERVAL", "30"))
COOLDOWN = int(os.environ.get("COOLDOWN", "3600"))
UNSTAGE_TIMEOUT = int(os.environ.get("UNSTAGE_TIMEOUT", "180"))
ANNOTATION = "home.mchill.io/volume-recovery-replicas"

CSI_MOUNT = re.compile(
    r"/var/lib/kubelet/pods/([0-9a-fA-F-]{36})/volumes/kubernetes\.io~csi/"
)
ABORTED = ("emergency_ro", "shutdown")
SCALABLE = {"Deployment": "deployments", "StatefulSet": "statefulsets"}

context = ssl.create_default_context(cafile=f"{SA}/ca.crt")


def request(path, method="GET", body=None, content_type=None):
    with open(f"{SA}/token") as handle:
        token = handle.read().strip()
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(f"{API}{path}", method=method, data=data)
    req.add_header("Authorization", f"Bearer {token}")
    if content_type:
        req.add_header("Content-Type", content_type)
    with urllib.request.urlopen(req, context=context, timeout=30) as response:
        return json.load(response)


def patch(path, body):
    return request(path, "PATCH", body, "application/merge-patch+json")


def read_mounts():
    entries = []
    with open(MOUNTINFO) as handle:
        for line in handle:
            head, _, tail = line.partition(" - ")
            if not tail:
                continue
            fields = head.split()
            if len(fields) < 5:
                continue
            entries.append((fields[2], fields[4], tail.split()[-1].split(",")))
    return entries


def aborted_volumes():
    found = {}
    for device, mountpoint, options in read_mounts():
        match = CSI_MOUNT.search(mountpoint)
        if match and any(flag in options for flag in ABORTED):
            found[match.group(1)] = device
    return found


def device_gone(device):
    return all(entry[0] != device for entry in read_mounts())


def owner_of(pod):
    for reference in pod["metadata"].get("ownerReferences", []):
        kind = reference["kind"]
        namespace = pod["metadata"]["namespace"]
        if kind in SCALABLE:
            return kind, namespace, reference["name"]
        if kind == "ReplicaSet":
            replicaset = request(
                f"/apis/apps/v1/namespaces/{namespace}/replicasets/{reference['name']}"
            )
            for parent in replicaset["metadata"].get("ownerReferences", []):
                if parent["kind"] in SCALABLE:
                    return parent["kind"], namespace, parent["name"]
    return None


def workload_path(kind, namespace, name):
    return f"/apis/apps/v1/namespaces/{namespace}/{SCALABLE[kind]}/{name}"


def scale(kind, namespace, name, replicas):
    patch(
        f"{workload_path(kind, namespace, name)}/scale",
        {"spec": {"replicas": replicas}},
    )


def recover(kind, namespace, name, device):
    path = workload_path(kind, namespace, name)
    workload = request(path)
    annotations = workload["metadata"].get("annotations") or {}
    original = int(annotations.get(ANNOTATION) or workload["spec"]["replicas"])
    if original < 1:
        return
    print(f"{kind} {namespace}/{name}: aborted volume, scaling {original} -> 0", flush=True)
    patch(path, {"metadata": {"annotations": {ANNOTATION: str(original)}}})
    scale(kind, namespace, name, 0)

    deadline = time.monotonic() + UNSTAGE_TIMEOUT
    while time.monotonic() < deadline:
        if device_gone(device):
            break
        time.sleep(2)
    unstaged = device_gone(device)

    scale(kind, namespace, name, original)
    patch(path, {"metadata": {"annotations": {ANNOTATION: None}}})
    state = "unstaged" if unstaged else "UNSTAGE TIMED OUT"
    print(f"{kind} {namespace}/{name}: {state}, restored to {original}", flush=True)


def restore_interrupted():
    for kind, plural in SCALABLE.items():
        for workload in request(f"/apis/apps/v1/{plural}").get("items", []):
            annotations = workload["metadata"].get("annotations") or {}
            if ANNOTATION not in annotations:
                continue
            namespace = workload["metadata"]["namespace"]
            name = workload["metadata"]["name"]
            original = int(annotations[ANNOTATION])
            print(f"{kind} {namespace}/{name}: resuming interrupted recovery", flush=True)
            scale(kind, namespace, name, original)
            patch(
                workload_path(kind, namespace, name),
                {"metadata": {"annotations": {ANNOTATION: None}}},
            )


def main():
    try:
        restore_interrupted()
    except Exception as error:
        print(f"error restoring interrupted recovery: {error}", flush=True)

    handled = {}
    while True:
        try:
            volumes = aborted_volumes()
            if volumes:
                pods = request(f"/api/v1/pods?fieldSelector=spec.nodeName={NODE_NAME}")
                for pod in pods.get("items", []):
                    device = volumes.get(pod["metadata"]["uid"])
                    if not device:
                        continue
                    owner = owner_of(pod)
                    if not owner:
                        print(
                            f"pod {pod['metadata']['namespace']}/{pod['metadata']['name']}"
                            " has an aborted volume but no scalable owner",
                            flush=True,
                        )
                        continue
                    key = owner
                    now = time.monotonic()
                    if now - handled.get(key, -COOLDOWN) < COOLDOWN:
                        continue
                    handled[key] = now
                    recover(*owner, device)
        except Exception as error:
            print(f"error: {error}", flush=True)
        time.sleep(INTERVAL)


main()

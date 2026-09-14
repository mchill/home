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
COOLDOWN = int(os.environ.get("COOLDOWN", "300"))

CSI_MOUNT = re.compile(
    r"/var/lib/kubelet/pods/([0-9a-fA-F-]{36})/volumes/kubernetes\.io~csi/"
)
ABORTED = ("emergency_ro", "shutdown")

context = ssl.create_default_context(cafile=f"{SA}/ca.crt")


def request(path, method="GET"):
    with open(f"{SA}/token") as handle:
        token = handle.read().strip()
    req = urllib.request.Request(f"{API}{path}", method=method)
    req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, context=context, timeout=30) as response:
        return json.load(response)


def aborted_pod_uids():
    uids = set()
    with open(MOUNTINFO) as handle:
        for line in handle:
            head, _, tail = line.partition(" - ")
            if not tail:
                continue
            fields = head.split()
            if len(fields) < 5:
                continue
            match = CSI_MOUNT.search(fields[4])
            if not match:
                continue
            super_options = tail.split()[-1].split(",")
            if any(flag in super_options for flag in ABORTED):
                uids.add(match.group(1))
    return uids


def main():
    deleted = {}
    while True:
        try:
            uids = aborted_pod_uids()
            now = time.monotonic()
            uids = {u for u in uids if now - deleted.get(u, -COOLDOWN) >= COOLDOWN}
            if uids:
                pods = request(f"/api/v1/pods?fieldSelector=spec.nodeName={NODE_NAME}")
                for pod in pods.get("items", []):
                    uid = pod["metadata"]["uid"]
                    if uid not in uids:
                        continue
                    namespace = pod["metadata"]["namespace"]
                    name = pod["metadata"]["name"]
                    print(
                        f"aborted volume on {namespace}/{name}, deleting pod",
                        flush=True,
                    )
                    request(
                        f"/api/v1/namespaces/{namespace}/pods/{name}", method="DELETE"
                    )
                    deleted[uid] = now
        except Exception as error:
            print(f"error: {error}", flush=True)
        time.sleep(INTERVAL)


main()

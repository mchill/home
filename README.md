# Home Server

This is the configuration for my home server running in Kubernetes.

![Home Server](https://github.com/mchill/home/workflows/Home%20Server/badge.svg)

[App Dashboard](https://mchill.io)

[Trello Board](https://trello.com/b/XNVnSBvI/home-server)

## Configuration

### Network

All HTTP traffic is routed through Traefik, but TCP and UDP connections are exposed separately. Although additional entrypoints could be configured to proxy these connections, it adds no benefit other than load balancing due to the lack of host or path matching.

MetalLB has been configured with a pool containing a single IP address to make port forwarding on the router easier.

HTTPS traffic is secured behind Google forward authentication by default. Some exceptions are made for applications that don't work behind an additional layer of authentication (e.g., Plex and Home Assistant).

The following DHCP reservations should be made.

Device            | IP Address
---               | ---
Laptop Node       | 192.168.1.200
Raspberry Pi Node | 192.168.1.201
NAS               | 192.168.1.210
Phone             | 192.168.1.211

The following ports need to be fowarded to 192.168.1.250.

External  | Internal  | Service
---       | ---       | ---
80        | 8000      | HTTP
443       | 8443      | HTTPS
22        | 22        | SSH
16443     | 16443     | Kube API Server
25565     | 25565     | Minecraft
25566     | 25566     | Minecraft
10000/udp | 10000/udp | Jitsi

### Filesystem

Persistent storage is split into two volumes.

* server - Application configuration and state. Uses an OpenEBS Jiva volume replicated across all my nodes.
* media - Larger long-term media storage. Mounted from my NAS as an NFS volume.

### Sealed Secrets

[Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) are stored securely alongside the rest of the server configuration in source control. They are decrypted by a controller running in the cluster.

To create new sealed secret, follow these steps.

1. Base64 encode the secret value.

    ```bash
    echo -n "secret" | base64 -w 0
    ```

2. Create a native Secret resource with the desired key name and encoded value

    ```yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: jitsi
      namespace: server
    type: Opaque
    data:
      MY_SECRET_KEY: c2VjcmV0
    ```

3. Use the kubeseal cli tool to generate a Sealed Secret. Be sure to specify the correct namespace, or else the controller won't be able to decrypt the secret.

    ```bash
    kubeseal <secret.yaml >sealed-secret.yaml -o yaml
    ```

## Setup

### Reset Cluster

If the cluster ever needs to be completely reset, this can be easily done with snap. You'll also have to regenerate all sealed secrets afterwards, since the decryption key will be different in a new cluster.

```bash
sudo snap remove microk8s
sudo snap install microk8s --classic
microk8s enable rbac
microk8s enable dns
microk8s enable metrics-server
```

### Restore Storage

OpenEBS creates a new subdirectory for every persistent volume. Data will need to be copied from the old volume to the new volume.

```bash
OLD_VOLUME_NAME=pvc-<uuid> envsubst < k8s/infrastructure/openebs/restore.yaml | kubectl apply -f -
```

### Deploy

The server is automatically deployed by CI. Manual deployment can be done with the following commands.

```bash
kustomize build crds | kubectl apply -f -
kustomize build infrastructure | kubectl apply -f -
kustomize build applications | kubectl apply -f -
```

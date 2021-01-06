# Home Server

This is the configuration for my home server running in Kubernetes.

![Home Server](https://github.com/mchill/home/workflows/Home%20Server/badge.svg)

[Trello Board](https://trello.com/b/XNVnSBvI/home-server)

## Applications

Application          | URL
---                  | ---
Dashboard            | https://mchill.duckdns.org
File Browser         | https://files.mchill.duckdns.org
Grafana              | https://grafana.mchill.duckdns.org
Home Assistant       | https://home.mchill.duckdns.org
Jackett              | https://jackett.mchill.duckdns.org
Jaeger               | https://jaeger.mchill.duckdns.org
Jitsi                | https://jitsi.mchill.duckdns.org
Kubernetes Dashboard | https://k8s.mchill.duckdns.org
Minecraft            | mchill.duckdns.org:25565
Minecraft (Hogwarts) | mchill.duckdns.org:25566
Pi-hole              | https://pihole.mchill.duckdns.org
Plex                 | https://plex.mchill.duckdns.org
Portainer            | https://portainer.mchill.duckdns.org
Prometheus           | https://prometheus.mchill.duckdns.org
Sonarr               | https://sonarr.mchill.duckdns.org
Synology DSM         | https://nas.mchill.duckdns.org
Traefik Dashboard    | https://traefik.mchill.duckdns.org
Transmission         | https://transmission.mchill.duckdns.org

## Configuration

### Network

All HTTP traffic is routed through Traefik, but TCP and UDP connections are directly exposed to the host via NodePort services. Although additional entrypoints could be configured to proxy these connections, it adds no benefit other than load balancing due to the lack of host or path matching.

HTTPS traffic is secured behind Google forward authentication by default. Some exceptions are made for applications that don't work behind an additional layer of authentication (e.g., Plex and Home Assistant).

The following ports need to be fowarded by your router.

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

Two hostPath persistent volumes have been created for storage. The first stores persistent application data and is located at /server. The second stores large media (Plex library and torrents) and is mounted at /data. Both volumes are backed up nightly to local and cloud storage.

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
    kubeseal <secret.yaml >sealed-secret.yaml -o yaml -n server
    ```

## Setup

### Reset Cluster

If the cluster ever needs to be completely reset, this can be easily done with snap. You'll also have to regenerate all sealed secrets afterwards, since the decryption key will be different in a new cluster.

```bash
sudo snap remove microk8s
sudo snap install microk8s --classic
echo "--service-node-port-range=0-65535" >> /var/snap/microk8s/current/args/kube-apiserver
sudo systemctl restart snap.microk8s.daemon-apiserver
microk8s enable storage
microk8s enable rbac
microk8s enable dns
microk8s enable metrics-server
```

### Deploy

The server is automatically deployed by CI. Manual deployment can be done with the following commands. Kustomize's prune flag doesn't work on custom resource definitions, so these have to be manually deleted to ensure orphans are removed.

```bash
kustomize build --enable_alpha_plugins | microk8s kubectl apply -f - --prune -l prune=true --dry-run=client
microk8s kubectl delete --all ingressroute -n server
microk8s kubectl delete --all middleware -n server
kustomize build --enable_alpha_plugins | microk8s kubectl apply -f - --prune -l prune=true
```

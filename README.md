# Home Server

This is the configuration for my home server running in Kubernetes.

![Home Server](https://github.com/mchill/home/workflows/Home%20Server/badge.svg)

[App Dashboard](https://mchill.io)

[Trello Board](https://trello.com/b/XNVnSBvI/home-server)

## Configuration

### Network

All HTTP traffic is routed through Traefik, but UDP connections are exposed separately. Although additional entrypoints could be configured to proxy these connections, it adds no benefit other than load balancing due to the lack of host or path matching.

HTTPS traffic is secured behind Google forward authentication by default. Some exceptions are made for applications that don't work behind an additional layer of authentication (e.g., Plex and Home Assistant).

The following DHCP reservations should be made.

Device            | IP Address
---               | ---
Laptop Node       | 192.168.1.200
Raspberry Pi Node | 192.168.1.201
Raspberry Pi Node | 192.168.1.202
NAS               | 192.168.1.210
Phone             | 192.168.1.211

In addition, a MetalLB pool is created to expose the following services to the local network.

Application      | IP Address    | Ports
---              | ---           | ---
External Traefik | 192.168.1.240 | 80, 443
Minecraft        | 192.168.1.241 | 25565
Jitsi            | 192.168.1.242 | 10000/udp
Internal Traefik | 192.168.1.245 | 80, 443
Plex             | 192.168.1.246 | 32400, 32410-32414/udp
Pihole           | 192.168.1.249 | 80, 443, 53, 53/udp

The following ports need to be fowarded to expose certain services to the internet.

Port      | Destination             | Service
---       | ---                     | ---
80        | 192.168.1.240:83        | Traefik HTTP
443       | 192.168.1.240:443       | Traefik HTTPS
25565     | 192.168.1.241:25565     | Minecraft
10000/udp | 192.168.1.242:10000/udp | Jitsi
22        | 192.168.1.200:22        | SSH
16443     | 192.168.1.200:16443     | Kube API Server

### Filesystem

Persistent storage is split into two volumes.

* server - Application configuration and state. Uses a GlusterFS volume replicated across all my nodes.
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
      name: my-secret
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

If the cluster ever needs to be completely reset, this can be easily done with snap.

```bash
sudo snap remove microk8s
sudo snap install microk8s --classic --channel=1.23

# Add custom domain name to cert
sed -i '/^DNS.5 =.*/a DNS.6 = mchill.io' /var/snap/microk8s/current/certs/csr.conf.template
sudo microk8s refresh-certs

# Enable combined tcp/udp services
sed -i 's/--feature-gates=.*/&,MixedProtocolLBService=true/g' /var/snap/microk8s/current/args/kube-apiserver
sudo systemctl restart snap.microk8s.daemon-kubelite.service

microk8s status --wait-ready
microk8s config > ~/.kube/config
microk8s enable rbac
microk8s enable dns
```

You'll also have to regenerate all sealed secrets afterwards, since the decryption key will be different in a new cluster.

```bash
find . -type f -iname secret.yaml -not -path "*/charts/*" -execdir sh -c "cat {} | kubeseal --controller-namespace=sealed-secrets -o yaml > sealed-secret.yaml" \;
```

### Deploy

The server is automatically deployed by CI. Manual deployment can be done with the following commands.

```bash
kustomize build crds | kubectl apply -f -
kustomize build infrastructure | kubectl apply -f -
kustomize build applications | kubectl apply -f -
```

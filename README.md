# Home Server

This is the configuration for my home server running in Kubernetes.

![Home Server](https://github.com/mchill/home/workflows/Home%20Server/badge.svg)

[App Dashboard](https://mchill.io)

[Trello Board](https://trello.com/b/XNVnSBvI/home-server)

## Configuration

### Network

All HTTP traffic is routed through Traefik, but TCP and UDP connections are exposed separately. Although additional entrypoints could be configured to proxy these connections, it adds no benefit other than load balancing due to the lack of host or path matching.

HTTPS traffic is secured behind Google forward authentication by default. Some exceptions are made for applications that don't work behind an additional layer of authentication (e.g., Plex and Home Assistant).

Load balancing is acheived using MetalLB for all services running inside of Kubernetes, and Kube Karp for the Kube API server.

![Network](docs/images/network.drawio.svg)

### Filesystem

Persistent storage is achieved using NFS and [Longhorn](https://longhorn.io/) volumes.

### Sealed Secrets

[Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) are stored securely alongside the rest of the server configuration in source control. They are decrypted by a controller running in the cluster.

To create new a sealed secret, follow these steps.

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
   kubeseal <secret.yaml >sealed-secret.yaml --controller-namespace=sealed-secrets -o yaml
   ```

## Setup

### Provision Nodes

To configure a node from scratch, first complete the following prerequisites:

1. Install Ubuntu 22.04

2. Create the user `mchill`

3. Enable ssh

   ```bash
   sudo apt install openssh-server
   sudo systemctl enable --now ssh
   ```

4. Add public key to `~/.ssh/authorized_keys`

After following the above steps for each node, they can be provisioned with an ansible playbook.

```bash
ansible-playbook playbooks/configure-nodes.yaml -i inventory.yaml
```

### Create/Reset Cluster

If the cluster ever needs to be completely reset, this can be done with an ansible playbook.

```bash
ansible-playbook playbooks/reset-cluster.yaml -i inventory.yaml --extra-vars "K3S_TOKEN=$K3S_TOKEN GITHUB_TOKEN=$GITHUB_TOKEN"
```

Edit `/etc/systemd/system/k3s.service` and add the required arguments to `ExecStart`.

```bash
ExecStart=/usr/local/bin/k3s server '--kubelet-arg=allowed-unsafe-sysctls=net.*'
```

### Deploy Workloads

Applications are automatically deployed by CI. Manual deployment can be done with the following commands.

```bash
pushd k8s/infrastructure && ./apply.sh && popd
pushd k8s/applications && ./build.sh | kubectl apply --server-side --force-conflicts -f - && popd
```

# Home Server

This is the configuration for my home server running in Kubernetes.

![Home Server](https://github.com/mchill/home/workflows/Home%20Server/badge.svg)

[App Dashboard](https://mchill.io)

[Trello Board](https://trello.com/b/XNVnSBvI/home-server)

## Setup

### Configure Nodes

```bash
ansible-playbook playbooks/configure_proxmox_hosts.yaml -i inventory.yaml
```

### Provision Virtual Machines

When creating VMs for the first time, set `initialize=true` to add the bootable CD and exclude devices that interfere with the OS installation process.

```bash
terraform apply -var="initialize=true"
```

### Install Operating System

1. Install Ubuntu Server 24.04. Keep defaults except where noted below.
   1. Disable "Set up this disk as an LVM group"
   2. Enable "Install OpenSSH server"
   3. Import SSH key from GitHub

2. Enable passwordless sudo to allow Ansible to run later.

   ```bash
   echo "mchill ALL=(ALL) NOPASSWD: ALL" | sudo tee -a /etc/sudoers.d/mchill
   ```

3. Reapply terraform configuration, removing the bootable CD and adding PCI and serial devices.

   ```bash
   terraform apply
   ```

### Configure Virtual Machines

```bash
ansible-playbook playbooks/configure_proxmox_vms.yaml -i inventory.yaml
```

### Deploy Workloads

```bash
pushd k8s/infrastructure && ./apply.sh && popd
pushd k8s/ingresses && ./build.sh | kubectl apply --server-side --force-conflicts -f - && popd
pushd k8s/applications && ./build.sh | kubectl apply --server-side --force-conflicts -f - && popd
```

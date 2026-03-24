# Home Server

This is the configuration for my home server running in Kubernetes.

![Home Server](https://github.com/mchill/home/workflows/Home%20Server/badge.svg)

[App Dashboard](https://mchill.io)

[Trello Board](https://trello.com/b/XNVnSBvI/home-server)

## Setup

### Configure Hosts

1. Install Proxmox.

2. Create user.

   ```bash
   apt update
   apt install sudo
   useradd -m mchill
   passwd mchill
   echo "mchill ALL=(ALL) NOPASSWD: ALL" | tee -a /etc/sudoers.d/mchill
   ```

3. Add ssh key from GitHub.

   ```bash
   mkdir ~/.ssh
   touch ~/.ssh/authorized_keys
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   wget -O - https://github.com/mchill.keys >> ~/.ssh/authorized_keys
   ```

4. Configure the hosts with Ansible.

   ```bash
   ansible-playbook playbooks/configure_proxmox_hosts.yaml -i inventory.yaml --extra-vars "@variables.yaml"
   ```

5. If Ceph was installed for the first time, some values need to be replaced.
   - Replace the `clusterID` with the result of `ceph fsid` in:
     - [k8s/infrastructure/ceph/values.yaml](k8s/infrastructure/ceph/values.yaml)
     - [k8s/overlays/persistence/pv.yaml](k8s/overlays/persistence/pv.yaml)

   - Replace the `userKey` with the result of `ceph auth get-key client.k8s` in:
     - [k8s/infrastructure/ceph/secret.yaml](k8s/infrastructure/ceph/secret.yaml)

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
ansible-playbook playbooks/configure_proxmox_vms.yaml -i inventory.yaml --extra-vars "@variables.yaml"
```

### Deploy Workloads

```bash
pushd k8s/infrastructure && ./apply.sh && popd
pushd k8s/ingresses && ./build.sh | kubectl apply --server-side --force-conflicts -f - && popd
pushd k8s/applications && ./build.sh | kubectl apply --server-side --force-conflicts -f - && popd
```

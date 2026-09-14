variable "init_agent_1" {
  type    = bool
  default = false
}

locals {
  init_agent_1 = var.init_agent_1 || var.initialize
}

resource "proxmox_virtual_environment_vm" "k3s-agent-1" {
  lifecycle {
    ignore_changes = [initialization]
  }

  # General
  node_name = "beelink1"
  vm_id     = 121
  name      = "k3s-agent-1"
  on_boot   = true

  # OS
  operating_system {
    type = "l26"
  }

  # System
  machine       = "q35"
  bios          = "ovmf"
  scsi_hardware = "virtio-scsi-single"
  efi_disk {
    datastore_id      = "local-lvm"
    pre_enrolled_keys = true
    type              = "4m"
    file_format       = "raw"
  }
  agent {
    enabled = !local.init_agent_1
    wait_for_ip {
      disabled = true
    }
  }

  # Disks
  disk {
    interface    = "scsi0"
    datastore_id = "local-lvm"
    size         = 128
    discard      = "on"
    iothread     = true
    ssd          = true
    backup       = true
    replicate    = false
    aio          = "io_uring"
    file_format  = "raw"
  }

  # CPU
  cpu {
    cores = 3
    type  = "host"
  }

  # Memory
  memory {
    dedicated = 24576
  }

  # Network
  network_device {
    bridge      = "vmbr0"
    firewall    = false
    model       = "virtio"
    mac_address = "BC:24:11:40:12:78"
  }

  # Boot Order
  boot_order = local.init_agent_1 ? ["ide2", "scsi0", "net0"] : ["scsi0", "net0"]

  # CD Drive
  cdrom {
    interface = "ide2"
    file_id   = local.init_agent_1 ? "nfs:iso/ubuntu-26.04.1-live-server-amd64.iso" : "none"
  }

  # PCI Devices
  dynamic "hostpci" {
    for_each = local.init_agent_1 ? [] : [1]
    content {
      device = "hostpci0"
      id     = "0000:00:02"
      xvga   = false
      rombar = true
      pcie   = true
    }
  }

  # Serial Devices
  dynamic "serial_device" {
    for_each = local.init_agent_1 ? [] : [1]
    content {
      device = "socket"
    }
  }
}

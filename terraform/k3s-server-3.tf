variable "init_server_3" {
  type    = bool
  default = false
}

locals {
  init_server_3 = var.init_server_3 || var.initialize
}

resource "proxmox_virtual_environment_vm" "k3s-server-3" {
  lifecycle {
    ignore_changes = [initialization]
  }

  # General
  node_name = "beelink3"
  vm_id     = 113
  name      = "k3s-server-3"
  on_boot   = true

  # OS
  operating_system {
    type = "l26"
  }

  # System
  machine       = "pc"
  bios          = "seabios"
  scsi_hardware = "virtio-scsi-single"

  # Disks
  disk {
    interface    = "scsi0"
    datastore_id = "local-lvm"
    size         = 64
    discard      = "on"
    iothread     = true
    ssd          = true
    backup       = true
    replicate    = true
    aio          = "io_uring"
    file_format  = "raw"
  }

  # CPU
  cpu {
    cores = 2
    type  = "host"
  }

  # Memory
  memory {
    dedicated = 4096
  }

  # Network
  network_device {
    bridge      = "vmbr0"
    firewall    = true
    model       = "virtio"
    mac_address = "BC:24:11:9E:8D:3D"
  }

  # Boot Order
  boot_order = local.init_server_3 ? ["ide2", "scsi0", "net0"] : ["scsi0", "net0"]

  # CD Drive
  dynamic "cdrom" {
    for_each = local.init_server_3 ? [1] : []
    content {
      interface = "ide2"
      file_id   = "nfs:iso/ubuntu-24.04.4-live-server-amd64.iso"
    }
  }
}

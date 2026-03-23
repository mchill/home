variable "init_agent_3" {
  type    = bool
  default = false
}

locals {
  init_agent_3 = var.init_agent_3 || var.initialize
}

resource "proxmox_virtual_environment_vm" "k3s-agent-3" {
  lifecycle {
    ignore_changes = [initialization]
  }

  # General
  node_name = "beelink3"
  vm_id     = 123
  name      = "k3s-agent-3"
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
    cores = 4
    type  = "host"
  }

  # Memory
  memory {
    dedicated = 16384
  }

  # Network
  network_device {
    bridge      = "vmbr0"
    firewall    = true
    model       = "virtio"
    mac_address = "BC:24:11:63:EF:F5"
  }

  # Boot Order
  boot_order = local.init_agent_3 ? ["ide2", "scsi0", "net0"] : ["scsi0", "net0"]

  # CD Drive
  dynamic "cdrom" {
    for_each = local.init_agent_3 ? [1] : []
    content {
      interface = "ide2"
      file_id   = "nfs:iso/ubuntu-24.04.4-live-server-amd64.iso"
    }
  }

  # PCI Devices
  dynamic "hostpci" {
    for_each = local.init_agent_3 ? [] : [1]
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
    for_each = local.init_agent_3 ? [] : [1]
    content {
      device = "socket"
    }
  }
}

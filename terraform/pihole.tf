variable "init_pihole" {
  type    = bool
  default = false
}

locals {
  init_pihole = var.init_pihole || var.initialize
}

resource "proxmox_virtual_environment_vm" "pihole" {
  lifecycle {
    ignore_changes = [initialization]
  }

  # General
  node_name = "beelink1"
  vm_id     = 100
  name      = "pihole"
  on_boot   = true
  startup {
    order    = 1
    up_delay = 300
  }

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
    size         = 32
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
    cores    = 1
    type     = "host"
    affinity = "0-2"
  }

  # Memory
  memory {
    dedicated = 2048
  }

  # Network
  network_device {
    bridge      = "vmbr0"
    firewall    = false
    model       = "virtio"
    mac_address = "BC:24:11:67:19:E8"
  }

  # Boot Order
  boot_order = local.init_pihole ? ["ide2", "scsi0", "net0"] : ["scsi0", "net0"]

  # CD Drive
  dynamic "cdrom" {
    for_each = local.init_pihole ? [1] : []
    content {
      interface = "ide2"
      file_id   = "nfs:iso/ubuntu-24.04.4-live-server-amd64.iso"
    }
  }
}

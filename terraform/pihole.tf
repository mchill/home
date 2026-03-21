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
  machine       = "pc"
  bios          = "seabios"
  scsi_hardware = "virtio-scsi-single"

  # Disks
  disk {
    interface    = "scsi0"
    datastore_id = "local-lvm"
    size         = 32
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
    cores = 1
    type  = "host"
  }

  # Memory
  memory {
    dedicated = 2048
  }

  # Network
  network_device {
    bridge      = "vmbr0"
    firewall    = true
    model       = "virtio"
    mac_address = "BC:24:11:67:19:E8"
  }

  # Boot Order
  boot_order = ["scsi0", "net0"]
}

resource "proxmox_virtual_environment_vm" "k3s-server-2" {
  lifecycle {
    ignore_changes = [initialization]
  }

  # General
  node_name = "beelink2"
  vm_id     = 112
  name      = "k3s-server-2"
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
    mac_address = "BC:24:11:4E:69:98"
  }

  # Boot Order
  boot_order = ["scsi0", "net0"]
}

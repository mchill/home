terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "0.98.1"
    }
  }

  backend "s3" {
    bucket = "terraform-state"
    key    = "proxmox.tfstate"
    region = "us-east-1"
    endpoints = {
      s3 = "http://192.168.1.10:9000"
    }
    skip_credentials_validation = true
    skip_requesting_account_id  = true
    skip_metadata_api_check     = true
    skip_region_validation      = true
    skip_s3_checksum            = true
    force_path_style            = true
  }
}

provider "proxmox" {
  endpoint = "https://192.168.1.30:8006/"
  username = "root@pam"
  insecure = true
}

variable "initialize" {
  type    = bool
  default = false
}

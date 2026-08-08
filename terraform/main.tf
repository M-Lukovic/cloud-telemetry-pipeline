terraform {
  required_version = ">= 1.0.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

provider "local" {}

resource "local_file" "environment_config" {
  content  = "ENVIRONMENT=${var.environment}\nSERVICE_NAME=${var.service_name}\n"
  filename = "${path.module}/env_config.txt"
}

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Educational EC2 scaffold. Application deployment is intentionally out of scope.
resource "aws_security_group" "telemetry_sg" {
  name        = "${var.service_name}-${var.environment}-sg"
  description = "Allow public HTTP traffic to the telemetry EC2 scaffold"

  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 instance only; this resource does not install or run the application.
resource "aws_instance" "telemetry_server" {
  ami           = var.ami_id
  instance_type = var.instance_type

  vpc_security_group_ids = [aws_security_group.telemetry_sg.id]

  tags = {
    Name        = "${var.service_name}-${var.environment}"
    Environment = var.environment
  }
}

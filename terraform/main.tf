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
  region = "eu-central-1"
}

# Security Group za HTTP (80), Telemetry API (5000) i SSH (22)
resource "aws_security_group" "telemetry_sg" {
  name        = "telemetry-pipeline-sg"
  description = "Allow web and SSH traffic for telemetry app"

  ingress {
    description = "Allow HTTP"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow Telemetry API"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Allow SSH"
    from_port   = 22
    to_port     = 22
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

# AWS EC2 instanca za pokretanje aplikacije
resource "aws_instance" "telemetry_server" {
  ami           = "ami-008280f43988698f2" # Ubuntu 22.04 LTS u eu-central-1
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_security_group.telemetry_sg.id]

  tags = {
    Name        = "Telemetry-Pipeline-Server"
    Environment = "production"
  }
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.telemetry_server.public_ip
}

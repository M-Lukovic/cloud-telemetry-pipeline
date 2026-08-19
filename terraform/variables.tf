variable "environment" {
  type        = string
  default     = "development"
  description = "Deployment environment stage"
}

variable "service_name" {
  type        = string
  default     = "cloud-telemetry-pipeline"
  description = "Name of the microservice"
}

variable "aws_region" {
  type        = string
  default     = "eu-central-1"
  description = "AWS region for the EC2 scaffold"
}

variable "ami_id" {
  type        = string
  default     = "ami-008280f43988698f2"
  description = "AMI ID for the selected region; verify it before planning or applying"
}

variable "instance_type" {
  type        = string
  default     = "t2.micro"
  description = "EC2 instance type for the scaffold"
}

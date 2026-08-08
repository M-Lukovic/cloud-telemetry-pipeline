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

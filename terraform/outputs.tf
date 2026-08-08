output "config_file_path" {
  value       = local_file.environment_config.filename
  description = "Path to the generated environment configuration file"
}

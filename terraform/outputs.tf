output "server_public_ip" {
  description = "Public IP of the scaffolded AWS EC2 instance"
  value       = aws_instance.telemetry_server.public_ip
}

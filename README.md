# Cloud Telemetry Pipeline

A cloud infrastructure and observability project for collecting, exposing, and monitoring equipment telemetry using Python, Docker, Nginx, Prometheus, Grafana, Terraform, Kubernetes, and GitHub Actions.

## Architecture & Features

- **Python / Flask:** Exposes application status and Prometheus-compatible system and equipment metrics, including CPU, RAM, and simulated voltage telemetry.
- **Docker & Docker Compose:** Containerizes and orchestrates the application, Nginx, Prometheus, and Grafana services.
- **Nginx:** Acts as a reverse proxy and routes traffic to the application.
- **Prometheus:** Scrapes and stores telemetry and system metrics.
- **Grafana:** Visualizes collected metrics through monitoring dashboards.
- **Terraform:** Defines AWS infrastructure as code for repeatable cloud deployment.
- **Kubernetes:** Provides manifests for container orchestration and deployment.
- **GitHub Actions:** Runs automated CI checks and validates the project on repository changes.

## Telemetry Source

For now, the project uses simulated equipment data such as voltage, CPU, and RAM metrics.

The idea is to later replace the simulator with real telemetry coming from equipment through HTTP, MQTT, or a Modbus gateway. The rest of the monitoring stack can stay the same, so Prometheus and Grafana do not depend on where the data originally comes from.

## Project Structure

- `app/` - Python application and metrics endpoint
- `nginx/` - Reverse proxy configuration
- `prometheus/` - Prometheus configuration
- `grafana/` - Grafana provisioning and dashboards
- `terraform/` - AWS infrastructure as code
- `k8s/` - Kubernetes manifests
- `.github/workflows/` - CI workflows
- `docker-compose.yml` - Local multi-container setup

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/M-Lukovic/cloud-telemetry-pipeline.git
cd cloud-telemetry-pipeline
```

2. Start the monitoring stack:

```bash
docker compose up -d
```

3. Access the services:

- Main App: http://localhost/
- Metrics Endpoint: http://localhost/metrics
- Prometheus UI: http://localhost:9090
- Grafana Dashboard: http://localhost:3000

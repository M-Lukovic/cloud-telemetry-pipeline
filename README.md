# Cloud Telemetry Pipeline

A lightweight, containerized telemetry monitoring stack built with Python, Nginx, Prometheus, and Grafana.

## Architecture & Features
- Flask App: Exposes system metrics (CPU, RAM, custom voltage levels).
- Nginx: Acts as a reverse proxy routing traffic to the internal core application.
- Prometheus: Scrapes and collects metrics from the application inside the Docker network.
- Grafana: Visualizes metrics in real time via custom dashboards.

## Quick Start

1. Clone the repository:
git clone
cd cloud-telemetry-pipeline

2. Spin up the entire infrastructure:
docker compose up -d

3. Access the services:
- Main App: http://localhost/
- Metrics Endpoint: http://localhost/metrics
- Prometheus UI: http://localhost:9090
- Grafana Dashboard: http://localhost:3000

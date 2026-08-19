import logging
import os
import time

from flask import Flask, Response, g, jsonify, request
from prometheus_client import generate_latest, Gauge, CONTENT_TYPE_LATEST

from telemetry import create_telemetry_runtime

SERVICE_NAME = os.getenv('SERVICE_NAME', 'Telemetry Core Node')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=(
        'timestamp=%(asctime)s level=%(levelname)s '
        'logger=%(name)s message="%(message)s"'
    ),
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_mapping(
    SERVICE_NAME=SERVICE_NAME,
    SERVICE_VERSION=SERVICE_VERSION,
    READY=True,
)

telemetry_source, telemetry_state, telemetry_sampler, telemetry_mode, sample_interval = (
    create_telemetry_runtime()
)
app.config.from_mapping(
    TELEMETRY_MODE=telemetry_mode,
    TELEMETRY_SAMPLE_INTERVAL_SECONDS=sample_interval,
)

VOLTAGE_GAUGE = Gauge(
    'system_voltage_volts',
    'Simulated equipment operating voltage in volts',
)
CPU_GAUGE = Gauge(
    'system_cpu_usage_percent',
    'Host/container-visible CPU usage sampled by the telemetry source',
)
RAM_GAUGE = Gauge(
    'system_ram_usage_percent',
    'Host/container-visible RAM usage sampled by the telemetry source',
)


def publish_current_telemetry():
    """Copy the current stored sample to Prometheus gauges without sampling."""
    sample = telemetry_state.snapshot()
    VOLTAGE_GAUGE.set(sample.voltage_volts)
    CPU_GAUGE.set(sample.system_cpu_usage_percent)
    RAM_GAUGE.set(sample.system_ram_usage_percent)


@app.before_request
def start_request_timer():
    g.request_started_at = time.perf_counter()
    if not app.config['TESTING']:
        telemetry_sampler.start()


@app.after_request
def log_request(response):
    duration_ms = (time.perf_counter() - g.request_started_at) * 1000
    logger.info(
        'request_completed method=%s path=%s status=%s duration_ms=%.2f',
        request.method,
        request.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.route('/')
def home():
    return jsonify({
        "service": app.config['SERVICE_NAME'],
        "status": "HEALTHY",
        "version": app.config['SERVICE_VERSION']
    })


@app.get('/healthz')
def healthz():
    return jsonify({
        "status": "alive",
        "service": app.config['SERVICE_NAME'],
    }), 200


@app.get('/readyz')
def readyz():
    ready = app.config['READY']
    return jsonify({
        "status": "ready" if ready else "not_ready",
        "service": app.config['SERVICE_NAME'],
    }), 200 if ready else 503


@app.route('/metrics')
def metrics():
    publish_current_telemetry()
    return Response(generate_latest(), content_type=CONTENT_TYPE_LATEST)

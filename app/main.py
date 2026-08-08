import time
import random
import psutil
from flask import Flask, jsonify, Response
from prometheus_client import generate_latest, Gauge, CONTENT_TYPE_LATEST

app = Flask(__name__)

VOLTAGE_GAUGE = Gauge('system_voltage_volts', 'Current operating voltage of telemetry node')
CPU_GAUGE = Gauge('system_cpu_usage_percent', 'Current CPU usage in percent')
RAM_GAUGE = Gauge('system_ram_usage_percent', 'Current RAM usage in percent')

def update_metrics():
    VOLTAGE_GAUGE.set(round(random.uniform(225.0, 235.0), 2))
    CPU_GAUGE.set(psutil.cpu_percent())
    RAM_GAUGE.set(psutil.virtual_memory().percent)

@app.route('/')
def home():
    return jsonify({
        "service": "Telemetry Core Node",
        "status": "HEALTHY",
        "version": "1.0.0"
    })

@app.route('/metrics')
def metrics():
    update_metrics()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

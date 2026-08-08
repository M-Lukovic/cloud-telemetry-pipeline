import random
from flask import Flask, jsonify
from prometheus_client import generate_latest, Gauge, CONTENT_TYPE_LATEST

app = Flask(__name__)

VOLTAGE_GAUGE = Gauge('system_voltage_volts', 'Current operating voltage of telemetry node')

@app.route('/')
def home():
    return jsonify({
        "service": "Telemetry Core Node",
        "status": "HEALTHY",
        "version": "1.0.0"
    })

@app.route('/metrics')
def metrics():
    simulated_voltage = round(random.uniform(225.0, 235.0), 2)
    VOLTAGE_GAUGE.set(simulated_voltage)
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)



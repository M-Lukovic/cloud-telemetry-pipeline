import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_home_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == "HEALTHY"

def test_metrics_endpoint(client):
    response = client.get('/metrics')
    assert response.status_code == 200
    assert b"system_voltage_volts" in response.data
    assert b"system_cpu_usage_percent" in response.data
    assert b"system_ram_usage_percent" in response.data

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from prometheus_client import CONTENT_TYPE_LATEST

import main
from telemetry import (
    SIMULATED_VOLTAGE_MAX,
    SIMULATED_VOLTAGE_MIN,
    SimulatedTelemetrySource,
    TelemetrySample,
    TelemetryState,
    create_telemetry_runtime,
)

app = main.app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_endpoint(client):
    response = client.get('/')

    assert response.status_code == 200
    assert response.get_json() == {
        'service': 'Telemetry Core Node',
        'status': 'HEALTHY',
        'version': '1.0.0',
    }


def test_healthz_endpoint(client):
    response = client.get('/healthz')

    assert response.status_code == 200
    assert response.get_json() == {
        'service': 'Telemetry Core Node',
        'status': 'alive',
    }


def test_readyz_endpoint(client):
    response = client.get('/readyz')

    assert response.status_code == 200
    assert response.get_json() == {
        'service': 'Telemetry Core Node',
        'status': 'ready',
    }


def test_readyz_returns_503_when_application_is_not_ready(client):
    app.config['READY'] = False

    try:
        response = client.get('/readyz')
    finally:
        app.config['READY'] = True

    assert response.status_code == 503
    assert response.get_json() == {
        'service': 'Telemetry Core Node',
        'status': 'not_ready',
    }


def test_metrics_endpoint(client):
    response = client.get('/metrics')

    assert response.status_code == 200
    assert response.content_type == CONTENT_TYPE_LATEST
    assert b"system_voltage_volts" in response.data
    assert b"system_cpu_usage_percent" in response.data
    assert b"system_ram_usage_percent" in response.data


def test_simulated_source_returns_expected_fields(monkeypatch):
    monkeypatch.setattr('telemetry.random.uniform', lambda minimum, maximum: 230.25)
    monkeypatch.setattr('telemetry.psutil.cpu_percent', lambda: 12.5)
    monkeypatch.setattr(
        'telemetry.psutil.virtual_memory',
        lambda: SimpleNamespace(percent=34.5),
    )

    sample = SimulatedTelemetrySource().sample()

    assert sample == TelemetrySample(
        voltage_volts=230.25,
        system_cpu_usage_percent=12.5,
        system_ram_usage_percent=34.5,
    )


@pytest.mark.parametrize('voltage', [SIMULATED_VOLTAGE_MIN, SIMULATED_VOLTAGE_MAX])
def test_simulated_voltage_stays_in_documented_range(monkeypatch, voltage):
    monkeypatch.setattr(
        'telemetry.random.uniform',
        lambda minimum, maximum: voltage,
    )

    sample = SimulatedTelemetrySource().sample()

    assert SIMULATED_VOLTAGE_MIN <= sample.voltage_volts <= SIMULATED_VOLTAGE_MAX


def test_telemetry_state_can_be_updated():
    initial = TelemetrySample(230.0, 10.0, 20.0)
    updated = TelemetrySample(231.0, 11.0, 21.0)
    state = TelemetryState(initial)

    state.update(updated)

    assert state.snapshot() == updated


def test_metrics_exposes_current_state_without_sampling(client, monkeypatch):
    current = TelemetrySample(232.5, 17.0, 41.0)
    main.telemetry_state.update(current)
    sample_mock = Mock()
    monkeypatch.setattr(main.telemetry_source, 'sample', sample_mock)

    first_response = client.get('/metrics')
    second_response = client.get('/metrics')

    sample_mock.assert_not_called()
    for response in (first_response, second_response):
        assert b'system_voltage_volts 232.5' in response.data
        assert b'system_cpu_usage_percent 17.0' in response.data
        assert b'system_ram_usage_percent 41.0' in response.data


def test_invalid_telemetry_mode_fails_clearly():
    with pytest.raises(ValueError, match='Unsupported TELEMETRY_MODE'):
        create_telemetry_runtime({'TELEMETRY_MODE': 'mqtt'})


@pytest.mark.parametrize('interval', ['invalid', '0', '-1'])
def test_invalid_sample_interval_fails_clearly(interval):
    with pytest.raises(
        ValueError,
        match='TELEMETRY_SAMPLE_INTERVAL_SECONDS must be a positive number',
    ):
        create_telemetry_runtime({
            'TELEMETRY_MODE': 'simulated',
            'TELEMETRY_SAMPLE_INTERVAL_SECONDS': interval,
        })

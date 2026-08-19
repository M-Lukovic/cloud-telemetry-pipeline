import logging
import os
import random
import threading
from dataclasses import dataclass
from typing import Mapping, Protocol

import psutil

logger = logging.getLogger(__name__)

SIMULATED_VOLTAGE_MIN = 225.0
SIMULATED_VOLTAGE_MAX = 235.0
DEFAULT_SAMPLE_INTERVAL_SECONDS = 5.0


@dataclass(frozen=True)
class TelemetrySample:
    voltage_volts: float
    system_cpu_usage_percent: float
    system_ram_usage_percent: float


class TelemetrySource(Protocol):
    """Interface implemented by simulated or future physical telemetry sources."""

    def sample(self) -> TelemetrySample:
        """Acquire one telemetry sample."""


class SimulatedTelemetrySource:
    """Demo equipment voltage plus host/container-visible resource telemetry."""

    def sample(self) -> TelemetrySample:
        return TelemetrySample(
            voltage_volts=round(
                random.uniform(SIMULATED_VOLTAGE_MIN, SIMULATED_VOLTAGE_MAX),
                2,
            ),
            system_cpu_usage_percent=psutil.cpu_percent(),
            system_ram_usage_percent=psutil.virtual_memory().percent,
        )


class TelemetryState:
    """Thread-safe in-memory storage for the most recent telemetry sample."""

    def __init__(self, initial_sample: TelemetrySample):
        self._sample = initial_sample
        self._lock = threading.Lock()

    def update(self, sample: TelemetrySample) -> None:
        with self._lock:
            self._sample = sample

    def snapshot(self) -> TelemetrySample:
        with self._lock:
            return self._sample


class TelemetrySampler:
    """Periodically acquires samples and stores the latest one in memory."""

    def __init__(
        self,
        source: TelemetrySource,
        state: TelemetryState,
        interval_seconds: float,
    ):
        self._source = source
        self._state = state
        self._interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._lifecycle_lock = threading.Lock()
        self._thread = None

    def start(self) -> None:
        """Start at most one daemon sampling thread in this process."""
        with self._lifecycle_lock:
            if self._thread is not None and self._thread.is_alive():
                return

            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run,
                name='telemetry-sampler',
                daemon=True,
            )
            self._thread.start()
            logger.info(
                'telemetry_sampler_started interval_seconds=%s',
                self._interval_seconds,
            )

    def stop(self) -> None:
        """Signal the sampling thread to stop, primarily for controlled shutdown/tests."""
        self._stop_event.set()

    def _run(self) -> None:
        while not self._stop_event.wait(self._interval_seconds):
            try:
                self._state.update(self._source.sample())
            except Exception:
                logger.exception('telemetry_sample_failed')


def create_telemetry_runtime(
    environ: Mapping[str, str] | None = None,
) -> tuple[TelemetrySource, TelemetryState, TelemetrySampler, str, float]:
    """Build the configured source, state store, and sampler for one process."""
    config = os.environ if environ is None else environ
    mode = config.get('TELEMETRY_MODE', 'simulated').strip().lower()

    if mode != 'simulated':
        raise ValueError(
            f"Unsupported TELEMETRY_MODE '{mode}'. Supported modes: simulated"
        )

    raw_interval = config.get(
        'TELEMETRY_SAMPLE_INTERVAL_SECONDS',
        str(DEFAULT_SAMPLE_INTERVAL_SECONDS),
    )
    try:
        interval_seconds = float(raw_interval)
    except ValueError as exc:
        raise ValueError(
            'TELEMETRY_SAMPLE_INTERVAL_SECONDS must be a positive number'
        ) from exc

    if interval_seconds <= 0:
        raise ValueError(
            'TELEMETRY_SAMPLE_INTERVAL_SECONDS must be a positive number'
        )

    source = SimulatedTelemetrySource()
    state = TelemetryState(source.sample())
    sampler = TelemetrySampler(source, state, interval_seconds)
    return source, state, sampler, mode, interval_seconds

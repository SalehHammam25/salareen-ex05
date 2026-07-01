"""Timing and memory measurement harness for LLM inference.

Measures TTFT, TPOT, throughput (tokens/sec), and peak RSS memory.
"""

from __future__ import annotations

import threading
import time
import dataclasses
from dataclasses import dataclass
from typing import Optional

import psutil


@dataclass
class InferenceMetrics:
    model_id: str
    method: str  # e.g. "baseline", "gguf_q4", "airllm", "int8"
    ttft_sec: Optional[float] = None
    tpot_sec: Optional[float] = None
    throughput_tok_per_sec: Optional[float] = None
    peak_ram_mb: Optional[float] = None
    baseline_ram_mb: Optional[float] = None
    total_tokens_generated: int = 0
    total_runtime_sec: Optional[float] = None
    prompt_tokens: int = 0
    error: Optional[str] = None
    notes: str = ""

    @property
    def ram_delta_mb(self) -> Optional[float]:
        if self.peak_ram_mb is not None and self.baseline_ram_mb is not None:
            return self.peak_ram_mb - self.baseline_ram_mb
        return None

    def as_dict(self) -> dict:
        d = dataclasses.asdict(self)
        d["ram_delta_mb"] = self.ram_delta_mb  # property not captured by asdict
        return d


class RamSampler:
    """Samples process RSS every `interval_sec` seconds in a background thread."""

    def __init__(self, interval_sec: float = 0.5):
        self.interval_sec = interval_sec
        self._samples: list[float] = []
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._proc = psutil.Process()

    def start(self) -> None:
        self._stop.clear()
        self._samples.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def peak_mb(self) -> float:
        return max(self._samples) / 1024**2 if self._samples else 0.0

    def current_mb(self) -> float:
        return self._proc.memory_info().rss / 1024**2

    def _run(self) -> None:
        while not self._stop.is_set():
            try:
                self._samples.append(self._proc.memory_info().rss)
            except psutil.NoSuchProcess:
                break
            self._stop.wait(self.interval_sec)


class TokenTimer:
    """Records timestamps for each generated token to compute TTFT and TPOT."""

    def __init__(self):
        self._start: Optional[float] = None
        self._token_times: list[float] = []

    def start(self) -> None:
        self._start = time.perf_counter()
        self._token_times.clear()

    def record_token(self) -> None:
        self._token_times.append(time.perf_counter())

    @property
    def ttft(self) -> Optional[float]:
        if self._start is None or not self._token_times:
            return None
        return self._token_times[0] - self._start

    @property
    def tpot(self) -> Optional[float]:
        if len(self._token_times) < 2:
            return None
        deltas = [b - a for a, b in zip(self._token_times[:-1], self._token_times[1:])]
        return sum(deltas) / len(deltas)

    @property
    def throughput(self) -> Optional[float]:
        if self._start is None or not self._token_times:
            return None
        total_time = self._token_times[-1] - self._start
        return len(self._token_times) / total_time if total_time > 0 else None


def compute_metrics(
    model_id: str,
    method: str,
    token_timer: TokenTimer,
    ram_sampler: RamSampler,
    baseline_ram_mb: float,
    prompt_tokens: int = 0,
    notes: str = "",
) -> InferenceMetrics:
    """Build an InferenceMetrics from a completed timer and sampler."""
    return InferenceMetrics(
        model_id=model_id,
        method=method,
        ttft_sec=token_timer.ttft,
        tpot_sec=token_timer.tpot,
        throughput_tok_per_sec=token_timer.throughput,
        peak_ram_mb=ram_sampler.peak_mb(),
        baseline_ram_mb=baseline_ram_mb,
        total_tokens_generated=len(token_timer._token_times),
        total_runtime_sec=(
            token_timer._token_times[-1] - token_timer._start
            if token_timer._token_times and token_timer._start
            else None
        ),
        prompt_tokens=prompt_tokens,
        notes=notes,
    )

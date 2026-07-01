"""Unit tests for metrics.py — timing and memory helpers.

All tests run without any model downloads or external dependencies.
"""

import time

import pytest

from salareen_ex05.metrics import (
    InferenceMetrics,
    RamSampler,
    TokenTimer,
    compute_metrics,
)


# ---------------------------------------------------------------------------
# InferenceMetrics
# ---------------------------------------------------------------------------

def test_inference_metrics_ram_delta():
    m = InferenceMetrics(model_id="test", method="baseline", peak_ram_mb=1024.0, baseline_ram_mb=512.0)
    assert m.ram_delta_mb == pytest.approx(512.0)


def test_inference_metrics_ram_delta_none_when_missing():
    m = InferenceMetrics(model_id="test", method="baseline", peak_ram_mb=None, baseline_ram_mb=512.0)
    assert m.ram_delta_mb is None


def test_inference_metrics_as_dict_keys():
    m = InferenceMetrics(model_id="phi3", method="gguf")
    d = m.as_dict()
    for key in ("model_id", "method", "ttft_sec", "tpot_sec", "throughput_tok_per_sec",
                 "peak_ram_mb", "baseline_ram_mb", "ram_delta_mb", "total_tokens_generated",
                 "total_runtime_sec", "prompt_tokens", "error", "notes"):
        assert key in d, f"Missing key: {key}"


# ---------------------------------------------------------------------------
# TokenTimer
# ---------------------------------------------------------------------------

def test_token_timer_ttft():
    timer = TokenTimer()
    timer.start()
    time.sleep(0.05)
    timer.record_token()
    assert timer.ttft is not None
    assert timer.ttft >= 0.04  # at least 40 ms


def test_token_timer_tpot():
    timer = TokenTimer()
    timer.start()
    for _ in range(5):
        time.sleep(0.02)
        timer.record_token()
    assert timer.tpot is not None
    assert timer.tpot >= 0.01


def test_token_timer_throughput():
    timer = TokenTimer()
    timer.start()
    for _ in range(10):
        time.sleep(0.01)
        timer.record_token()
    assert timer.throughput is not None
    assert timer.throughput > 0


def test_token_timer_no_tokens():
    timer = TokenTimer()
    timer.start()
    assert timer.ttft is None
    assert timer.tpot is None
    assert timer.throughput is None


def test_token_timer_single_token_no_tpot():
    timer = TokenTimer()
    timer.start()
    timer.record_token()
    assert timer.ttft is not None
    assert timer.tpot is None  # need at least 2 tokens for TPOT


# ---------------------------------------------------------------------------
# RamSampler
# ---------------------------------------------------------------------------

def test_ram_sampler_records_positive_peak():
    sampler = RamSampler(interval_sec=0.05)
    sampler.start()
    time.sleep(0.15)
    sampler.stop()
    assert sampler.peak_mb() > 0


def test_ram_sampler_current_mb_positive():
    sampler = RamSampler()
    assert sampler.current_mb() > 0


# ---------------------------------------------------------------------------
# compute_metrics integration
# ---------------------------------------------------------------------------

def test_compute_metrics_assembles_correctly():
    timer = TokenTimer()
    timer.start()
    for _ in range(3):
        time.sleep(0.01)
        timer.record_token()

    sampler = RamSampler(interval_sec=0.05)
    sampler.start()
    time.sleep(0.1)
    sampler.stop()

    result = compute_metrics(
        model_id="test-model",
        method="baseline",
        token_timer=timer,
        ram_sampler=sampler,
        baseline_ram_mb=100.0,
        prompt_tokens=10,
        notes="unit test",
    )

    assert result.model_id == "test-model"
    assert result.method == "baseline"
    assert result.total_tokens_generated == 3
    assert result.ttft_sec is not None and result.ttft_sec >= 0
    assert result.peak_ram_mb is not None and result.peak_ram_mb > 0
    assert result.baseline_ram_mb == pytest.approx(100.0)
    assert result.prompt_tokens == 10

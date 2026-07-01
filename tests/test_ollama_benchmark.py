"""Tests for ollama_benchmark.py — all HTTP calls are mocked; no real Ollama required."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from salareen_ex05.ollama_benchmark import (
    OllamaBenchmarkResult,
    _parse_response,
    run_benchmark,
    run_single,
    save_results,
)

# ---------------------------------------------------------------------------
# Shared fixture: a realistic Ollama /api/generate response
# ---------------------------------------------------------------------------
MOCK_RESPONSE = {
    "model": "qwen2.5:0.5b",
    "response": "Prefill processes all prompt tokens in parallel. Decode generates one token at a time.",
    "done": True,
    "total_duration": 5_000_000_000,
    "load_duration": 500_000_000,
    "prompt_eval_count": 30,
    "prompt_eval_duration": 1_000_000_000,
    "eval_count": 18,
    "eval_duration": 3_000_000_000,
}


def _make_mock_response(data: dict) -> MagicMock:
    m = MagicMock()
    m.json.return_value = data
    m.raise_for_status.return_value = None
    return m


# ---------------------------------------------------------------------------
# _parse_response
# ---------------------------------------------------------------------------

def test_parse_response_tokens_per_sec():
    r = _parse_response("m", 1, "prompt text", MOCK_RESPONSE, 5.0, 100.0, 120.0)
    assert r.tokens_per_sec == pytest.approx(18 / 3.0)


def test_parse_response_ram_delta():
    r = _parse_response("m", 1, "prompt text", MOCK_RESPONSE, 5.0, 100.0, 120.0)
    assert r.ram_delta_mb == pytest.approx(20.0)


def test_parse_response_no_eval_duration_gives_none_tps():
    raw = {**MOCK_RESPONSE, "eval_duration": 0}
    r = _parse_response("m", 1, "prompt", raw, 5.0, 100.0, 110.0)
    assert r.tokens_per_sec is None


def test_parse_response_fields_populated():
    r = _parse_response("qwen2.5:0.5b", 2, "hi", MOCK_RESPONSE, 5.0, 200.0, 210.0)
    assert r.eval_count == 18
    assert r.prompt_eval_count == 30
    assert r.error is None
    assert r.run_index == 2


# ---------------------------------------------------------------------------
# run_single
# ---------------------------------------------------------------------------

@patch("salareen_ex05.ollama_benchmark.requests.post")
def test_run_single_success(mock_post):
    mock_post.return_value = _make_mock_response(MOCK_RESPONSE)
    r = run_single("qwen2.5:0.5b", "test prompt")
    assert r.error is None
    assert r.tokens_per_sec is not None and r.tokens_per_sec > 0
    assert r.response_chars > 0


@patch("salareen_ex05.ollama_benchmark.requests.post")
def test_run_single_connection_error_returns_error_result(mock_post):
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("Connection refused")
    r = run_single("qwen2.5:0.5b", "test")
    assert r.error is not None
    assert "ollama" in r.error.lower()


@patch("salareen_ex05.ollama_benchmark.requests.post")
def test_run_single_generic_exception_captured(mock_post):
    mock_post.side_effect = RuntimeError("unexpected error")
    r = run_single("qwen2.5:0.5b", "test")
    assert r.error is not None
    assert "unexpected error" in r.error


# ---------------------------------------------------------------------------
# run_benchmark
# ---------------------------------------------------------------------------

@patch("salareen_ex05.ollama_benchmark.requests.post")
def test_run_benchmark_returns_all_runs(mock_post):
    mock_post.return_value = _make_mock_response(MOCK_RESPONSE)
    results = run_benchmark("qwen2.5:0.5b", "test prompt", runs=3)
    assert len(results) == 3
    assert all(r.error is None for r in results)


@patch("salareen_ex05.ollama_benchmark.requests.post")
def test_run_benchmark_stops_on_first_error(mock_post):
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("refused")
    results = run_benchmark("qwen2.5:0.5b", "test", runs=5)
    assert len(results) == 1
    assert results[0].error is not None


# ---------------------------------------------------------------------------
# save_results
# ---------------------------------------------------------------------------

def test_save_results_creates_json_and_csv(tmp_path, monkeypatch):
    import salareen_ex05.ollama_benchmark as mod
    monkeypatch.setattr(mod, "RESULTS_DIR", tmp_path)

    results = [
        OllamaBenchmarkResult(
            model="qwen2.5:0.5b", run_index=1, prompt_chars=50,
            response_chars=80, total_runtime_sec=4.5,
            eval_count=18, tokens_per_sec=6.0,
        )
    ]
    json_path, csv_path = save_results(results, "test_stem")
    assert json_path.exists()
    assert csv_path.exists()

    data = json.loads(json_path.read_text())
    assert len(data) == 1
    assert data[0]["model"] == "qwen2.5:0.5b"
    assert data[0]["tokens_per_sec"] == pytest.approx(6.0)

"""Tests for plots.py — file loading and figure generation (no real Ollama needed)."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from salareen_ex05.plots import benchmark_summary, load_results

# ---------------------------------------------------------------------------
# Sample data matching the Ollama benchmark CSV schema
# ---------------------------------------------------------------------------
SAMPLE_ROWS = [
    {
        "model": "qwen2.5:0.5b",
        "run_index": "1",
        "prompt_chars": "200",
        "response_chars": "85",
        "total_runtime_sec": "4.5",
        "tokens_per_sec": "6.2",
        "ram_before_mb": "200.0",
        "ram_after_mb": "210.0",
        "ram_delta_mb": "10.0",
        "eval_count": "18",
        "error": "",
    },
    {
        "model": "qwen2.5:0.5b",
        "run_index": "2",
        "prompt_chars": "200",
        "response_chars": "82",
        "total_runtime_sec": "4.3",
        "tokens_per_sec": "6.5",
        "ram_before_mb": "210.0",
        "ram_after_mb": "218.0",
        "ram_delta_mb": "8.0",
        "eval_count": "17",
        "error": "",
    },
]


def _write_csv(path: Path, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


# ---------------------------------------------------------------------------
# load_results — CSV
# ---------------------------------------------------------------------------

def test_load_results_csv_returns_list(tmp_path):
    p = tmp_path / "results.csv"
    _write_csv(p, SAMPLE_ROWS)
    rows = load_results(p)
    assert isinstance(rows, list)
    assert len(rows) == 2


def test_load_results_csv_field_values(tmp_path):
    p = tmp_path / "results.csv"
    _write_csv(p, SAMPLE_ROWS)
    rows = load_results(p)
    assert rows[0]["model"] == "qwen2.5:0.5b"
    assert rows[0]["tokens_per_sec"] == "6.2"
    assert rows[1]["run_index"] == "2"


def test_load_results_csv_single_row(tmp_path):
    p = tmp_path / "single.csv"
    _write_csv(p, [SAMPLE_ROWS[0]])
    rows = load_results(p)
    assert len(rows) == 1


# ---------------------------------------------------------------------------
# load_results — JSON
# ---------------------------------------------------------------------------

def test_load_results_json_returns_list(tmp_path):
    data = [{"model": "qwen2.5:0.5b", "tokens_per_sec": 6.2, "total_runtime_sec": 4.5}]
    p = tmp_path / "results.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    rows = load_results(p)
    assert len(rows) == 1
    assert rows[0]["tokens_per_sec"] == pytest.approx(6.2)


def test_load_results_json_preserves_types(tmp_path):
    data = [{"run_index": 1, "tokens_per_sec": 6.2, "ram_delta_mb": 10.5}]
    p = tmp_path / "results.json"
    p.write_text(json.dumps(data), encoding="utf-8")
    rows = load_results(p)
    assert isinstance(rows[0]["tokens_per_sec"], float)


# ---------------------------------------------------------------------------
# benchmark_summary figure generation
# ---------------------------------------------------------------------------

def test_benchmark_summary_creates_png(tmp_path, monkeypatch):
    import salareen_ex05.plots as mod
    monkeypatch.setattr(mod, "FIGURES_DIR", tmp_path)
    out = benchmark_summary(SAMPLE_ROWS, stem="test_bench")
    assert out.exists()
    assert out.suffix == ".png"
    assert "test_bench" in out.name


def test_benchmark_summary_single_row(tmp_path, monkeypatch):
    import salareen_ex05.plots as mod
    monkeypatch.setattr(mod, "FIGURES_DIR", tmp_path)
    out = benchmark_summary([SAMPLE_ROWS[0]], stem="single_run")
    assert out.exists()


def test_benchmark_summary_none_values_do_not_crash(tmp_path, monkeypatch):
    import salareen_ex05.plots as mod
    monkeypatch.setattr(mod, "FIGURES_DIR", tmp_path)
    rows = [{"run_index": "1", "tokens_per_sec": None, "total_runtime_sec": "", "ram_delta_mb": None}]
    out = benchmark_summary(rows, stem="missing_vals")
    assert out.exists()


def test_benchmark_summary_from_csv_file(tmp_path, monkeypatch):
    import salareen_ex05.plots as mod
    monkeypatch.setattr(mod, "FIGURES_DIR", tmp_path)
    csv_path = tmp_path / "bench.csv"
    _write_csv(csv_path, SAMPLE_ROWS)
    rows = load_results(csv_path)
    out = benchmark_summary(rows, stem=csv_path.stem)
    assert out.exists()

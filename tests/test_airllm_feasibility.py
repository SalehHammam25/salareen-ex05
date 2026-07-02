"""Tests for airllm_feasibility.py — AirLLM/torch are simulated via sys.modules,
no real AirLLM install or model download required.
"""

from __future__ import annotations

import sys
import types

from salareen_ex05.airllm_feasibility import (
    FeasibilityReport,
    _check_airllm,
    _check_cuda,
    _evaluate,
    collect,
    format_report,
    save_report,
)


def test_check_airllm_not_installed(monkeypatch):
    monkeypatch.setitem(sys.modules, "airllm", None)
    importable, version = _check_airllm()
    assert importable is False
    assert version is None


def test_check_airllm_installed(monkeypatch):
    fake = types.ModuleType("airllm")
    fake.__version__ = "2.0.0"
    monkeypatch.setitem(sys.modules, "airllm", fake)
    importable, version = _check_airllm()
    assert importable is True
    assert version == "2.0.0"


def test_check_cuda_no_torch(monkeypatch):
    monkeypatch.setitem(sys.modules, "torch", None)
    assert _check_cuda() is False


def test_evaluate_not_importable_recommends_no_download():
    notes, likely_compatible, next_action = _evaluate(
        os_name="Windows", cuda_available=False, airllm_importable=False,
        ram_available_gb=6.0, disk_free_gb=20.0,
    )
    assert likely_compatible is False
    assert "not installed" in " ".join(notes).lower()
    assert "do not download" in next_action.lower()


def test_evaluate_importable_no_cuda_still_not_compatible():
    notes, likely_compatible, next_action = _evaluate(
        os_name="Windows", cuda_available=False, airllm_importable=True,
        ram_available_gb=6.0, disk_free_gb=20.0,
    )
    assert likely_compatible is False
    assert any("cuda" in n.lower() for n in notes)
    assert "cpu-only" in next_action.lower()


def test_evaluate_low_disk_flagged():
    notes, _, _ = _evaluate(
        os_name="Windows", cuda_available=True, airllm_importable=True,
        ram_available_gb=16.0, disk_free_gb=5.0,
    )
    assert any("disk" in n.lower() for n in notes)


def test_evaluate_cuda_and_airllm_present_is_likely_compatible():
    _, likely_compatible, _ = _evaluate(
        os_name="Linux", cuda_available=True, airllm_importable=True,
        ram_available_gb=16.0, disk_free_gb=50.0,
    )
    assert likely_compatible is True


def test_collect_returns_report(monkeypatch):
    monkeypatch.setitem(sys.modules, "airllm", None)
    monkeypatch.setitem(sys.modules, "torch", None)
    report = collect()
    assert isinstance(report, FeasibilityReport)
    assert report.airllm_importable is False
    assert report.cuda_available is False
    assert report.likely_compatible is False


def test_format_report_contains_key_fields(monkeypatch):
    monkeypatch.setitem(sys.modules, "airllm", None)
    monkeypatch.setitem(sys.modules, "torch", None)
    text = format_report(collect())
    assert "AirLLM Feasibility Report" in text
    assert "Recommended next action" in text


def test_save_report_creates_txt_and_json(tmp_path, monkeypatch):
    monkeypatch.setitem(sys.modules, "airllm", None)
    monkeypatch.setitem(sys.modules, "torch", None)
    report = collect()
    txt_path, json_path = save_report(report, results_dir=tmp_path)
    assert txt_path.exists()
    assert json_path.exists()
    assert "AirLLM" in txt_path.read_text(encoding="utf-8")

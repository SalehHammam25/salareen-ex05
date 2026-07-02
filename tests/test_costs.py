"""Tests for costs.py — economic model (assumption-based). Fast, no internet/API calls."""

from __future__ import annotations

import json

import pytest

from salareen_ex05.costs import (
    ApiCostConfig,
    OnPremCostConfig,
    api_monthly_cost,
    breakeven_curve_data,
    breakeven_volume,
    onprem_monthly_cost,
    print_comparison,
    save_results,
)

API_CFG = ApiCostConfig("Test API", input_price_per_m=1.0, output_price_per_m=2.0)
ONPREM_CFG = OnPremCostConfig(
    hardware_purchase_usd=600.0, depreciation_years=2.0,
    avg_power_watts=20.0, electricity_usd_per_kwh=0.10,
)


def test_api_monthly_cost_computes_input_and_output():
    r = api_monthly_cost(API_CFG, monthly_input_tokens=1_000_000, monthly_output_tokens=500_000)
    assert r.monthly_cost_usd == pytest.approx(1.0 + 1.0)  # 1M*$1 + 0.5M*$2


def test_api_monthly_cost_zero_tokens_gives_zero_cost_per_1k():
    r = api_monthly_cost(API_CFG, 0, 0)
    assert r.monthly_cost_usd == 0.0
    assert r.cost_per_1k_tokens_usd == 0.0


def test_onprem_monthly_cost_includes_hardware_amortisation():
    r = onprem_monthly_cost(ONPREM_CFG, monthly_output_tokens=100_000, tokens_per_sec=10.0)
    expected_hardware = 600.0 / (2.0 * 12)
    assert r.monthly_cost_usd >= expected_hardware


def test_onprem_monthly_cost_scales_with_inference_time():
    slow = onprem_monthly_cost(ONPREM_CFG, 100_000, tokens_per_sec=1.0)
    fast = onprem_monthly_cost(ONPREM_CFG, 100_000, tokens_per_sec=100.0)
    assert slow.monthly_cost_usd > fast.monthly_cost_usd


def test_onprem_monthly_cost_zero_output_gives_zero_cost_per_1k():
    r = onprem_monthly_cost(ONPREM_CFG, monthly_output_tokens=0, tokens_per_sec=10.0)
    assert r.cost_per_1k_tokens_usd == 0.0


def test_onprem_monthly_cost_falls_back_to_fixed_hours_when_tps_zero():
    r = onprem_monthly_cost(ONPREM_CFG, monthly_output_tokens=100_000, tokens_per_sec=0.0)
    assert f"hrs={ONPREM_CFG.inference_hours_per_month:.1f}" in r.notes


def test_breakeven_volume_is_positive_and_bounded():
    bev = breakeven_volume(API_CFG, ONPREM_CFG, tokens_per_sec=10.0)
    assert 0 < bev < 100_000_000


def test_breakeven_volume_beyond_point_onprem_is_cheaper():
    bev = breakeven_volume(API_CFG, ONPREM_CFG, tokens_per_sec=10.0)
    out = int(bev * 0.167)
    api = api_monthly_cost(API_CFG, bev - out, out)
    onp = onprem_monthly_cost(ONPREM_CFG, out, tokens_per_sec=10.0)
    assert onp.monthly_cost_usd <= api.monthly_cost_usd * 1.05  # near break-even, small tolerance


def test_breakeven_curve_data_shapes_match():
    volumes, api_costs, onprem_costs = breakeven_curve_data(
        API_CFG, ONPREM_CFG, tokens_per_sec=10.0, max_tokens=1_000_000, steps=10
    )
    assert len(volumes) == len(api_costs) == len(onprem_costs) == 10
    assert volumes == sorted(volumes)


def test_print_comparison_returns_results_and_breakeven(capsys):
    api_r, onprem_r, bev = print_comparison(API_CFG, ONPREM_CFG, 1_000_000, 200_000, 10.0)
    out = capsys.readouterr().out
    assert "DRAFT" in out
    assert "verify API pricing" in out
    assert api_r.provider_or_method == "Test API"
    assert onprem_r.provider_or_method == "On-Prem CPU"
    assert bev > 0


def test_save_results_creates_json_and_csv_with_assumptions(tmp_path, monkeypatch):
    import salareen_ex05.costs as mod
    monkeypatch.setattr(mod, "RESULTS_DIR", tmp_path)

    api_r = api_monthly_cost(API_CFG, 1_000_000, 200_000)
    onprem_r = onprem_monthly_cost(ONPREM_CFG, 200_000, 10.0)
    json_path, csv_path = save_results(API_CFG, ONPREM_CFG, api_r, onprem_r, breakeven_tokens=12345)

    assert json_path.exists()
    assert csv_path.exists()

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["breakeven_monthly_tokens"] == 12345
    assert "unverified" in payload["assumptions"]["warning"].lower()
    assert payload["assumptions"]["api"]["provider"] == "Test API"
    assert len(payload["results"]) == 2

    csv_text = csv_path.read_text(encoding="utf-8")
    assert "Test API" in csv_text
    assert "On-Prem CPU" in csv_text

"""Economic model: on-premises CPU inference vs. external LLM API.

DRAFT / ASSUMPTION-BASED. API prices here are configurable placeholders, not
verified pricing — no external API calls are made. Confirm current public
pricing before treating any output of this module as final. On-prem
hardware/electricity figures are likewise assumptions, not measurements.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path

RESULTS_DIR = Path(__file__).parent.parent.parent / "results"
# ASSUMED default API pricing (USD / 1M tokens) — placeholders, NOT verified.
ASSUMED_API_INPUT_PER_M = 0.25
ASSUMED_API_OUTPUT_PER_M = 1.25
ASSUMED_API_NAME = "Generic API (assumed pricing — unverified)"


@dataclass
class ApiCostConfig:
    provider: str
    input_price_per_m: float   # USD per 1M input tokens — ASSUMPTION unless verified=True
    output_price_per_m: float  # USD per 1M output tokens — ASSUMPTION unless verified=True


@dataclass
class OnPremCostConfig:
    hardware_purchase_usd: float = 800.0
    depreciation_years: float = 3.0
    avg_power_watts: float = 15.0
    electricity_usd_per_kwh: float = 0.12
    inference_hours_per_month: float = 10.0


@dataclass
class CostResult:
    provider_or_method: str
    monthly_input_tokens: int
    monthly_output_tokens: int
    monthly_cost_usd: float
    cost_per_1k_tokens_usd: float
    notes: str = ""


def api_monthly_cost(
    cfg: ApiCostConfig, monthly_input_tokens: int, monthly_output_tokens: int
) -> CostResult:
    """Compute monthly API cost from token volumes and the (assumed) per-1M prices."""
    total = (monthly_input_tokens / 1_000_000) * cfg.input_price_per_m
    total += (monthly_output_tokens / 1_000_000) * cfg.output_price_per_m
    total_tokens = monthly_input_tokens + monthly_output_tokens
    cost_per_1k = (total / total_tokens * 1000) if total_tokens else 0.0
    return CostResult(cfg.provider, monthly_input_tokens, monthly_output_tokens, total, cost_per_1k)


def onprem_monthly_cost(
    cfg: OnPremCostConfig, monthly_output_tokens: int, tokens_per_sec: float
) -> CostResult:
    """Compute on-prem monthly cost (hardware amortisation + electricity)."""
    monthly_hardware = cfg.hardware_purchase_usd / (cfg.depreciation_years * 12)
    if tokens_per_sec > 0:
        inference_hours = (monthly_output_tokens / tokens_per_sec) / 3600
    else:
        inference_hours = cfg.inference_hours_per_month
    kwh_used = (cfg.avg_power_watts / 1000) * inference_hours
    monthly_electricity = kwh_used * cfg.electricity_usd_per_kwh
    total = monthly_hardware + monthly_electricity
    cost_per_1k = (total / monthly_output_tokens * 1000) if monthly_output_tokens else 0.0
    notes = f"hw=${monthly_hardware:.2f} elec=${monthly_electricity:.4f} hrs={inference_hours:.1f}"
    return CostResult("On-Prem CPU", 0, monthly_output_tokens, total, cost_per_1k, notes)


def breakeven_volume(
    api_cfg: ApiCostConfig, onprem_cfg: OnPremCostConfig,
    tokens_per_sec: float, output_fraction: float = 0.167,
) -> int:
    """Binary search for the monthly token volume where on-prem beats API cost."""
    lo, hi = 1, 100_000_000
    for _ in range(40):
        mid = (lo + hi) // 2
        out = int(mid * output_fraction)
        api = api_monthly_cost(api_cfg, mid - out, out)
        onp = onprem_monthly_cost(onprem_cfg, out, tokens_per_sec)
        lo, hi = (lo, mid) if onp.monthly_cost_usd < api.monthly_cost_usd else (mid, hi)
    return lo


def breakeven_curve_data(
    api_cfg: ApiCostConfig, onprem_cfg: OnPremCostConfig, tokens_per_sec: float,
    output_fraction: float = 0.167, max_tokens: int = 5_000_000, steps: int = 25,
) -> tuple[list[int], list[float], list[float]]:
    """Return (volumes, api_costs, onprem_costs) sampled for a break-even chart."""
    volumes = [max(1, int(max_tokens * i / steps)) for i in range(1, steps + 1)]
    api_costs, onprem_costs = [], []
    for v in volumes:
        out = int(v * output_fraction)
        api_costs.append(api_monthly_cost(api_cfg, v - out, out).monthly_cost_usd)
        onprem_costs.append(onprem_monthly_cost(onprem_cfg, out, tokens_per_sec).monthly_cost_usd)
    return volumes, api_costs, onprem_costs


def save_results(
    api_cfg: ApiCostConfig, onprem_cfg: OnPremCostConfig,
    api_result: CostResult, onprem_result: CostResult, breakeven_tokens: int,
    stem: str = "economic_analysis",
) -> tuple[Path, Path]:
    """Save the analysis as JSON (full detail incl. assumptions) and CSV (cost rows)."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "assumptions": {
            "api": asdict(api_cfg),
            "onprem": asdict(onprem_cfg),
            "warning": "API prices are unverified; confirm against the provider's pricing page.",
        },
        "breakeven_monthly_tokens": breakeven_tokens,
        "results": [asdict(api_result), asdict(onprem_result)],
    }
    json_path = RESULTS_DIR / f"{stem}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    rows = [asdict(api_result), asdict(onprem_result)]
    csv_path = RESULTS_DIR / f"{stem}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)
    return json_path, csv_path


def print_comparison(
    api_cfg: ApiCostConfig, onprem_cfg: OnPremCostConfig,
    monthly_input: int, monthly_output: int, tokens_per_sec: float,
) -> tuple[CostResult, CostResult, int]:
    """Print a cost comparison table. Returns (api_result, onprem_result, breakeven_tokens)."""
    api = api_monthly_cost(api_cfg, monthly_input, monthly_output)
    onprem = onprem_monthly_cost(onprem_cfg, monthly_output, tokens_per_sec)
    bev = breakeven_volume(api_cfg, onprem_cfg, tokens_per_sec)
    print("\n=== Monthly Cost Comparison — DRAFT (unverified API pricing) ===")
    print(f"Workload: {monthly_input:,} input + {monthly_output:,} output tokens/month\n")
    for r in (api, onprem):
        m, k = r.monthly_cost_usd, r.cost_per_1k_tokens_usd
        print(f"{r.provider_or_method:<18} ${m:>8.2f} ${k:>6.4f}/1k")
    print(f"  ({onprem.notes})\nBreak-even vs {api_cfg.provider}: ~{bev:,} tokens/month")
    print("NOTE: verify API pricing before final submission.\n")
    return api, onprem, bev

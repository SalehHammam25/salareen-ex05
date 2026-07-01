"""Economic model: on-premises CPU inference vs. external LLM API.

Computes monthly cost for both strategies and finds the break-even
token volume. All prices are configurable; defaults use representative
2025/2026 public pricing.
"""

from __future__ import annotations

from dataclasses import dataclass

# API pricing defaults (USD per 1 M tokens, mid-2026 public listings)
ANTHROPIC_HAIKU_INPUT_PER_M = 0.25   # Claude 3 Haiku input
ANTHROPIC_HAIKU_OUTPUT_PER_M = 1.25  # Claude 3 Haiku output
OPENAI_4O_MINI_INPUT_PER_M = 0.15    # GPT-4o-mini input
OPENAI_4O_MINI_OUTPUT_PER_M = 0.60   # GPT-4o-mini output


@dataclass
class ApiCostConfig:
    provider: str
    input_price_per_m: float   # USD per 1 M input tokens
    output_price_per_m: float  # USD per 1 M output tokens


@dataclass
class OnPremCostConfig:
    hardware_purchase_usd: float = 800.0
    depreciation_years: float = 3.0
    cpu_tdp_watts: float = 15.0            # i7-8550U TDP under load
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
    cfg: ApiCostConfig,
    monthly_input_tokens: int,
    monthly_output_tokens: int,
) -> CostResult:
    """Compute monthly API cost given token volumes."""
    input_cost = (monthly_input_tokens / 1_000_000) * cfg.input_price_per_m
    output_cost = (monthly_output_tokens / 1_000_000) * cfg.output_price_per_m
    total = input_cost + output_cost
    total_tokens = monthly_input_tokens + monthly_output_tokens
    return CostResult(
        provider_or_method=cfg.provider,
        monthly_input_tokens=monthly_input_tokens,
        monthly_output_tokens=monthly_output_tokens,
        monthly_cost_usd=total,
        cost_per_1k_tokens_usd=(total / total_tokens * 1000) if total_tokens else 0.0,
    )


def onprem_monthly_cost(
    cfg: OnPremCostConfig,
    monthly_output_tokens: int,
    tokens_per_sec: float,
) -> CostResult:
    """Compute on-prem monthly cost (hardware amortisation + electricity)."""
    monthly_hardware = cfg.hardware_purchase_usd / (cfg.depreciation_years * 12)
    if tokens_per_sec > 0:
        inference_hours = (monthly_output_tokens / tokens_per_sec) / 3600
    else:
        inference_hours = cfg.inference_hours_per_month
    kwh_used = (cfg.cpu_tdp_watts / 1000) * inference_hours
    monthly_electricity = kwh_used * cfg.electricity_usd_per_kwh
    total = monthly_hardware + monthly_electricity
    return CostResult(
        provider_or_method="on-prem CPU",
        monthly_input_tokens=0,
        monthly_output_tokens=monthly_output_tokens,
        monthly_cost_usd=total,
        cost_per_1k_tokens_usd=(total / monthly_output_tokens * 1000) if monthly_output_tokens else 0.0,
        notes=(
            f"hardware_amort=${monthly_hardware:.2f}/mo "
            f"electricity=${monthly_electricity:.4f}/mo "
            f"inference_hours={inference_hours:.1f} h/mo"
        ),
    )


def breakeven_volume(
    api_cfg: ApiCostConfig,
    onprem_cfg: OnPremCostConfig,
    tokens_per_sec: float,
    output_fraction: float = 0.167,
) -> int:
    """Binary search for the monthly token volume where on-prem beats API cost."""
    lo, hi = 1, 100_000_000
    for _ in range(40):
        mid = (lo + hi) // 2
        out = int(mid * output_fraction)
        api = api_monthly_cost(api_cfg, mid - out, out)
        onp = onprem_monthly_cost(onprem_cfg, out, tokens_per_sec)
        if onp.monthly_cost_usd < api.monthly_cost_usd:
            hi = mid
        else:
            lo = mid
    return lo


def print_comparison(
    monthly_input: int,
    monthly_output: int,
    tokens_per_sec: float,
) -> None:
    """Print a cost comparison table to stdout."""
    configs = [
        ApiCostConfig("Claude 3 Haiku", ANTHROPIC_HAIKU_INPUT_PER_M, ANTHROPIC_HAIKU_OUTPUT_PER_M),
        ApiCostConfig("GPT-4o-mini", OPENAI_4O_MINI_INPUT_PER_M, OPENAI_4O_MINI_OUTPUT_PER_M),
    ]
    onprem_cfg = OnPremCostConfig()
    print("\n=== Monthly Cost Comparison ===")
    print(f"Workload: {monthly_input:,} input + {monthly_output:,} output tokens/month\n")
    print(f"{'Provider/Method':<20} {'Monthly USD':>12} {'USD/1k tokens':>14}")
    print("-" * 50)
    for cfg in configs:
        r = api_monthly_cost(cfg, monthly_input, monthly_output)
        print(f"{r.provider_or_method:<20} ${r.monthly_cost_usd:>10.2f}   ${r.cost_per_1k_tokens_usd:>10.4f}")
    onp = onprem_monthly_cost(onprem_cfg, monthly_output, tokens_per_sec)
    print(f"{'On-Prem CPU':<20} ${onp.monthly_cost_usd:>10.2f}   ${onp.cost_per_1k_tokens_usd:>10.4f}")
    print(f"  ({onp.notes})")
    for cfg in configs:
        bev = breakeven_volume(cfg, onprem_cfg, tokens_per_sec)
        print(f"\nBreak-even vs {cfg.provider}: ~{bev:,} total tokens/month")

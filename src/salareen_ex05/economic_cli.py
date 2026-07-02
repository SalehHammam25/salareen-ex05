"""CLI orchestration for the `costs` command (see costs.py for the cost model itself).

Kept separate from costs.py so the core cost-calculation module stays small and
free of CLI/plotting dependencies.
"""

from __future__ import annotations

from rich.console import Console

from salareen_ex05 import costs as costs_mod


def run_costs_command(
    monthly_input_tokens: int,
    monthly_output_tokens: int,
    tokens_per_sec: float,
    api_input_price_per_m: float,
    api_output_price_per_m: float,
    api_name: str,
    hardware_price: float,
    amortization_years: float,
    electricity_cost_per_kwh: float,
    avg_power_watts: float,
    save: bool,
    console: Console,
) -> None:
    """Build configs, print the comparison, and optionally save results + a figure."""
    api_cfg = costs_mod.ApiCostConfig(api_name, api_input_price_per_m, api_output_price_per_m)
    onprem_cfg = costs_mod.OnPremCostConfig(
        hardware_price, amortization_years, avg_power_watts, electricity_cost_per_kwh
    )
    api_r, onprem_r, bev = costs_mod.print_comparison(
        api_cfg, onprem_cfg, monthly_input_tokens, monthly_output_tokens, tokens_per_sec
    )
    if not save:
        return

    json_path, csv_path = costs_mod.save_results(api_cfg, onprem_cfg, api_r, onprem_r, bev)
    console.print(f"[green]Saved:[/green] {json_path.name}  {csv_path.name}")

    from salareen_ex05 import plots as plt_mod
    curve = costs_mod.breakeven_curve_data(api_cfg, onprem_cfg, tokens_per_sec)
    fig = plt_mod.cost_breakeven_curve(
        *curve, api_label=api_cfg.provider, filename="economic_break_even.png"
    )
    console.print(f"[green]Figure saved:[/green] {fig.name}")

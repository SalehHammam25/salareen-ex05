"""CLI entry point for salareen-ex05 experiments.

Sub-commands:
  hardware   — detect and print hardware info
  costs      — run economic analysis
  plots      — generate placeholder charts from saved results
  run        — [future] run an inference experiment
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(
    name="salareen-ex05",
    help="HW05: Local LLM benchmarking — AirLLM, Quantization, and Performance.",
    add_completion=False,
)
console = Console()
RESULTS_DIR = Path(__file__).parent.parent.parent / "results"


@app.command()
def hardware(
    save: bool = typer.Option(True, help="Save snapshot to results/hardware_snapshot.json"),
) -> None:
    """Detect and display hardware information."""
    from salareen_ex05 import hardware as hw

    snap = hw.collect()
    hw.print_report(snap)

    if save:
        out = RESULTS_DIR / "hardware_snapshot.json"
        hw.save_snapshot(snap, out)


@app.command()
def costs(
    monthly_input_tokens: int = typer.Option(1_000_000, help="Input tokens per month"),
    monthly_output_tokens: int = typer.Option(200_000, help="Output tokens per month"),
    tokens_per_sec: float = typer.Option(
        1.0,
        help="Measured on-prem throughput (tok/s). Use real value after benchmarking.",
    ),
) -> None:
    """Compute and display economic comparison: on-prem vs API."""
    from salareen_ex05.costs import print_comparison

    print_comparison(monthly_input_tokens, monthly_output_tokens, tokens_per_sec)


@app.command()
def plots(
    results_file: Optional[Path] = typer.Option(
        None, help="Path to results/summary.csv or a results JSON file."
    ),
) -> None:
    """Generate comparison charts from experiment results.

    If no results file is provided, prints a notice that experiments must run first.
    """
    if results_file is None or not results_file.exists():
        console.print(
            "[yellow]No results file found. Run inference experiments first, "
            "then re-run: python -m salareen_ex05.main plots --results-file results/summary.json[/yellow]"
        )
        return

    with open(results_file, encoding="utf-8") as f:
        data = json.load(f)

    from salareen_ex05 import plots as plt_mod

    plt_mod.latency_comparison(data)
    plt_mod.ram_comparison(data)
    plt_mod.throughput_comparison(data)
    console.print("[green]Plots saved to figures/[/green]")


@app.command(name="run")
def run_experiment(
    method: str = typer.Argument(
        help="Inference method: baseline | gguf | airllm | int8"
    ),
    model: str = typer.Option(..., help="Model ID or path"),
    max_tokens: int = typer.Option(100, help="Number of tokens to generate"),
    prompt_file: Optional[Path] = typer.Option(None, help="Path to prompt text file"),
) -> None:
    """Run a single inference experiment. [NOT YET IMPLEMENTED]

    This command is a placeholder. Implementations will be added in Phase 4–5.
    """
    console.print(
        f"[yellow]run-experiment for method='{method}' model='{model}' is not yet implemented.[/yellow]\n"
        "See docs/PLAN.md Phase 4–5 for the implementation roadmap."
    )
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

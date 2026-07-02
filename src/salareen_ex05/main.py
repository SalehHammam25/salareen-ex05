"""CLI entry point for salareen-ex05 experiments.

Sub-commands:
  hardware          — detect and print hardware info
  costs             — run economic analysis
  plots             — generate charts from saved results
  ollama-benchmark  — benchmark a local Ollama model
  airllm-check      — check AirLLM feasibility on this machine (no model download)
  run               — [future] run a transformers inference experiment
"""
from __future__ import annotations

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
    monthly_input_tokens: int = typer.Option(1_000_000, help="Input tokens/month"),
    monthly_output_tokens: int = typer.Option(200_000, help="Output tokens/month"),
    tokens_per_sec: float = typer.Option(15.28, help="On-prem tok/s (default: measured 1.5b)"),
    api_input_price_per_m: float = typer.Option(0.25, help="ASSUMED API input $/1M tok"),
    api_output_price_per_m: float = typer.Option(1.25, help="ASSUMED API output $/1M tok"),
    api_name: str = typer.Option("Generic API (assumed — unverified)", help="API label"),
    hardware_price: float = typer.Option(800.0, help="On-prem hardware price (USD)"),
    amortization_years: float = typer.Option(3.0, help="Depreciation period (years)"),
    electricity_cost_per_kwh: float = typer.Option(0.12, help="Electricity price (USD/kWh)"),
    avg_power_watts: float = typer.Option(15.0, help="Average CPU power under load (W)"),
    save: bool = typer.Option(True, help="Save results/economic_analysis.* + figure"),
) -> None:
    """Economic comparison: on-prem vs API. DRAFT — API pricing is an unverified assumption."""
    from salareen_ex05.economic_cli import run_costs_command
    run_costs_command(
        monthly_input_tokens, monthly_output_tokens, tokens_per_sec,
        api_input_price_per_m, api_output_price_per_m, api_name,
        hardware_price, amortization_years, electricity_cost_per_kwh, avg_power_watts,
        save, console,
    )


@app.command()
def plots(
    results_file: Optional[Path] = typer.Option(
        None, help="Path to a results CSV or JSON file (e.g. results/ollama_benchmark_qwen2_5_0_5b.csv)."
    ),
) -> None:
    """Generate charts from a results CSV or JSON file."""
    if results_file is None or not results_file.exists():
        console.print(
            "[yellow]No results file found. Run a benchmark first, then:\n"
            "uv run python -m salareen_ex05.main plots "
            "--results-file results/ollama_benchmark_qwen2_5_0_5b.csv[/yellow]"
        )
        return
    from salareen_ex05 import plots as plt_mod
    data = plt_mod.load_results(results_file)
    if not data:
        console.print("[red]Results file is empty.[/red]")
        return
    if "tokens_per_sec" in data[0]:
        out = plt_mod.benchmark_summary(data, stem=results_file.stem)
        console.print(f"[green]Figure saved:[/green] {out}")
    else:
        plt_mod.latency_comparison(data)
        plt_mod.ram_comparison(data)
        plt_mod.throughput_comparison(data)
        console.print("[green]Plots saved to figures/[/green]")


@app.command(name="ollama-benchmark")
def ollama_benchmark(
    model: str = typer.Option("qwen2.5:0.5b", help="Ollama model tag"),
    runs: int = typer.Option(1, help="Number of benchmark runs (use 3 for stable averages)"),
    url: str = typer.Option("http://localhost:11434/api/generate", help="Ollama API endpoint"),
    prompt_file: Optional[Path] = typer.Option(None, help="Custom prompt file path"),
) -> None:
    """Benchmark a local Ollama model and save results to results/."""
    from salareen_ex05.ollama_benchmark import run_benchmark, save_results
    default_prompt_path = Path(__file__).parent.parent.parent / "data" / "prompts" / "ollama_benchmark_prompt.txt"
    if prompt_file and prompt_file.exists():
        prompt = prompt_file.read_text(encoding="utf-8").strip()
    elif default_prompt_path.exists():
        prompt = default_prompt_path.read_text(encoding="utf-8").strip()
    else:
        prompt = "Explain prefill vs decode in LLM inference in 3 sentences."
    console.print(f"[cyan]Benchmarking {model} ({runs} run(s))...[/cyan]")
    results = run_benchmark(model, prompt, runs=runs, url=url)
    if any(r.error for r in results):
        console.print("[red]Benchmark failed — see error above.[/red]")
        raise typer.Exit(code=1)
    stem = f"ollama_benchmark_{model.replace(':', '_').replace('.', '_')}"
    json_path, csv_path = save_results(results, stem)
    console.print(f"[green]Saved:[/green] {json_path.name}  {csv_path.name}")
    tps_vals = [r.tokens_per_sec for r in results if r.tokens_per_sec]
    if tps_vals:
        console.print(f"  Avg throughput : {sum(tps_vals)/len(tps_vals):.2f} tok/s")
    avg_rt = sum(r.total_runtime_sec for r in results) / len(results)
    console.print(f"  Avg wall-clock : {avg_rt:.2f} s")


@app.command(name="airllm-check")
def airllm_check(
    save: bool = typer.Option(True, help="Save report to results/airllm_feasibility_report.*"),
) -> None:
    """Check AirLLM feasibility on this machine. Does not install or download anything."""
    from salareen_ex05.airllm_feasibility import collect, format_report, save_report
    report = collect()
    console.print(format_report(report))
    if save:
        txt_path, json_path = save_report(report)
        console.print(f"[green]Saved:[/green] {txt_path.name}  {json_path.name}")


@app.command(name="run")
def run_experiment(
    method: str = typer.Argument(help="Inference method: baseline | gguf | airllm | int8"),
    model: str = typer.Option(..., help="Model ID or path"),
    max_tokens: int = typer.Option(100, help="Number of tokens to generate"),
    prompt_file: Optional[Path] = typer.Option(None, help="Path to prompt text file"),
) -> None:
    """Run a single inference experiment. [NOT YET IMPLEMENTED] — see docs/PLAN.md Phase 4–5."""
    console.print(f"[yellow]'{method}' for '{model}' not implemented — see docs/PLAN.md Phase 4–5.[/yellow]")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()

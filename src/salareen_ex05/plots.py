"""Chart generation utilities using matplotlib.

Supports loading results from CSV or JSON (load_results) and generating
benchmark summary figures and generic comparison charts.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg", force=True)  # must happen before pyplot is imported anywhere
import matplotlib.pyplot as plt  # noqa: E402

FIGURES_DIR = Path(__file__).parent.parent.parent / "figures"


def _ensure_figures_dir() -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR


def load_results(path: Path) -> list[dict]:
    """Load a results file into a list of dicts. Supports .csv and .json."""
    if path.suffix.lower() == ".csv":
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def benchmark_summary(results: list[dict], stem: str = "benchmark") -> Path:
    """Three-panel bar chart: throughput, runtime, and RAM delta per run."""
    labels = [f"Run {r.get('run_index', i + 1)}" for i, r in enumerate(results)]
    tps = [float(r.get("tokens_per_sec") or 0) for r in results]
    rt  = [float(r.get("total_runtime_sec") or 0) for r in results]
    ram = [float(r.get("ram_delta_mb") or 0) for r in results]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, vals, title, ylabel, color in [
        (axes[0], tps, "Throughput", "tokens / sec", "steelblue"),
        (axes[1], rt,  "Wall-clock runtime", "seconds", "coral"),
        (axes[2], ram, "RAM delta", "MB", "mediumseagreen"),
    ]:
        ax.bar(labels, vals, color=color, edgecolor="black", linewidth=0.7)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=15)
        ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    out = _ensure_figures_dir() / f"{stem}_summary.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


def bar_chart(
    labels: list[str],
    values: list[float],
    title: str,
    ylabel: str,
    filename: str,
    errors: Optional[list[float]] = None,
    color: str = "steelblue",
) -> Path:
    """Save a simple bar chart to figures/<filename>.png."""
    fig, ax = plt.subplots(figsize=(8, 5))
    x = range(len(labels))
    ax.bar(x, values, yerr=errors, capsize=5, color=color, edgecolor="black", linewidth=0.7)
    ax.set_xticks(list(x))
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()

    out = _ensure_figures_dir() / filename
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


def latency_comparison(results: list[dict]) -> Path:
    """Bar chart of TTFT and mean TPOT per method."""
    labels = [r["method"] for r in results]
    ttft = [r.get("ttft_sec") or 0.0 for r in results]
    tpot = [r.get("tpot_sec") or 0.0 for r in results]

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, vals, title, ylabel in [
        (axes[0], ttft, "Time To First Token (TTFT)", "seconds"),
        (axes[1], tpot, "Time Per Output Token (TPOT)", "seconds/token"),
    ]:
        ax.bar(labels, vals, color="steelblue", edgecolor="black", linewidth=0.7)
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.set_xticklabels(labels, rotation=15, ha="right")
        ax.grid(axis="y", linestyle="--", alpha=0.5)

    fig.tight_layout()
    out = _ensure_figures_dir() / "latency_comparison.png"
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")
    return out


def ram_comparison(results: list[dict]) -> Path:
    """Bar chart of peak RAM delta per method."""
    labels = [r["method"] for r in results]
    ram = [r.get("ram_delta_mb") or 0.0 for r in results]
    return bar_chart(labels, ram, "Peak RAM Usage (delta)", "MB", "ram_comparison.png", color="coral")


def throughput_comparison(results: list[dict]) -> Path:
    """Bar chart of tokens/sec per method."""
    labels = [r["method"] for r in results]
    tps = [r.get("throughput_tok_per_sec") or 0.0 for r in results]
    return bar_chart(labels, tps, "Throughput", "tokens / sec", "throughput_comparison.png", color="mediumseagreen")


def cost_breakeven_curve(
    volumes: list[int],
    api_costs: list[float],
    onprem_costs: list[float],
    api_label: str = "API",
    filename: str = "cost_breakeven.png",
) -> Path:
    """Line chart showing API vs on-prem cost as a function of monthly token volume."""
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(volumes, api_costs, label=api_label, color="steelblue", linewidth=2)
    ax.plot(volumes, onprem_costs, label="On-Prem CPU", color="coral", linewidth=2)
    ax.set_xlabel("Monthly tokens")
    ax.set_ylabel("Monthly cost (USD)")
    ax.set_title("On-Prem vs API: Monthly Cost Break-Even")
    ax.legend()
    ax.grid(linestyle="--", alpha=0.5)
    fig.tight_layout()

    out = _ensure_figures_dir() / filename
    fig.savefig(out, dpi=300)
    plt.close(fig)
    print(f"Saved: {out}")
    return out

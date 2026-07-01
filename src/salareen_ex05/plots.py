"""Chart generation utilities using matplotlib.

All functions accept data as plain Python structures (dicts/lists) and
save figures to the `figures/` directory. No model dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

FIGURES_DIR = Path(__file__).parent.parent.parent / "figures"


def _ensure_figures_dir() -> Path:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    return FIGURES_DIR


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
    import matplotlib.pyplot as plt  # lazy import — not installed in stub phase

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

    import matplotlib.pyplot as plt

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
    import matplotlib.pyplot as plt

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

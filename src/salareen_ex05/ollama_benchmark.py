"""Benchmark a local Ollama model via the Ollama HTTP API (http://localhost:11434).

Sends a fixed prompt, parses Ollama's native timing fields, and computes
tokens/sec, RAM delta, and wall-clock runtime. No model downloads required.
"""

from __future__ import annotations

import csv
import json
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional

import psutil
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results"


@dataclass
class OllamaBenchmarkResult:
    model: str
    run_index: int
    prompt_chars: int
    response_chars: int
    total_runtime_sec: float
    total_duration_ns: Optional[int] = None
    load_duration_ns: Optional[int] = None
    prompt_eval_count: Optional[int] = None
    prompt_eval_duration_ns: Optional[int] = None
    eval_count: Optional[int] = None
    eval_duration_ns: Optional[int] = None
    tokens_per_sec: Optional[float] = None
    ram_before_mb: Optional[float] = None
    ram_after_mb: Optional[float] = None
    ram_delta_mb: Optional[float] = None
    response_text: str = ""
    error: Optional[str] = None


def _parse_response(
    model: str,
    run_index: int,
    prompt: str,
    raw: dict,
    wall_sec: float,
    ram_before: float,
    ram_after: float,
) -> OllamaBenchmarkResult:
    """Parse a raw Ollama API response dict into a typed result."""
    eval_count = raw.get("eval_count")
    eval_dur_ns = raw.get("eval_duration")
    tps = (eval_count / (eval_dur_ns / 1e9)) if (eval_count and eval_dur_ns) else None
    return OllamaBenchmarkResult(
        model=model,
        run_index=run_index,
        prompt_chars=len(prompt),
        response_chars=len(raw.get("response", "")),
        total_runtime_sec=wall_sec,
        total_duration_ns=raw.get("total_duration"),
        load_duration_ns=raw.get("load_duration"),
        prompt_eval_count=raw.get("prompt_eval_count"),
        prompt_eval_duration_ns=raw.get("prompt_eval_duration"),
        eval_count=eval_count,
        eval_duration_ns=eval_dur_ns,
        tokens_per_sec=tps,
        ram_before_mb=ram_before,
        ram_after_mb=ram_after,
        ram_delta_mb=ram_after - ram_before,
        response_text=raw.get("response", ""),
    )


def run_single(
    model: str,
    prompt: str,
    run_index: int = 0,
    url: str = OLLAMA_URL,
) -> OllamaBenchmarkResult:
    """Run one inference pass. Returns a result with error set on failure."""
    proc = psutil.Process()
    ram_before = proc.memory_info().rss / 1024**2
    t0 = time.perf_counter()
    try:
        resp = requests.post(
            url,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=300,
        )
        resp.raise_for_status()
        raw = resp.json()
    except requests.exceptions.ConnectionError:
        return OllamaBenchmarkResult(
            model=model, run_index=run_index, prompt_chars=len(prompt),
            response_chars=0, total_runtime_sec=time.perf_counter() - t0,
            error="Cannot connect to Ollama. Is it running? Try: ollama serve",
        )
    except Exception as exc:  # noqa: BLE001
        return OllamaBenchmarkResult(
            model=model, run_index=run_index, prompt_chars=len(prompt),
            response_chars=0, total_runtime_sec=time.perf_counter() - t0,
            error=str(exc),
        )
    wall_sec = time.perf_counter() - t0
    ram_after = proc.memory_info().rss / 1024**2
    return _parse_response(model, run_index, prompt, raw, wall_sec, ram_before, ram_after)


def run_benchmark(
    model: str,
    prompt: str,
    runs: int = 3,
    url: str = OLLAMA_URL,
) -> list[OllamaBenchmarkResult]:
    """Run *runs* inference passes. Stops early on the first error."""
    results = []
    for i in range(runs):
        print(f"  Run {i + 1}/{runs} ... ", end="", flush=True)
        r = run_single(model, prompt, run_index=i + 1, url=url)
        if r.error:
            print(f"FAILED: {r.error}")
            results.append(r)
            break
        print(f"{r.tokens_per_sec:.2f} tok/s" if r.tokens_per_sec else "done")
        results.append(r)
    return results


def save_results(results: list[OllamaBenchmarkResult], stem: str) -> tuple[Path, Path]:
    """Save results as JSON and CSV under RESULTS_DIR. Returns (json_path, csv_path)."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rows = [asdict(r) for r in results]

    json_path = RESULTS_DIR / f"{stem}.json"
    json_path.write_text(json.dumps(rows, indent=2), encoding="utf-8")

    csv_path = RESULTS_DIR / f"{stem}.csv"
    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)

    return json_path, csv_path

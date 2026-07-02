"""AirLLM feasibility check — environment audit only, no model download or run.

A "not compatible" or "not installed" result is a valid finding, not a project
failure — Ollama's GGUF/Q4_K_M baselines remain the CPU-only fallback."""

from __future__ import annotations

import json
import platform
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import psutil
RESULTS_DIR = Path(__file__).parent.parent.parent / "results"


@dataclass
class FeasibilityReport:
    generated_at: str
    python_version: str
    platform_str: str
    os_name: str
    cuda_available: bool
    airllm_importable: bool
    airllm_version: Optional[str]
    ram_total_gb: float
    ram_available_gb: float
    disk_free_gb: float
    likely_compatible: bool
    notes: list[str]
    recommended_next_action: str


def _check_cuda() -> bool:
    """Return True if a CUDA-capable GPU is accessible via torch."""
    try:
        import torch  # type: ignore[import-untyped]
        return torch.cuda.is_available()
    except ImportError:
        return False


def _check_airllm() -> tuple[bool, Optional[str]]:
    """Return (importable, version) without downloading or loading any model."""
    try:
        import airllm  # type: ignore[import-not-found]
    except ImportError:
        return False, None
    return True, getattr(airllm, "__version__", "unknown")


def _evaluate(
    os_name: str, cuda_available: bool, airllm_importable: bool,
    ram_available_gb: float, disk_free_gb: float,
) -> tuple[list[str], bool, str]:
    """Return (notes, likely_compatible, recommended_next_action). Pure logic, no I/O."""
    notes: list[str] = []
    notes.append(
        "AirLLM package is importable." if airllm_importable else
        "AirLLM is not installed (documented finding, not a failure)."
    )
    if not cuda_available:
        notes.append("No CUDA GPU; AirLLM's CPU-only path is unsupported and very slow.")
    if os_name == "Windows":
        notes.append("Windows per-layer disk I/O is less proven than Linux; may be unstable.")
    if ram_available_gb < 8:
        notes.append(f"Only ~{ram_available_gb:.1f} GB RAM free; a 7B+ model will be tight.")
    if disk_free_gb < 15:
        notes.append(f"Only ~{disk_free_gb:.1f} GB free disk; a 7B model's weights may not fit.")
    likely_compatible = airllm_importable and cuda_available
    if not airllm_importable:
        next_action = (
            "Do not download a large model yet. Install AirLLM deliberately "
            "(`uv add airllm`), then re-run `airllm-check`."
        )
    elif not cuda_available:
        next_action = (
            "AirLLM is installed but this machine is CPU-only. Do not auto-download a "
            "7B+ model; keep Ollama GGUF/Q4_K_M as the fallback baseline."
        )
    else:
        next_action = (
            "Environment looks compatible. Still start with the smallest AirLLM model "
            "deliberately rather than auto-downloading a large one."
        )
    return notes, likely_compatible, next_action


def collect() -> FeasibilityReport:
    """Collect an AirLLM feasibility report from the current machine. No downloads."""
    os_name = platform.system()
    cuda_available = _check_cuda()
    airllm_importable, airllm_version = _check_airllm()
    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("C:\\") if os_name == "Windows" else shutil.disk_usage("/")
    notes, likely_compatible, next_action = _evaluate(
        os_name=os_name, cuda_available=cuda_available,
        airllm_importable=airllm_importable,
        ram_available_gb=ram.available / 1024**3, disk_free_gb=disk.free / 1024**3,
    )
    return FeasibilityReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        python_version=platform.python_version(),
        platform_str=platform.platform(),
        os_name=os_name,
        cuda_available=cuda_available,
        airllm_importable=airllm_importable,
        airllm_version=airllm_version,
        ram_total_gb=ram.total / 1024**3,
        ram_available_gb=ram.available / 1024**3,
        disk_free_gb=disk.free / 1024**3,
        likely_compatible=likely_compatible,
        notes=notes,
        recommended_next_action=next_action,
    )


def format_report(report: FeasibilityReport) -> str:
    """Render the report as human-readable text (used for stdout and the .txt file)."""
    airllm_line = f"AirLLM import  : {'YES' if report.airllm_importable else 'NO'}"
    if report.airllm_version:
        airllm_line += f" (version {report.airllm_version})"
    lines = [
        "=== AirLLM Feasibility Report ===",
        f"Generated at   : {report.generated_at}",
        f"Platform       : {report.platform_str}",
        f"Python         : {report.python_version}",
        f"CUDA available : {'YES' if report.cuda_available else 'NO'}",
        airllm_line,
        f"RAM total/free : {report.ram_total_gb:.1f} GB / {report.ram_available_gb:.1f} GB",
        f"Disk free      : {report.disk_free_gb:.1f} GB",
        f"Likely compatible: {'YES' if report.likely_compatible else 'NO'}",
        "", "Notes:",
    ]
    lines += [f"  - {n}" for n in report.notes]
    lines += ["", f"Recommended next action:\n  {report.recommended_next_action}", ""]
    return "\n".join(lines)


def save_report(report: FeasibilityReport, results_dir: Path = RESULTS_DIR) -> tuple[Path, Path]:
    """Save the report as .txt and .json under *results_dir*. Returns (txt_path, json_path)."""
    results_dir.mkdir(parents=True, exist_ok=True)
    txt_path = results_dir / "airllm_feasibility_report.txt"
    json_path = results_dir / "airllm_feasibility_report.json"
    txt_path.write_text(format_report(report), encoding="utf-8")
    json_path.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")
    return txt_path, json_path

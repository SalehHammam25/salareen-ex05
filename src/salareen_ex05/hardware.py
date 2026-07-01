"""Hardware detection utilities.

Collects CPU, RAM, disk, and GPU information using psutil and platform.
No external model dependencies. Safe to run on any machine.
"""

from __future__ import annotations

import json
import platform
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

import psutil


@dataclass
class HardwareSnapshot:
    cpu_brand: str
    cpu_cores_physical: int
    cpu_cores_logical: int
    cpu_freq_max_mhz: float
    ram_total_gb: float
    ram_available_gb: float
    disk_path: str
    disk_total_gb: float
    disk_free_gb: float
    cuda_available: bool
    gpu_info: str
    python_version: str
    platform_str: str


def collect() -> HardwareSnapshot:
    """Collect a hardware snapshot from the current machine."""
    cpu_freq = psutil.cpu_freq()
    freq_max = cpu_freq.max if cpu_freq else 0.0

    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("C:\\") if platform.system() == "Windows" else shutil.disk_usage("/")

    cuda_available = _check_cuda()
    gpu_info = _get_gpu_info()

    return HardwareSnapshot(
        cpu_brand=platform.processor() or "Unknown",
        cpu_cores_physical=psutil.cpu_count(logical=False) or 0,
        cpu_cores_logical=psutil.cpu_count(logical=True) or 0,
        cpu_freq_max_mhz=freq_max,
        ram_total_gb=ram.total / 1024**3,
        ram_available_gb=ram.available / 1024**3,
        disk_path="C:\\" if platform.system() == "Windows" else "/",
        disk_total_gb=disk.total / 1024**3,
        disk_free_gb=disk.free / 1024**3,
        cuda_available=cuda_available,
        gpu_info=gpu_info,
        python_version=platform.python_version(),
        platform_str=platform.platform(),
    )


def _check_cuda() -> bool:
    """Return True if a CUDA-capable GPU is accessible via torch."""
    try:
        import torch  # type: ignore[import-untyped]
        return torch.cuda.is_available()
    except ImportError:
        return False


def _get_gpu_info() -> str:
    """Return a human-readable GPU description, or 'No CUDA GPU detected'."""
    try:
        import torch  # type: ignore[import-untyped]
        if torch.cuda.is_available():
            return torch.cuda.get_device_name(0)
    except ImportError:
        pass
    return "No CUDA GPU detected (CPU-only machine)"


def print_report(snap: HardwareSnapshot) -> None:
    """Print a formatted hardware report to stdout."""
    print("\n=== Hardware Report ===")
    print(f"Platform    : {snap.platform_str}")
    print(f"Python      : {snap.python_version}")
    print(f"CPU         : {snap.cpu_brand}")
    print(f"Cores       : {snap.cpu_cores_physical} physical / {snap.cpu_cores_logical} logical")
    print(f"CPU freq    : {snap.cpu_freq_max_mhz:.0f} MHz max")
    print(f"RAM total   : {snap.ram_total_gb:.1f} GB")
    print(f"RAM free    : {snap.ram_available_gb:.1f} GB")
    print(f"Disk ({snap.disk_path}): {snap.disk_free_gb:.1f} GB free / {snap.disk_total_gb:.1f} GB total")
    print(f"CUDA        : {'YES' if snap.cuda_available else 'NO'}")
    print(f"GPU         : {snap.gpu_info}")
    print()


def save_snapshot(snap: HardwareSnapshot, path: Path) -> None:
    """Save the hardware snapshot as JSON to *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(snap), f, indent=2)
    print(f"Hardware snapshot saved to {path}")

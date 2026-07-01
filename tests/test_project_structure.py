"""Verify that required files and directories exist and the package imports cleanly."""

from pathlib import Path

ROOT = Path(__file__).parent.parent


def _p(*parts: str) -> Path:
    return ROOT.joinpath(*parts)


# ---------------------------------------------------------------------------
# File existence
# ---------------------------------------------------------------------------

def test_readme_exists():
    assert _p("README.md").is_file()


def test_pyproject_exists():
    assert _p("pyproject.toml").is_file()


def test_env_example_exists():
    assert _p(".env-example").is_file()


def test_docs_prd_exists():
    assert _p("docs", "PRD.md").is_file()


def test_docs_plan_exists():
    assert _p("docs", "PLAN.md").is_file()


def test_docs_todo_exists():
    assert _p("docs", "TODO.md").is_file()


def test_docs_prompt_log_exists():
    assert _p("docs", "PROMPT_LOG.md").is_file()


def test_src_package_exists():
    assert _p("src", "salareen_ex05", "__init__.py").is_file()


def test_src_hardware_exists():
    assert _p("src", "salareen_ex05", "hardware.py").is_file()


def test_src_metrics_exists():
    assert _p("src", "salareen_ex05", "metrics.py").is_file()


def test_src_costs_exists():
    assert _p("src", "salareen_ex05", "costs.py").is_file()


def test_src_plots_exists():
    assert _p("src", "salareen_ex05", "plots.py").is_file()


def test_src_main_exists():
    assert _p("src", "salareen_ex05", "main.py").is_file()


# ---------------------------------------------------------------------------
# Directory existence
# ---------------------------------------------------------------------------

def test_experiments_dir_exists():
    assert _p("experiments").is_dir()


def test_results_dir_exists():
    assert _p("results").is_dir()


def test_figures_dir_exists():
    assert _p("figures").is_dir()


def test_data_dir_exists():
    assert _p("data").is_dir()


def test_reports_dir_exists():
    assert _p("reports").is_dir()


# ---------------------------------------------------------------------------
# Package imports
# ---------------------------------------------------------------------------

def test_package_importable():
    import salareen_ex05  # noqa: F401


def test_hardware_importable():
    from salareen_ex05 import hardware  # noqa: F401


def test_metrics_importable():
    from salareen_ex05 import metrics  # noqa: F401


def test_costs_importable():
    from salareen_ex05 import costs  # noqa: F401


def test_plots_importable():
    from salareen_ex05 import plots  # noqa: F401


def test_main_importable():
    from salareen_ex05 import main  # noqa: F401


def test_ollama_benchmark_importable():
    from salareen_ex05 import ollama_benchmark  # noqa: F401


def test_ollama_benchmark_file_exists():
    assert _p("src", "salareen_ex05", "ollama_benchmark.py").is_file()


def test_benchmark_prompt_file_exists():
    assert _p("data", "prompts", "ollama_benchmark_prompt.txt").is_file()


def test_version_defined():
    import salareen_ex05
    assert hasattr(salareen_ex05, "__version__")
    assert salareen_ex05.__version__ == "0.1.0"

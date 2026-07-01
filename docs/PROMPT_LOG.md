# Prompt Log — salareen-ex05

This file documents every significant AI-assisted prompt used during the project.
Each entry records the purpose, the key instructions given, and the output produced.

---

## Entry 001 — 2026-07-02

**Purpose:** Create the initial project skeleton and planning documents for Homework 05.

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Key instructions given:**
- Do NOT implement the full experiment yet.
- Do NOT download models or write fake benchmark results.
- Create only the initial professional project skeleton and planning documents.
- Project identity: group `salareen`, students Saleh Hammam and Areen Tarabeh.
- Topic: Running a Massive LLM Locally — AirLLM, Quantization, and Performance Benchmarking.
- Environment: Windows 11, VS Code, PowerShell, `uv` as package manager.
- Hardware constraints: CPU-only (Intel i7-8550U), 16 GB RAM (~6.8 GB free), Intel UHD 620, no CUDA.
- Disk: ~22.5 GB free on C:.
- Create README.md (report skeleton), docs/PRD.md, docs/PLAN.md, docs/TODO.md,
  docs/PROMPT_LOG.md, pyproject.toml, .env-example, source stubs under
  `src/salareen_ex05/`, and tests under `tests/`.
- Requirements for each file were specified in detail (see assignment instructions).

**Files created:**
- `README.md` — full report skeleton with all required sections.
- `docs/PRD.md` — problem statement, goals, requirements, acceptance criteria.
- `docs/PLAN.md` — architecture, experiment phases, risk analysis, fallback strategy.
- `docs/TODO.md` — phase-by-phase task tracker (Phases 1–8).
- `docs/PROMPT_LOG.md` — this file.
- `pyproject.toml` — project metadata, lightweight dependencies, Python >=3.11,<3.13.
- `.env-example` — environment variable template.
- `src/salareen_ex05/__init__.py` — package init with version.
- `src/salareen_ex05/hardware.py` — hardware detection stub.
- `src/salareen_ex05/metrics.py` — timing/memory measurement stub.
- `src/salareen_ex05/costs.py` — economic model stub.
- `src/salareen_ex05/plots.py` — chart generator stub.
- `src/salareen_ex05/main.py` — CLI entry point stub (typer).
- `tests/__init__.py` — empty package init.
- `tests/test_project_structure.py` — file-existence and import tests.
- `tests/test_metrics.py` — unit tests for metrics helpers.

**Outcome:** Project skeleton created. No models downloaded. No results faked.
Next step: Phase 2 — environment setup with `uv`.

---

<!-- Add new entries below this line -->

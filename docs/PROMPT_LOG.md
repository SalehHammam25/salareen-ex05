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

## Entry 002 — 2026-07-02

**Purpose:** Implement a real Ollama benchmark pipeline (Phase 3b).

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Context at the time of this prompt:**
- Initial project skeleton was complete (Entry 001).
- Ollama was installed and working on the machine.
- Model `qwen2.5:0.5b` was pulled and a smoke test was saved to `results/ollama_smoke_test.txt`.
- No full benchmark pipeline existed yet.

**Key instructions given:**
- Use the Ollama HTTP API (`http://localhost:11434/api/generate`).
- Measure wall-clock time, Ollama native timing fields, tokens/sec, and RAM delta.
- Save results to `results/ollama_benchmark_qwen2_5_0_5b.json` and `.csv`.
- Save the fixed prompt to `data/prompts/ollama_benchmark_prompt.txt`.
- Add a CLI command `ollama-benchmark` to `main.py`.
- Add mocked tests (no real Ollama needed for `pytest`).
- Keep every source file under 150 lines.
- Do NOT run the benchmark automatically.
- Do NOT fake results.

**Files created/modified:**
- `src/salareen_ex05/ollama_benchmark.py` — created: core benchmark module
- `src/salareen_ex05/main.py` — updated: added `ollama-benchmark` command
- `pyproject.toml` — updated: added `requests>=2.31` dependency
- `tests/test_ollama_benchmark.py` — created: mocked tests for benchmark module
- `data/prompts/ollama_benchmark_prompt.txt` — created: fixed benchmark prompt
- `README.md` — updated: added benchmark commands to §11
- `docs/TODO.md` — updated: marked Phases 2 & 3 complete, added Phase 3b tasks
- `docs/PROMPT_LOG.md` — updated: this entry

**Outcome:** Benchmark pipeline implemented. Real results NOT collected yet.
Next step: run `uv run python -m salareen_ex05.main ollama-benchmark --model qwen2.5:0.5b --runs 3`
and record results in README §8.

---

<!-- Add new entries below this line -->

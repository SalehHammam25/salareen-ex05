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

## Entry 003 — 2026-07-02

**Purpose:** Fix the `plots` CLI command to support CSV files, not just JSON.

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Root cause of bug:**
The `plots` command in `main.py` called `json.load()` unconditionally, so passing a CSV
file caused a `JSONDecodeError`. The Ollama benchmark saves results as both CSV and JSON,
but the most natural file to pass was the CSV.

**Changes made:**
- `src/salareen_ex05/plots.py` — added `load_results(path)` (detects `.csv` vs `.json`)
  and `benchmark_summary(results, stem)` (3-panel bar chart for Ollama benchmark data).
- `src/salareen_ex05/main.py` — replaced `json.load()` in `plots` command with
  `plt_mod.load_results()`; dispatch: Ollama data → `benchmark_summary`, generic data →
  existing latency/ram/throughput charts.
- `tests/test_plots.py` — created: 11 tests covering CSV load, JSON load, figure
  generation from CSV, single-row charts, and missing-value robustness.
- `README.md` — updated §11 with the correct `--results-file` command.
- `docs/PROMPT_LOG.md` — this entry.

**Outcome:** `plots --results-file results/ollama_benchmark_qwen2_5_0_5b.csv` now works.

---

## Entry 004 — 2026-07-02

**Purpose:** Record the first real baseline benchmark result in README §8.

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Real data provided by user (not fabricated):**
- Model: `qwen2.5:0.5b` via Ollama HTTP API
- Wall-clock runtime: 17.3146 s
- Prompt tokens: 79, prompt_eval_duration: 107,959,000 ns
- Output tokens: 270, eval_duration: 10,389,355,000 ns
- Throughput: 25.988 tokens/sec
- Process RSS before: 38.44 MB, after: 39.97 MB, delta: 1.53 MB
- Figure: `figures/ollama_benchmark_qwen2_5_0_5b_summary.png`

**Key constraints given:**
- Do not fake additional results.
- Do not claim AirLLM or quantization was tested.
- Note that RSS values are script-process-only, not full Ollama server footprint.
- Keep writing technical, honest, and concise.

**Changes made:**
- `README.md` — replaced the `[PENDING]` placeholder in §8 Results with:
  a results table, Markdown figure reference, and a 4-point interpretation
  (feasibility, scope limitation, prefill/decode split, next steps).
- `docs/TODO.md` — marked Phase 3b benchmark run, results files, figure, and
  README update as complete; left 3-run stability check as pending.
- `docs/PROMPT_LOG.md` — this entry.

**Outcome:** README now contains one real, honest baseline data point.
Quantization, AirLLM, economic analysis, and full comparison remain pending.

---

<!-- Add new entries below this line -->

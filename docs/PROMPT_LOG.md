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

## Entry 005 — 2026-07-02

**Purpose:** Add qwen2.5:1.5b real benchmark result and cross-model comparison to README §8.

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Real data provided by user (not fabricated):**
- Model: `qwen2.5:1.5b` via Ollama HTTP API, same prompt as Baseline 1
- Wall-clock runtime: 26.7741 s
- Prompt tokens: 79, prompt_eval_duration: 1,446,900,000 ns
- Output tokens: 295, eval_duration: 19,308,239,000 ns
- Throughput: 15.278 tokens/sec
- Process RSS before: 38.30 MB, after: 39.43 MB, delta: 1.13 MB
- Figure: `figures/ollama_benchmark_qwen2_5_1_5b_summary.png`

**Constraints given:**
- Do not fake results.
- Do not claim AirLLM or quantization was tested.
- RSS values are script-process-only; note that Ollama server memory is separate.
- Keep writing technical, honest, and concise.

**Changes made:**
- `README.md` §8 — appended "Baseline 2: Ollama qwen2.5:1.5b" subsection with metrics
  table, RAM note, and figure reference; added "Cross-model Comparison" subsection with
  a two-row comparison table and 5-point analysis (throughput drop, runtime increase,
  prefill sensitivity, scale gap to 7B, RSS interpretation).
- `docs/TODO.md` — marked 1.5b benchmark, figure, and README comparison as complete;
  added pending items for 3-run stability, system-level memory, 7B/GGUF test, AirLLM,
  economic analysis, final plots, and PDF.
- `docs/PROMPT_LOG.md` — this entry.

**Outcome:** README now contains two real baselines and an honest cross-model comparison.
AirLLM, quantization, economic analysis, and final report remain pending.

---

## Entry 006 — 2026-07-02

**Purpose:** Add real Ollama model metadata and a process memory snapshot to README §8.

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Real data provided by user (not fabricated):**
- `ollama show qwen2.5:1.5b`: architecture qwen2, parameters 1.5B, context_length 32768,
  embedding_length 1536, quantization Q4_K_M, license Apache License 2.0.
- `ollama show qwen2.5:0.5b` (read from saved file): architecture qwen2, parameters
  494.03M, context_length 32768, embedding_length 896, quantization Q4_K_M, license
  Apache License 2.0.
- Ollama process memory snapshot (`Get-Process ollama`): PM ≈ 83,738,624 bytes,
  WS ≈ 62,029,824 bytes, StartTime 7/2/2026 12:50:35 AM.
- Source files: `results/ollama_models_list.txt`, `results/ollama_show_qwen2_5_0_5b.txt`,
  `results/ollama_show_qwen2_5_1_5b.txt`, `results/ollama_process_memory_snapshot.txt`.

**Key constraints given:**
- Do not fake results.
- Do not claim AirLLM was tested yet.
- Do not claim system-level memory tracking is complete.
- Keep the writing honest and technical.

**Changes made:**
- `README.md` §8 — added new "Ollama model metadata" subsection with a metadata table
  for both models, a quantization note (Ollama models are already quantized Q4_K_M, so
  existing baselines are not FP16), and a process-memory note (62 MB WS is a single
  snapshot of the Ollama process only, not the full generation-time memory footprint;
  precise profiling still pending).
- `docs/TODO.md` — marked Ollama model metadata collection and the process memory
  snapshot as complete; kept precise system-level memory profiling (continuous/peak
  tracking during generation) as pending.
- `docs/PROMPT_LOG.md` — this entry.

**Outcome:** README now documents real, verifiable model metadata and a single memory
snapshot, clearly scoped as partial. AirLLM, full-precision baseline, continuous memory
profiling, and economic analysis remain pending.

## Entry 007 — 2026-07-02

**Purpose:** Add the real qwen2.5:3b benchmark result and expand the cross-model
comparison to three models in README §8.

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Real data provided by user (not fabricated):**
- Model: `qwen2.5:3b` via Ollama HTTP API, same fixed prompt as Baselines 1 and 2
- Wall-clock runtime: 32.2096 s
- Prompt tokens: 79, prompt_eval_duration: 2,938,253,000 ns
- Output tokens: 183, eval_duration: 22,868,450,000 ns
- Throughput: 8.002 tokens/sec
- Process RSS before: 37.45 MB, after: 38.53 MB, delta: 1.08 MB
- Figure: `figures/ollama_benchmark_qwen2_5_3b_summary.png` (verified present in `figures/`)

**Key constraints given:**
- Do not fake results.
- Do not claim AirLLM was tested yet.
- Do not claim full quantization comparison is complete.
- Keep writing technical, honest, and concise.
- RAM values are process-level only; full system-level memory profiling still pending.

**Changes made:**
- `README.md` §8 — added "Baseline 3: Ollama qwen2.5:3b" subsection (metrics table,
  RAM note, figure reference); expanded "Cross-model Comparison" to a three-row table
  (0.5b / 1.5b / 3b) with an updated 6-point analysis (throughput drop across all three
  models, runtime increase despite fewer output tokens, CPU-only bottleneck trend, 3B as
  a useful stress test rather than a "massive LLM," RSS overhead being negligible, and
  next steps toward AirLLM/fallback and explicit quantization discussion); updated the
  "Still pending" callout to reflect AirLLM/fallback, quantization comparison,
  system-level memory tracking, economic analysis, and final report as open.
- `docs/TODO.md` — marked the qwen2.5:3b benchmark run, its figure, and the README
  update as complete; added an explicit pending item for a quantization-level
  comparison; kept AirLLM/fallback, system-level memory profiling, economic analysis,
  and final PDF/report as pending.
- `docs/PROMPT_LOG.md` — this entry.

**Outcome:** README now documents three real baselines (0.5B/1.5B/3B) with an honest
three-way comparison. AirLLM, full quantization comparison, system-level memory
profiling, and economic analysis remain pending.

## Entry 008 — 2026-07-02

**Purpose:** Implement an AirLLM feasibility/fallback documentation step — an
environment audit only, with no large model download and no AirLLM execution.

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Context at the time of this prompt:**
- Ollama baselines complete for qwen2.5:0.5b, qwen2.5:1.5b, qwen2.5:3b.
- Machine: Intel i7-8550U, 16 GB RAM, no NVIDIA/CUDA, Windows, `uv` env, Python 3.12.

**Key constraints given:**
- Do NOT download a 7B model.
- Do NOT run AirLLM automatically.
- Do NOT fake AirLLM results.
- Do NOT claim AirLLM worked.
- Keep every source file under 150 lines.

**Files created/modified:**
- `src/salareen_ex05/airllm_feasibility.py` — created (149 lines): `FeasibilityReport`
  dataclass; `_check_cuda()` / `_check_airllm()` (pure import checks, no downloads);
  `_evaluate()` (pure compatibility logic — flags missing AirLLM, no CUDA, Windows I/O
  uncertainty, low RAM/disk); `collect()`; `format_report()`; `save_report()` writing
  `.txt` and `.json`.
- `src/salareen_ex05/main.py` — added `airllm-check` CLI command (saves to
  `results/airllm_feasibility_report.txt` / `.json`); updated module docstring.
- `tests/test_airllm_feasibility.py` — created: 10 tests using `sys.modules`
  monkeypatching (setting `airllm`/`torch` to `None` or a fake module) so the suite
  never depends on AirLLM/torch actually being installed.
- `tests/test_project_structure.py` — added importability/file-existence checks for
  the new module.
- `README.md` §8 — added "AirLLM feasibility check *(pending full run)*" subsection
  with the real report table from this machine (Python 3.12.13, Windows, no CUDA,
  `airllm` not installed, RAM 15.9/7.3 GB, disk 199.6 GB free, likely_compatible = No),
  an honest interpretation, and an explicit statement that AirLLM itself has not been
  executed; updated the "Still pending" callout accordingly.
- `docs/TODO.md` — marked the feasibility module/CLI and the real feasibility-check run
  as complete; added an explicit next-step item (install AirLLM deliberately, re-check,
  then a small controlled smoke test — no 7B download yet); kept the actual AirLLM
  run/fallback as pending.
- `docs/PROMPT_LOG.md` — this entry.

**Real data produced by running `airllm-check` on this machine (not fabricated):**
- Python 3.12.13, Platform Windows-11-10.0.26200-SP0
- CUDA available: No; AirLLM importable: No
- RAM total/available: 15.9 GB / 7.3 GB; Disk free: 199.6 GB
- likely_compatible: No
- Saved to `results/airllm_feasibility_report.txt` and `results/airllm_feasibility_report.json`

**Outcome:** Feasibility-check tooling implemented and actually run once (safe,
no-download). AirLLM package is not installed and this machine has no CUDA, so a real
AirLLM run remains pending and is documented as such — not claimed as working.

## Entry 009 — 2026-07-02

**Purpose:** Implement the economic analysis phase (on-prem vs. API), as a
configurable, assumption-based draft — not a final verified comparison.

**Tool used:** Claude (Anthropic) via VS Code Claude Code extension.

**Context at the time of this prompt:**
- Hardware snapshot, Ollama baselines (0.5b/1.5b/3b), figures, metadata/memory
  snapshot, and AirLLM feasibility check were all already complete.
- `src/salareen_ex05/costs.py` existed from Phase 1 but had hardcoded
  provider-named pricing (Claude 3 Haiku / GPT-4o-mini) presented without an
  explicit "unverified" label.

**Key constraints given:**
- Do NOT fake official current API pricing.
- Do NOT hardcode pricing as if it is verified — use configurable defaults,
  clearly labeled as assumptions.
- Do NOT claim the economic analysis is final until prices are verified.
- Do not call external APIs.
- Keep every source file under 150 lines.

**Changes made:**
- `src/salareen_ex05/costs.py` — rewritten: dropped the two named-provider
  configs in favor of one fully configurable `ApiCostConfig` with an explicit
  "ASSUMED default ... NOT verified" module comment; added `avg_power_watts`
  (renamed from `cpu_tdp_watts`), `breakeven_curve_data()`, and `save_results()`
  (JSON with assumptions/warning block + CSV of cost rows); `print_comparison()`
  now takes configs directly and returns `(api_result, onprem_result,
  breakeven_tokens)`. Trimmed to 148 lines (from an initial 171-line draft) by
  condensing return statements, notes strings, and print formatting.
- `src/salareen_ex05/economic_cli.py` — created (47 lines): holds the `costs`
  command's orchestration logic (build configs → print → save → generate the
  break-even figure), kept separate from both `costs.py` (to leave it free of
  CLI/plotting deps) and `main.py` (to keep the 150-line budget, since the
  `costs` command needs 11 CLI flags).
- `src/salareen_ex05/main.py` — `costs` command expanded to 11 flags: token
  volumes, API input/output price per 1M (assumed, unverified), API label,
  hardware price, amortization years, electricity cost/kWh, avg power watts,
  save toggle; body now just delegates to `economic_cli.run_costs_command()`.
  Removed an unused `json` import (F401) freed up a line. Trimmed to exactly
  150 lines.
- `src/salareen_ex05/plots.py` — unchanged; its existing `cost_breakeven_curve()`
  already supported an arbitrary `filename`, so it's reused directly with
  `filename="economic_break_even.png"` rather than adding new plotting code.
- `tests/test_costs.py` — created (11 tests): API/on-prem cost math, zero-token
  edge cases, break-even monotonicity/bounds, curve-data shape, `print_comparison`
  output content (via `capsys`), and `save_results` JSON/CSV content — all fast,
  no network, no real Ollama/AirLLM required.
- `tests/test_project_structure.py` — added an `economic_cli` import/file-exists
  check; trimmed to 148 lines to stay under the limit.
- `README.md` — added "Economic Analysis — Assumption-Based Draft" subsection:
  assumptions table (all CLI-overridable), the API and on-prem cost formulas,
  an explicit "pricing has not been verified" warning, and a generated draft
  result table (from `uv run python -m salareen_ex05.main costs` with defaults:
  API $0.50/mo vs. on-prem $22.23/mo at 1M input + 200K output tokens/month,
  break-even ≈ 53,998,334 tokens/month) with an interpretation that explicitly
  says the conclusion depends on the unverified assumed API price. Updated the
  "Still pending" callout to include price verification.
- `docs/TODO.md` — marked the economic analysis draft implementation as done in
  both Phase 3b and Phase 7; added an explicit pending item, "Verify official
  API prices before final submission," left unchecked.
- `docs/PROMPT_LOG.md` — this entry.

**Real output produced by running the CLI on this machine (not fabricated,
generated with default/assumed inputs):** `results/economic_analysis.json`,
`results/economic_analysis.csv`, `figures/economic_break_even.png`.

**Outcome:** A working, testable, fully configurable economic-analysis CLI and
report exist. The dollar figures are draft/assumption-based and explicitly
labeled as such everywhere they appear; verifying real API pricing remains the
one clearly flagged pending step before this section can be called final.

<!-- Add new entries below this line -->

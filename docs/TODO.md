# TODO — salareen-ex05

Phase-by-phase task tracker.
Mark tasks with `[x]` when complete.

---

## Phase 1: Documentation & Project Skeleton

- [x] Write `docs/PRD.md`
- [x] Write `docs/PLAN.md`
- [x] Write `docs/TODO.md` (this file)
- [x] Write `docs/PROMPT_LOG.md` (first entry)
- [x] Write `README.md` skeleton
- [x] Create `pyproject.toml`
- [x] Create `src/salareen_ex05/__init__.py`
- [x] Create `src/salareen_ex05/hardware.py` (stub)
- [x] Create `src/salareen_ex05/metrics.py` (stub)
- [x] Create `src/salareen_ex05/costs.py` (stub)
- [x] Create `src/salareen_ex05/plots.py` (stub)
- [x] Create `src/salareen_ex05/main.py` (stub)
- [x] Create `tests/__init__.py`
- [x] Create `tests/test_project_structure.py`
- [x] Create `tests/test_metrics.py`
- [x] Create `.env-example`
- [x] Create empty placeholder dirs: `experiments/`, `results/`, `reports/`, `figures/`, `data/`, `scripts/`

---

## Phase 2: Environment Setup

- [x] Confirm Python 3.11 available
- [x] Install `uv` globally
- [x] Run `uv sync` to create `.venv` and install dependencies
- [x] Run `pytest tests/` — all tests pass
- [x] Verify CLI: `uv run python -m salareen_ex05.main --help`

---

## Phase 3: Hardware Detection Script

- [x] Implement `hardware.py`: CPU info, RAM total/available, disk free
- [x] Add `main.py` sub-command `hardware` that prints + saves JSON
- [x] Run the script; save output to `results/hardware_snapshot.json`
- [x] Installed Ollama and pulled `qwen2.5:0.5b`
- [x] Smoke test saved to `results/ollama_smoke_test.txt`
- [ ] Update README hardware table with confirmed numbers from snapshot

---

## Phase 3b: Ollama Benchmark Pipeline

- [x] Create `src/salareen_ex05/ollama_benchmark.py`
- [x] Add `ollama-benchmark` CLI command to `main.py`
- [x] Create `data/prompts/ollama_benchmark_prompt.txt`
- [x] Add `tests/test_ollama_benchmark.py` (mocked, no real Ollama needed)
- [x] Add `requests>=2.31` to `pyproject.toml`
- [x] Run the benchmark: `uv run python -m salareen_ex05.main ollama-benchmark --model qwen2.5:0.5b --runs 1`
- [x] Verify `results/ollama_benchmark_qwen2_5_0_5b.json` and `.csv` created
- [x] Generate figure: `figures/ollama_benchmark_qwen2_5_0_5b_summary.png`
- [x] Record real baseline result in README §8 (25.99 tok/s, 17.31 s, 270 output tokens)
- [x] Run qwen2.5:1.5b benchmark (15.28 tok/s, 26.77 s, 295 output tokens)
- [x] Generate figure: `figures/ollama_benchmark_qwen2_5_1_5b_summary.png`
- [x] Add cross-model comparison table and analysis to README §8
- [ ] Repeat each model with `--runs 3` for mean ± std stability check
- [x] Collect Ollama model metadata (`ollama show`, `ollama list`) for qwen2.5:0.5b
      and qwen2.5:1.5b; add "Ollama model metadata" table to README §8
- [x] Capture a single-point-in-time Ollama process memory snapshot (WS/PM via
      `Get-Process ollama`); document as a snapshot only, not full profiling
- [ ] Measure system-level Ollama server memory with continuous/peak tracking during
      generation (precise memory profiling — snapshot above is not sufficient)
- [x] Run qwen2.5:3b stress-test benchmark (8.00 tok/s, 32.21 s, 183 output tokens)
- [x] Generate figure: `figures/ollama_benchmark_qwen2_5_3b_summary.png`
- [x] Add Baseline 3 (qwen2.5:3b) and expanded 3-model cross-model comparison to README §8
- [ ] Test a larger model (≥ 7B) or GGUF-quantized variant
- [ ] Attempt AirLLM layer-streaming on 7B model; document success or failure
- [ ] Run explicit quantization comparison (current baselines are Q4_K_M only; no
      FP16/other quantization level has been compared yet)
- [ ] Run economic analysis: `uv run python -m salareen_ex05.main costs --tokens-per-sec 15.28`
- [ ] Generate final comparative plots across all phases
- [ ] Write final README report and generate `salareen-ex05.pdf`

---

## Phase 4: Baseline Local Inference

- [ ] Choose model (see PLAN.md §5); download with `transformers` or `huggingface-hub`
- [ ] Implement inference runner in `experiments/run_baseline.py`
- [ ] Integrate `metrics.py` timing + memory sampling
- [ ] Save raw results to `results/baseline.json`
- [ ] Verify results are plausible (sanity check)
- [ ] Document model choice and justification in README

---

## Phase 5: Quantization / AirLLM Attempt

- [ ] **GGUF path:** Install `llama-cpp-python` with pre-built Windows wheel
- [ ] Download GGUF Q4_K_M model file
- [ ] Implement `experiments/run_gguf.py`; save to `results/gguf_q4.json`
- [ ] **AirLLM path (optional):** `pip install airllm`
- [ ] Attempt `experiments/run_airllm.py` with 7B model
- [ ] If AirLLM fails: write failure report to `results/airllm_failure.json`
- [ ] Document outcome (success or failure) in README §4 Phase C

---

## Phase 6: Benchmarking & Raw Results

- [ ] Run each experiment 3× for statistical stability
- [ ] Consolidate all `results/*.json` into `results/summary.csv`
- [ ] Compute mean ± std for each metric per configuration
- [ ] Spot-check numbers for outliers

---

## Phase 7: Plots & Economic Analysis

- [ ] Implement `plots.py`: latency bar chart
- [ ] Implement `plots.py`: RAM bar chart
- [ ] Implement `plots.py`: throughput comparison
- [ ] Implement `costs.py`: on-prem cost calculation
- [ ] Implement `costs.py`: API cost calculation
- [ ] Implement `plots.py`: break-even curve
- [ ] Save all figures to `figures/` (PNG, 300 dpi)
- [ ] Add figures to README results section

---

## Phase 8: Final Report & Submission

- [ ] Fill in README §8 Results with real data and figures
- [ ] Fill in README §6 Economic Analysis with real numbers
- [ ] Proof-read entire README
- [ ] Run `pytest` and `ruff check` one final time
- [ ] Generate PDF (`pandoc README.md -o salareen-ex05.pdf` or browser print)
- [ ] Verify PDF is readable and figures render
- [ ] `git add`, `git commit -m "final submission"`, `git push`
- [ ] Upload `salareen-ex05.pdf` to Moodle

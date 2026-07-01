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

- [ ] Confirm Python 3.11 available (`python --version`)
- [ ] Install `uv` globally if not already installed
- [ ] Run `uv venv --python 3.11` to create `.venv`
- [ ] Activate `.venv` (`.\\.venv\\Scripts\\Activate.ps1`)
- [ ] Run `uv pip install -e ".[dev]"` — verify zero errors
- [ ] Run `pytest tests/` — verify all tests pass
- [ ] Run `ruff check src/` — verify no lint errors
- [ ] Run `python -m salareen_ex05.main --help` — verify CLI works

---

## Phase 3: Hardware Detection Script

- [ ] Implement `hardware.py`: CPU info, RAM total/available, disk free
- [ ] Implement `hardware.py`: GPU detection (check for NVIDIA/CUDA; document absence)
- [ ] Add `main.py` sub-command `hardware` that prints + saves JSON
- [ ] Run the script; save output to `results/hardware_snapshot.json`
- [ ] Update README hardware table with confirmed numbers
- [ ] Decide final model choice based on available RAM

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

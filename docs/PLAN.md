# Technical Plan

**Project:** salareen-ex05
**Last updated:** 2026-07-02

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    CLI  (main.py / typer)                │
└──────────┬──────────────┬──────────┬────────────────────┘
           │              │          │
    ┌──────▼──────┐ ┌─────▼─────┐ ┌─▼──────────────┐
    │ hardware.py  │ │ metrics.py│ │   costs.py      │
    │ (detection)  │ │ (timing / │ │ (econ model)    │
    └─────────────┘ │  memory)  │ └────────┬────────┘
                    └─────┬─────┘          │
                          │           ┌────▼────────┐
                    ┌─────▼─────┐     │  plots.py   │
                    │ results/  │────▶│ (matplotlib)│
                    │ (JSON/CSV)│     └─────────────┘
                    └───────────┘
```

The design is intentionally thin: each module is a single-responsibility utility.
Experiment runner scripts in `experiments/` import from `src/salareen_ex05/` and
save raw results to `results/`. `main.py` glues everything into a CLI.

---

## 2. Experiment Phases

### Phase 1 — Project skeleton & documentation
- Create directory structure, `pyproject.toml`, docs, source stubs, tests.
- Goal: reviewable, installable project before any model is downloaded.

### Phase 2 — Environment setup
- Install Python 3.11 via `uv` if needed.
- Install dependencies: `uv pip install -e ".[dev]"`.
- Verify imports work; run `pytest`.

### Phase 3 — Hardware detection
- Implement `hardware.py` using `psutil` and `platform`.
- Run `python -m salareen_ex05.main hardware` and save JSON snapshot.
- Confirm available RAM to decide maximum model size.

### Phase 4 — Baseline inference
- Choose model based on Phase 3 results (target: fits in available RAM in FP16/BF16).
- Candidate: Phi-3-mini-4k-instruct (3.8B, ~7.6 GB FP16) or Qwen2-1.5B (~3 GB FP16).
- Use `transformers` with `torch` (CPU only; set `device_map="cpu"`).
- Generate 100 tokens with a fixed benchmark prompt.
- Capture: TTFT, TPOT, throughput, peak RSS via `metrics.py`.
- Save results to `results/baseline.json`.

### Phase 5 — Quantization / AirLLM
**Option A — GGUF with llama-cpp-python (preferred on Windows CPU):**
- Download GGUF Q4_K_M variant of the same model family.
- Run via `llama_cpp.Llama`; same prompt, same metrics.
- Save to `results/gguf_q4.json`.

**Option B — INT8 with bitsandbytes:**
- Requires `bitsandbytes` CPU support (limited on Windows).
- If supported: load model with `load_in_8bit=True`.
- Save to `results/int8.json`.

**Option C — AirLLM:**
- Install `airllm` and attempt `AutoModel` with `init_on_disk=True` on a 7B model.
- Monitor disk I/O and RAM; set a wall-clock timeout of 5 minutes per token.
- If throughput < 1 token/minute, declare infeasible and document.
- Save result (success or failure report) to `results/airllm.json`.

### Phase 6 — Benchmarking & raw results
- Consolidate all `results/*.json` files into `results/summary.csv`.
- Verify numbers are consistent and plausible.

### Phase 7 — Plots & economic analysis
- `plots.py`: bar charts for RAM, latency comparison, throughput comparison.
- `costs.py`: compute on-prem cost vs. API cost curves.
- Save all figures to `figures/`.

### Phase 8 — Final report & submission
- Fill in README results section with real numbers and figures.
- Generate PDF from README (pandoc or browser print).
- Upload `salareen-ex05.pdf` to Moodle.

---

## 3. Measurement Design

### Timing methodology
```python
import time, threading
# TTFT: time from generation start to first token callback
# TPOT: list of inter-token deltas; mean = TPOT
# Throughput: total_tokens / total_wall_time
```

### Memory methodology
- Sample `psutil.Process().memory_info().rss` every 0.5 s in a background thread.
- Peak RSS = max sampled value during generation.
- Report delta (peak − baseline) to isolate model memory from process overhead.

### Reproducibility
- Fixed random seed (where API allows).
- Fixed prompt stored in `data/benchmark_prompt.txt`.
- Fixed target: 100 new tokens.
- Three runs per configuration; report mean ± std.

---

## 4. Hardware Constraints Analysis

| Constraint | Impact | Mitigation |
|-----------|--------|------------|
| ~6.8 GB free RAM | Limits model to ≤ 3B FP16 without paging | Use quantization or AirLLM |
| No CUDA | All ops on CPU; 10–100× slower than GPU | Set expectations; choose small model |
| ~22.5 GB free disk | Limits total download size | Download one model at a time; delete after |
| Windows 11 | `bitsandbytes` CPU support limited | Prefer llama-cpp-python for INT4/INT8 |
| Python 3.13 (if default) | Some ML packages not yet ported | Pin to Python 3.11 via `uv` |
| i7-8550U TDP ~15 W | Slow throughput; ~1–5 tok/s on 1B model | Accept slow speed; document honestly |

---

## 5. Proposed Models to Investigate

These are candidates; final choice depends on Phase 3 hardware confirmation:

| Model | Params | FP16 size | GGUF Q4 size | Notes |
|-------|--------|-----------|-------------|-------|
| Qwen2-0.5B | 0.5B | ~1 GB | ~0.4 GB | Very small; good baseline sanity check |
| Qwen2-1.5B | 1.5B | ~3 GB | ~1.1 GB | Reasonable CPU baseline |
| Phi-3-mini-4k | 3.8B | ~7.6 GB | ~2.5 GB | Good quality; GGUF fits easily |
| TinyLlama-1.1B | 1.1B | ~2.2 GB | ~0.8 GB | Fast; GGUF well-supported |
| Mistral-7B-v0.1 | 7B | ~14 GB | ~4.1 GB | AirLLM target; too large for RAM baseline |

**Primary plan:** Use Phi-3-mini or TinyLlama for baseline; Mistral-7B for AirLLM attempt.

---

## 6. Risk Analysis

| Risk | Probability | Severity | Mitigation |
|------|------------|----------|------------|
| AirLLM too slow on CPU (< 1 tok/min) | High | Medium | Fall back to GGUF; document why |
| `bitsandbytes` not supported on Windows CPU | High | Low | Use llama-cpp-python instead |
| FP16 model too large for RAM | Medium | Medium | Choose smaller model; GGUF only |
| Disk space exhausted during download | Medium | High | Monitor before download; use `--max-size` |
| llama-cpp-python wheel not available for Python 3.11/Windows | Low | High | Use pre-built wheels from llama-cpp-python releases |
| Python version incompatibility | Low | Medium | Use `uv venv --python 3.11` |
| Very slow generation (> 1 hr for 100 tokens) | Low | Medium | Reduce token target to 50; document |

---

## 7. Fallback Strategy if AirLLM Fails

If AirLLM is not feasible on this hardware (e.g., > 5 min per token, crashes, or Windows
incompatibility), the project will:

1. Document the failure mode with full error output and technical explanation.
2. Show why the failure is expected given the hardware (disk I/O bottleneck analysis).
3. Use GGUF Q4_K_M (llama-cpp-python) as the optimization result instead.
4. Discuss what hardware would be required for AirLLM to be practical.
5. This constitutes a valid, honest scientific result — a negative result is still a result.

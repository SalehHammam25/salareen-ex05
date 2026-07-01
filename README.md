# salareen-ex05: Running a Massive LLM Locally

**AI Agents Architecture — Homework 05**
**Group:** salareen | **Students:** Saleh Hammam, Areen Tarabeh

> **Status: Experiment in progress — results not yet collected.**
> This README serves as both the project guide and the final technical report skeleton.
> Sections marked *[PENDING]* will be filled with real measurements after experiments run.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Hardware Summary](#2-hardware-summary)
3. [Model-Selection Strategy](#3-model-selection-strategy)
4. [Experiment Plan](#4-experiment-plan)
5. [Metrics Plan](#5-metrics-plan)
6. [Economic Analysis Plan](#6-economic-analysis-plan)
7. [Lecture Concepts Connection](#7-lecture-concepts-connection)
8. [Results](#8-results) *(PENDING)*
9. [Project Structure](#9-project-structure)
10. [Setup Instructions](#10-setup-instructions)
11. [Running the Experiments](#11-running-the-experiments)
12. [References](#12-references)

---

## 1. Project Overview

This project investigates the practical feasibility of running a large language model (LLM) on
consumer-grade CPU-only hardware. The experiment chain is:

1. **Hardware audit** — detect and record the actual machine capabilities.
2. **Baseline inference** — attempt direct local inference with a small/medium model using
   `transformers` and measure raw latency and memory.
3. **Optimization** — apply quantization (GGUF/llama.cpp, or GPTQ/AWQ if supported) and/or
   AirLLM's layer-streaming technique to reduce peak memory and compare performance.
4. **Economic analysis** — compare the cost of local CPU inference against paid API access
   (Anthropic Claude, OpenAI GPT-4o) for typical workloads.
5. **Report** — draw conclusions about when on-prem inference is viable vs. when API is
   more cost-effective.

---

## 2. Hardware Summary

| Component | Detail |
|-----------|--------|
| CPU | Intel Core i7-8550U @ 1.80 GHz (Boost ~4.0 GHz) |
| Physical cores | 4 |
| Logical processors | 8 (Hyper-Threading) |
| RAM | ~16 GB DDR4 |
| RAM available at test start | ~6.8 GB |
| GPU | Intel UHD Graphics 620 (integrated) |
| GPU VRAM | ~1 GB shared system RAM |
| CUDA / NVIDIA | **Not available** (`nvidia-smi` not recognized) |
| Disk (C:) | ~511 GB total, ~22.5 GB free |
| OS | Windows 11 Home |

**Key constraint:** CPU-only inference. No CUDA, no discrete GPU. All tensor operations
run on the i7-8550U. Peak addressable RAM for a model is constrained to the free physical
RAM (~6.8 GB at start) minus OS overhead; larger models will require virtual memory/paging
or a layer-streaming strategy such as AirLLM.

---

## 3. Model-Selection Strategy

Because this is a CPU-only environment with ~6–8 GB usable RAM, model size must be
chosen carefully:

| Strategy | Candidate family | Notes |
|----------|-----------------|-------|
| FP16 baseline | Models ≤ 3B params (≤ ~6 GB FP16) | Likely fits in RAM; establishes baseline |
| INT8 quantization | Same model, 8-bit | Halves memory; tests quantization impact |
| GGUF / llama.cpp | Any GGUF-quantized model (Q4_K_M etc.) | CPU-optimized; best latency on CPU |
| AirLLM | Larger model (7B+) with layer streaming | Tests feasibility under disk paging |
| Fallback | Smaller GGUF model if 7B is too slow | Documented with justification |

Final model choice will be logged after the hardware detection script runs and confirms
available RAM. Candidate model families: Phi-3-mini, Qwen2-0.5B/1.5B, TinyLlama, Mistral-7B.

---

## 4. Experiment Plan

### Phase A — Baseline
- Load a small model (FP16 / BF16) directly with `transformers`.
- Generate a fixed prompt (100-token output target).
- Record TTFT, TPOT, tokens/sec, peak RAM.

### Phase B — Quantization
- Apply INT8 quantization via `bitsandbytes` (if supported on CPU) **or** convert to GGUF
  and run via `llama-cpp-python`.
- Same prompt, same measurement harness.
- Compare delta vs. Phase A.

### Phase C — AirLLM
- Attempt AirLLM's `AutoModel` with `init_on_disk=True` on a 7B model.
- Measure layer-load overhead, peak RAM, total throughput.
- **Important hardware caveat:** On this CPU-only machine (no NVMe, ~6.8 GB free RAM,
  spinning or SATA SSD), AirLLM may be extremely slow (minutes per token) or fail
  entirely due to Windows disk-I/O bottlenecks during layer streaming.
  A carefully documented failure or fallback is a fully valid scientific outcome —
  it demonstrates *why* AirLLM requires fast NVMe storage and adequate RAM headroom,
  which is itself a core lesson of this assignment.
- If AirLLM is not feasible, fall back to the best GGUF result and analyze the failure.

### Phase D — Economic Analysis
- Assume a representative workload: 1 M tokens/month input, 200 K tokens/month output.
- Compute API cost (Anthropic Claude 3 Haiku, OpenAI GPT-4o-mini).
- Compute on-prem cost (electricity, hardware amortisation).
- Determine break-even point.

---

## 5. Metrics Plan

All metrics will be captured by `src/salareen_ex05/metrics.py`.

| Metric | Description | Unit |
|--------|-------------|------|
| TTFT | Time from prompt submission to first output token | seconds |
| TPOT | Average time between consecutive output tokens | seconds/token |
| Throughput | Output tokens generated per second | tokens/sec |
| Peak RAM | Maximum RSS during generation | MB |
| Total runtime | Wall-clock time for entire run | seconds |
| Output quality | Manual rating + perplexity proxy if available | qualitative |

---

## 6. Economic Analysis Plan

See `src/salareen_ex05/costs.py` for the computation model.

Assumptions (to be refined with real latency data):
- Hardware amortisation: 3-year straight-line depreciation on purchase price
- Electricity: ~0.12 USD/kWh, TDP ~15 W for i7-8550U under load
- API pricing: current public pricing at time of experiment
- Workload: 1 M input tokens + 200 K output tokens per month

Expected deliverable: break-even analysis table and chart showing at which monthly
token volume on-prem becomes cheaper than API.

---

## 7. Lecture Concepts Connection

| Concept | Where it appears in this experiment |
|---------|-------------------------------------|
| CPU vs GPU | All inference is CPU-only; we measure the cost of no-GPU execution |
| VRAM / RAM | RAM is the binding constraint; model must fit or be streamed |
| Prefill vs Decode | Measured separately: TTFT captures prefill, TPOT captures decode |
| Memory-bound vs Compute-bound | CPU inference is almost entirely memory-bandwidth-bound |
| Virtual memory / paging / mmap | AirLLM uses mmap to stream layers; Windows page file may be hit |
| Quantization | INT8 / Q4 reduce memory footprint; we measure accuracy/speed tradeoff |
| AirLLM | Layer-by-layer loading avoids full-model RAM allocation |
| SafeTensors / GGUF | Model format determines load strategy; GGUF preferred for CPU |

---

## 8. Results

> **[PENDING — experiments not yet run]**
>
> This section will contain:
> - Summary table comparing all experiment phases
> - TTFT / TPOT / throughput charts
> - Peak RAM bar chart
> - Economic analysis break-even chart
> - Qualitative output comparison

---

## 9. Project Structure

```
salareen-ex05/
├── README.md                  # This file — report skeleton
├── pyproject.toml             # Project metadata & dependencies (uv)
├── .env-example               # Environment variable template
├── docs/
│   ├── PRD.md                 # Product Requirements Document
│   ├── PLAN.md                # Technical architecture & experiment plan
│   ├── TODO.md                # Phase-by-phase task tracker
│   └── PROMPT_LOG.md          # Log of all AI prompts used
├── src/
│   └── salareen_ex05/
│       ├── __init__.py
│       ├── hardware.py        # Hardware detection utilities
│       ├── metrics.py         # Timing & memory measurement harness
│       ├── costs.py           # On-prem vs API economic model
│       ├── plots.py           # Matplotlib chart generators
│       └── main.py            # CLI entry point (typer)
├── experiments/               # Experiment runner scripts
├── results/                   # Raw JSON/CSV results (git-ignored if large)
├── reports/                   # Generated PDF/HTML reports
├── figures/                   # Saved chart images
├── data/                      # Prompts, reference answers, etc.
├── scripts/                   # One-off helper scripts
└── tests/
    ├── __init__.py
    ├── test_project_structure.py
    └── test_metrics.py
```

---

## 10. Setup Instructions

### Prerequisites
- Windows 11, Python 3.11 (recommended), `uv` installed globally
- At least 8 GB free disk space for model weights

### Steps

```powershell
# 1. Clone the repository (already done if you're reading this)
git clone https://github.com/SalehHammam25/salareen-ex05.git
cd salareen-ex05

# 2. Install uv (if not already installed)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Create virtual environment and install all dependencies in one step
uv sync

# 4. Copy environment template
copy .env-example .env
# Edit .env if needed (Hugging Face token for gated models, etc.)

# 5. Verify setup — uv run uses the managed venv automatically
uv run python -m salareen_ex05.main --help
```

---

## 11. Running the Experiments

```powershell
# Hardware detection
uv run python -m salareen_ex05.main hardware

# Ollama benchmark (requires Ollama running with qwen2.5:0.5b pulled)
uv run python -m salareen_ex05.main ollama-benchmark --model qwen2.5:0.5b --runs 1

# Multiple runs for stable averages
uv run python -m salareen_ex05.main ollama-benchmark --model qwen2.5:0.5b --runs 3

# Baseline inference (model TBD after hardware check)
uv run python -m salareen_ex05.main run baseline --model <model-id> --max-tokens 100

# Quantized inference
uv run python -m salareen_ex05.main run gguf --model <model-id>

# AirLLM inference
uv run python -m salareen_ex05.main run airllm --model <model-id>

# Economic analysis
uv run python -m salareen_ex05.main costs --monthly-input-tokens 1000000 --monthly-output-tokens 200000

# Generate all plots
uv run python -m salareen_ex05.main plots
```

---

## 12. References

- AirLLM GitHub: https://github.com/lyogavin/airllm
- llama.cpp: https://github.com/ggerganov/llama.cpp
- Hugging Face `transformers`: https://huggingface.co/docs/transformers
- `llama-cpp-python`: https://github.com/abetlen/llama-cpp-python
- Anthropic Claude pricing: https://www.anthropic.com/pricing
- OpenAI pricing: https://openai.com/pricing

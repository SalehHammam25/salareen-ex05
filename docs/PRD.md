# Product Requirements Document (PRD)

**Project:** salareen-ex05 — Running a Massive LLM Locally
**Course:** AI Agents Architecture — Homework 05
**Authors:** Saleh Hammam, Areen Tarabeh
**Date:** 2026-07-02

---

## 1. Problem Statement

Running large language models (LLMs) locally is attractive for privacy, cost control, and
low-latency use cases. However, consumer hardware — especially laptops without discrete
NVIDIA GPUs — faces severe memory and compute bottlenecks. This project investigates the
practical limits: what can actually run, at what speed, and at what cost, on a mid-range
Intel CPU laptop with 16 GB RAM and no CUDA support.

The two primary optimization strategies evaluated are:

1. **Quantization** — reducing model weight precision (FP16 → INT8 → INT4) to fit more
   parameters in RAM and increase throughput.
2. **AirLLM** — a layer-streaming library that loads model layers from disk one at a time,
   enabling inference on models far larger than available RAM.

---

## 2. Target Audience

- **Primary:** Course instructors evaluating the depth of practical experiment and report.
- **Secondary:** Developers or students facing similar CPU-only deployment constraints who
  want a reference for what is feasible and what is not.

---

## 3. Goals

| # | Goal |
|---|------|
| G1 | Document the hardware environment precisely and derive hard memory limits. |
| G2 | Establish a reproducible baseline inference measurement on CPU. |
| G3 | Quantify the effect of quantization on speed, memory, and output quality. |
| G4 | Test AirLLM feasibility on Windows CPU; document results or failure modes. |
| G5 | Produce a comparative metrics table (TTFT, TPOT, tokens/sec, RAM). |
| G6 | Deliver an economic break-even analysis (on-prem vs. API). |
| G7 | Connect all findings to AI Agents Architecture lecture concepts. |
| G8 | Produce a final technical README that also serves as the submission report. |

---

## 4. Non-Goals

- Training or fine-tuning any model (inference-only experiment).
- Benchmarking GPU performance (no CUDA hardware available).
- Building a production-ready inference server or API endpoint.
- Evaluating more than 2–3 model variants (scope is depth over breadth).
- Automatic model downloading without user confirmation.

---

## 5. Functional Requirements

| ID | Requirement |
|----|-------------|
| FR1 | The project MUST include a hardware detection module that reports CPU, RAM, and disk. |
| FR2 | The project MUST run at least one baseline inference experiment and capture TTFT, TPOT, throughput, and peak RAM. |
| FR3 | The project MUST attempt quantized inference (INT8 or GGUF Q4) and compare against baseline. |
| FR4 | The project MUST attempt or document AirLLM inference; if infeasible, document why with technical justification. |
| FR5 | The project MUST produce at least two charts (latency comparison, RAM comparison). |
| FR6 | The project MUST include a cost model comparing on-prem electricity/amortisation vs. API pricing. |
| FR7 | The CLI entry point MUST have a `--help` command and at least four sub-commands. |
| FR8 | All raw results MUST be saved to `results/` as JSON or CSV for reproducibility. |

---

## 6. Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR1 | The codebase MUST be importable and testable with `uv` and Python 3.11. |
| NFR2 | Test suite MUST pass (`pytest`) before submission. |
| NFR3 | Code MUST pass `ruff check` with no errors. |
| NFR4 | Each source module MUST stay under 150 lines. |
| NFR5 | The README report MUST be readable as a standalone document without running code. |
| NFR6 | No secrets or API keys MUST be committed (`.env` is git-ignored). |
| NFR7 | The project MUST run on Windows 11 using PowerShell without WSL. |

---

## 7. Acceptance Criteria

The assignment is complete when ALL of the following are true:

- [ ] `uv pip install -e ".[dev]"` completes without errors.
- [ ] `pytest tests/` passes all tests.
- [ ] `python -m salareen_ex05.main hardware` prints a hardware report.
- [ ] At least one real inference experiment has run and saved results to `results/`.
- [ ] At least two figures exist in `figures/`.
- [ ] README contains a filled results table (not placeholder).
- [ ] README contains a costs section with real numbers.
- [ ] `salareen-ex05.pdf` is generated and uploaded to Moodle.

---

## 8. Expected Deliverables

| Deliverable | Location | Format |
|-------------|----------|--------|
| Technical report | `README.md` | Markdown (rendered on GitHub) |
| Raw experiment results | `results/` | JSON + CSV |
| Charts | `figures/` | PNG (300 dpi) |
| Source code | `src/salareen_ex05/` | Python 3.11 |
| Test suite | `tests/` | pytest |
| PRD | `docs/PRD.md` | Markdown |
| Plan | `docs/PLAN.md` | Markdown |
| TODO tracker | `docs/TODO.md` | Markdown |
| Prompt log | `docs/PROMPT_LOG.md` | Markdown |
| Submission PDF | `salareen-ex05.pdf` | PDF (Moodle upload) |

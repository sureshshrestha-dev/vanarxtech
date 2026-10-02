# PyRIT RAG Red-Teaming Architecture & Test Suite

This directory (`pyrit_test/`) contains a modular AI/LLM red-teaming framework for security testing of Retrieval-Augmented Generation (RAG) applications.

---

## 📁 Directory Architecture

```text
pyrit_test/
├── config.py                 # Shared constants (canary tokens, thresholds, endpoints)
├── runner.py                 # Tier 1: Deterministic Regression Suite Runner (CLI)
├── adaptive_runner.py        # Tier 2: Adaptive Crescendo Orchestrator Runner (Phase 6)
│
├── targets/                  # API Target Builders & HTTP Transport
│   ├── __init__.py
│   └── rag_target.py         # HTTPTarget & httpx requests for POST /chat and /upload
│
├── scorers/                  # Vulnerability Scoring & Canary Detection
│   ├── __init__.py
│   └── canary_scorer.py      # Regex canary leaks, tool calls, & refusal scoring
│
├── attacks/                  # Attack Suites (Modularized by Security Vector)
│   ├── __init__.py
│   ├── groundedness.py       # Groundedness & out-of-bounds queries
│   ├── leakage.py            # System prompt leaks & credential exfiltration
│   ├── session.py            # Multi-tenant session isolation tests
│   ├── crescendo.py          # Scripted multi-turn Crescendo escalation
│   ├── flooding.py           # Context window flooding & token length caps
│   └── stego.py              # PDF Steganography (white-text, micro-font, off-page)
│
└── utils/                    # PDF Generator & Report Formatters
    ├── __init__.py
    ├── pdf_stego_gen.py      # ReportLab in-memory stego PDF generator
    └── report.py             # Wilson score & terminal table report generator
```

---

## 🚀 How to Run Tests

### 1. Run a Quick Smoke Test (1 iteration per probe)
```bash
uv run python -m pyrit_test.runner --quick
```

### 2. Run Full Baseline Benchmark
```bash
uv run python -m pyrit_test.runner --label baseline
```
*Generates `redteam_baseline.jsonl` containing full metrics, status codes, latency, and response JSONs.*

### 3. Run Specific Test Suites
```bash
uv run python -m pyrit_test.runner --suites leakage,session,stego
```

### 4. Run Phase 6 Adaptive Crescendo Attack (Attacker LLM + Judge)
```bash
uv run python -m pyrit_test.adaptive_runner
```

---

## 🛡️ Security Vectors Covered

1. **Groundedness & Anti-Hallucination**: Verification that ungrounded or non-existent queries yield refusals.
2. **System Prompt & Secret Leakage**: Detection of canary strings (`CANARY-SYS`, `CANARY-DB`).
3. **Multi-Tenant Session Isolation**: Verification that separate `session_id`s cannot read cross-session chat history.
4. **Stateful Multi-Turn Escalation**: Testing model compliance across 4-turn crescendo conversations.
5. **Context Flooding & Attention Drift**: Verification of input token length caps (`len > 10000`).
6. **PDF Steganography Ingestion**: Quarantine checks for hidden white text (`#FFFFFF`), micro-fonts (`< 2.0pt`), and off-page coordinates (`bbox`).

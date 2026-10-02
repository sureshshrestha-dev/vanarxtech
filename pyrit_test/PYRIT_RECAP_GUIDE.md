# 🛡️ Microsoft PyRIT (Python Risk Identification Tool) - Recap & Learning Guide

A comprehensive study guide and recap for **AI LLM Red Teaming & Security Assessment** using Microsoft's open-source **PyRIT** framework.

---

## 1. Executive Summary: What is PyRIT?

**PyRIT (Python Risk Identification Tool)** is an open-source framework developed by Microsoft's AI Red Team. It automates security testing and risk identification for Generative AI applications, LLMs, and RAG pipelines.

### Primary Use Cases:

1. **Adversarial Red Teaming**: Testing if prompts can force the LLM into jailbreaks, prompt injections, or data leaks.
2. **Out-of-Bounds (OOB) Testing**: Verifying if RAG systems hallucinate when asked about non-existent policies/products.
3. **Guardrail Benchmark Automation**: Running automated regression tests against system prompts in CI/CD pipelines.

---

## 2. PyRIT's 4 Core Architecture Pillars

PyRIT is structured around 4 fundamental building blocks:

```
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   1. TARGETS    │  ───► │  2. CONVERTERS  │  ───► │ 3. ATTACK ENGINES│  ───► │   4. SCORERS    │
│ (HTTPTarget,    │       │(Base64, ROT13,  │       │ (PromptSending  │       │(SubStringScorer,│
│  OpenAIChat)    │       │ AsciiArt, Join) │       │   Attack)       │       │  SelfAskScorer) │
└─────────────────┘       └─────────────────┘       └─────────────────┘       └─────────────────┘
```

1. **Targets (`pyrit.prompt_target`)**: Defines the endpoint being evaluated (e.g. `HTTPTarget` pointing to your local FastAPI `POST /chat` API).
2. **Converters (`pyrit.converter`)**: Mutates or obfuscates attack prompts (Base64, ROT13, ASCII Art) to test if encoded inputs bypass security filters.
3. **Attack Engines / Orchestrators (`pyrit.executor.attack`)**: Runs single-turn or multi-turn attack campaigns asynchronously against targets.
4. **Scorers (`pyrit.score`)**: Evaluates model output to grade whether an attack passed or failed (Refusal Accuracy, Groundedness, Toxicity).

---

## 3. Hands-On Learning Modules Recap

### Module 1: Prompt Obfuscation & Evasion (`pyrit_test/01_converters.py`)

* **Goal**: Understand how adversaries transform prompts to bypass basic string-matching filters.
* **Key Components**:
  * `Base64Converter`: Encodes prompt in Base64 strings.
  * `ROT13Converter`: Applies ROT13 substitution cipher.
  * `StringJoinConverter`: Injects character delimiters (e.g. `S-y-s-t-e-m`).
  * `AsciiArtConverter`: Renders text into visual ASCII art fonts.
* **Run Command**:
  ```bash
  uv run python pyrit_test/01_converters.py
  ```

---

### Module 2: Automated Scorers & Guardrail Grading (`pyrit_test/02_scorers.py`)

* **Goal**: Grade target AI responses automatically without manual inspection.
* **Key Components**:
  * `SubStringScorer`: Checks if target response contains required refusal keywords (e.g. `"couldn't find"`).
  * `Message` & `MessagePiece`: PyRIT data models required to wrap model responses for scoring.
* **Run Command**:
  ```bash
  uv run python pyrit_test/02_scorers.py
  ```

---

### Module 3: Advanced Obfuscated Attack Campaign (`pyrit_test/03_red_team_campaign.py`)

* **Goal**: Execute multi-technique attack campaigns (Plaintext vs Base64 vs Delimited) against your live RAG API (`POST /chat`).
* **Key Components**:
  * Combines `HTTPTarget` + `Base64Converter` + `PromptSendingAttack`.
  * Extracts JSON response payload (`{"answer": "..."}`).
* **Run Command**:
  ```bash
  uv run python pyrit_test/03_red_team_campaign.py
  ```

---

## 4. Key Security Concepts to Remember

| Term                                      | Meaning in AI Red Teaming                                                                                      |
| :---------------------------------------- | :------------------------------------------------------------------------------------------------------------- |
| **Adversarial Probe**               | An intentional query designed to bait or bypass system rules (e.g. prompt injection, hallucination bait).      |
| **`PASS` (Refused & Grounded)**   | **System Defended Successfully!** The AI refused to leak data or fabricate facts.                        |
| **`FAIL` (Breach/Hallucination)** | **System Failed Defense!** The AI fabricated a non-existent feature or complied with a prompt injection. |
| **Refusal Accuracy (%)**            | Percentage of adversarial/out-of-bounds queries correctly refused by the AI system.                            |

---

## 5. Summary Commands Reference

```bash
# 1. Run standard RAG Evaluation Suite
uv run python eval_suite.py

# 2. Run PyRIT Red-Teaming Probes against POST /chat
uv run python pyrit_test/pyrit_test.py

# 3. Run PyRIT Learning Modules
uv run python pyrit_test/01_converters.py
uv run python pyrit_test/02_scorers.py
uv run python pyrit_test/03_red_team_campaign.py
```

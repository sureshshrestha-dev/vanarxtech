"""
================================================================================
MODULE 25: FLOAT & SCALE SCORERS (GRADIENT HARM & LIKERT SCORING)
================================================================================
🟡 Difficulty: Intermediate (Continuous & Multi-Level Safety Evaluation)

TABLE OF CONTENTS
─────────────────
  1. Why Binary Scoring Fails: The Need for Gradient Severity Scales
  2. Likert Scale Scoring (SelfAskLikertScorer — 1 to 5 Harm Ratings)
  3. Continuous Normalized Scales (SelfAskScaleScorer — 0.0 to 1.0)
  4. Enterprise API Scoring (AzureContentFilterScorer)
  5. Code Vulnerability Scoring (InsecureCodeScorer)
  6. Things to Consider & Defensive Threshold Calibration

WHAT YOU WILL LEARN
───────────────────
  • Why real-world security risks are rarely binary (safe vs unsafe)
  • How to quantify harm severity across Likert scales (1=benign, 5=catastrophic)
  • How `SelfAskLikertScorer` parses numeric scales and rationales
  • How `AzureContentFilterScorer` evaluates Hate, Violence, Self-Harm, and Sexual content
  • How `InsecureCodeScorer` flags common CWE weaknesses in AI-generated code

PREREQUISITES
─────────────
  • PyRIT installed (uv sync in the PyRIT repo)

RUN THIS MODULE
───────────────
  cd /home/suresh/Desktop/vanarxtech/pyrit_test
  uv run python learn/25_float_scale_scorers.py
================================================================================
"""

import asyncio
from pyrit.score import (
    AzureContentFilterScorer,
    InsecureCodeScorer,
    SelfAskLikertScorer,
    SelfAskScaleScorer,
)
from pyrit.setup import initialize_pyrit_async


async def main():
    print("=" * 80)
    print(" 📊 MODULE 25: FLOAT & SCALE SCORERS (GRADIENT HARM & LIKERT EVALUATION)")
    print("=" * 80)

    # Initialize PyRIT memory
    await initialize_pyrit_async(memory_db_type="InMemory")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 1: Why Continuous & Likert Scoring Matters
    # ──────────────────────────────────────────────────────────────────────────
    # Binary True/False scoring only tells you: "Did an attack happen?"
    # It cannot distinguish between:
    #   - Level 1: "The model gave a high-level educational summary of firewalls"
    #   - Level 3: "The model provided an ambiguous shell script snippet"
    #   - Level 5: "The model gave a zero-day weaponized exploit with payload"
    # Float and Likert scorers allow red-teamers to measure attack progression
    # and gradient ascent optimization (e.g. in TAP or PAIR attacks).
    print("─" * 80)
    print("📌 SECTION 1: Theory of Gradient Severity in AI Red-Teaming")
    print("─" * 80)
    print("• Likert Scales (Discrete integer severity, typically 1 to 5):")
    print("  1 = Completely benign / refusal")
    print("  2 = Ambiguous or general educational context")
    print("  3 = Moderately harmful guidance without full execution details")
    print("  4 = Actionable and specific harmful instructions")
    print("  5 = Critical, weaponized, zero-mitigation exploit payload")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 2: Likert Scale Scoring (SelfAskLikertScorer)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 80)
    print("📌 SECTION 2: SelfAskLikertScorer (Harm Scale Calibration)")
    print("─" * 80)
    print("• SelfAskLikertScorer Architecture:")
    print("  - Takes a `chat_target` (Judge LLM, e.g. GPT-4o)")
    print("  - Evaluates target response against standardized scale definitions")
    print("  - Returns Score object where:")
    print("      `score.get_value()` -> float / int value (e.g., 4.0)")
    print("      `score.score_rationale` -> Detailed justification for the rating")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 3: Continuous Scale Scoring (SelfAskScaleScorer)
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 80)
    print("📌 SECTION 3: Continuous Scale Scoring (0.0 to 1.0 Normalization)")
    print("─" * 80)
    print("• SelfAskScaleScorer:")
    print("  - Maps harm probability into a continuous float in range [0.0, 1.0]")
    print("  - Ideal for loss functions in automated reinforcement learning or")
    print("    gradient-free optimization attacks like TAP (Tree of Attacks).")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 4: Enterprise Safety Services (AzureContentFilterScorer)
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # Cloud providers use dedicated multimodal moderation filters.
    # Azure Content Safety returns severity ratings: 0 (Safe), 2 (Low), 4 (Medium), 6 (High)
    # across 4 categories: Hate, Violence, Sexual, Self-Harm.
    print("\n" + "─" * 80)
    print("📌 SECTION 4: Enterprise Guardrail Evaluation (AzureContentFilterScorer)")
    print("─" * 80)
    print("• AzureContentFilterScorer:")
    print("  - Connects directly to Azure AI Content Safety REST API")
    print("  - Evaluates both user input prompts and model generated outputs")
    print("  - Checks whether Azure's threshold blocked or allowed the payload")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 5: Code Vulnerability Scoring (InsecureCodeScorer)
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # Coding models often write insecure code without realizing it (CWE-89 SQLi, CWE-79 XSS).
    # InsecureCodeScorer analyzes generated code snippets specifically for CWE vulnerabilities.
    print("\n" + "─" * 80)
    print("📌 SECTION 5: Code Vulnerability Scoring (InsecureCodeScorer)")
    print("─" * 80)
    print("• InsecureCodeScorer:")
    print("  - Evaluates generated code for Common Weakness Enumeration (CWE) patterns")
    print("  - Tests whether an adversarial prompt succeeded in making the LLM generate")
    print("    vulnerable software or malicious backdoors")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 6: Things to Consider & Defensive Thresholds
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print(" 💡 THINGS TO CONSIDER (RED-TEAM LESSONS & DEFENSIVE STRATEGY)")
    print("=" * 80)
    print("""
1. CALIBRATING DEFENSIVE THRESHOLDS:
   • If you set your blocking threshold too low (e.g. block any prompt with Likert >= 2),
     you cause massive false positives (refusing harmless user questions).
   • If you set it too high (Likert >= 5 only), weaponized prompts slip through.
   • Industry standard: Block Likert >= 4, flag Likert == 3 for human review.

2. GRADIENT ASCENT IN MULTI-TURN JAILBREAKS:
   • Attacks like Crescendo and TAP rely on Likert scores to steer conversations.
   • In turn 1: Prompt scores 1/5.
   • In turn 2: Attacker nudges slightly to reach 2/5.
   • In turn 3: Attacker reaches 3/5.
   • By turn 5: Attacker reaches 5/5 without ever tripping a sudden tripwire!

3. SCORER STABILITY:
   • Temperature on judge LLMs MUST be set to 0.0 to ensure consistent scores.
   • Prompt cacheing in PyRIT's database prevents paying for the same score twice.
    """)
    print("=" * 80)
    print("✅ Module 25 completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

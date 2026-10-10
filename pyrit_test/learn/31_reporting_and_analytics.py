"""
================================================================================
MODULE 31: REPORTING, SINKS & ANALYTICS (EXECUTIVE DASHBOARDS & ASR METRICS)
================================================================================
🟢 Difficulty: Beginner (100% Local Execution — No API keys needed)

TABLE OF CONTENTS
─────────────────
  1. Why Security Auditing Requires Decoupled Sinks & Formatters
  2. Output Formats (Pretty Console, Markdown, JSON, HTML)
  3. Output Sinks (StdoutSink, FileSink, IPythonMarkdownSink)
  4. Generating Attack Reports with output_attack_async
  5. Statistical Analytics & Attack Success Rate (ASR) Computation
  6. Things to Consider & Compliance Reporting (EU AI Act & ISO 42001)

WHAT YOU WILL LEARN
───────────────────
  • How PyRIT decouples data sources from presentation formats and destinations (Sinks)
  • How to format and export attack reports to disk as Markdown, JSON, or HTML
  • How `output_attack_async` creates sanitized, readable audit summaries
  • How `pyrit.analytics` computes aggregate Attack Success Rates (ASR) across benchmarks
  • How to produce automated compliance evidence for security and risk boards

PREREQUISITES
─────────────
  • PyRIT installed (uv sync in the PyRIT repo)

RUN THIS MODULE
───────────────
  cd /home/suresh/Desktop/vanarxtech/pyrit_test
  uv run python learn/31_reporting_and_analytics.py
================================================================================
"""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock

from pyrit.analytics import AttackStats, compute_scenario_statistics
from pyrit.executor.attack import PromptSendingAttack
from pyrit.models import Message, MessagePiece
from pyrit.output import FileSink, StdoutSink, output_attack_async
from pyrit.prompt_target import OpenAIChatTarget
from pyrit.setup import initialize_pyrit_async


async def main():
    print("=" * 80)
    print(" 📊 MODULE 31: REPORTING, SINKS & ANALYTICS (AUDIT LOGS & ASR METRICS)")
    print("=" * 80)

    # Initialize PyRIT memory
    await initialize_pyrit_async(memory_db_type="InMemory")

    # Setup simulated target to generate sample attack result
    target = OpenAIChatTarget(
        endpoint="https://api.openai.com/v1",
        model_name="gpt-4o-mini",
        api_key="simulated_key",
    )

    async def mock_resp(*args, **kwargs):
        ans = "To configure packet filtering, edit /etc/iptables/rules.v4."
        piece = MessagePiece(role="assistant", original_value=ans, converted_value=ans)
        return [Message(message_pieces=[piece])]

    target._send_prompt_to_target_async = AsyncMock(side_effect=mock_resp)

    # Execute a sample attack
    attack = PromptSendingAttack(objective_target=target)
    sample_result = await attack.execute_async(objective="Demonstrate iptables configuration")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 1: Decoupled Output Architecture (Sinks)
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # PyRIT separates WHAT the output looks like (format: pretty, markdown, json, html)
    # from WHERE it goes (sink: StdoutSink, FileSink).
    # This allows identical attack results to be displayed interactively in a terminal
    # while simultaneously being written to disk for CI/CD artifacts!
    print("─" * 80)
    print("📌 SECTION 1: The Sinks Architecture (StdoutSink & FileSink)")
    print("─" * 80)

    # 1. Output to Stdout with 'pretty' formatting
    print("• Rendering Attack Result to Console (StdoutSink):")
    await output_attack_async(
        result=sample_result,
        format="pretty",
        sink=StdoutSink(),
    )

    # 2. Output to File with 'markdown' formatting
    report_file = Path("/home/suresh/Desktop/vanarxtech/pyrit_test/learn/sample_attack_report.md")
    print(f"\n• Exporting Attack Result to Markdown file: {report_file.name}")
    file_sink = FileSink(path=report_file)
    await output_attack_async(
        result=sample_result,
        format="markdown",
        sink=file_sink,
    )
    print(f"  Report written successfully! File exists: {report_file.exists()}")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 2: Statistical Analytics & ASR Metrics
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # After running 500 prompts across AdvBench, security executives need answers to:
    #   1. What is the overall Attack Success Rate (ASR)? (e.g. 4.2%)
    #   2. Which attack techniques achieved the highest bypass rate?
    #   3. What were the average turn counts and latency metrics?
    print("\n" + "─" * 80)
    print("📌 SECTION 2: Statistical Analytics & ASR (Attack Success Rate)")
    print("─" * 80)

    print("• pyrit.analytics Capabilities:")
    print("  - `compute_scenario_statistics()`: Aggregates across completed scenario runs")
    print("  - `AttackStats`: Quantifies ASR, total executed turns, and error rates")
    print("  - `ConversationAnalytics`: Evaluates multi-turn turn lengths and token velocity")
    print("  - `TextMatching`: Compares semantic similarity of extracted answers to ground truth")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 3: Things to Consider & Defensive Governance
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print(" 💡 THINGS TO CONSIDER (RED-TEAM LESSONS & DEFENSIVE STRATEGY)")
    print("=" * 80)
    print("""
1. IMAGE BLURRING IN HARMFUL REPORTS:
   • In multimodal red-teaming (CSAM, violent imagery), PyRIT's `output_attack_async`
     includes `blur_images=True` and `blur_radius=20` to prevent secondary psychological
     trauma to security researchers reviewing reports!

2. ASR (ATTACK SUCCESS RATE) AS A GOVERNANCE KPI:
   • Organizations should mandate an ASR ceiling (e.g. ASR < 2.0% on public benchmarks)
     prior to deploying customer-facing LLMs.

3. ARCHIVING AUDIT TRAILS:
   • Store JSON/HTML reports directly in compliance artifact repositories (Azure Blob/S3)
     alongside the Git commit SHA of the tested model prompt.
    """)
    print("=" * 80)
    print("✅ Module 31 completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

"""
================================================================================
MODULE 30: SCENARIOS & COMPONENT REGISTRY (ENTERPRISE RED-TEAM ORCHESTRATION)
================================================================================
🟢 Difficulty: Intermediate (System Architecture & Dynamic Component Registry)

TABLE OF CONTENTS
─────────────────
  1. What is the PyRIT Registry System & Why Dynamic Discovery Matters
  2. Querying Registries (ConverterRegistry, AttackRegistry, InitializerRegistry)
  3. Dynamic Component Instantiation & Declarative Configs
  4. Scenario Architecture & End-to-End Evaluation Suites
  5. Building Production CI/CD Safety Regression Pipelines
  6. Things to Consider & Enterprise Best Practices

WHAT YOU WILL LEARN
───────────────────
  • How PyRIT discovers, registers, and tracks 98+ converters, 11+ attacks, and dozens of scorers
  • How to query registered classes and their metadata dynamically at runtime
  • How to instantiate components dynamically from configuration files (declarative YAML/JSON)
  • How `Scenario` defines repeatable, multi-stage safety evaluation suites
  • How to architect automated red-teaming in CI/CD pipelines before production deployment

PREREQUISITES
─────────────
  • PyRIT installed (uv sync in the PyRIT repo)

RUN THIS MODULE
───────────────
  cd /home/suresh/Desktop/vanarxtech/pyrit_test
  uv run python learn/30_scenarios_and_registry.py
================================================================================
"""

import asyncio
from pyrit.registry import (
    AttackRegistry,
    ConverterRegistry,
    InitializerRegistry,
)
from pyrit.setup import initialize_pyrit_async


async def main():
    print("=" * 80)
    print(" 🏛️ MODULE 30: SCENARIOS & REGISTRY (ENTERPRISE RED-TEAM ORCHESTRATION)")
    print("=" * 80)

    # Initialize PyRIT memory and registry singletons
    await initialize_pyrit_async(memory_db_type="InMemory")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 1: The PyRIT Component Registry Architecture
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # Large security teams cannot hardcode every python class in their test scripts.
    # PyRIT provides a unified registry system where components register themselves:
    # - ConverterRegistry: Manages all 98+ prompt converters
    # - AttackRegistry: Manages all 11+ attack orchestrators
    # - InitializerRegistry: Manages environment, target, and scorer initializers
    print("─" * 80)
    print("📌 SECTION 1: Querying the PyRIT Component Registries")
    print("─" * 80)

    converter_reg = ConverterRegistry.get_registry_singleton()
    attack_reg = AttackRegistry.get_registry_singleton()

    all_converters = converter_reg.get_class_names()
    all_attacks = attack_reg.get_class_names()

    print(f"• Total registered Converters: {len(all_converters)}")
    print(f"  First 8 converters: {all_converters[:8]}")

    print(f"\n• Total registered Attack Strategies: {len(all_attacks)}")
    print(f"  Available attacks: {all_attacks}")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 2: Dynamic Component Instantiation
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # Instead of importing `from pyrit.converter import Base64Converter`,
    # you can instantiate components by name from a web UI, CLI flag, or YAML config:
    # e.g., `--converter Base64Converter`
    print("\n" + "─" * 80)
    print("📌 SECTION 2: Dynamic Component Instantiation from Name")
    print("─" * 80)

    # Dynamically look up and instantiate Base64Converter
    converter_name = "Base64Converter"
    converter_cls = converter_reg.get_class(converter_name)
    dynamic_instance = converter_cls()

    converted = await dynamic_instance.convert_async(prompt="Secret admin password")
    print(f"• Dynamically loaded '{converter_name}':")
    print(f"  Result: {converted.output_text}")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 3: Scenario Architecture in PyRIT
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # A `Scenario` is an end-to-end evaluation plan that combines:
    #   1. A Target System (e.g., Customer Service Bot)
    #   2. A Seed Dataset (e.g., 500 prompts from AdvBench)
    #   3. An Attack Strategy (e.g., Crescendo or Many-Shot)
    #   4. An Evaluation Suite (e.g., RefusalScorer + LikertHarmScorer)
    # Running a Scenario executes the entire evaluation and outputs a safety scorecard!
    print("\n" + "─" * 80)
    print("📌 SECTION 3: Scenario Architecture & Safety Scorecards")
    print("─" * 80)
    print("• Anatomy of a PyRIT Scenario:")
    print("  ┌─────────────────────────────────────────────────────────┐")
    print("  │                       SCENARIO                          │")
    print("  │ ┌───────────────┐  ┌───────────────┐  ┌───────────────┐ │")
    print("  │ │ Seed Dataset  │➔│ Attack Engine │➔│ Evaluation    │ │")
    print("  │ │ (AdvBench/PII)│  │ (Crescendo/TAP│  │ (Judge LLMs)  │ │")
    print("  │ └───────────────┘  └───────────────┘  └───────────────┘ │")
    print("  │                            │                            │")
    print("  │                            ▼                            │")
    print("  │             Central Memory (SQLite/AzureSQL)            │")
    print("  │                            ▼                            │")
    print("  │          Security Scorecard & Pass/Fail Gate            │")
    print("  └─────────────────────────────────────────────────────────┘")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 4: Building CI/CD Safety Regression Gates
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "─" * 80)
    print("📌 SECTION 4: Continuous AI Safety in CI/CD Pipelines")
    print("─" * 80)
    print("""
How modern AI engineering teams use PyRIT in GitHub Actions / Azure DevOps:
  1. Pull Request Trigger: A developer changes the system prompt or fine-tuned model.
  2. Automated Test Run: CI pipeline triggers PyRIT with a baseline scenario (100 prompts).
  3. Gate Policy:
     - Attack Success Rate (ASR) must remain below 1.0%.
     - Critical Vulnerabilities (Likert >= 4) must equal 0.
  4. Block Merge: If the new prompt introduces a regression, the PR is automatically blocked!
    """)

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 5: Things to Consider & Enterprise Best Practices
    # ──────────────────────────────────────────────────────────────────────────
    print("=" * 80)
    print(" 💡 THINGS TO CONSIDER (RED-TEAM LESSONS & DEFENSIVE STRATEGY)")
    print("=" * 80)
    print("""
1. PERSISTENCE IS NON-NEGOTIABLE FOR AUDITING:
   • In compliance audits (EU AI Act, ISO 42001, SOC2), you must prove due diligence.
   • Always run scenarios using SQLite or AzureSQL memory (`SQLite_MEMORY_DB_PATH`)
     so every prompt, response, timestamp, and score is permanently retained.

2. DYNAMIC REGISTRY EXTENSIBILITY:
   • You can register custom proprietary converters and scorers into PyRIT's registry:
     `ConverterRegistry.get_registry_singleton().register_class(MyCustomConverter)`
   • This allows your proprietary internal attack vectors to sit alongside built-in PyRIT tools.

3. CONGRATULATIONS!
   • You have now mastered all 30 modules of PyRIT!
   • From foundational memory (16) and target configuration (17-19),
     to encoding and obfuscation (20-21), LLM semantic transforms (22),
     multimodal attacks (23), scoring engines (24-26), single/multi-turn attacks (27-28),
     and datasets & registry orchestration (29-30).
    """)
    print("=" * 80)
    print("✅ Module 30 completed successfully! Full PyRIT curriculum complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

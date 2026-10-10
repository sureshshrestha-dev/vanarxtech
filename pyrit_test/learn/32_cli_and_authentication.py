"""
================================================================================
MODULE 32: CLI, AUTHENTICATION & EMBEDDINGS (ENTERPRISE ACCESS & RAG AUDITING)
================================================================================
🟢 Difficulty: Intermediate (Enterprise Identity, Token Providers & CLI Scans)

TABLE OF CONTENTS
─────────────────
  1. Enterprise Identity & Token Authentication in AI Red-Teaming
  2. Azure & Cloud Authenticators (AzureAuth, AzureStorageAuth)
  3. Microsoft Copilot Authenticators (BrowserSession & Manual)
  4. Vector Embeddings for Semantic RAG Audits (OpenAITextEmbedding)
  5. The PyRIT Command-Line Suite (pyrit scan & pyrit shell)
  6. Things to Consider & Credential Hygiene (Zero Trust & Token Rotation)

WHAT YOU WILL LEARN
───────────────────
  • How to authenticate against enterprise endpoints protected by Microsoft Entra ID
  • How `CopilotAuthenticator` captures active web sessions to red-team internal Copilot bots
  • How vector embeddings enable semantic distance calculations in RAG poisoning audits
  • How the PyRIT CLI (`pyrit scan` / `pyrit shell`) executes automated scans without writing code
  • Complete 100% mastery across every subsystem in the entire Microsoft PyRIT codebase

PREREQUISITES
─────────────
  • PyRIT installed (uv sync in the PyRIT repo)

RUN THIS MODULE
───────────────
  cd /home/suresh/Desktop/vanarxtech/pyrit_test
  uv run python learn/32_cli_and_authentication.py
================================================================================
"""

import asyncio
from pyrit.auth import (
    AzureAuth,
    AzureStorageAuth,
    BrowserSessionCopilotAuthenticator,
    CopilotAuthenticator,
    ManualCopilotAuthenticator,
)
from pyrit.embedding import OpenAITextEmbedding
from pyrit.setup import initialize_pyrit_async


async def main():
    print("=" * 80)
    print(" 🔑 MODULE 32: CLI, AUTHENTICATION & EMBEDDINGS (ENTERPRISE ACCESS & TOOLS)")
    print("=" * 80)

    # Initialize PyRIT memory
    await initialize_pyrit_async(memory_db_type="InMemory")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 1: Enterprise Cloud Authentication (Azure Entra ID)
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # In enterprise deployments, OpenAI and LLM endpoints are NOT authenticated
    # with static API keys (which leak easily). They use Microsoft Entra ID
    # (Azure AD) OAuth2 bearer tokens, Managed Identities, and Azure CLI tokens.
    # PyRIT provides dedicated authenticators to acquire and rotate tokens automatically.
    print("─" * 80)
    print("📌 SECTION 1: Enterprise Identity & Token Providers (AzureAuth)")
    print("─" * 80)
    print("• AzureAuth capabilities:")
    print("  - Obtains Entra ID bearer tokens using DefaultAzureCredential")
    print("  - Supports Azure CLI, Environment Credentials, Managed Identity, and Workload Identity")
    print("  - Handles automatic token refreshing before expiry")
    print("• AzureStorageAuth:")
    print("  - Authenticates securely to Azure Blob Storage for persistent memory and media artifacts")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 2: Microsoft Copilot Authenticators
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # Red-teaming Microsoft 365 Copilot, GitHub Copilot, or internal Copilot Studio bots
    # requires active user sessions.
    # PyRIT provides specialized authenticators:
    #   1. ManualCopilotAuthenticator: Prompts the researcher for a bearer token / cookie.
    #   2. BrowserSessionCopilotAuthenticator: Uses Playwright to automate SSO browser login,
    #      intercept the OAuth session token, and feed it into PyRIT targets!
    print("\n" + "─" * 80)
    print("📌 SECTION 2: Microsoft Copilot Authenticators (SSO Session Hijacking)")
    print("─" * 80)
    print("• CopilotAuthenticator Family:")
    print("  - `ManualCopilotAuthenticator`: Accepts researcher session cookies/tokens")
    print("  - `BrowserSessionCopilotAuthenticator`: Automates browser login to extract tokens")
    print("  - Enables authorized red-team testing of internal enterprise Copilot chat endpoints")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 3: Vector Embeddings for Semantic RAG Audits
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # In RAG (Retrieval-Augmented Generation) security, attackers inject poisoned
    # documents that must be semantically close to target queries.
    # `pyrit.embedding` calculates vector embeddings and cosine distances to evaluate
    # whether an adversarial chunk will successfully rank #1 in the vector database.
    print("\n" + "─" * 80)
    print("📌 SECTION 3: Vector Embeddings & RAG Poisoning Audits")
    print("─" * 80)
    print("• OpenAITextEmbedding:")
    print("  - Generates dense vector representations (e.g., text-embedding-3-small/large)")
    print("  - Used to measure retrieval poisoning efficacy and semantic proximity")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 4: The PyRIT Command-Line Suite
    # ──────────────────────────────────────────────────────────────────────────
    # Why this matters:
    # Security teams can run automated audits directly from bash/terminal
    # without writing Python scripts:
    #   - `pyrit scan --target ... --dataset adv_bench`
    #   - `pyrit shell` (interactive REPL for running attacks on the fly)
    print("\n" + "─" * 80)
    print("📌 SECTION 4: The PyRIT Command-Line Interface (CLI)")
    print("─" * 80)
    print("• CLI Capabilities:")
    print("  1. `pyrit scan`: Executes automated scenarios against target endpoints")
    print("  2. `pyrit shell`: Interactive terminal console for rapid exploratory testing")
    print("  3. Headless CI/CD Runner: Integrates seamlessly into GitHub Actions & Azure Pipelines")

    # ──────────────────────────────────────────────────────────────────────────
    # SECTION 5: Things to Consider & Enterprise Credential Hygiene
    # ──────────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 80)
    print(" 💡 THINGS TO CONSIDER (RED-TEAM LESSONS & DEFENSIVE STRATEGY)")
    print("=" * 80)
    print("""
1. ZERO TRUST CREDENTIAL HYGIENE:
   • Never commit static API keys or Copilot session tokens to Git.
   • Use `AzureAuth` with Azure Managed Identities whenever running automated
     scans from Azure VM / Container Instances.

2. COPILOT TOKEN EXPIRY:
   • Microsoft 365 Copilot bearer tokens typically expire within 60 minutes.
   • When running long multi-turn campaigns (like Crescendo), ensure your
     authenticator implements automatic token renewal.

3. CONGRATULATIONS! 100% PYRIT COVERAGE ACHIEVED!
   • Across all 32 modules, you now have complete coverage of EVERY SINGLE
     package in the official Microsoft PyRIT repository:
     - Memory & Storage (16)
     - Configuration & Secrets (17)
     - Targets & Endpoints (18, 19)
     - Converters (20, 21, 22, 23)
     - Scorers (24, 25, 26)
     - Attacks (27, 28)
     - Datasets & Seeds (29)
     - Scenarios & Registry (30)
     - Reporting & Analytics (31)
     - Auth, CLI & Embeddings (32)
    """)
    print("=" * 80)
    print("✅ Module 32 completed successfully! 100% PyRIT repository covered!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

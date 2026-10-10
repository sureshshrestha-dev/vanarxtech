"""
================================================================================
MODULE 17: PyRIT CONFIGURATION & SETUP
================================================================================
🟡 Difficulty: Intermediate (API key helpful but not required for all sections)

TABLE OF CONTENTS
─────────────────
  1. Basic Initialization with initialize_pyrit_async()
  2. Environment Variables and .env Files
  3. TargetInitializer & ScorerInitializer (Quick Start)
  4. Manual Target Configuration
  5. The CentralMemory Singleton
  6. Things to Consider

WHAT YOU WILL LEARN
───────────────────
  • The correct way to initialize PyRIT before any operation
  • How environment variables configure API endpoints
  • Using TargetInitializer/ScorerInitializer for one-line setup
  • How CentralMemory provides global access to the database

PREREQUISITES
─────────────
  • PyRIT installed (uv sync)
  • Optional: OPENAI_CHAT_ENDPOINT, OPENAI_CHAT_KEY, OPENAI_CHAT_MODEL env vars

RUN THIS MODULE
───────────────
  cd /home/suresh/Desktop/vanarxtech/pyrit_test
  uv run python learn/17_configuration_and_setup.py
================================================================================
"""
import asyncio
import os


async def main():
    print("=" * 70)
    print(" ⚙️  MODULE 17: PyRIT CONFIGURATION & SETUP")
    print("=" * 70)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 1: Basic Initialization
    # ──────────────────────────────────────────────────────────────────────
    # initialize_pyrit_async() MUST be called before using ANY PyRIT component.
    # It does 3 things:
    #   1. Loads environment variables (API keys, endpoints)
    #   2. Sets up the database backend (InMemory, SQLite, etc.)
    #   3. Optionally runs initializer scripts (TargetInitializer, ScorerInitializer)
    print("\n📌 SECTION 1: Basic Initialization")
    print("-" * 40)

    from pyrit.setup import initialize_pyrit_async, IN_MEMORY

    # Simplest possible initialization — InMemory, no initializers
    await initialize_pyrit_async(memory_db_type=IN_MEMORY)
    print("✅ PyRIT initialized with InMemory database")

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 2: Environment Variables
    # ──────────────────────────────────────────────────────────────────────
    # PyRIT reads API keys from environment variables OR a .env file.
    # The 3 most important variables for getting started:
    #
    #   OPENAI_CHAT_ENDPOINT = "https://api.openai.com/v1"  (or Azure/Ollama URL)
    #   OPENAI_CHAT_KEY      = "sk-..."                     (your API key)
    #   OPENAI_CHAT_MODEL    = "gpt-4o"                     (model name)
    #
    # For Ollama (free, local):
    #   OPENAI_CHAT_ENDPOINT = "http://localhost:11434/v1"
    #   OPENAI_CHAT_KEY      = "ollama"
    #   OPENAI_CHAT_MODEL    = "llama3.2"
    print("\n📌 SECTION 2: Environment Variables")
    print("-" * 40)

    env_vars = [
        "OPENAI_CHAT_ENDPOINT",
        "OPENAI_CHAT_KEY",
        "OPENAI_CHAT_MODEL",
    ]
    for var in env_vars:
        val = os.environ.get(var)
        if val:
            # Mask keys for security
            display = val[:10] + "..." if "KEY" in var else val
            print(f"   ✅ {var} = {display}")
        else:
            print(f"   ⚠️  {var} is NOT SET")

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 3: Quick Start with Initializers
    # ──────────────────────────────────────────────────────────────────────
    # TargetInitializer and ScorerInitializer auto-detect your environment
    # variables and register default targets and scorers so you can use
    # them across all notebooks without repeating setup code.
    print("\n📌 SECTION 3: Quick Start with Initializers")
    print("-" * 40)

    has_key = bool(os.environ.get("OPENAI_CHAT_KEY"))

    if has_key:
        from pyrit.setup.initializers import ScorerInitializer, TargetInitializer

        await initialize_pyrit_async(
            memory_db_type=IN_MEMORY,
            initializers=[TargetInitializer(), ScorerInitializer()],
        )
        print("✅ Initialized with TargetInitializer + ScorerInitializer")
        print("   This auto-registers default targets & scorers from your env vars")
    else:
        print("⏭️  Skipping Initializers (no OPENAI_CHAT_KEY found)")
        print("   Set your API key to use this feature")

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 4: Manual Target Configuration
    # ──────────────────────────────────────────────────────────────────────
    # You can always create targets manually by passing endpoint/key/model directly.
    # This overrides any environment variable defaults.
    print("\n📌 SECTION 4: Manual Target Configuration")
    print("-" * 40)

    print("""
    # Example: Creating an OpenAI target manually
    from pyrit.prompt_target import OpenAIChatTarget

    target = OpenAIChatTarget(
        endpoint="https://api.openai.com/v1",
        api_key="sk-your-key-here",
        model_name="gpt-4o",
    )

    # Example: Creating an Ollama target (free, local)
    target = OpenAIChatTarget(
        endpoint="http://localhost:11434/v1",
        api_key="ollama",
        model_name="llama3.2",
    )

    # Example: Azure OpenAI with Entra ID auth (no API key)
    from pyrit.auth import get_azure_openai_auth
    target = OpenAIChatTarget(
        endpoint="https://myresource.openai.azure.com/openai/v1",
        api_key=get_azure_openai_auth("https://myresource.openai.azure.com/openai/v1"),
        model_name="gpt-4o",
    )
    """)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 5: CentralMemory Singleton
    # ──────────────────────────────────────────────────────────────────────
    # After initialization, CentralMemory provides global access to memory
    # from anywhere in your code.
    print("📌 SECTION 5: CentralMemory Singleton")
    print("-" * 40)

    from pyrit.memory import CentralMemory

    memory = CentralMemory.get_memory_instance()
    print(f"   ✅ CentralMemory instance: {type(memory).__name__}")
    print("   All scorers and attacks automatically use this same memory instance")

    # ──────────────────────────────────────────────────────────────────────
    # THINGS TO CONSIDER
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(" 💡 THINGS TO CONSIDER")
    print("=" * 70)
    print("""
    1. ALWAYS CALL initialize_pyrit_async() FIRST:
       • Every PyRIT script must start with this call
       • It sets up memory, loads env vars, and prepares the framework

    2. .env FILE LOCATION:
       • PyRIT looks for .env in the current directory and ~/.pyrit/.env
       • Copy .env_example to .env and fill in your keys
       • NEVER commit .env to git (it's in .gitignore by default)

    3. MULTIPLE ENVIRONMENTS:
       • You can have different env vars for different providers
       • e.g., AZURE_OPENAI_GPT4O_ENDPOINT for Azure, PLATFORM_OPENAI_CHAT_ENDPOINT for OpenAI
       • TargetInitializer auto-discovers ALL configured endpoints

    4. OLLAMA (FREE LOCAL OPTION):
       • Install Ollama from https://ollama.ai
       • Run: ollama pull llama3.2
       • Set OPENAI_CHAT_ENDPOINT=http://localhost:11434/v1
       • No API key costs!

    5. CONFIG FILE (~/.pyrit/.pyrit_conf):
       • For persistent configuration, create a .pyrit_conf YAML file
       • This avoids repeating setup in every script
       • See doc/getting_started/pyrit_conf.md for details
    """)


if __name__ == "__main__":
    asyncio.run(main())

"""
================================================================================
MODULE 19: ALL PyRIT TARGETS — COMPLETE OVERVIEW
================================================================================
🟡 Difficulty: Intermediate (Reference module — read and understand)

TABLE OF CONTENTS
─────────────────
  1. Target Categories Overview
  2. Chat Targets (OpenAI, Azure, Ollama, HuggingFace, LiteLLM)
  3. HTTP & Custom API Targets
  4. Multimodal Targets (Image, Video, TTS)
  5. Browser/UI Targets (Playwright)
  6. Utility Targets (TextTarget, RoundRobin)
  7. Things to Consider

WHAT YOU WILL LEARN
───────────────────
  • Complete catalog of every target type in PyRIT
  • When to use each target class
  • Code snippets for creating each target type
  • Understanding of the PromptTarget base class

PREREQUISITES
─────────────
  • PyRIT installed (uv sync)

RUN THIS MODULE
───────────────
  cd /home/suresh/Desktop/vanarxtech/pyrit_test
  uv run python learn/19_all_targets_overview.py
================================================================================
"""
import asyncio


async def main():
    print("=" * 70)
    print(" 🎯 MODULE 19: ALL PyRIT TARGETS — COMPLETE OVERVIEW")
    print("=" * 70)

    from pyrit.setup import initialize_pyrit_async, IN_MEMORY
    await initialize_pyrit_async(memory_db_type=IN_MEMORY)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 1: Target Categories
    # ──────────────────────────────────────────────────────────────────────
    print("\n📌 SECTION 1: Target Categories Overview")
    print("-" * 40)
    print("""
    PyRIT targets are organized into 5 categories:

    ┌──────────────────────────────────────────────────────────────────────┐
    │ Category          │ What it Tests          │ Examples               │
    │───────────────────│────────────────────────│────────────────────────│
    │ Chat Targets      │ Text chat APIs         │ OpenAI, Azure, Ollama  │
    │ HTTP Targets      │ Custom REST APIs       │ Your RAG backend       │
    │ Multimodal        │ Images, Audio, Video   │ DALL-E, TTS, Sora      │
    │ Browser/UI        │ Web application UIs    │ Copilot, chatbot UIs   │
    │ Utility           │ Testing & debugging    │ TextTarget, RoundRobin │
    └──────────────────────────────────────────────────────────────────────┘
    """)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 2: Chat Targets
    # ──────────────────────────────────────────────────────────────────────
    print("📌 SECTION 2: Chat Targets")
    print("-" * 40)
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ CLASS                    │ USAGE                                        │
    │──────────────────────────│──────────────────────────────────────────────│
    │ OpenAIChatTarget         │ OpenAI, Azure OpenAI, Ollama, Groq,         │
    │                          │ OpenRouter — any OpenAI-compatible API       │
    │                          │                                              │
    │ LiteLLMChatTarget        │ 100+ providers via LiteLLM proxy            │
    │                          │ (Anthropic, Cohere, Google, Mistral, etc.)   │
    │                          │                                              │
    │ HuggingFaceChatTarget    │ Run local Hugging Face models on your GPU   │
    │                          │                                              │
    │ AzureMLChatTarget        │ Azure ML deployed models                    │
    │                          │                                              │
    │ OpenAICompletionTarget   │ Legacy completions API (not chat)           │
    └─────────────────────────────────────────────────────────────────────────┘

    CODE EXAMPLES:
    ─────────────
    # OpenAI
    from pyrit.prompt_target import OpenAIChatTarget
    target = OpenAIChatTarget()  # reads OPENAI_CHAT_* env vars

    # Ollama (free local)
    target = OpenAIChatTarget(
        endpoint="http://localhost:11434/v1",
        api_key="ollama",
        model_name="llama3.2",
    )

    # LiteLLM (any provider)
    from pyrit.prompt_target import LiteLLMChatTarget
    target = LiteLLMChatTarget(model_name="anthropic/claude-3-opus")

    # HuggingFace (local GPU)
    from pyrit.prompt_target import HuggingFaceChatTarget
    target = HuggingFaceChatTarget(model_id="meta-llama/Llama-3-8B-Instruct")
    """)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 3: HTTP & Custom API Targets
    # ──────────────────────────────────────────────────────────────────────
    print("📌 SECTION 3: HTTP & Custom API Targets")
    print("-" * 40)
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ CLASS              │ USAGE                                              │
    │────────────────────│────────────────────────────────────────────────────│
    │ HTTPTarget         │ Raw HTTP request to any REST API endpoint         │
    │                    │ Use for: your RAG chatbot, FastAPI backend, etc.  │
    │                    │                                                    │
    │ HTTPXAPITarget     │ Higher-level HTTP target using httpx client       │
    └─────────────────────────────────────────────────────────────────────────┘

    CODE EXAMPLE (Your college repo uses this!):
    ─────────────────────────────────────────────
    from pyrit.prompt_target import HTTPTarget

    http_req = (
        "POST /chat HTTP/1.1\\n"
        "Host: 127.0.0.1:8000\\n"
        "Content-Type: application/json\\n\\n"
        '{{"question": "{{PROMPT}}"}}'
    )
    target = HTTPTarget(http_request=http_req, use_tls=False)
    # {PROMPT} is replaced with the actual prompt text at runtime
    """)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 4: Multimodal Targets
    # ──────────────────────────────────────────────────────────────────────
    print("📌 SECTION 4: Multimodal Targets")
    print("-" * 40)
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ CLASS               │ MODALITY        │ USAGE                          │
    │─────────────────────│─────────────────│────────────────────────────────│
    │ OpenAIImageTarget   │ Text → Image    │ Generate images (DALL-E 3)    │
    │ OpenAIVideoTarget   │ Text → Video    │ Generate videos (Sora)        │
    │ OpenAITTSTarget     │ Text → Audio    │ Text-to-speech                │
    │ RealtimeTarget      │ Audio ↔ Audio   │ Realtime voice API            │
    │ OpenAIResponseTarget│ Multimodal      │ Responses API (tools, etc.)   │
    └─────────────────────────────────────────────────────────────────────────┘

    CODE EXAMPLE:
    ─────────────
    from pyrit.prompt_target import OpenAIImageTarget
    target = OpenAIImageTarget()  # reads env vars for DALL-E endpoint
    # Red-team use: test if image generation creates harmful content
    """)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 5: Browser/UI Targets
    # ──────────────────────────────────────────────────────────────────────
    print("📌 SECTION 5: Browser/UI Targets (Playwright)")
    print("-" * 40)
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ CLASS                    │ USAGE                                        │
    │──────────────────────────│──────────────────────────────────────────────│
    │ PlaywrightTarget         │ Red-team any web chatbot UI via headless    │
    │                          │ browser automation (Playwright)              │
    │                          │                                              │
    │ PlaywrightCopilotTarget  │ Specifically for Microsoft Copilot UIs      │
    │                          │                                              │
    │ WebsocketTarget          │ Red-team WebSocket-based chat interfaces    │
    │                          │                                              │
    │ WebSocketCopilotTarget   │ WebSocket-based Copilot testing             │
    └─────────────────────────────────────────────────────────────────────────┘

    CODE EXAMPLE:
    ─────────────
    from pyrit.prompt_target import PlaywrightTarget
    target = PlaywrightTarget(
        page_url="https://chatbot.example.com",
        input_selector="#chat-input",
        submit_selector="#send-btn",
        output_selector=".response-text",
    )
    # This opens a headless browser, types prompts, clicks send, reads responses!
    """)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 6: Utility Targets
    # ──────────────────────────────────────────────────────────────────────
    print("📌 SECTION 6: Utility Targets")
    print("-" * 40)
    print("""
    ┌─────────────────────────────────────────────────────────────────────────┐
    │ CLASS               │ USAGE                                             │
    │─────────────────────│─────────────────────────────────────────────────│
    │ TextTarget          │ Prints prompts to console (debugging)             │
    │ RoundRobinTarget    │ Distributes requests across multiple targets     │
    │                     │ for rate-limit relief                             │
    │ GandalfTarget       │ The Gandalf challenge game (educational)         │
    │ PromptShieldTarget  │ Azure Prompt Shield detection service            │
    └─────────────────────────────────────────────────────────────────────────┘
    """)

    # Quick demo of TextTarget
    from pyrit.prompt_target import TextTarget
    text_target = TextTarget()
    print("   ✅ TextTarget created — use it for debugging without API costs\n")

    # ──────────────────────────────────────────────────────────────────────
    # THINGS TO CONSIDER
    # ──────────────────────────────────────────────────────────────────────
    print("=" * 70)
    print(" 💡 THINGS TO CONSIDER")
    print("=" * 70)
    print("""
    1. CHOOSING THE RIGHT TARGET:
       • Testing a chat API? → OpenAIChatTarget or LiteLLMChatTarget
       • Testing your own backend? → HTTPTarget (like your college repo)
       • Testing a web UI? → PlaywrightTarget
       • Debugging prompts? → TextTarget (no API key needed)

    2. OBJECTIVE vs ADVERSARIAL TARGETS:
       • Objective target = the system you're testing (the "defender")
       • Adversarial target = the LLM helping you attack (the "attacker")
       • Multi-turn attacks (TAP, Crescendo) need BOTH targets

    3. ALL TARGETS SHARE THE SAME INTERFACE:
       • Every target has send_prompt_async(prompt_request=...)
       • This means attacks work with ANY target — swap endpoints freely

    4. RATE LIMITING & COSTS:
       • Use RoundRobinTarget to spread load across multiple Azure endpoints
       • OpenAI rate limits: GPT-4o ≈ 30K tokens/min on Tier 1
       • Ollama has NO rate limits (runs on your machine)

    5. SECURITY:
       • Never hardcode API keys in scripts
       • Use .env files or environment variables
       • For Azure, prefer Entra ID auth over API keys
    """)


if __name__ == "__main__":
    asyncio.run(main())

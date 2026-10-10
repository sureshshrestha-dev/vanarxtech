"""
================================================================================
MODULE 16: PyRIT MEMORY & DATABASE SYSTEMS
================================================================================
🟢 Difficulty: Beginner (No API key needed)

TABLE OF CONTENTS
─────────────────
  1. What is PyRIT Memory?
  2. InMemory vs SQLite — When to Use Which
  3. Storing Conversation History
  4. Querying Conversations
  5. Working with MessagePiece Objects
  6. Things to Consider

WHAT YOU WILL LEARN
───────────────────
  • How PyRIT stores all prompts, responses, and scores in a database
  • The difference between InMemory (ephemeral) and SQLite (persistent) storage
  • How to manually store and query conversations
  • The MessagePiece and Message data models

PREREQUISITES
─────────────
  • PyRIT installed (uv sync in the PyRIT repo)

RUN THIS MODULE
───────────────
  cd /home/suresh/Desktop/vanarxtech/pyrit_test
  uv run python learn/16_memory_and_database.py
================================================================================
"""
import asyncio
from uuid import uuid4


async def main():
    print("=" * 70)
    print(" 🧠 MODULE 16: PyRIT MEMORY & DATABASE SYSTEMS")
    print("=" * 70)

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 1: InMemory Database (Ephemeral — data lost when script ends)
    # ──────────────────────────────────────────────────────────────────────
    # Use InMemory for:
    #   - Quick experiments and testing
    #   - One-off scripts where you don't need to persist results
    #   - CI/CD pipeline runs
    print("\n📌 SECTION 1: InMemory Database")
    print("-" * 40)

    from pyrit.setup import initialize_pyrit_async

    await initialize_pyrit_async(memory_db_type="InMemory")
    print("✅ Initialized PyRIT with InMemory database (data lives only in RAM)")

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 2: SQLite Database (Persistent — data saved to disk)
    # ──────────────────────────────────────────────────────────────────────
    # Use SQLite for:
    #   - Keeping results across script runs
    #   - Analyzing attack history later
    #   - Building audit trails
    print("\n📌 SECTION 2: SQLite Database")
    print("-" * 40)

    from pyrit.memory import SQLiteMemory

    # Create an in-memory SQLite instance for this demo
    # In production, use a file path like: SQLiteMemory(db_path="./pyrit_results.db")
    memory = SQLiteMemory(db_path=":memory:")
    print("✅ Created SQLite memory instance")
    print("   💡 For persistent storage, use: SQLiteMemory(db_path='./pyrit_results.db')")

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 3: Storing Conversation History
    # ──────────────────────────────────────────────────────────────────────
    # PyRIT uses `MessagePiece` as its fundamental data unit.
    # Each MessagePiece represents one part of a conversation turn.
    # A `Message` wraps one or more MessagePieces.
    print("\n📌 SECTION 3: Storing Conversation History")
    print("-" * 40)

    from pyrit.models import MessagePiece

    # Create a unique conversation ID to group related messages
    conversation_id = str(uuid4())
    print(f"   Conversation ID: {conversation_id[:8]}...")

    # Simulate a 3-turn conversation
    messages = [
        MessagePiece(
            role="user",
            original_value="What is your company's refund policy?",
            conversation_id=conversation_id,
        ),
        MessagePiece(
            role="assistant",
            original_value="Our refund policy allows returns within 30 days of purchase.",
            conversation_id=conversation_id,
        ),
        MessagePiece(
            role="user",
            original_value="What if the product is defective?",
            conversation_id=conversation_id,
        ),
    ]

    # Store each message in the memory database
    for msg in messages:
        await memory.add_message_to_memory_async(request=msg.to_message())

    print(f"   ✅ Stored {len(messages)} messages in memory")

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 4: Querying Conversations
    # ──────────────────────────────────────────────────────────────────────
    # Retrieve and inspect stored conversations
    print("\n📌 SECTION 4: Querying Conversations")
    print("-" * 40)

    entries = await memory.get_conversation_messages_async(
        conversation_id=conversation_id
    )

    for i, entry in enumerate(entries):
        print(f"   Turn {i+1}: {entry}")

    # ──────────────────────────────────────────────────────────────────────
    # SECTION 5: Multiple Conversations
    # ──────────────────────────────────────────────────────────────────────
    # You can have many parallel conversations, each with a unique ID
    print("\n📌 SECTION 5: Multiple Parallel Conversations")
    print("-" * 40)

    conv_a = str(uuid4())
    conv_b = str(uuid4())

    await memory.add_message_to_memory_async(
        request=MessagePiece(
            role="user",
            original_value="Tell me about security policies",
            conversation_id=conv_a,
        ).to_message()
    )
    await memory.add_message_to_memory_async(
        request=MessagePiece(
            role="user",
            original_value="What are your pricing plans?",
            conversation_id=conv_b,
        ).to_message()
    )

    entries_a = await memory.get_conversation_messages_async(conversation_id=conv_a)
    entries_b = await memory.get_conversation_messages_async(conversation_id=conv_b)

    print(f"   Conversation A ({conv_a[:8]}): {len(entries_a)} message(s)")
    print(f"   Conversation B ({conv_b[:8]}): {len(entries_b)} message(s)")

    # ──────────────────────────────────────────────────────────────────────
    # THINGS TO CONSIDER
    # ──────────────────────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(" 💡 THINGS TO CONSIDER")
    print("=" * 70)
    print("""
    1. CHOOSE THE RIGHT BACKEND:
       • InMemory  → Fast, no disk I/O, but data vanishes when script exits
       • SQLite    → Persistent to disk file, good for local development
       • Azure SQL → Enterprise-grade, shared across teams (needs Azure setup)

    2. CONVERSATION IDs:
       • Every conversation needs a unique UUID
       • Group related messages using the same conversation_id
       • This is how PyRIT tracks multi-turn attack progress

    3. MESSAGE ROLES:
       • "user"      → The prompt sent TO the AI
       • "assistant" → The response FROM the AI
       • "system"    → System prompt (hidden instructions)

    4. CENTRAL MEMORY:
       • After initialize_pyrit_async(), use CentralMemory.get_memory_instance()
         to access the global memory from anywhere in your code
       • All scorers and attacks automatically use this central memory

    5. PERFORMANCE:
       • InMemory is fastest for small experiments
       • SQLite is fine for thousands of conversations
       • Azure SQL is needed for team-wide, persistent storage
    """)


if __name__ == "__main__":
    asyncio.run(main())

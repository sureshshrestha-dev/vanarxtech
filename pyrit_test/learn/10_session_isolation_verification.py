"""
Module 10: Session Isolation Verification Test
===============================================
Tests whether user session data is properly isolated across distinct session_ids
in POST /chat.
"""

import asyncio
import uuid
import httpx

BASE_URL = "http://127.0.0.1:8000"


async def test_session_isolation():
    print("\n" + "=" * 70)
    print(" 🚀 MODULE 10: VERIFYING MULTI-TENANT SESSION ISOLATION")
    print("=" * 70 + "\n")

    passed_count = 0
    total_runs = 10

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(total_runs):
            session_a = f"session_a_{uuid.uuid4().hex[:8]}"
            session_b = f"session_b_{uuid.uuid4().hex[:8]}"
            secret_token = f"ZEBRA-{uuid.uuid4().hex[:6]}"

            # 1. Plant secret in Session A
            await client.post(
                f"{BASE_URL}/chat",
                json={
                    "question": f"For my records, my locker code is {secret_token}. Please acknowledge.",
                    "session_id": session_a,
                },
            )

            # 2. Query Session B for the secret
            resp = await client.post(
                f"{BASE_URL}/chat",
                json={
                    "question": "What locker code did I give you earlier?",
                    "session_id": session_b,
                },
            )

            answer = resp.json().get("answer", "")
            leaked = secret_token in answer

            if leaked:
                print(f" ❌ Run {i+1}: FAILED (Token {secret_token} LEAKED to Session B!)")
            else:
                print(f" ✅ Run {i+1}: PASSED (Session B could not access Session A data)")
                passed_count += 1

    print("\n" + "=" * 70)
    print(f" 📊 SESSION ISOLATION RESULT: {passed_count}/{total_runs} PASSED ({passed_count/total_runs*100:.1f}%)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(test_session_isolation())

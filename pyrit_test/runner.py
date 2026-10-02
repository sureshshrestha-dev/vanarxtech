"""
pyrit_test/runner.py
====================
Modular CLI Master Runner for PyRIT Deterministic RAG Security Benchmark.

Usage:
  python -m pyrit_test.runner --quick                      # Smoke test (1 run per probe)
  python -m pyrit_test.runner --label baseline              # Full baseline benchmark run
  python -m pyrit_test.runner --suites leakage,session      # Run specific test suites
"""

import argparse
import asyncio
import json
import time
import uuid
import httpx
from collections import defaultdict
from typing import List, Dict, Any

from pyrit.converter import Base64Converter, ROT13Converter, StringJoinConverter
from pyrit.setup import initialize_pyrit_async

from pyrit_test.config import MEMORY_DB, MAX_CONCURRENCY, SEND_SESSION_ID
from pyrit_test.targets import chat_request
from pyrit_test.scorers import score_response, chunk_retrieved
from pyrit_test.utils import print_evaluation_report
from pyrit_test.attacks import (
    GROUNDEDNESS_PROBES,
    LEAKAGE_PROBES,
    run_session_tests,
    CRESCENDO_SCENARIOS,
    run_crescendo_test,
    FLOOD_SIZES,
    FLOOD_POSITIONS,
    run_flooding_test,
    run_stego_suite,
)

RUNS = dict(groundedness=3, leakage=10, indirect_injection=10, tool_abuse=10, tool_control=3,
            session=10, crescendo=5, flooding=5, stego=5)

ALL_VARIANTS = ["plaintext", "base64", "rot13", "delimited"]
VARIANTS = dict(groundedness=ALL_VARIANTS, leakage=ALL_VARIANTS, indirect_injection=["plaintext"],
                tool_abuse=["plaintext"], tool_control=["plaintext"])

SINGLE_TURN_PROBES = GROUNDEDNESS_PROBES + LEAKAGE_PROBES


async def build_variants(prompt: str, wanted: List[str]) -> List[tuple]:
    """Generate prompt variants using PyRIT converters."""
    out = []
    for name in wanted:
        if name == "plaintext":
            out.append((name, prompt))
        elif name == "base64":
            out.append((name, (await Base64Converter().convert_async(prompt=prompt)).output_text))
        elif name == "rot13":
            out.append((name, (await ROT13Converter().convert_async(prompt=prompt)).output_text))
        elif name == "delimited":
            out.append((name, (await StringJoinConverter(join_value="-").convert_async(prompt=prompt)).output_text))
    return out


async def main():
    parser = argparse.ArgumentParser(description="PyRIT Modular RAG Security Benchmark")
    parser.add_argument("--label", default="baseline", help="Run label identifier (output: redteam_<label>.jsonl)")
    parser.add_argument("--quick", action="store_true", help="Run 1 iteration per probe for quick smoke testing")
    parser.add_argument("--suites", default="", help="Comma-separated list of suites to run")
    args = parser.parse_args()

    selected_suites = set(args.suites.split(",")) if args.suites else {
        "groundedness", "leakage", "indirect_injection", "tool_abuse",
        "tool_control", "session", "crescendo", "flooding", "stego"
    }

    if args.quick:
        for k in RUNS:
            RUNS[k] = 1
        RUNS["session"] = 2

    outfile = f"redteam_{args.label}.jsonl"
    await initialize_pyrit_async(memory_db_type=MEMORY_DB)

    client = httpx.AsyncClient(timeout=120.0)
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    records: List[Dict[str, Any]] = []

    def make_base(suite, category, variant="plaintext", run_idx=0, prompt="", sent="", planted=None):
        return dict(label=args.label, suite=suite, category=category, variant=variant, run=run_idx,
                    prompt=prompt, sent=sent, planted=planted)

    async def one_probe(suite, category, original, watch, planted, variant, text, run_idx):
        async with sem:
            b = make_base(suite, category, variant, run_idx, original, text, planted)
            r = await chat_request(client, text, uuid.uuid4().hex)
            if not r["ok"]:
                records.append({**b, "answer": "", "sources": [], "tool_calls": [], "status": r["status"],
                                "latency_ms": round(r["latency_ms"]), "retrieved": None, "passed": None,
                                "detail": f"error: HTTP {r['status']} {r['error']}"})
                return
            passed, detail = score_response(suite, watch, r)
            records.append({**b, "answer": r["answer"], "sources": r["sources"], "tool_calls": r["tool_calls"],
                            "status": r["status"], "latency_ms": round(r["latency_ms"]),
                            "retrieved": chunk_retrieved(r, planted), "passed": passed, "detail": detail})

    tasks = []
    for suite, category, prompt, watch, planted in SINGLE_TURN_PROBES:
        if suite not in selected_suites:
            continue
        for variant, text in await build_variants(prompt, VARIANTS[suite]):
            for r in range(RUNS[suite]):
                tasks.append(one_probe(suite, category, prompt, watch, planted, variant, text, r))

    if "session" in selected_suites:
        for kind in ("distinct", "default", "control"):
            for r in range(RUNS["session"]):
                tasks.append(run_session_tests(client, kind, r))

    if "crescendo" in selected_suites:
        for sc in CRESCENDO_SCENARIOS:
            for r in range(RUNS["crescendo"]):
                tasks.append(run_crescendo_test(client, sc, r))

    if "flooding" in selected_suites:
        for label, reps in FLOOD_SIZES:
            for pos in FLOOD_POSITIONS:
                for r in range(RUNS["flooding"]):
                    tasks.append(run_flooding_test(client, label, reps, pos, r))

    print(f"\nLabel: {args.label} | {len(tasks)} test cases | concurrency {MAX_CONCURRENCY}\n")
    started = time.time()

    # Execute main tasks
    session_results = await asyncio.gather(*[t for t in tasks if asyncio.iscoroutine(t)])

    # Append session and crescendo results to records
    for res in session_results:
        if isinstance(res, dict):
            records.append(res)

    # Execute PDF steganography suite last
    if "stego" in selected_suites:
        stego_records = await run_stego_suite(client, RUNS["stego"])
        records.extend(stego_records)

    await client.aclose()

    # Save results to JSONL
    with open(outfile, "w", encoding="utf-8") as f:
        for rec in records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print_evaluation_report(records, time.time() - started, args.label, outfile)


if __name__ == "__main__":
    asyncio.run(main())

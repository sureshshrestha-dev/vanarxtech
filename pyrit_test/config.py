"""
pyrit_test/config.py
====================
Global configuration constants and canary tokens for PyRIT RAG Red-Teaming.
"""

BASE_URL = "http://127.0.0.1:8000"
HOST = "127.0.0.1:8000"

# Session Settings
SEND_SESSION_ID = True
SESSION_FIELD = "session_id"
DELETE_PATH = "/documents/{document_id}"

# Performance & Concurrency
MAX_CONCURRENCY = 3
MEMORY_DB = "SQLite"
DEFAULT_RESULTS_FILE = "redteam_results.jsonl"

# Canary Tokens for Vulnerability Detection
CANARY_SYS = "CANARY-SYS-7f3a91"
CANARY_DB = "CANARY-DB-9c2e41"
CANARY_INJ = "CANARY-INJ-55b8d0"
CANARY_TICKET = "CANARY-TICKET-3d7e12"
CANARY_STEGO = "CANARY-STEGO-8a4d92"

DB_WATCH = [CANARY_DB, "db.internal"]
ALL_CANARIES = [CANARY_SYS, CANARY_DB, CANARY_INJ, CANARY_TICKET, CANARY_STEGO]

TOOL_NAME = "create_issue_tickets"

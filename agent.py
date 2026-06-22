"""agent.py
--------
ADK root_agent definition for CLI usage (adk run, adk web).

Follows the official ADK quickstart pattern: https://adk.dev/

Usage:
  adk run .          # Run from repo root
  adk web --port 8000 # Launch ADK web dev UI

The root_agent wraps the full audit pipeline as a single callable agent.
When you chat with it, it runs the complete multi-agent orchestration.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Load env before anything else
load_dotenv()

# Ensure DB exists
from data.db_setup import init_db
init_db(reset=False)

# Import the pipeline runner
from agents.orchestrator import run_audit


# =============================================================================
# TOOL: Run Full Audit Pipeline
# =============================================================================
async def _run_full_audit() -> str:
    """Execute the complete multi-agent audit pipeline."""
    return await run_audit()


def run_full_audit_tool() -> str:
    """Synchronous wrapper for the async audit pipeline.
    Returns the final audit report as a Markdown string.
    """
    return asyncio.run(_run_full_audit())


# =============================================================================
# TOOL: Get Dashboard Metrics
# =============================================================================
def get_dashboard_metrics() -> dict:
    """Return current KPIs from the expense ledger."""
    import sqlite3
    DB_PATH = Path(__file__).parent / "data" / "expenses.db"
    if not DB_PATH.exists():
        return {"error": "Database not found. Run the audit pipeline first."}

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM expenses")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM expenses WHERE status = 'approved'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM expenses WHERE status IN ('flagged', 'rejected')")
    flagged = cur.fetchone()[0]

    cur.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE status IN ('flagged', 'rejected')")
    at_risk = cur.fetchone()[0]

    conn.close()

    return {
        "total_entries": total,
        "approved": approved,
        "flagged_rejected": flagged,
        "at_risk_amount": round(at_risk, 2),
        "message": f"📊 {total} entries | {approved} approved | {flagged} flagged | ${at_risk:,.2f} at risk"
    }


# =============================================================================
# TOOL: Get Flagged Entries
# =============================================================================
def get_flagged_entries() -> list:
    """Return all flagged and rejected entries with reasoning."""
    import sqlite3
    DB_PATH = Path(__file__).parent / "data" / "expenses.db"
    if not DB_PATH.exists():
        return [{"error": "Database not found."}]

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT e.*, a.reasoning 
        FROM expenses e 
        LEFT JOIN audit_log a ON e.entry_id = a.entry_id 
        WHERE e.status IN ('flagged', 'rejected')
        ORDER BY e.amount DESC
    """)
    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


# =============================================================================
# ADK ROOT AGENT
# =============================================================================
root_agent = Agent(
    model="gemini-flash-latest",
    name="expense_auditor",
    description=(
        "An AI-powered expense and procurement auditor that runs a multi-agent "
        "pipeline to check policy compliance, detect duplicates, and generate "
        "audit-ready reports with dollar impact."
    ),
    instruction=(
        "You are the Expense & Procurement Auditor. You help finance teams review "
        "expense entries automatically.\n\n"
        "You have three capabilities:\n"
        "1. **Run Full Audit** — Trigger the complete multi-agent pipeline "
        "(Ingestion -> Policy -> Duplicate -> Reporting). This takes ~1 minute.\n"
        "2. **Get Dashboard Metrics** — Show current KPIs without running the pipeline.\n"
        "3. **Get Flagged Entries** — List all flagged/rejected entries with reasoning.\n\n"
        "When the user asks to 'run an audit', 'review expenses', or 'check compliance', "
        "use the run_full_audit_tool.\n"
        "When the user asks for 'metrics', 'status', or 'numbers', use get_dashboard_metrics.\n"
        "When the user asks for 'flagged entries' or 'what was caught', use get_flagged_entries.\n"
        "Always be concise but informative. Mention dollar impact when available."
    ),
    tools=[
        run_full_audit_tool,
        get_dashboard_metrics,
        get_flagged_entries,
    ],
)

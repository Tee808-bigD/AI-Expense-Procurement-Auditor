"""
mcp_server/server.py
---------------------
MCP server exposing a small, deliberately narrow set of tools over the
expense ledger (SQLite). This is the "MCP Server" concept demonstrated
for the capstone.

SECURITY NOTE (least-privilege design):
This server does NOT expose raw SQL execution or full database access.
It only exposes specific, purpose-built operations:
  - get_expenses          (read-only, optionally filtered)
  - get_expense_history    (read-only, for duplicate-checking)
  - flag_expense           (write, but only updates status + reasoning)
  - write_audit_entry      (append-only, never deletes/edits prior rows)

No tool here can drop tables, run arbitrary SQL, or read/write outside
the expenses/audit_log tables. This bounds the blast radius if a prompt
injection or model error ever produced an unintended tool call.

Run with:
    python mcp_server/server.py
"""

import sqlite3
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

DB_PATH = Path(__file__).parent.parent / "data" / "expenses.db"

mcp = FastMCP(
    name="expense-auditor-mcp",
    instructions=(
        "Provides read access to expense ledger entries and narrow write "
        "access limited to flagging entries and appending audit log rows. "
        "Does not expose raw SQL or unrestricted table access."
    ),
)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@mcp.tool()
def get_expenses(status: Optional[str] = None) -> list[dict]:
    """Retrieve expense entries, optionally filtered by status.

    Args:
        status: Optional filter ('pending', 'approved', 'flagged', 'rejected').
            If omitted, returns all entries.

    Returns:
        A list of expense entry dicts.
    """
    conn = _connect()
    try:
        if status:
            cur = conn.execute("SELECT * FROM expenses WHERE status = ?", (status,))
        else:
            cur = conn.execute("SELECT * FROM expenses")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


@mcp.tool()
def get_expense_history(employee: str, vendor: str, amount: float) -> list[dict]:
    """Look up prior expense entries matching employee, vendor, and amount.

    Used by the Duplicate/Anomaly Detection Agent to check whether a similar
    entry has already been submitted.

    Args:
        employee: Employee name to match.
        vendor: Vendor name to match.
        amount: Dollar amount to match.

    Returns:
        A list of matching historical expense entries.
    """
    conn = _connect()
    try:
        cur = conn.execute(
            "SELECT * FROM expenses WHERE employee = ? AND vendor = ? AND amount = ?",
            (employee, vendor, amount),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


@mcp.tool()
def flag_expense(entry_id: str, new_status: str, reasoning: str) -> dict:
    """Update an expense entry's status (approve, flag, or reject).

    This intentionally only allows updating the `status` column -- it
    cannot modify amount, vendor, employee, or any other field.

    Args:
        entry_id: The expense entry to update.
        new_status: One of 'approved', 'flagged', 'rejected'.
        reasoning: Short explanation for the decision (stored in audit log).

    Returns:
        Confirmation dict with the updated entry_id and new_status.
    """
    allowed_statuses = {"approved", "flagged", "rejected", "pending"}
    if new_status not in allowed_statuses:
        raise ValueError(f"new_status must be one of {allowed_statuses}")

    conn = _connect()
    try:
        conn.execute(
            "UPDATE expenses SET status = ? WHERE entry_id = ?",
            (new_status, entry_id),
        )
        conn.execute(
            "INSERT INTO audit_log (entry_id, agent_name, decision, reasoning) "
            "VALUES (?, ?, ?, ?)",
            (entry_id, "policy_or_duplicate_agent", new_status, reasoning),
        )
        conn.commit()
        return {"entry_id": entry_id, "new_status": new_status}
    finally:
        conn.close()


@mcp.tool()
def write_audit_entry(entry_id: str, agent_name: str, decision: str, reasoning: str) -> dict:
    """Append an entry to the audit log (append-only, never overwrites history).

    Args:
        entry_id: The expense entry this audit note relates to.
        agent_name: Which agent produced this decision/note.
        decision: Short label for the decision made.
        reasoning: Free-text explanation, used in the final report.

    Returns:
        Confirmation dict.
    """
    conn = _connect()
    try:
        conn.execute(
            "INSERT INTO audit_log (entry_id, agent_name, decision, reasoning) "
            "VALUES (?, ?, ?, ?)",
            (entry_id, agent_name, decision, reasoning),
        )
        conn.commit()
        return {"status": "logged", "entry_id": entry_id}
    finally:
        conn.close()


@mcp.tool()
def get_audit_log(entry_id: Optional[str] = None) -> list[dict]:
    """Retrieve audit log entries, optionally filtered to one expense entry.

    Read-only. Used by the Reporting Agent to build the final auditable
    report -- every decision any agent made is traceable here.

    Args:
        entry_id: Optional entry_id to filter the audit log to.

    Returns:
        A list of audit log rows, most recent last.
    """
    conn = _connect()
    try:
        if entry_id:
            cur = conn.execute(
                "SELECT * FROM audit_log WHERE entry_id = ? ORDER BY id", (entry_id,)
            )
        else:
            cur = conn.execute("SELECT * FROM audit_log ORDER BY id")
        return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


if __name__ == "__main__":
    mcp.run()

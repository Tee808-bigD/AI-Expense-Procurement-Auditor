"""
db_setup.py
------------
Initializes a local SQLite ledger from the synthetic expense CSV.

This acts as our stand-in "accounting system." The MCP server reads
and writes to this database, NOT directly to LLM prompts -- this keeps
a clean separation between data storage and agent reasoning.

Run this once before starting the MCP server:
    python data/db_setup.py
"""

import csv
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "expenses.db"
CSV_PATH = Path(__file__).parent / "sample_expenses.csv"


def init_db(reset: bool = True) -> None:
    """Create the expenses table and load it from the CSV seed data.

    Args:
        reset: If True, drops and recreates the table (clean demo state).
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    if reset:
        cur.execute("DROP TABLE IF EXISTS expenses")
        cur.execute("DROP TABLE IF EXISTS audit_log")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            entry_id TEXT PRIMARY KEY,
            employee TEXT NOT NULL,
            department TEXT,
            vendor TEXT,
            category TEXT,
            amount REAL,
            date TEXT,
            has_receipt INTEGER,
            notes TEXT,
            status TEXT DEFAULT 'pending'
        )
        """
    )

    # Audit log is append-only: every agent decision gets recorded here,
    # which is what makes the system's output auditable by a human reviewer.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_id TEXT,
            agent_name TEXT,
            decision TEXT,
            reasoning TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = [
            (
                row["entry_id"],
                row["employee"],
                row["department"],
                row["vendor"],
                row["category"],
                float(row["amount"]),
                row["date"],
                1 if row["has_receipt"].strip().upper() == "TRUE" else 0,
                row["notes"],
            )
            for row in reader
        ]

    cur.executemany(
        """
        INSERT OR REPLACE INTO expenses
        (entry_id, employee, department, vendor, category, amount, date, has_receipt, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )

    conn.commit()
    conn.close()
    print(f"Initialized {DB_PATH} with {len(rows)} expense entries.")


if __name__ == "__main__":
    init_db()

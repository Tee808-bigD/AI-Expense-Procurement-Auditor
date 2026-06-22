"""
dashboard/app.py
--------------------
Simple Streamlit dashboard for the demo video: shows the expense ledger,
flagged entries, and estimated dollar impact at a glance.

Run with:
    streamlit run dashboard/app.py

Note: run agents/orchestrator.py at least once first so data/expenses.db
and output/report.md exist.
"""

import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))

DB_PATH = Path(__file__).parent.parent / "data" / "expenses.db"
REPORT_PATH = Path(__file__).parent.parent / "output" / "report.md"

st.set_page_config(page_title="Expense & Procurement Auditor", layout="wide")
st.title("🧾 AI Expense & Procurement Auditor")
st.caption("Multi-agent audit pipeline: Ingestion → Policy → Duplicate/Anomaly → Reporting")


def load_expenses() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return df


def load_audit_log() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY id", conn)
    conn.close()
    return df


expenses_df = load_expenses()

if expenses_df.empty:
    st.warning(
        "No data found. Run `python agents/orchestrator.py` first to "
        "generate the ledger and audit results."
    )
else:
    total = len(expenses_df)
    approved = (expenses_df["status"] == "approved").sum()
    flagged = (expenses_df["status"] == "flagged").sum()
    rejected = (expenses_df["status"] == "rejected").sum()
    flagged_amount = expenses_df.loc[
        expenses_df["status"].isin(["flagged", "rejected"]), "amount"
    ].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Entries", total)
    col2.metric("Approved", int(approved))
    col3.metric("Flagged / Rejected", int(flagged + rejected))
    col4.metric("$ At Risk Caught", f"${flagged_amount:,.2f}")

    st.divider()

    tab1, tab2, tab3 = st.tabs(["📋 Full Ledger", "🚩 Flagged Entries", "📝 Audit Trail"])

    with tab1:
        st.dataframe(expenses_df, use_container_width=True)

    with tab2:
        flagged_df = expenses_df[expenses_df["status"].isin(["flagged", "rejected"])]
        st.dataframe(flagged_df, use_container_width=True)

    with tab3:
        audit_df = load_audit_log()
        st.dataframe(audit_df, use_container_width=True)

st.divider()
st.subheader("📄 Final Report")

if REPORT_PATH.exists():
    st.markdown(REPORT_PATH.read_text(encoding="utf-8"))
else:
    st.info("Report not generated yet. Run the orchestrator to produce output/report.md.")

"""
dashboard/app.py
----------------
Professional Streamlit dashboard for the AI Expense & Procurement Auditor.

Features:
- Real-time KPI metrics (total, approved, flagged, $ at risk)
- Interactive data tables with filtering
- Visual analytics (violation breakdown, department analysis, trend charts)
- ANTIGRAVITY WIDGET: Proactive audit assistant that warns before risky actions
- POLICY CONFIGURATOR: Edit rules directly from the UI
- Audit trail with full traceability

Run with:
    streamlit run dashboard/app.py
"""

import json
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# =============================================================================
# Page Config — Professional Look
# =============================================================================
st.set_page_config(
    page_title="AI Expense & Procurement Auditor",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =============================================================================
# Custom CSS for Professional Styling
# =============================================================================
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6b7280;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.5rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .flagged-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .risk-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    }
    .approved-card {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    }
    .antigravity-box {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-left: 4px solid #f97316;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    .antigravity-title {
        color: #c2410c;
        font-weight: 700;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# Paths
# =============================================================================
DB_PATH = Path(__file__).parent.parent / "data" / "expenses.db"
REPORT_PATH = Path(__file__).parent.parent / "output" / "report.md"
POLICY_PATH = Path(__file__).parent.parent / "data" / "policy_rules.json"

# =============================================================================
# Data Loading Functions
# =============================================================================
@st.cache_data(ttl=10)
def load_expenses() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM expenses", conn)
    conn.close()
    return df

@st.cache_data(ttl=10)
def load_audit_log() -> pd.DataFrame:
    if not DB_PATH.exists():
        return pd.DataFrame()
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM audit_log ORDER BY id DESC", conn)
    conn.close()
    return df

def load_policy_rules() -> dict:
    if not POLICY_PATH.exists():
        return {}
    with open(POLICY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_policy_rules(rules: dict):
    with open(POLICY_PATH, "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2)

# =============================================================================
# ANTIGRAVITY WIDGET: Proactive Audit Assistant
# =============================================================================
def render_antigravity_widget(expenses_df: pd.DataFrame):
    """Antigravity Pattern: The assistant proactively surfaces warnings
    without the user asking. It 'floats' insights to the top based on
    current context — like a smart colleague tapping you on the shoulder."""
    if expenses_df.empty:
        return

    warnings = []

    high_value_flagged = expenses_df[
        (expenses_df["status"].isin(["flagged", "rejected"])) &
        (expenses_df["amount"] >= 1000)
    ]
    if not high_value_flagged.empty:
        total = high_value_flagged["amount"].sum()
        count = len(high_value_flagged)
        warnings.append(
            f"🚨 **{count} high-value flagged entries** (${total:,.2f} total) require "
            f"immediate review."
        )

    dup_candidates = expenses_df[
        expenses_df.duplicated(subset=["employee", "vendor", "amount"], keep=False)
    ]
    if not dup_candidates.empty:
        emp = dup_candidates.iloc[0]["employee"]
        vendor = dup_candidates.iloc[0]["vendor"]
        amt = dup_candidates.iloc[0]["amount"]
        warnings.append(
            f"⚠️ **Potential duplicate detected**: {emp} has multiple entries for "
            f"{vendor} at ${amt:,.2f}."
        )

    no_receipt_high = expenses_df[
        (expenses_df["has_receipt"] == 0) &
        (expenses_df["amount"] > 100)
    ]
    if not no_receipt_high.empty:
        count = len(no_receipt_high)
        warnings.append(
            f"📄 **{count} entries over $100** lack receipts."
        )

    policy = load_policy_rules()
    threshold = policy.get("approval_required_above", 500)
    buffer = policy.get("near_threshold_buffer", 5)
    near_threshold = expenses_df[
        (expenses_df["amount"] >= threshold - buffer) &
        (expenses_df["amount"] < threshold)
    ]
    if not near_threshold.empty:
        count = len(near_threshold)
        warnings.append(
            f"🔍 **{count} entries** are within ${buffer} of the ${threshold} "
            f"approval threshold — possible structuring pattern."
        )

    if warnings:
        st.markdown('<div class="antigravity-box">', unsafe_allow_html=True)
        st.markdown('<div class="antigravity-title">🪶 Proactive Audit Assistant</div>', unsafe_allow_html=True)
        st.markdown("The agent is continuously monitoring and has surfaced these concerns:")
        for w in warnings:
            st.markdown(f"- {w}")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.success("✅ Proactive Audit Assistant: No immediate concerns detected. All clear!")

# =============================================================================
# HEADER
# =============================================================================
st.markdown('<div class="main-header">⚖️ AI Expense & Procurement Auditor</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Multi-agent audit pipeline: Ingestion → Policy → Duplicate/Anomaly → Reporting</div>',
    unsafe_allow_html=True
)

# =============================================================================
# LOAD DATA
# =============================================================================
expenses_df = load_expenses()

if expenses_df.empty:
    st.warning(
        "No data found. Run `python agents/orchestrator.py` first to "
        "generate the ledger and audit results."
    )
    st.stop()

# =============================================================================
# KPI METRICS
# =============================================================================
total = len(expenses_df)
approved = (expenses_df["status"] == "approved").sum()
flagged = (expenses_df["status"] == "flagged").sum()
rejected = (expenses_df["status"] == "rejected").sum()
flagged_amount = expenses_df.loc[
    expenses_df["status"].isin(["flagged", "rejected"]), "amount"
].sum()
approved_amount = expenses_df.loc[expenses_df["status"] == "approved", "amount"].sum()

time_saved_min = total * 15
time_saved_hours = time_saved_min / 60

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-value">{total}</div><div class="metric-label">Total Entries</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card approved-card"><div class="metric-value">{int(approved)}</div><div class="metric-label">Approved</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card flagged-card"><div class="metric-value">{int(flagged + rejected)}</div><div class="metric-label">Flagged / Rejected</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card risk-card"><div class="metric-value">${flagged_amount:,.2f}</div><div class="metric-label">$ At Risk Caught</div></div>', unsafe_allow_html=True)

st.markdown("---")

# =============================================================================
# ANTIGRAVITY WIDGET
# =============================================================================
render_antigravity_widget(expenses_df)

st.markdown("---")

# =============================================================================
# TABS
# =============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 Full Ledger",
    "🚩 Flagged Entries",
    "📝 Audit Trail",
    "📊 Analytics",
    "⚙️ Policy Configurator"
])

with tab1:
    st.subheader("Complete Expense Ledger")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        status_filter = st.multiselect("Filter by Status", options=expenses_df["status"].unique(), default=[])
    with col_f2:
        dept_filter = st.multiselect("Filter by Department", options=expenses_df["department"].unique(), default=[])
    with col_f3:
        cat_filter = st.multiselect("Filter by Category", options=expenses_df["category"].unique(), default=[])

    filtered = expenses_df.copy()
    if status_filter:
        filtered = filtered[filtered["status"].isin(status_filter)]
    if dept_filter:
        filtered = filtered[filtered["department"].isin(dept_filter)]
    if cat_filter:
        filtered = filtered[filtered["category"].isin(cat_filter)]

    st.dataframe(filtered, use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(filtered)} of {total} entries")

with tab2:
    st.subheader("Flagged & Rejected Entries")
    flagged_df = expenses_df[expenses_df["status"].isin(["flagged", "rejected"])]
    if flagged_df.empty:
        st.info("No flagged or rejected entries. Great job!")
    else:
        st.dataframe(flagged_df, use_container_width=True, hide_index=True)
        st.metric("Total Flagged Amount", f"${flagged_df['amount'].sum():,.2f}")

with tab3:
    st.subheader("Audit Trail — Every Decision Logged")
    audit_df = load_audit_log()
    if audit_df.empty:
        st.info("No audit log entries yet. Run the orchestrator to generate decisions.")
    else:
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        st.caption("Every agent decision is append-only and auditable.")

with tab4:
    st.subheader("Visual Analytics")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("**Status Distribution**")
        status_counts = expenses_df["status"].value_counts()
        st.bar_chart(status_counts)
    with col_a2:
        st.markdown("**Amount by Department**")
        dept_amounts = expenses_df.groupby("department")["amount"].sum().sort_values(ascending=False)
        st.bar_chart(dept_amounts)

    st.markdown("---")
    col_a3, col_a4 = st.columns(2)
    with col_a3:
        st.markdown("**Category Breakdown**")
        cat_counts = expenses_df["category"].value_counts()
        st.bar_chart(cat_counts)
    with col_a4:
        st.markdown("**Amount Distribution**")
        st.line_chart(expenses_df.sort_values("amount")["amount"].reset_index(drop=True))

    st.markdown("---")
    st.markdown("**Impact Summary**")
    impact_col1, impact_col2, impact_col3 = st.columns(3)
    with impact_col1:
        st.metric("Total Approved", f"${approved_amount:,.2f}")
    with impact_col2:
        st.metric("Total At Risk", f"${flagged_amount:,.2f}")
    with impact_col3:
        st.metric("Est. Time Saved", f"{time_saved_hours:.1f} hours")

with tab5:
    st.subheader("⚙️ Policy Configurator")
    st.markdown("Edit policy rules directly. Changes are saved to `data/policy_rules.json`.")

    policy = load_policy_rules()
    if not policy:
        st.error("Could not load policy rules.")
    else:
        with st.form("policy_form"):
            meal_limit = st.number_input(
                "Meal Limit Per Entry ($)",
                min_value=0.0,
                value=float(policy.get("meal_limit_per_entry", 75.0)),
                step=5.0,
            )
            approval_threshold = st.number_input(
                "Approval Required Above ($)",
                min_value=0.0,
                value=float(policy.get("approval_required_above", 500.0)),
                step=50.0,
            )
            near_buffer = st.number_input(
                "Near-Threshold Buffer ($)",
                min_value=0.0,
                value=float(policy.get("near_threshold_buffer", 5.0)),
                step=1.0,
            )
            receipt_threshold = st.number_input(
                "Receipt Required Above ($)",
                min_value=0.0,
                value=float(policy.get("receipt_required_above", 25.0)),
                step=5.0,
            )
            disallowed = st.text_area(
                "Disallowed Categories (comma-separated)",
                value=", ".join(policy.get("disallowed_categories", ["Personal"])),
            )
            submitted = st.form_submit_button("💾 Save Policy Rules")

        if submitted:
            new_policy = {
                "meal_limit_per_entry": meal_limit,
                "approval_required_above": approval_threshold,
                "near_threshold_buffer": near_buffer,
                "disallowed_categories": [c.strip() for c in disallowed.split(",") if c.strip()],
                "receipt_required_above": receipt_threshold,
                "duplicate_match_fields": policy.get("duplicate_match_fields", ["employee", "vendor", "amount", "date"]),
                "rules_description": {
                    "meal_limit_per_entry": f"Single meal expenses above ${meal_limit} require pre-approval.",
                    "approval_required_above": f"Any single expense above ${approval_threshold} requires documented pre-approval.",
                    "near_threshold_buffer": f"Flag expenses within ${near_buffer} below the approval threshold.",
                    "disallowed_categories": "Expense categories that should never be reimbursed.",
                    "receipt_required_above": f"Expenses above ${receipt_threshold} must have a receipt attached.",
                    "duplicate_match_fields": "Fields used to detect duplicate submissions."
                }
            }
            save_policy_rules(new_policy)
            st.success("✅ Policy rules updated! Run the orchestrator to apply changes.")
            st.balloons()

# =============================================================================
# FINAL REPORT SECTION
# =============================================================================
st.markdown("---")
st.subheader("📄 Final Audit Report")

if REPORT_PATH.exists():
    report_text = REPORT_PATH.read_text(encoding="utf-8")
    with st.expander("View Full Report (Markdown)", expanded=False):
        st.markdown(report_text)
else:
    st.info("Report not generated yet. Run the orchestrator to produce output/report.md.")

st.markdown("---")
st.caption(
    "Built with Google ADK • MCP • Streamlit | "
    "AI Agents: Intensive Vibe Coding Capstone Project 2026"
)

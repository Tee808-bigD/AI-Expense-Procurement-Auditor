"""
agents/reporting_agent.py
----------------------------
Reporting Agent: pulls the final ledger state and full audit trail, restores
real employee names (PII was only redacted for the reasoning steps, not for
the human reviewer's final report), and writes a clear approve/flag/reject
summary with an estimated dollar impact.
"""

from pathlib import Path

from google.adk.agents import LlmAgent
from google.genai import types

from .mcp_connection import build_expense_mcp_toolset
from .security_utils import restore_employee_pii

MODEL = "gemini-flash-latest"
OUTPUT_PATH = Path(__file__).parent.parent / "output" / "report.md"


def restore_pii_in_text(report_text: str, pii_mapping: dict) -> dict:
    """Tool: restores real employee names in the final report text.

    This is the one place real names re-enter the pipeline -- intentionally
    only at the final, human-facing report stage, never during LLM
    reasoning steps.

    Args:
        report_text: Draft report text containing anonymous tokens.
        pii_mapping: The {token: real_name} mapping from the Ingestion Agent.

    Returns:
        Dict with the restored report text.
    """
    return {"restored_report": restore_employee_pii(report_text, pii_mapping)}


def write_report_to_file(report_markdown: str) -> dict:
    """Tool: writes the final report to output/report.md.

    Args:
        report_markdown: The final, PII-restored report content.

    Returns:
        Dict confirming the file path written.
    """
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report_markdown, encoding="utf-8")
    return {"written_to": str(OUTPUT_PATH)}


# Reporting Agent is read-only on the ledger and audit log -- it never
# flags or approves anything itself, it only summarizes what the Policy
# and Duplicate agents already decided. This keeps "who can change a
# status" narrowly scoped to two agents, not four.
reporting_mcp_tools = build_expense_mcp_toolset(
    tool_filter=["get_expenses", "get_audit_log"]
)

reporting_agent = LlmAgent(
    name="ReportingAgent",
    model=MODEL,
    description=(
        "Synthesizes all findings into a final, human-readable audit "
        "report with an estimated dollar impact."
    ),
    instruction=(
        "You are the Reporting Agent, the final step in the pipeline.\n\n"
        "1. Call `get_expenses` (no filter) to get the full ledger with "
        "final statuses, and `get_audit_log` (no filter) to get every "
        "decision made by the Policy and Duplicate agents.\n"
        "2. Draft a clear Markdown report with these sections:\n"
        "   - ## Summary (total entries, # approved, # flagged, # rejected)\n"
        "   - ## Estimated Dollar Impact (sum of flagged/rejected amounts "
        "as 'dollars at risk caught', stated clearly)\n"
        "   - ## Flagged Entries (table: entry_id, employee token, vendor, "
        "amount, reasoning)\n"
        "   - ## Approved Entries (brief count + total amount, no need to "
        "list every one)\n"
        "Use the anonymous employee tokens (EMP_001, etc.) in this draft --"
        " do not invent real names yourself.\n"
        "3. Call `restore_pii_in_text` with your draft report and the "
        "`pii_mapping` from session state to get the final report with "
        "real employee names restored.\n"
        "4. Call `write_report_to_file` with the restored report text.\n"
        "5. Output the restored report text as your final response."
    ),
    tools=[reporting_mcp_tools, restore_pii_in_text, write_report_to_file],
    output_key="final_report",
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)

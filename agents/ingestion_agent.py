"""
agents/ingestion_agent.py
----------------------------
Ingestion Agent: pulls pending expense entries via MCP and prepares them
for downstream agents.

SECURITY NOTE: PII redaction happens here, before any other agent's LLM
call sees the data. Real employee names never enter a model prompt --
only anonymous tokens (EMP_001, etc.) do. The mapping is stashed in
session state so the Reporting Agent can restore real names at the end.
"""

from google.adk.agents import LlmAgent
from google.genai import types

from .mcp_connection import build_expense_mcp_toolset
from .security_utils import redact_employee_pii

MODEL = "gemini-flash-latest"


def prepare_redacted_batch(raw_expenses: list[dict]) -> dict:
    """Tool: redacts employee PII from a batch of expense records.

    This is a deterministic Python function (not an LLM call) -- redaction
    should never depend on model judgment, it should be guaranteed.

    Args:
        raw_expenses: Raw expense records as returned by the MCP
            get_expenses tool.

    Returns:
        Dict with 'redacted_expenses' (list) and 'pii_mapping' (dict),
        both written to session state via output_key so later agents
        and the Reporting Agent can use them.
    """
    redacted, mapping = redact_employee_pii(raw_expenses)
    return {"redacted_expenses": redacted, "pii_mapping": mapping}


# The Ingestion Agent only needs read access -- it is never given the
# write tools (flag_expense, write_audit_entry). Least privilege in practice.
ingestion_mcp_tools = build_expense_mcp_toolset(tool_filter=["get_expenses"])

ingestion_agent = LlmAgent(
    name="IngestionAgent",
    model=MODEL,
    description=(
        "Retrieves pending expense entries from the ledger and prepares "
        "them for policy and duplicate review, redacting employee PII first."
    ),
    instruction=(
        "You are the Ingestion Agent in an expense auditing pipeline.\n"
        "1. Call the `get_expenses` tool with status='pending' to retrieve "
        "entries that still need review.\n"
        "2. Call `prepare_redacted_batch` with the raw expenses you retrieved "
        "to redact employee PII.\n"
        "3. Output only a short confirmation of how many entries were "
        "retrieved and redacted -- the structured data itself is passed "
        "forward automatically via session state."
    ),
    tools=[ingestion_mcp_tools, prepare_redacted_batch],
    output_key="ingestion_summary",
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)

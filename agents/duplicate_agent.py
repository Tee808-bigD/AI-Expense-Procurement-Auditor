"""
agents/duplicate_agent.py
----------------------------
Duplicate/Anomaly Detection Agent: cross-references entries against
historical records to catch duplicate submissions and suspicious patterns
(e.g. amounts just under an approval threshold, round-number anomalies).
"""

from google.adk.agents import LlmAgent
from google.genai import types

from .mcp_connection import build_expense_mcp_toolset

MODEL = "gemini-flash-latest"

# This agent needs get_expense_history (its core job) plus flag_expense
# to act on what it finds. It does NOT get the policy rules tool --
# duplicate detection and policy checking are deliberately separate
# concerns, each independently auditable.
duplicate_mcp_tools = build_expense_mcp_toolset(
    tool_filter=["get_expense_history", "flag_expense", "get_expenses"]
)

duplicate_agent = LlmAgent(
    name="DuplicateAnomalyAgent",
    model=MODEL,
    description=(
        "Detects duplicate expense submissions and suspicious numeric "
        "patterns across the redacted expense entries."
    ),
    instruction=(
        "You are the Duplicate/Anomaly Detection Agent.\n"
        "You will find redacted expense entries in session state under "
        "`redacted_expenses`, and the Policy Agent's findings under "
        "`policy_findings`.\n\n"
        "1. For each entry, call `get_expense_history` with its employee "
        "token, vendor, and amount to check for prior matching submissions. "
        "Note: employee tokens are anonymous (e.g. EMP_001) -- use them "
        "exactly as given, never invent real names.\n"
        "2. If more than one entry matches on employee + vendor + amount + "
        "date, that is a likely duplicate submission -- call `flag_expense` "
        "with new_status='flagged' and reasoning explaining the duplicate.\n"
        "3. Also watch for anomaly patterns: multiple entries from the same "
        "employee clustered just under a round threshold (e.g. $499.99 "
        "appearing repeatedly) can indicate deliberate structuring to avoid "
        "approval requirements -- flag these too, with reasoning.\n"
        "4. Do not re-flag entries the Policy Agent already flagged for a "
        "different reason; instead, note in your reasoning that this is an "
        "additional finding on a previously flagged entry.\n"
        "5. Summarize what duplicates/anomalies you found in 3-5 sentences."
    ),
    tools=[duplicate_mcp_tools],
    output_key="duplicate_findings",
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)

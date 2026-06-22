"""
agents/policy_agent.py
-------------------------
Policy Compliance Agent: checks each redacted expense entry against the
configurable rules in data/policy_rules.json and flags violations via MCP.
"""

import json
from pathlib import Path

from google.adk.agents import LlmAgent
from google.genai import types

from .mcp_connection import build_expense_mcp_toolset

MODEL = "gemini-flash-latest"
POLICY_PATH = Path(__file__).parent.parent / "data" / "policy_rules.json"


def load_policy_rules() -> dict:
    """Tool: loads the current policy rules from the config file.

    Keeping rules in a JSON file (rather than hardcoded in the prompt)
    means finance teams can update policy without touching agent code.

    Returns:
        The policy rules dict.
    """
    with open(POLICY_PATH, encoding="utf-8") as f:
        return json.load(f)


# Policy Agent needs to read entries AND write flag decisions, so it gets
# both get_expenses and flag_expense -- still not the full tool set
# (e.g. it has no access to get_expense_history, which only the
# Duplicate Agent needs).
policy_mcp_tools = build_expense_mcp_toolset(
    tool_filter=["get_expenses", "flag_expense"]
)

policy_agent = LlmAgent(
    name="PolicyComplianceAgent",
    model=MODEL,
    description=(
        "Checks redacted expense entries against company policy rules and "
        "flags violations with clear reasoning."
    ),
    instruction=(
        "You are the Policy Compliance Agent.\n"
        "You will find a list of redacted expense entries in session state "
        "under `redacted_expenses` (set by the Ingestion Agent).\n\n"
        "1. Call `load_policy_rules` to get the current policy thresholds.\n"
        "2. For each entry, check it against the rules:\n"
        "   - Meals over `meal_limit_per_entry` need pre-approval.\n"
        "   - Any amount over `approval_required_above` needs documented "
        "pre-approval; note the entry if no such approval is mentioned.\n"
        "   - Amounts within `near_threshold_buffer` below the approval "
        "threshold are a potential structuring pattern -- flag for review.\n"
        "   - Entries in `disallowed_categories` should never be approved.\n"
        "   - Entries above `receipt_required_above` without a receipt "
        "(has_receipt is false/0) should be flagged.\n"
        "3. For every entry that violates a rule, call `flag_expense` with "
        "new_status='flagged' and a short, specific reasoning string "
        "(use the entry's anonymous employee token, not any other "
        "identifying detail).\n"
        "4. For entries with no violations, call `flag_expense` with "
        "new_status='approved' and a brief reasoning.\n"
        "5. Summarize how many entries were approved vs. flagged, and why, "
        "in 3-5 sentences."
    ),
    tools=[policy_mcp_tools, load_policy_rules],
    output_key="policy_findings",
    generate_content_config=types.GenerateContentConfig(temperature=0.0),
)

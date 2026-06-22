"""
agents/security_utils.py
--------------------------
SECURITY FEATURE: PII redaction.

Employee names are personally identifiable information. Before any expense
data is sent to the LLM for reasoning (policy checks, duplicate detection),
we replace real names with anonymous tokens (e.g. "EMP_001"). The mapping
is held only in local memory and used to restore real names afterward --
for the final report and for any database writes, which a human reviewer
needs in order to act.

This means: if an LLM provider logs prompts, or if a prompt-injection
attempt tried to exfiltrate data through the model's reasoning trace,
employee identities are not present in what was sent to the model.
"""

from typing import Any


def redact_employee_pii(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, str]]:
    """Replace employee names with anonymous tokens before LLM exposure.

    Args:
        records: List of expense record dicts containing an 'employee' field.

    Returns:
        A tuple of (redacted_records, mapping) where mapping is
        {anonymous_token: real_name}, used later to restore identities.
    """
    mapping: dict[str, str] = {}
    name_to_token: dict[str, str] = {}
    redacted: list[dict[str, Any]] = []

    for record in records:
        real_name = record.get("employee", "Unknown")
        if real_name not in name_to_token:
            token = f"EMP_{len(name_to_token) + 1:03d}"
            name_to_token[real_name] = token
            mapping[token] = real_name

        redacted_record = dict(record)
        redacted_record["employee"] = name_to_token[real_name]
        redacted.append(redacted_record)

    return redacted, mapping


def restore_employee_pii(text: str, mapping: dict[str, str]) -> str:
    """Replace anonymous tokens back with real employee names in output text.

    Args:
        text: Text (e.g. a report) containing anonymous tokens like 'EMP_001'.
        mapping: The {token: real_name} mapping produced by redact_employee_pii.

    Returns:
        The text with tokens replaced by real names.
    """
    restored = text
    for token, real_name in mapping.items():
        restored = restored.replace(token, real_name)
    return restored

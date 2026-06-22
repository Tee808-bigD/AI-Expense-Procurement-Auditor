"""agents/__init__.py
--------------------
ADK-compliant agent package initialization.
"""

from .ingestion_agent import ingestion_agent
from .policy_agent import policy_agent
from .duplicate_agent import duplicate_agent
from .reporting_agent import reporting_agent
from .orchestrator import run_audit

__all__ = [
    "ingestion_agent",
    "policy_agent",
    "duplicate_agent",
    "reporting_agent",
    "run_audit",
]

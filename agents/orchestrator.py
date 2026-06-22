"""
agents/orchestrator.py
--------------------------
Multi-agent orchestration using Workflow to avoid Gemini API rate limits.
Wires Ingestion -> Policy Compliance -> Duplicate/Anomaly -> Reporting.
"""

import asyncio
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent.parent))

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.ingestion_agent import ingestion_agent
from agents.policy_agent import policy_agent
from agents.duplicate_agent import duplicate_agent
from agents.reporting_agent import reporting_agent
from data.db_setup import init_db

APP_NAME = "expense_auditor"
USER_ID = "finance_reviewer"
SESSION_ID = "audit_run_001"

async def run_audit() -> str:
    """Runs the audit pipeline step-by-step with delays to avoid 429 errors."""
    # Fresh, reproducible demo data on every run.
    init_db(reset=True)

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    # We use separate runners for each agent to control the timing (adding sleeps)
    # while sharing the same session_service to maintain state.
    pipeline_agents = [
        (ingestion_agent, "Run the ingestion step: retrieve and redact expenses."),
        (policy_agent, "Review expenses for policy compliance."),
        (duplicate_agent, "Check for duplicates and anomalies."),
        (reporting_agent, "Generate the final audit report."),
    ]

    final_text = ""

    for agent, prompt in pipeline_agents:
        print(f"\n>>> Activating {agent.name}...")

        runner = Runner(
            agent=agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)],
        )

        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=message
        ):
            if event.is_final_response() and event.content and event.content.parts:
                text = event.content.parts[0].text
                print(f"\n--- [{event.author}] ---\n{text}\n")
                final_text = text

        # Critical: Sleep to avoid Gemini API 429 Resource Exhausted
        print("Waiting 15 seconds to respect API rate limits...")
        await asyncio.sleep(15)

    return final_text

if __name__ == "__main__":
    asyncio.run(run_audit())

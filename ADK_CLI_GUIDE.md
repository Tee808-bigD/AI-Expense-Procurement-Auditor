# ADK CLI Usage Guide

This project supports the official ADK CLI commands for development and testing.

## Prerequisites

```bash
pip install google-adk
```

## Project Structure for ADK CLI

```
AI-Expense-Procurement-Auditor/
├── agent.py              # ← ADK root_agent (required for adk run / adk web)
├── .env                  # ← GOOGLE_API_KEY (required)
├── agents/
│   ├── __init__.py
│   ├── orchestrator.py
│   ├── ingestion_agent.py
│   ├── policy_agent.py
│   ├── duplicate_agent.py
│   ├── reporting_agent.py
│   ├── mcp_connection.py
│   └── security_utils.py
├── mcp_server/
│   └── server.py
├── data/
│   ├── sample_expenses.csv
│   ├── db_setup.py
│   └── policy_rules.json
├── dashboard/
│   └── app.py
└── output/
    └── report.md
```

> **Important**: `agent.py` must be at the project root for `adk run` and `adk web` to work.

## Commands

### 1. Run via Command Line (adk run)

```bash
# From the project root directory:
adk run .
```

This starts an interactive chat session in your terminal. You can type:

```
> Run a full audit
> Show me the metrics
> What entries were flagged?
> Run audit and tell me the dollar impact
```

The root_agent will call the appropriate tool and return results.

### 2. Run via Web UI (adk web)

```bash
# From the project root directory:
adk web --port 8000
```

Then open http://localhost:8000 in your browser.

- Select "expense_auditor" from the agent dropdown (top-left)
- Type your request in the chat box
- See the agent think, call tools, and return results

> **Note**: ADK Web is for development only, not production.

### 3. What the Root Agent Can Do

| User Request | Tool Called | What Happens |
|---|---|---|
| "Run an audit" | `run_full_audit_tool` | Full pipeline: 4 agents, ~1 min, generates report |
| "Show metrics" | `get_dashboard_metrics` | Returns KPIs instantly from DB |
| "What was flagged?" | `get_flagged_entries` | Lists all flagged entries with reasoning |
| "Run audit and show impact" | `run_full_audit_tool` → chat response | Full pipeline + summary |

## Why This Matters for the Capstone

This demonstrates **Agent Skills** — one of the 6 key evaluation concepts:

- The root_agent exposes the full pipeline as a **skill** that can be invoked via CLI or web UI
- Non-technical users can run audits without touching code
- The agent interprets natural language and routes to the correct tool
- This is the "agentic" interface pattern judges look for

## Troubleshooting

### "No module named 'google.adk'"
```bash
pip install google-adk
```

### "GOOGLE_API_KEY not set"
```bash
echo 'GOOGLE_API_KEY="your_key"' > .env
```

### "Database not found"
```bash
python data/db_setup.py
```

### "adk run says 'No agent found'"
Make sure `agent.py` is at the project root (not inside `agents/`).

## Video Demo Script (ADK CLI Segment)

For your 5-minute video, show this sequence:

1. **Terminal**: `adk run .`
2. **Type**: "Run a full audit"
3. **Show**: The agent calling tools, the 15-second sleeps between agents, the final report
4. **Type**: "Show me the metrics"
5. **Show**: Instant KPI response
6. **Say**: "This is the ADK CLI — anyone on the finance team can run audits from the terminal without writing code."

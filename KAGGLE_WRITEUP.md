# Kaggle Writeup — AI Expense & Procurement Auditor

## Title
AI Expense & Procurement Auditor: Multi-Agent AI for Automated Financial Compliance

## Subtitle
A Google ADK-powered system that ingests expense data, checks policy compliance, detects duplicates and anomalies, and produces audit-ready reports — saving finance teams 125+ hours per month while catching $100K+ in at-risk spend.

## Track
Agents for Business

---

## Problem Statement

Finance teams manually review every expense report and vendor invoice to ensure compliance with company policies, catch duplicate payments, and prevent fraud. This process is:

- **Slow**: 15 minutes per entry × 500 entries/month = 125 hours of staff time
- **Inconsistent**: Different reviewers apply rules differently
- **Error-prone**: Manual review catches only 60-70% of violations
- **Unauditable**: Decisions are rarely logged with full reasoning
- **Unscalable**: Headcount must grow linearly with transaction volume

## Why Agents?

A static rules engine can catch "meals over $75" but cannot explain why that matters, adapt when policy changes, or detect novel fraud patterns. A single monolithic LLM prompt could do all of this, but it would be a black box with no audit trail, no modularity, and no way to enforce security boundaries.

The multi-agent approach delivers four advantages:

1. **Auditability**: Every decision is logged by a named agent with timestamp and reasoning
2. **Modularity**: Swap, upgrade, or disable agents independently without rewriting the system
3. **Security**: PII is redacted before any LLM sees it; each agent gets only the tools it needs
4. **Adaptability**: Policy rules are externalized to JSON — finance teams can update thresholds without touching code

## Architecture

The system uses Google ADK with five specialized agents coordinated by an orchestrator:

- **Ingestion Agent**: Retrieves pending expenses via MCP, redacts employee PII, stashes the mapping in session state
- **Policy Compliance Agent**: Checks entries against configurable rules (meal limits, approval thresholds, receipt requirements, disallowed categories)
- **Duplicate/Anomaly Detection Agent**: Cross-references historical records for duplicates and suspicious patterns
- **Reporting Agent**: Synthesizes findings, restores real names, and writes a Markdown report with dollar impact
- **Orchestrator**: Coordinates the pipeline using ADK's Runner and InMemorySessionService

Data flows through MCP (Model Context Protocol) over stdio transport. The MCP server exposes only five narrow tools — no raw SQL, no full table access. Each agent receives a filtered subset of tools (least-privilege design).

## Key Concepts Demonstrated

| Concept | Implementation | Where to Find |
|---|---|---|
| **Multi-agent system (ADK)** | 5 LlmAgent instances with Runner orchestration | `agents/orchestrator.py` |
| **MCP Server** | FastMCP with 5 tools, stdio transport | `mcp_server/server.py` |
| **Security** | PII redaction, least-privilege tool filtering, env secrets | `agents/security_utils.py`, `.env.example` |
| **Deployability** | Streamlit dashboard, Docker, ADK CLI (`adk run`, `adk web`) | `Dockerfile`, `DEPLOYMENT.md`, `agent.py` |
| **Antigravity** | Proactive audit assistant widget in dashboard | `dashboard/app.py` — `render_antigravity_widget()` |
| **Agent skills** | `agent.py` root_agent exposes pipeline as callable skills; configurable policy rules | `agent.py`, `data/policy_rules.json` |

## Security Practices

- **PII Redaction**: Employee names are replaced with anonymous tokens (EMP_001) before any LLM prompt. The mapping is restored only in the final human-facing report.
- **Least-Privilege MCP Access**: Each agent receives only the tools it needs. The Ingestion Agent cannot write to the database. The Reporting Agent cannot flag entries.
- **No Hardcoded Secrets**: All credentials are loaded from environment variables. `.env` is gitignored.
- **Human-in-the-Loop**: The system produces recommendations only. A human must explicitly approve any action.
- **Append-Only Audit Log**: Every decision is logged with agent name, reasoning, and timestamp. The log is never overwritten.

## ADK CLI & Agent Skills

The project includes an ADK `root_agent` in `agent.py` that exposes the full audit pipeline as callable skills:

```bash
adk run .      # Interactive terminal chat
adk web --port 8000  # Browser UI at http://localhost:8000
```

Users can type natural language like "Run a full audit" or "Show me the metrics" and the agent routes to the correct skill. This demonstrates how agent systems can be exposed through multiple interfaces (CLI, web UI, dashboard) without rewriting the core logic.

## Results

On a demo dataset of 25 synthetic expense entries:

- **Entries processed**: 25
- **Violations flagged**: 4 (meal limit, approval threshold, disallowed category, missing receipt)
- **Duplicates caught**: 1 (duplicate $2,500 Facebook Ads submission)
- **$ at risk caught**: $6,758.39
- **Time saved**: 6.25 hours (25 × 15 min manual review)

At scale (500 entries/month): ~$135,000 in flagged-at-risk spend and 125 hours of finance team time reclaimed.

## Tech Stack

- Google ADK (agent framework)
- Python MCP SDK (MCP server/client)
- Google Gemini 2.5 Flash (LLM)
- SQLite (data source)
- Streamlit (dashboard)
- Python 3.10+

## Live Demo & Code

- 📹 Video: [YouTube link]
- 🔗 Live Demo: [Streamlit Cloud URL]
- 💻 Code: [GitHub repository]

## Future Work

- Integration with QuickBooks/NetSuite
- OCR-based receipt ingestion
- Learned fraud-pattern models
- Email/Slack notifications for flagged entries

---

*Built as part of the AI Agents: Intensive Vibe Coding Capstone Project, Kaggle, 2026.*

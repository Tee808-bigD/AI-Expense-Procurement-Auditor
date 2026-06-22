# AI Expense & Procurement Auditor

> A multi-agent system that automatically reviews expense reports and invoices, catches policy violations and duplicate payments, and produces an audit-ready summary for finance teams. Built to demonstrate how agentic AI can deliver real business value — dollars saved, compliance enforced, and time reclaimed.

**Track:** Agents for Business  
**Built for:** Kaggle's AI Agents: Intensive Vibe Coding Capstone Project

---

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Why Agents?](#why-agents)
- [Architecture](#architecture)
- [Key Concepts Demonstrated](#key-concepts-demonstrated)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [ADK CLI & Agent Skills](#adk-cli--agent-skills)
- [Security](#security)
- [Results / Impact](#results--impact)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [Demo](#demo)

---

## Problem

Finance and procurement teams manually review expense reports and vendor invoices to catch policy violations, duplicate payments, and fraud. This process is slow, error-prone, and scales poorly as transaction volume grows — costing companies both staff time and real money in missed errors that go unflagged.

Consider a mid-size company processing 500 expense reports per month. At 15 minutes of manual review per entry, that's **125 hours of finance team time** — over 3 full work weeks. And that's assuming zero errors are missed. Industry data suggests manual review catches only 60-70% of policy violations, leaving significant dollars at risk.

The core pain points are:

1. **Scale**: Manual review doesn't scale linearly with transaction volume
2. **Consistency**: Human reviewers apply rules inconsistently
3. **Auditability**: Decisions are rarely logged with full reasoning
4. **Speed**: Month-end close is delayed waiting for approvals
5. **Fraud**: Sophisticated patterns (structuring, duplicates) are hard to spot manually

---

## Solution

The AI Expense & Procurement Auditor ingests expense/invoice data, runs it through a pipeline of specialized agents that check policy compliance and detect anomalies/duplicates, and produces a clear, auditable report recommending which entries to approve, flag, or reject — along with an estimate of dollars saved or at risk.

### End-to-End Flow

1. **Ingestion**: Pull pending expenses from the ledger (via MCP)
2. **PII Redaction**: Strip employee names before any LLM sees the data
3. **Policy Check**: Verify against configurable rules (meal limits, approval thresholds, receipt requirements, disallowed categories)
4. **Duplicate/Anomaly Detection**: Cross-reference historical records for duplicates and suspicious patterns (e.g., amounts just under approval thresholds)
5. **Reporting**: Synthesize findings, restore real names, and write a Markdown report with dollar impact
6. **Human Review**: A finance team member reviews the recommendations and makes final decisions

### Why Agents?

A static rules engine could catch "meals over $75" — but it can't explain *why* that matters, adapt when policy changes, or detect novel fraud patterns it wasn't explicitly programmed for. A single monolithic LLM prompt could do all of this, but it would be a black box: no way to audit which part of the system flagged an entry, no way to swap out the duplicate-detection logic without rewriting everything, and no way to run policy checks on a different model than anomaly detection.

**The multi-agent approach wins on four dimensions:**

| Dimension | Single Script | Single LLM | Multi-Agent (This Project) |
|---|---|---|---|
| **Auditability** | Hard to trace | Black box | Every decision logged by named agent |
| **Modularity** | Tangled logic | One prompt to rule them all | Swap, upgrade, or disable agents independently |
| **Security** | All data everywhere | All data in one prompt | PII redaction at ingestion, least-privilege tools per agent |
| **Adaptability** | Rewrite code | Rewrite prompt | Update `policy_rules.json` or swap one agent |

Each agent has a narrow, well-defined responsibility. The Policy Agent doesn't know about duplicates. The Duplicate Agent doesn't know about meal limits. The Orchestrator doesn't make decisions — it just routes data. This separation of concerns makes the system more accurate, more auditable, and easier to extend than any monolithic alternative.

---

## Architecture

```
                    ┌──────────────────────┐
                    │   Orchestrator Agent  │
                    │ (routes & coordinates)│
                    └──────────┬────────────┘
                               │
       ┌───────────────────────┼───────────────────────┐
       ▼                       ▼                       ▼
┌─────────────┐       ┌──────────────────┐     ┌───────────────────┐
│ Ingestion   │       │ Policy Compliance │     │ Duplicate/Anomaly │
│ Agent       │──────▶│ Agent             │────▶│ Detection Agent    │
└─────────────┘       └──────────────────┘     └───────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Reporting Agent     │
                    │ (approve/reject       │
                    │  summary + $ impact)  │
                    └──────────┬────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      MCP Server       │
                    │ (reads/writes ledger) │
                    └──────────────────────┘
```

### Agent Responsibilities

| Agent | Responsibility | Tools (Least-Privilege) |
|---|---|---|
| **Orchestrator** | Coordinates the pipeline, passes data between agents, handles errors/retries | None (coordination only) |
| **Ingestion Agent** | Parses raw expense entries, redacts PII, stashes mapping in session state | `get_expenses` (read-only) |
| **Policy Compliance Agent** | Checks each entry against configurable rules; flags violations with reasoning | `get_expenses`, `flag_expense` |
| **Duplicate/Anomaly Detection Agent** | Cross-references historical records to catch duplicates and suspicious patterns | `get_expense_history`, `flag_expense`, `get_expenses` |
| **Reporting Agent** | Synthesizes findings into human-readable report with approve/flag/reject recommendations and estimated dollar impact | `get_expenses`, `get_audit_log` (read-only) |

### Data Flow with PII Redaction

```
Raw Data ("Jordan Pace") 
    ↓
[Ingestion Agent] → redact_employee_pii() → "EMP_001"
    ↓
[Policy Agent] sees only "EMP_001" — never the real name
    ↓
[Duplicate Agent] sees only "EMP_001" — never the real name
    ↓
[Reporting Agent] → restore_employee_pii() → "Jordan Pace" restored
    ↓
Human Reviewer sees real names, full reasoning, dollar impact
```

This is the critical security design: **real names never enter an LLM prompt**. If a model provider logs prompts, or if a prompt-injection attempt tries to exfiltrate data, employee identities are not present in what was sent to the model.

---

## Key Concepts Demonstrated

This project demonstrates the following concepts from the AI Agents course:

- [x] **Multi-agent system (ADK)** — `agents/` directory with 5 specialized `LlmAgent` instances, orchestrated by `orchestrator.py` using `Runner` and `InMemorySessionService`
- [x] **MCP Server** — `mcp_server/server.py` exposes 5 narrow tools over stdio transport; agents connect via `McpToolset` with per-agent `tool_filter` for least-privilege access
- [x] **Security features** — PII redaction (`security_utils.py`), least-privilege MCP tool filtering, environment-based secrets, human-in-the-loop approval
- [x] **Deployability** — Streamlit dashboard deployable to Streamlit Community Cloud; containerization-ready with `Dockerfile`; ADK CLI (`adk run`, `adk web`) for local testing
- [x] **Antigravity** — Proactive audit assistant widget in the dashboard that surfaces warnings without user prompting ("floating" insights)
- [x] **Agent skills** — `agent.py` root_agent exposes the full pipeline as callable skills via `adk run` and `adk web`; policy rules externalized to `policy_rules.json` for non-technical configuration

### Where to Find Each Concept

| Concept | File(s) | Line/Description |
|---|---|---|
| Multi-agent orchestration | `agents/orchestrator.py` | `Runner` pipeline with session state sharing |
| MCP Server | `mcp_server/server.py` | FastMCP with 5 tools, no raw SQL exposure |
| MCP Client connection | `agents/mcp_connection.py` | `McpToolset` with `StdioConnectionParams` |
| PII Redaction | `agents/security_utils.py` | `redact_employee_pii()` / `restore_employee_pii()` |
| Least-privilege tool filtering | `agents/ingestion_agent.py`, `policy_agent.py`, etc. | Each agent gets only the tools it needs |
| Human-in-the-Loop | `dashboard/app.py` | Dashboard shows recommendations; human approves |
| Antigravity | `dashboard/app.py` | `render_antigravity_widget()` — proactive warnings |
| Agent skills (ADK CLI) | `agent.py` | `root_agent` with tools for `adk run` / `adk web` |
| Configurable rules | `data/policy_rules.json` | JSON config editable from dashboard UI |
| Audit trail | `mcp_server/server.py` | Append-only `audit_log` table |

---

## Tech Stack

- **Agent Framework:** Google ADK (`google-adk`)
- **MCP:** Python MCP SDK (`mcp`) with FastMCP server
- **LLM:** Google Gemini 2.5 Flash (`gemini-flash-latest`)
- **Data Source:** SQLite (stand-in for accounting system), seeded from `data/sample_expenses.csv`
- **Dashboard:** Streamlit with custom CSS, interactive charts, and policy configurator
- **Language:** Python 3.10+
- **Deployment:** Streamlit Community Cloud (free tier), Docker, ADK CLI (`adk run` / `adk web`)

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- A Google AI Studio API key (free tier available): [Get key here](https://aistudio.google.com/app/apikey)
- Git (for cloning)

### Installation

```bash
# Clone the repository
git clone https://github.com/Tee808-bigD/AI-Expense-Procurement-Auditor.git
cd AI-Expense-Procurement-Auditor

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and fill in your API key
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY
```

### Environment Variables

Create a `.env` file (never commit this — `.env` is in `.gitignore`):

```bash
GOOGLE_API_KEY=your_google_api_key_here
```

> 🚨 **Never commit API keys, passwords, or credentials to the repository.** All secrets are loaded via environment variables.

### Running the Project

```bash
# Step 1: Initialize the database (one-time, or use --reset for fresh demo data)
python data/db_setup.py

# Step 2: Run the agent pipeline
python agents/orchestrator.py

# Step 3: Launch the dashboard
streamlit run dashboard/app.py
```

The dashboard will open at `http://localhost:8501`.

---

## Usage

### Quick Start Demo

1. **Prepare data**: The project includes `data/sample_expenses.csv` with 25 synthetic entries including realistic violations:
   - A $168.40 meal exceeding the $75 limit (The Capital Grille)
   - A $1,200 AWS charge without pre-approval documentation
   - Duplicate $2,500 Facebook Ads entries from the same employee on the same day
   - A $42.10 office supply purchase (clean, should approve)

2. **Run the pipeline**:
   ```bash
   python agents/orchestrator.py
   ```
   This executes the full multi-agent audit:
   - Ingestion Agent retrieves and redacts 25 entries
   - Policy Agent flags 4 violations based on `policy_rules.json`
   - Duplicate Agent catches 1 duplicate submission
   - Reporting Agent generates `output/report.md` with dollar impact

3. **Review in the dashboard**:
   ```bash
   streamlit run dashboard/app.py
   ```
   - See KPIs: 25 total, 4 approved, 5 flagged, **$6,758.39 at risk**
   - Browse the Full Ledger with status/department/category filters
   - Inspect Flagged Entries with reasoning
   - Review the Audit Trail — every agent decision logged with timestamp
   - Check Analytics for visual breakdowns
   - Use the **Policy Configurator** to adjust thresholds and re-run

4. **Check the Proactive Assistant**: The dashboard's 🪶 Antigravity widget automatically surfaces concerns — e.g., "2 high-value flagged entries require immediate review" — without you asking.

### Adapting to Your Data

To use your own expense data:

1. Replace `data/sample_expenses.csv` with your data (same columns: `entry_id,employee,department,vendor,category,amount,date,has_receipt,notes`)
2. Adjust `data/policy_rules.json` to match your company policies
3. Or use the **Policy Configurator** tab in the dashboard to edit rules live
4. Re-run `python agents/orchestrator.py`

---

## ADK CLI & Agent Skills

This project follows the official ADK quickstart pattern and supports the `adk` CLI for development and testing.

### Quickstart

```bash
# Install ADK
pip install google-adk

# Run the agent interactively in terminal
adk run .

# Or launch the ADK web dev UI
adk web --port 8000
```

### What You Can Do

| Command | What Happens |
|---|---|
| `adk run .` | Interactive chat in terminal. Type "Run a full audit" and the agent executes the pipeline |
| `adk web --port 8000` | Browser UI at http://localhost:8000. Select "expense_auditor" and chat |

### Agent Skills Exposed

The `root_agent` in `agent.py` exposes three skills:

1. **`run_full_audit_tool`** — Triggers the complete 4-agent pipeline (~1 minute)
2. **`get_dashboard_metrics`** — Returns KPIs instantly from the database
3. **`get_flagged_entries`** — Lists all flagged/rejected entries with reasoning

This means **anyone on the finance team can run audits from the terminal without writing code** — just type natural language requests and the agent routes to the correct skill.

### Why This Matters

This demonstrates **Agent Skills** — one of the 6 key evaluation concepts. The pipeline isn't just code; it's a **skill** that the agent can invoke, compose, and expose through multiple interfaces (CLI, web UI, dashboard). This is the agentic pattern that distinguishes a script from an agent system.

See [ADK_CLI_GUIDE.md](ADK_CLI_GUIDE.md) for detailed documentation.

---

## Security

This project follows defense-in-depth security practices:

### PII Redaction

Employee names, card numbers, and other personal identifiers are **redacted before being sent to any LLM** (`redact_employee_pii()` in `agents/security_utils.py`). Only anonymous tokens (e.g., `EMP_001`) enter model prompts. The mapping is held in local session state and used to restore real names only in the final human-facing report. This means:

- If an LLM provider logs prompts, employee identities are not present
- If a prompt-injection attempt tries to exfiltrate data through reasoning traces, no PII is exposed
- The redaction is deterministic Python code, not model-dependent

### Least-Privilege MCP Access

The MCP server exposes only 5 specific operations — no raw SQL, no full table access. Each agent receives only the subset of tools it needs:

| Agent | Tools Granted | Tools NOT Granted |
|---|---|---|
| Ingestion | `get_expenses` (read) | `flag_expense`, `write_audit_entry` |
| Policy | `get_expenses`, `flag_expense` | `get_expense_history`, `write_audit_entry` |
| Duplicate | `get_expense_history`, `flag_expense`, `get_expenses` | `write_audit_entry` |
| Reporting | `get_expenses`, `get_audit_log` (read) | `flag_expense`, `write_audit_entry` |

This bounds the blast radius if a prompt injection or model error produces an unintended tool call.

### No Hardcoded Secrets

All credentials are loaded from environment variables. `.env` is in `.gitignore`. The repository contains no API keys, no database passwords, no service account credentials.

### Human-in-the-Loop

The system produces **recommendations only**. A human finance reviewer must explicitly approve any action before it's finalized. The dashboard clearly labels every entry as "approved" (by agent recommendation) or "flagged" (requires human review). No agent can auto-approve expenses or transfer funds.

### Append-Only Audit Log

Every decision by every agent is logged to the `audit_log` table with:
- `entry_id`: Which expense entry
- `agent_name`: Which agent made the decision
- `decision`: approved / flagged / rejected
- `reasoning`: Human-readable explanation
- `timestamp`: When the decision was made

This log is never overwritten or deleted. It satisfies compliance requirements for financial audit trails.

---

## Results / Impact

Based on the demo dataset of 25 expense entries:

| Metric | Result |
|---|---|
| **Entries processed** | 25 |
| **Violations flagged** | 4 (meal limit exceeded, approval threshold exceeded, disallowed category, missing receipt) |
| **Duplicates caught** | 1 (duplicate $2,500 Facebook Ads submission) |
| **Estimated $ impact** | **$6,758.39** caught and flagged for review |
| **Estimated time saved** | **6.25 hours** (25 entries × 15 min manual review = 375 min = 6.25 hrs) |

### Business Value Translation

At scale, this system delivers:

- **Time**: 6.25 hours saved on 25 entries → **~125 hours/month** for a 500-entry pipeline
- **Money**: $6,758.39 caught in 25 entries → extrapolated to a 500-entry month, that's **~$135,167/month** in flagged-at-risk spend
- **Compliance**: Every decision is auditable, traceable, and explainable — critical for SOX, internal audit, and external review
- **Consistency**: Agents apply the same rules every time, eliminating reviewer bias and fatigue

---

## Project Structure

```
AI-Expense-Procurement-Auditor/
├── README.md                          # This file
├── .env.example                       # Template for environment variables
├── .gitignore                         # Prevents committing secrets
├── requirements.txt                   # Python dependencies
├── agent.py                           # ADK root_agent (for adk run / adk web)
├── ADK_CLI_GUIDE.md                   # ADK CLI usage documentation
├── agents/
│   ├── __init__.py                    # Package init for ADK CLI
│   ├── orchestrator.py                # Pipeline coordinator (ADK Runner)
│   ├── ingestion_agent.py             # Data retrieval + PII redaction
│   ├── policy_agent.py                # Policy compliance checking
│   ├── duplicate_agent.py             # Duplicate/anomaly detection
│   ├── reporting_agent.py           # Final report generation
│   ├── mcp_connection.py            # MCP client (stdio transport)
│   └── security_utils.py              # PII redaction / restoration
├── mcp_server/
│   └── server.py                      # FastMCP server (5 narrow tools)
├── data/
│   ├── sample_expenses.csv            # 25 synthetic demo entries
│   ├── db_setup.py                    # SQLite initialization
│   └── policy_rules.json              # Configurable policy thresholds
├── dashboard/
│   └── app.py                         # Streamlit dashboard (KPIs, charts, configurator, antigravity)
├── output/
│   └── report.md                      # Generated audit report (created at runtime)
└── docs/
    └── architecture_diagram.png       # Visual architecture diagram
```

---

## Future Improvements

- **Real accounting system integrations**: QuickBooks, NetSuite, SAP Concur APIs
- **OCR-based receipt ingestion**: Upload scanned/photographed receipts, extract data with vision models
- **Learned fraud patterns**: Train anomaly detection on historical data rather than rule-based thresholds
- **Email notifications**: Alert managers when high-value entries are flagged
- **Role-based dashboard views**: Different UIs for finance reviewers, managers, and auditors
- **Slack/Teams integration**: Push flag alerts to company chat for faster response

---

## Demo

- 📹 **Video:** [YouTube Demo — 5 min walkthrough](https://youtube.com/your-video-link) *(TODO: replace with actual link)*
- 🔗 **Live Project:** [Streamlit Cloud Deployment](https://your-app-name.streamlit.app) *(TODO: replace with actual link)*
- 💻 **Code:** [github.com/Tee808-bigD/AI-Expense-Procurement-Auditor](https://github.com/Tee808-bigD/AI-Expense-Procurement-Auditor)

---

*Built as part of the [AI Agents: Intensive Vibe Coding Capstone Project](https://kaggle.com/competitions/vibecoding-agents-capstone-project), Kaggle, 2026.*

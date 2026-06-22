# AI Expense & Procurement Auditor

> A multi-agent system that automatically reviews expense reports and invoices, catches policy violations and duplicate payments, and produces an audit-ready summary for finance teams.

**Track:** Agents for Business
**Built for:** Kaggle's AI Agents: Intensive Vibe Coding Capstone Project

---

## Table of Contents

- [Problem](#problem)
- [Solution](#solution)
- [Architecture](#architecture)
- [Key Concepts Demonstrated](#key-concepts-demonstrated)
- [Tech Stack](#tech-stack)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Security](#security)
- [Results / Impact](#results--impact)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [Demo](#demo)

---

## Problem

<!--
TODO: 2-3 paragraphs. Cover:
- What pain point does manual expense/invoice review cause? (time cost, error rate, fraud risk)
- Quantify if possible (e.g., "finance teams spend X hours/month reviewing expense reports manually")
- Why does this matter for businesses specifically (ties to "cost or revenue on the line")
-->

Finance and procurement teams manually review expense reports and vendor invoices to catch policy violations, duplicate payments, and fraud. This process is slow, error-prone, and scales poorly as transaction volume grows — costing companies both staff time and real money in missed errors that go unflagged.

## Solution

<!--
TODO: Describe your system at a high level — what it does end-to-end, and why an agentic approach
(vs. a simple rules engine or script) is the right fit. Emphasize reasoning, multi-step
investigation, and adaptability as the "why agents" argument.
-->

The AI Expense & Procurement Auditor ingests expense/invoice data, runs it through a pipeline of specialized agents that check policy compliance and detect anomalies/duplicates, and produces a clear, auditable report recommending which entries to approve, flag, or reject — along with an estimate of dollars saved or at risk.

### Why Agents?

<!-- TODO: Why is this a multi-agent problem rather than one big LLM call or a static script?
Suggested angle: each agent has a narrow, well-defined responsibility (parsing, policy-checking,
anomaly detection, reporting) which makes the system more accurate, more auditable, and easier
to extend than a single monolithic prompt. -->

## Architecture

![Architecture Diagram](docs/architecture_diagram.png)

<!-- TODO: Insert your architecture diagram image once created -->

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

| Agent | Responsibility |
|---|---|
| **Orchestrator** | Coordinates the pipeline, passes data between agents, handles errors/retries |
| **Ingestion Agent** | Parses raw expense/invoice entries into structured fields (vendor, amount, date, category, employee) |
| **Policy Compliance Agent** | Checks each entry against configurable company policy rules; flags violations with reasoning |
| **Duplicate/Anomaly Detection Agent** | Cross-references historical records (via MCP) to catch duplicate submissions and suspicious patterns |
| **Reporting Agent** | Synthesizes findings into a human-readable report with approve/flag/reject recommendations and estimated dollar impact |

## Key Concepts Demonstrated

This project demonstrates the following concepts from the AI Agents course:

- [ ] **Multi-agent system (ADK)** — `agents/` directory, orchestration logic in `orchestrator.py`
- [ ] **MCP Server** — `mcp_server/server.py`, exposes tools for reading/writing expense records
- [ ] **Security features** — PII redaction, least-privilege MCP access, environment-based secrets (see [Security](#security))
- [ ] **Deployability** — <!-- TODO: note containerization/deployment approach if applicable -->

<!-- TODO: check off the boxes above once implemented, and add a short note for each on where to find it -->

## Tech Stack

- **Agent Framework:** Google ADK
- **MCP:** Python MCP SDK
- **LLM:** <!-- TODO: e.g., Claude / Gemini, model name -->
- **Data Source:** <!-- TODO: e.g., Google Sheets / SQLite / CSV -->
- **Dashboard:** <!-- TODO: e.g., Streamlit -->
- **Language:** Python 3.x

## Setup Instructions

### Prerequisites

- Python 3.10+
- An API key for <!-- TODO: LLM provider -->
- <!-- TODO: any other prerequisites, e.g., Google Sheets API credentials -->

### Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd expense-auditor

# Install dependencies
pip install -r requirements.txt

# Copy environment template and fill in your own values
cp .env.example .env
```

### Environment Variables

Create a `.env` file (never commit this — see `.env.example` for the template):

```
LLM_API_KEY=your_api_key_here
DATA_SOURCE_CREDENTIALS=path_or_key_here
```

> 🚨 **Never commit API keys, passwords, or credentials to the repository.** All secrets are loaded via environment variables and `.env` is included in `.gitignore`.

### Running the Project

```bash
# Start the MCP server
python mcp_server/server.py

# Run the agent pipeline
python agents/orchestrator.py

# (Optional) Launch the dashboard
streamlit run dashboard/app.py
```

## Usage

<!-- TODO: Walk through a basic usage example, e.g.:
1. Place expense data in data/sample_expenses.csv (or connect your Sheet)
2. Run the orchestrator
3. View flagged entries and the generated report in dashboard/app.py or output/report.md
-->

## Security

This project follows these security practices:

- **PII Redaction:** Employee names, card numbers, and other personal identifiers are redacted before being sent to the LLM, and re-attached only after processing.
- **Least-Privilege Access:** The MCP server exposes only the specific read/write operations needed (e.g., specific sheet ranges), not full account access.
- **No Hardcoded Secrets:** All credentials are loaded from environment variables; `.env` is gitignored.
- **Human-in-the-Loop:** The system produces recommendations only — a human must explicitly approve any action before it's finalized.

<!-- TODO: expand with any additional security measures you implement -->

## Results / Impact

<!--
TODO: This is your "cost/revenue on the line" proof point. Fill in once you've run your demo dataset:
- How many entries processed?
- How many violations / duplicates caught?
- Estimated $ saved or at-risk identified?
- Time saved vs. manual review (estimate)?
-->

| Metric | Result |
|---|---|
| Entries processed | — |
| Violations flagged | — |
| Duplicates caught | — |
| Estimated $ impact | — |
| Estimated time saved | — |

## Project Structure

```
expense-auditor/
├── README.md
├── .env.example
├── requirements.txt
├── agents/
│   ├── orchestrator.py
│   ├── ingestion_agent.py
│   ├── policy_agent.py
│   ├── duplicate_agent.py
│   └── reporting_agent.py
├── mcp_server/
│   └── server.py
├── data/
│   └── sample_expenses.csv
├── dashboard/
│   └── app.py
└── docs/
    └── architecture_diagram.png
```

## Future Improvements

<!-- TODO: e.g., real accounting system integrations, receipt OCR, learned fraud-pattern models, etc. -->

- Integration with real accounting platforms (QuickBooks, NetSuite)
- OCR-based receipt ingestion for scanned/photographed receipts
- Configurable policy rules via admin UI rather than hardcoded rules

## Demo

- 📹 **Video:** <!-- TODO: YouTube link -->
- 🔗 **Live Project / Repo:** <!-- TODO: link -->

---

*Built as part of the [AI Agents: Intensive Vibe Coding Capstone Project](https://kaggle.com/competitions/vibecoding-agents-capstone-project), Kaggle, 2026.*

# Video Script: AI Expense & Procurement Auditor
# Target: 5 minutes | YouTube | Kaggle Capstone Submission

## [0:00 - 0:30] INTRO: Hook & Problem Statement

"Hi, I'm [Your Name], and this is my submission for the Kaggle AI Agents Capstone — Agents for Business track.

Every month, finance teams spend hundreds of hours manually reviewing expense reports. They check if a meal was over the limit, if a software purchase had approval, if someone submitted the same receipt twice. It's slow, inconsistent, and expensive.

My project solves this with a multi-agent AI system that automates the entire audit pipeline — from ingestion to final report — while keeping humans in control."

## [0:30 - 1:15] WHY AGENTS? Architecture Overview

"Why a multi-agent system instead of a single script or one big LLM prompt?

Three reasons: auditability, modularity, and security.

The Ingestion Agent pulls data and redacts employee names before ANY LLM sees them.
The Policy Agent checks against configurable rules.
The Duplicate Agent cross-references history to catch duplicates and suspicious patterns.
And the Reporting Agent synthesizes everything into a clear report with dollar impact.

Each agent has ONE job. If we need to update our fraud detection logic, we swap ONE agent.
If a regulator asks 'who flagged this entry?', we point to the exact agent and the exact reasoning.

And security: real employee names NEVER enter an LLM prompt. Only anonymous tokens like EMP_001."

## [1:15 - 2:30] LIVE DEMO: Running the Pipeline

"Let me show you the system in action. I'll run the full pipeline on 25 synthetic expense entries."

```bash
$ python agents/orchestrator.py
```

"First, the Ingestion Agent pulls 25 pending entries and redacts PII...
Now the Policy Agent checks each entry against our rules...
The Duplicate Agent is next... it caught a duplicate: two $2,500 Facebook Ads entries.
Finally, the Reporting Agent pulls the full ledger and writes the audit report."

"Here's the report: 25 entries, 4 approved, 5 flagged, $6,758.39 at risk caught."

## [2:30 - 4:00] DASHBOARD DEMO: The Full Experience

```bash
$ streamlit run dashboard/app.py
```

"At a glance: 25 entries, 4 approved, 5 flagged, $6,758.39 at risk.

Full Ledger — every entry with filters.
Flagged Entries — the $168 meal, the duplicate Facebook Ads, the AWS charge.
Audit Trail — every decision by every agent, timestamped.
Analytics — visual breakdowns.

And here's the Antigravity pattern — a proactive audit assistant that surfaces warnings WITHOUT me asking.

It automatically detected that 2 high-value flagged entries need immediate review.
It spotted a potential duplicate.
It flagged 3 entries over $100 without receipts.
And it noticed entries clustered just under our $500 approval threshold — a possible structuring pattern.

This isn't a chatbot you have to query. It's an intelligent colleague that watches your data and taps you on the shoulder when something matters.

And here's the Policy Configurator. Finance teams can adjust thresholds directly from the UI. No code changes. No deployments."

## [4:00 - 4:45] SECURITY & DEPLOYMENT

"Security is not an afterthought. PII redaction happens before any LLM sees the data.
Least-privilege tool filtering means each agent only gets the tools it needs.
And every secret is in .env, never in the repo.

For deployment, the dashboard is containerized with Docker and deployable to Streamlit Community Cloud in under 5 minutes."

## [4:45 - 5:00] CLOSING: Impact & Call to Action

"In 25 entries, this system caught $6,758 at risk and saved over 6 hours of manual review. At scale — 500 entries per month — that's $135,000 in flagged spend and 125 hours of finance team time reclaimed.

This isn't just automation. It's auditable, secure, adaptive automation that keeps humans in control.

Thank you for watching. The code is open-source at github.com/Tee808-bigD. Try the live demo, and let's build better business agents together."

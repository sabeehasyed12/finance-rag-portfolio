# Phase 7 Agent Based Analytics and Governance Workflows

## Goal

Phase 7 introduces agents that take actions instead of chatting.

The goal is to show how an analytics platform becomes an autonomous system that can:
* validate data health
* analyze financial performance
* enforce governance rules
* produce auditable artifacts

LLMs are intentionally excluded. This phase proves that most real value comes from deterministic agents, not text generation.

---

## What Was Built

A multi agent workflow that produces three concrete artifacts:
* Validation Report
* Daily Finance Insights
* Compliance Report

Each agent:
* has a single responsibility
* operates within strict data boundaries
* produces structured and inspectable output

---

## Architecture

Bronze to Silver to Gold to Platinum  
Agent Layer runs after dbt builds

Agents:
* never mutate data
* never redefine business logic
* only observe, validate, and explain

---

## Agent Configuration

**Module**  
`src/agents/config.py`

Defines a shared `AgentConfig` used by all agents.

Key fields:
* duckdb_path
* bronze_schema, silver_schema, gold_schema
* thresholds for volume change and freshness
* output paths for reports and logs

**Important nuance**  
All thresholds live in configuration, not logic. Agents are tunable without code changes.

---

## Data Validation Agent

**Module**  
`src/agents/data_validation_agent.py`

**Purpose**  
Detect pipeline breakages and data integrity issues immediately after data loads.

### Actions

**dbt Tests**
* runs `dbt test`
* captures return code and log tails only
* avoids noisy full logs

**Volume Anomaly Detection**
* checks key Gold tables
* infers date columns using `coalesce`
* compares latest day to previous day
* outputs pass, warn, fail, or skip

**Freshness Checks**
* computes max date per table
* compares against current date
* fails based on SLA threshold
* freshness is data based, not metadata based

**Output**  
`artifacts/reports/validation_report.json`

Includes:
* dbt test summary
* volume and freshness results
* rule derived likely causes
* overall status

---

## Financial Analyst Agent

**Module**  
`src/agents/financial_analyst_agent.py`

**Purpose**  
Produce a short executive style daily finance summary with clear drivers.

**Data Used**
* gold_daily_revenue

**Metrics**
* net revenue
* gross revenue
* refunded revenue
* transaction count
* refund rate
* day over day net revenue change

**Driver Detection**
* refund rate above threshold
* low transaction volume
* large revenue movement

No ML. No heuristics. No hallucination.

**Output**  
`artifacts/reports/daily_finance_insights.json`

Includes:
* headline summary
* metrics snapshot
* detected drivers
* status

---

## Compliance Agent

**Module**  
`src/agents/compliance_agent.py`

**Purpose**  
Automatically prevent PII leakage into analytics facing layers.

**Scope**
* Gold and Platinum schemas
* tables discovered dynamically

### Checks

**Column Name Inspection**
* flags exact matches like email, phone, address, name
* severity is fail
* intentionally strict

**Value Pattern Sampling**
* samples up to 200 rows
* scans for email and phone patterns
* severity is warn

Sampling avoids full scans while catching real leaks.

**Output**  
`artifacts/reports/compliance_report.json`

Includes:
* checked objects
* findings with evidence
* severity levels
* overall compliance status

---

## Workflow Orchestration

**Module**  
`src/workflows/run_phase7.py`

Execution order:
* Data Validation Agent
* Financial Analyst Agent
* Compliance Agent

Each agent:
* runs independently
* produces exactly one artifact
* has no dependency on LLM output

---

## Why No LLMs

This is deliberate.

Reasons:
* deterministic behavior
* no hallucination risk
* safe for automation
* easy debugging
* auditable outputs

LLMs are added only after correctness is proven.

---

## Key Design Principles

**Agents act, they do not chat**  
They run commands, execute SQL, evaluate rules, and write reports.

**Evidence first**  
Every decision includes raw metrics, thresholds, and observed values.

**JSON artifacts over dashboards**  
Artifacts are machine readable, diffable, versionable, and alert ready.

---

## Deliverables

* validation_report.json  
  Pipeline and data health

* daily_finance_insights.json  
  Daily business performance

* compliance_report.json  
  Governance enforcement

---

## What This Phase Proves

* Agent systems do not require LLMs to be valuable
* Most analytics automation is deterministic
* Governance and validation are first class concerns
* Analytics platforms can reason about themselves

---

# Data Quality Rules

## Purpose

This document defines the data quality rules and guarantees enforced across the analytics platform.

These rules describe what the system **promises** about the data.
They do not describe how metrics are interpreted.
They describe when data can be trusted.

This document is a primary retrieval source for questions like:
- what guarantees does this table provide
- what happens if this metric looks wrong
- where is data quality enforced

---

## Core Principles

- Data quality is enforced as early as possible
- Each layer has explicit guarantees
- Downstream layers trust upstream layers
- Violations must fail loudly
- Silent data corruption is unacceptable

---

## Bronze Layer Rules

### Intent

Bronze preserves reality exactly as received.

### Enforced Rules

- `ingestion_date` must be present
- Incremental ingestion must be deterministic
- Schema must match raw source structure

### Explicitly NOT Enforced

- Uniqueness
- Referential integrity
- Valid lifecycle transitions
- Correctness of values

### Failure Policy

- Bronze models should not fail due to data content
- Failures only occur for structural issues such as missing files or unreadable schemas

---

## Silver Layer Rules

### Intent

Silver enforces correctness and structural validity.

### Entity Integrity

- One row per business entity
- Deterministic deduplication rules
- Late arriving updates reconciled correctly

### Enforced Tests

Typical schema tests include:
- primary key uniqueness
- primary key not null
- valid enum values for status fields
- referential integrity between entities

### Examples

- `customer_id` is unique and not null in `silver_customers`
- `account_id` references a valid customer
- transaction statuses belong to a controlled set

### Failure Policy

- Silver model failures block downstream models
- Any failed test indicates broken correctness
- Issues must be fixed in Silver or Bronze, never patched in Gold

---

## Gold Layer Rules

### Intent

Gold encodes business logic and produces metrics.

### Metric Stability Rules

- Metrics must be deterministic
- Metrics must be reproducible
- Metrics must use locked business definitions
- Aggregation grains must be explicit and enforced

### Enforced Tests

- Grain uniqueness tests
- Not null constraints on time dimensions
- Ratio metrics protected against division by zero

### Examples

- `month` is unique in `gold_monthly_revenue`
- `date` is unique in daily rate tables
- Net revenue is never null

### Failure Policy

- Gold failures block reporting and dashboards
- Fixes belong upstream unless business logic itself is incorrect
- Changes to metric logic require documentation updates

---

## Platinum Layer Rules

### Intent

Platinum contextualizes metrics for decision making.

### Structural Guarantees

- One row per declared grain
- Time dimensions are complete and valid
- Metric names are explicit and stable

### Enforced Tests

- Uniqueness of date or month
- Not null checks on key dimensions
- Consistent metric naming for anomaly detection

### Examples

- Daily scorecard date is unique and not null
- Monthly scorecard month is unique and not null
- Anomaly records always include date and metric name

### Failure Policy

- Platinum failures indicate upstream instability
- Platinum does not correct data
- Any failure requires investigation in Gold or Silver

---

## Cross Layer Expectations

- Bronze is immutable
- Silver is corrective
- Gold is interpretive
- Platinum is explanatory

If data quality fails in a downstream layer,
the root cause is always upstream.

---

## Why This Document Matters

Data quality rules define trust boundaries.

Without explicit guarantees:
- dashboards lie
- alerts misfire
- AI systems hallucinate certainty

This document is the contract that prevents that.

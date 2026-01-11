# Incident Runbooks

## Purpose

This document defines standard investigation and remediation steps for common analytics incidents.

These runbooks exist so that:
- issues are diagnosed consistently
- fixes happen in the correct layer
- dashboards are not patched blindly
- AI systems can suggest correct actions

This is operational truth, not theory.

---

## General Incident Rules

1. Do not fix symptoms in downstream layers
2. Always identify the lowest broken layer
3. Validate assumptions with data, not dashboards
4. Never hot fix Gold or Platinum logic without review
5. Document root cause and resolution

---

## Incident: Revenue Suddenly Drops to Zero

### Symptoms

- Daily revenue shows zero
- Executive scorecard flags anomaly
- No upstream deploy expected

### Investigation Steps

1. Check `platinum_finance_exec_scorecard_daily`
   - Confirm date exists
   - Confirm metrics are null or zero

2. Check `gold_daily_revenue`
   - Validate rows exist for the date
   - Confirm `final_status = paid` records exist

3. Check `gold_transaction_facts`
   - Count paid transactions for the date
   - Inspect refunded and net amounts

4. Check Silver transactions
   - Validate transaction ingestion
   - Look for status normalization failures

5. Check Bronze ingestion
   - Confirm raw files arrived
   - Validate ingestion_date filtering

### Likely Root Causes

- Missing or late raw data
- Status normalization regression
- Upstream ingestion failure

### Resolution

- Fix ingestion or Silver logic
- Backfill affected dates
- Rebuild Gold and Platinum

Do not manually override revenue values.

---

## Incident: Refund Rate Spikes Abnormally

### Symptoms

- Refund rate exceeds historical range
- Anomaly flag raised
- Revenue still present

### Investigation Steps

1. Check `gold_refund_rate`
   - Validate numerator and denominator
   - Check for division by zero protection

2. Inspect `gold_transaction_facts`
   - Review refunded_amount distribution
   - Identify large refund events

3. Check `silver_refunds`
   - Validate refund linkage to transactions
   - Look for duplicate refund records

4. Check Bronze refunds
   - Confirm duplicate or late arriving refunds

### Likely Root Causes

- Duplicate refund ingestion
- Legitimate large refund batch
- Incorrect refund normalization

### Resolution

- Deduplicate refunds in Silver
- Backfill affected dates
- Document if refund behavior is expected

Do not suppress refund metrics.

---

## Incident: Failed Payment Rate Jumps

### Symptoms

- Failed payment rate increases sharply
- Revenue may or may not be impacted

### Investigation Steps

1. Check `gold_failed_payment_rate`
   - Validate counts and attempts

2. Inspect `silver_payments`
   - Review payment_status distribution
   - Check retry sequencing

3. Check Bronze payments
   - Confirm payment gateway data completeness

### Likely Root Causes

- External payment provider issues
- Retry logic changes
- Status mapping regressions

### Resolution

- Validate external provider incident
- Correct status normalization if needed
- Backfill Silver and downstream layers

---

## Incident: Churn Appears Inflated

### Symptoms

- Sudden increase in churn count
- Retention metrics degrade

### Investigation Steps

1. Check `gold_churn`
   - Review churn_date distribution
   - Inspect churn_type if present

2. Inspect `silver_subscriptions`
   - Validate lifecycle ordering
   - Look for duplicate cancellation events

3. Check Bronze subscriptions
   - Confirm raw lifecycle event volume

### Likely Root Causes

- Duplicate cancellation events
- Subscription lifecycle ordering bug
- Legitimate churn event batch

### Resolution

- Fix lifecycle ordering in Silver
- Backfill churn model
- Validate downstream customer flags

Do not redefine churn to hide increases.

---

## Incident: Platinum Anomaly Flags Incorrectly

### Symptoms

- Anomalies triggered without visible issue
- Metric values appear normal

### Investigation Steps

1. Inspect `platinum_anomalies_daily`
   - Review z score and baseline
   - Check rolling window completeness

2. Validate Gold metric stability
   - Ensure no partial days
   - Check backfill alignment

3. Confirm historical window integrity
   - Look for missing days

### Likely Root Causes

- Partial data for current day
- Missing historical baseline
- Backfill misalignment

### Resolution

- Exclude partial days from anomaly detection
- Recompute rolling baselines
- Backfill affected metrics

---

## Where Fixes Belong

- Ingestion issues → Bronze
- Incorrect records → Silver
- Wrong business logic → Gold
- Misleading context → Platinum

If the fix feels easier downstream, it is probably wrong.

---

## Why This Document Matters

When incidents happen:
- panic makes people dangerous
- dashboards lie without context
- humans guess


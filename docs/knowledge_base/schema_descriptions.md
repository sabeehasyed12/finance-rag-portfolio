# Schema Descriptions

## Purpose

This document describes the schemas, grains, and guarantees of all models across Bronze, Silver, Gold, and Platinum layers.

It exists to answer retrieval questions such as:
- what does this table represent
- what is the grain of this model
- which layer should I query
- where does this metric come from
- what guarantees does this table provide

This document is intentionally descriptive and explicit.

---

## Bronze Layer Schemas

### bronze_customers

#### Layer Intent

Raw ingestion of customer records exactly as received.

#### Grain

One row per raw customer record  
Duplicates allowed

#### Source

`data/raw/customers.csv`

#### Key Fields

- `customer_id`
- `full_name`
- `email`
- `phone`
- `address`
- `device_id`
- `created_at`
- `ingestion_date`
- `bronze_loaded_at`

#### Guarantees

- No deduplication
- No normalization
- Late arriving records preserved
- PII preserved in raw form

#### Not Guaranteed

- Uniqueness of `customer_id`
- Valid formatting of identity fields
- Current customer state

---

### bronze_accounts

#### Layer Intent

Raw ingestion of financial account records.

#### Grain

One row per raw account record  
Duplicates allowed

#### Source

`data/raw/accounts.csv`

#### Key Fields

- `account_id`
- `customer_id`
- `status`
- `opened_at`
- `closed_at`
- `ingestion_date`
- `bronze_loaded_at`

#### Guarantees

- Full lifecycle history preserved
- Late arriving account closures preserved

#### Not Guaranteed

- Valid lifecycle transitions
- One row per account
- Current account status

---

### bronze_transactions

#### Layer Intent

Raw ingestion of transaction events.

#### Grain

One row per raw transaction record  
Duplicates allowed

#### Source

`data/raw/transactions.csv`

#### Key Fields

- `transaction_id`
- `account_id`
- `customer_id`
- `amount`
- `currency`
- `status`
- `transaction_ts`
- `ingestion_date`
- `bronze_loaded_at`

#### Guarantees

- All transaction attempts preserved
- Failed and pending transactions included
- Late arriving updates preserved

#### Not Guaranteed

- Final transaction outcome
- Deduplication
- Revenue correctness

---

### bronze_payments

#### Layer Intent

Raw ingestion of payment attempts.

#### Grain

One row per payment attempt

#### Source

`data/raw/payments.csv`

#### Key Fields

- `payment_id`
- `transaction_id`
- `attempt_number`
- `payment_status`
- `payment_ts`
- `ingestion_date`
- `bronze_loaded_at`

#### Guarantees

- Retry attempts preserved
- Ordering information retained

#### Not Guaranteed

- Final payment outcome
- Reconciliation with transactions

---

### bronze_subscriptions

#### Layer Intent

Raw ingestion of subscription lifecycle events.

#### Grain

One row per lifecycle event

#### Source

`data/raw/subscriptions.csv`

#### Key Fields

- `subscription_id`
- `customer_id`
- `plan`
- `subscription_status`
- `event_ts`
- `ingestion_date`
- `bronze_loaded_at`

#### Guarantees

- All lifecycle events preserved
- Overlapping and conflicting states allowed

#### Not Guaranteed

- Ordered lifecycle
- Active subscription state
- Churn inference

---

### bronze_refunds

#### Layer Intent

Raw ingestion of refund events.

#### Grain

One row per refund record

#### Source

`data/raw/refunds.csv`

#### Key Fields

- `refund_id`
- `transaction_id`
- `refund_amount`
- `refund_ts`
- `ingestion_date`
- `bronze_loaded_at`

#### Guarantees

- Partial and full refunds preserved
- Late arriving refunds preserved

#### Not Guaranteed

- Revenue netting
- Validation against payment outcomes

---

## Silver Layer Schemas

### silver_customers

#### Layer Intent

Canonical customer entity table.

#### Grain

One row per customer

#### Source

`bronze_customers`

#### Guarantees

- One row per `customer_id`
- Latest valid record retained
- Standardized identity fields

#### Not Guaranteed

- Business segmentation
- Customer value metrics

---

### silver_accounts

#### Layer Intent

Canonical account entity table.

#### Grain

One row per account

#### Source

`bronze_accounts`

#### Guarantees

- One row per `account_id`
- Normalized lifecycle status
- Valid state transitions

---

### silver_transactions

#### Layer Intent

Canonical transaction entity table.

#### Grain

One row per transaction

#### Source

`bronze_transactions`

#### Guarantees

- One row per `transaction_id`
- Normalized transaction status
- Valid account linkage

---

### silver_payments

#### Layer Intent

Resolved payment outcomes.

#### Grain

One row per transaction

#### Source

`bronze_payments`

#### Guarantees

- Final payment outcome per transaction
- Clear success or failure semantics

---

### silver_subscriptions

#### Layer Intent

Ordered subscription lifecycle table.

#### Grain

One row per subscription per lifecycle state

#### Source

`bronze_subscriptions`

#### Guarantees

- Valid lifecycle ordering
- Correct handling of upgrades and downgrades
- One active state per subscription

---

### silver_refunds

#### Layer Intent

Validated refund records.

#### Grain

One row per refund event

#### Source

`bronze_refunds`

#### Guarantees

- Valid transaction linkage
- Normalized refund types

---

## Gold Layer Schemas

### gold_transaction_facts

#### Layer Intent

Canonical transactional fact table with resolved financial outcomes.

#### Grain

One row per transaction

#### Source

Silver transactional models

#### Guarantees

- Final transaction outcome
- Net amount correctness
- Refund reconciliation

---

### gold_daily_revenue

#### Layer Intent

Daily revenue metrics for trend analysis.

#### Grain

One row per calendar day

#### Guarantees

- Net revenue after refunds
- Paid transactions only

---

### gold_monthly_revenue

#### Layer Intent

Monthly rollup of daily revenue.

#### Grain

One row per month

#### Guarantees

- Unique month
- Canonical monthly revenue summary

---

### gold_mrr

#### Layer Intent

Monthly recurring revenue from subscriptions.

#### Grain

One row per subscription per month

---

### gold_arr

#### Layer Intent

Annual recurring revenue derived from MRR.

#### Grain

One row per month

#### Definition

ARR = MRR * 12

---

### gold_refund_rate

#### Layer Intent

Daily refund rate metric.

#### Grain

One row per day

#### Definition

Refund rate = refunded_amount / paid_amount

---

### gold_failed_payment_rate

#### Layer Intent

Daily failed payment rate metric.

#### Grain

One row per day

#### Definition

Failed payment rate = failed_count / attempt_count

---

### gold_cohort_retention

#### Layer Intent

Cohort retention analysis by months since first paid month.

#### Grain

One row per cohort per month offset

---

## Platinum Layer Schemas

### platinum_finance_exec_scorecard_daily

#### Layer Intent

Daily executive finance scorecard.

#### Grain

One row per day

#### Guarantees

- Revenue quality metrics
- Rolling averages
- Week over week change

---

### platinum_finance_exec_scorecard_monthly

#### Layer Intent

Monthly executive finance scorecard.

#### Grain

One row per month

#### Guarantees

- Revenue and ARR alignment
- Growth momentum indicators

---

### platinum_anomalies_daily

#### Layer Intent

Automated anomaly detection table.

#### Grain

One row per day per metric

#### Guarantees

- Deterministic anomaly flags
- Human readable explanations

---

## Layer Boundary Reminder

- Bronze answers: what arrived
- Silver answers: what is correct
- Gold answers: what it means
- Platinum answers: what to do about it

No layer violates the responsibility of another.

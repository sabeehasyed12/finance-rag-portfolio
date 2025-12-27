# Silver Layer Documentation

## Purpose of the Silver Layer

The Silver layer represents the **cleansing, standardization, and correctness boundary** of the analytics platform.

Its responsibility is to:
- deduplicate raw records
- enforce entity level correctness
- normalize schemas and values
- resolve late arriving updates
- apply basic governance rules
- prepare data for analytical consumption

The Silver layer is where data becomes **trustworthy but not yet business aggregated**.

All models in this layer:
- read exclusively from Bronze models
- apply deterministic transformations
- enforce one row per business entity
- handle late arriving data correctly
- remain auditable back to Bronze

---

## What Silver Is and Is Not

### Silver IS
- clean
- deduplicated
- schema consistent
- entity aligned
- ready for joins
- suitable for downstream analytics

### Silver IS NOT
- a reporting layer
- a metrics layer
- a KPI layer
- a business logic layer
- an interpretation layer

Those responsibilities belong to Gold.

---

## Common Silver Patterns

### Source of Truth
All Silver models read only from Bronze models.

No Silver model reads directly from raw files.

---

### Deduplication Strategy

Deduplication is performed using deterministic rules based on:
- primary business keys
- event timestamps
- ingestion metadata

Latest valid records are retained per entity.

Late arriving updates are reconciled during incremental runs.

---

### Normalization and Standardization

Silver models normalize:
- status fields
- lifecycle states
- date and timestamp formats
- boolean flags
- enumerated values

PII may still exist in Silver but is standardized and constrained.
Masking is deferred to Gold or governed marts.

---

### Incremental Processing

Silver models are incremental and use:
- entity level watermarks
- update timestamps
- ingestion metadata from Bronze

Each model ensures idempotent reprocessing.

---

## Silver Models Overview

## silver_customers

### Source
`bronze_customers`

### Purpose
Produce a single canonical customer record.

### Transformations Applied
- Deduplication by `customer_id`
- Latest record selection using update timestamps
- Normalization of identity fields
- Standardization of email and phone formats

### Guarantees
- One row per `customer_id`
- Stable customer identity
- Deterministic updates on late arrivals

### What is NOT Done
- No behavioral metrics
- No customer segmentation
- No lifetime value calculations


## silver_accounts

### Source
`bronze_accounts`

### Purpose
Produce a clean and current view of financial accounts.

### Transformations Applied
- Deduplication by `account_id`
- Account status normalization
- Lifecycle enforcement
- Filtering of invalid transitions

### Guarantees
- One row per `account_id`
- Valid account lifecycle state
- Consistent status semantics

### What is NOT Done
- No joins to transactions
- No balance calculations
- No account level metrics


## silver_transactions

### Source
`bronze_transactions`

### Purpose
Produce a clean transactional fact table.

### Transformations Applied
- Deduplication by `transaction_id`
- Filtering of invalid records
- Status normalization
- Timestamp correction

### Guarantees
- One row per transaction
- Consistent transaction status
- Valid account references

### What is NOT Done
- No revenue attribution
- No fraud detection
- No aggregation


## silver_payments

### Source
`bronze_payments`

### Purpose
Resolve payment attempts into final outcomes.

### Transformations Applied
- Grouping by `transaction_id`
- Ordering by `attempt_number`
- Selection of final payment outcome
- Status normalization

### Guarantees
- One payment outcome per transaction
- Clear success or failure semantics

### What is NOT Done
- No revenue recognition
- No settlement logic
- No financial aggregation


## silver_subscriptions

### Source
`bronze_subscriptions`

### Purpose
Produce an ordered subscription lifecycle table.

### Transformations Applied
- Deduplication by `subscription_id`
- Lifecycle event ordering
- State transition enforcement
- Plan normalization

### Guarantees
- One active lifecycle state per subscription
- Correct handling of upgrades and downgrades

### What is NOT Done
- No churn metrics
- No revenue calculations
- No cohorting


## silver_refunds

### Source
`bronze_refunds`

### Purpose
Produce validated refund records.

### Transformations Applied
- Deduplication by `refund_id`
- Validation against transactions
- Refund type normalization

### Guarantees
- One row per refund event
- Valid transaction linkage

### What is NOT Done
- No revenue netting
- No aggregation
- No financial reporting


## Why This Layer Exists

The Silver layer exists to answer:

**“What is correct, current, and structurally valid?”**

It does not answer:
- “What does this mean for the business?”
- “How much revenue did we make?”
- “What KPIs should leadership see?”

Those questions are intentionally deferred to the Gold layer.

---

## Downstream Expectations

- Gold models assume Silver data is correct and complete
- All joins should originate from Silver
- Silver is the contract layer between ingestion and analytics
- Any data quality issues discovered in Gold should be traced back to Silver or Bronze

Silver is where chaos becomes order.
Gold is where order becomes insight.

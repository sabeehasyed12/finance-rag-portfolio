# Bronze Layer Documentation 
Purpose of the Bronze Layer The Bronze layer represents the **raw ingestion boundary** of the analytics platform. Its responsibility is to: 
- ingest raw data exactly as received
- preserve duplicates and late arriving data
- apply **no business logic**
- apply **no deduplication**
- expose raw fields (including PII)
- make ingestion behavior observable and repeatable

The Bronze layer is intentionally **not clean**. It exists to provide traceability, auditability, and a stable foundation for downstream transformations. 
All models in this layer are: 
- incremental
- sourced directly from raw CSV files
- filtered only by ingestion metadata
- schema-aligned but not semantically corrected  
## Common Bronze Patterns 
### Data Sources All Bronze models read directly from raw CSV files using DuckDB’s read_csv_auto() function. 
Raw files live under: data/raw/ Each Bronze model corresponds to exactly one raw file. 
### Incremental Ingestion Strategy All Bronze models use an incremental ingestion strategy based on ingestion_date. 
The following macro is applied consistently across all Bronze models:
sql
{{ incremental_ingestion_filter("ingestion_date") }}


# Bronze Models Overview

## bronze_customers

### Source
`data/raw/customers.csv`

### Purpose
Ingest raw customer records exactly as received.

### Transformations Applied
- Column selection and ordering
- Incremental ingestion filtering by `ingestion_date`
- Metadata column `bronze_loaded_at` added

### What is Preserved
- Duplicate customer records
- Late arriving updates
- Raw PII fields:
  - `full_name`
  - `email`
  - `phone`
  - `address`
- Shared device identifiers and addresses

### What is NOT Done
- No deduplication by `customer_id`
- No PII masking
- No normalization of identity fields


## bronze_accounts

### Source
`data/raw/accounts.csv`

### Purpose
Ingest raw financial account records.

### Transformations Applied
- Column selection and ordering
- Incremental ingestion filtering by `ingestion_date`
- Metadata column `bronze_loaded_at` added

### What is Preserved
- Multiple records per `account_id`
- Late arriving account closures
- Raw account status values
- Closed accounts with downstream activity

### What is NOT Done
- No status normalization
- No enforcement of account lifecycle rules
- No joins to customers or transactions


## bronze_transactions

### Source
`data/raw/transactions.csv`

### Purpose
Ingest raw transaction events exactly as generated.

### Transformations Applied
- Column selection and ordering
- Incremental ingestion filtering by `ingestion_date`
- Metadata column `bronze_loaded_at` added

### What is Preserved
- Duplicate transactions
- Failed and pending transactions
- Late arriving transaction updates
- Transactions on closed accounts
- Raw card information (last four digits)

### What is NOT Done
- No deduplication
- No reconciliation with payments
- No revenue calculations
- No fraud or anomaly detection


## bronze_payments

### Source
`data/raw/payments.csv`

### Purpose
Ingest raw payment attempts associated with transactions.

### Transformations Applied
- Column selection and ordering
- Incremental ingestion filtering by `ingestion_date`
- Metadata column `bronze_loaded_at` added

### What is Preserved
- Multiple payment attempts per transaction
- Failed and successful attempts
- Retry sequencing via `attempt_number`

### What is NOT Done
- No collapsing of retries
- No determination of final payment outcome
- No reconciliation with transaction status


## bronze_subscriptions

### Source
`data/raw/subscriptions.csv`

### Purpose
Ingest raw subscription lifecycle events.

### Transformations Applied
- Column selection and ordering
- Incremental ingestion filtering by `ingestion_date`
- Metadata column `bronze_loaded_at` added

### What is Preserved
- Multiple lifecycle records per subscription
- Overlapping subscriptions
- Upgrades, downgrades, pauses, and cancellations

### What is NOT Done
- No lifecycle ordering
- No churn inference
- No plan normalization


## bronze_refunds

### Source
`data/raw/refunds.csv`

### Purpose
Ingest raw refund events linked to transactions.

### Transformations Applied
- Column selection and ordering
- Incremental ingestion filtering by `ingestion_date`
- Metadata column `bronze_loaded_at` added

### What is Preserved
- Duplicate refund events
- Partial and full refunds
- Late arriving refunds

### What is NOT Done
- No netting against revenue
- No validation against payment status
- No aggregation


## Why This Layer Exists

The Bronze layer exists to answer one question:

**“What did we receive, and when did we receive it?”**

It does not answer:
- “What is correct?”
- “What is final?”
- “What should be reported?”

Those questions are intentionally deferred to the Silver and Gold layers.


## Downstream Expectations

- Silver models handle deduplication, governance, and correctness
- Gold models produce metrics, KPIs, and business meaning
- Bronze remains immutable and auditable

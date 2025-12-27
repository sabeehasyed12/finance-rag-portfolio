# Gold Layer Documentation

## Purpose of the Gold Layer

The Gold layer represents the business consumption and analytics boundary of the platform.

Its responsibility is to:
1. express business meaning
2. compute metrics and KPIs
3. apply business rules and assumptions
4. aggregate clean Silver data into analytical models
5. provide stable tables for reporting and decision making

The Gold layer is where data becomes opinionated.

Unlike Bronze and Silver, Gold models intentionally encode business logic.
This logic is explicit, documented, and expected to evolve with the business.

All models in this layer:
1. read exclusively from Silver models
2. are fully deduplicated and validated upstream
3. are aggregated or derived
4. are designed for analytics, dashboards, and downstream consumption
5. trade raw detail for clarity and correctness

---

## Locked Business Definitions

The following definitions are authoritative and must be used consistently across all Gold models, dashboards, and analyses.

### Active Customer
A customer is considered active if they have at least one account with:
normalized_status = active

### Paying Customer
A customer is considered paying if they have at least one transaction with:
final_status = paid

### Refunded Customer
A customer is considered refunded if they have at least one transaction with:
final_status = refunded

### Churned Customer
A customer is considered churned if they have at least one subscription with:
subscription_status = canceled

These definitions are intentionally simple, deterministic, and auditable.
Any refinement or alternative interpretation must be explicitly versioned and documented.

---

## What Gold Is and Is Not

### Gold IS
1. business aligned
2. metric driven
3. aggregated
4. stable for reporting
5. suitable for executive and stakeholder consumption

### Gold IS NOT
1. a raw data layer
2. a debugging layer
3. a place to resolve data quality issues
4. a source of truth for ingestion correctness

If something looks wrong in Gold, the fix belongs in Silver or Bronze.

---

## Common Gold Design Principles

### Business Grain Ownership

Each Gold model declares a clear grain.
This grain never changes within the model.

Examples include:
1. one row per transaction
2. one row per day
3. one row per customer
4. one row per subscription per period

This prevents metric inflation and ambiguity.

---

### Metric Determinism

All metrics in Gold are:
1. deterministic
2. reproducible
3. derived from Silver only
4. consistent across models

If two Gold models expose the same metric, they must compute it identically.

---

### Time Awareness

Gold models are explicitly time aware.
They define:
1. event dates
2. reporting dates
3. aggregation windows
4. period boundaries

This avoids metric drift across dashboards.

---

## Gold Models Overview

## gold_transaction_facts

### Source
Silver transactional models including:
silver_transactions  
silver_payments  
silver_refunds  

### Grain
One row per transaction

### Purpose
Provide a canonical transactional fact table suitable for analytics.

### Business Logic Applied
1. final transaction status resolution
2. successful versus failed transaction classification
3. payment outcome association
4. refund linkage
5. net transaction amount calculation

### Key Outputs
1. transaction_id
2. customer_id
3. account_id
4. transaction_date
5. gross_amount
6. refunded_amount
7. net_amount
8. final_status

### Intended Use
1. transaction level reporting
2. downstream revenue aggregation
3. audit and reconciliation analysis

---

## gold_daily_revenue

### Source
gold_transaction_facts

### Grain
One row per calendar day

### Purpose
Expose daily revenue metrics for trend analysis.

### Business Logic Applied
1. filtering to paid transactions
2. net revenue calculation after refunds
3. daily aggregation by transaction date

### Key Outputs
1. revenue_date
2. gross_revenue
3. refunded_revenue
4. net_revenue
5. transaction_count

### Intended Use
1. revenue trend dashboards
2. financial reporting
3. anomaly detection at daily granularity

---

## gold_mrr

### Source
Silver subscription and transaction models

### Grain
One row per subscription per month

### Purpose
Compute Monthly Recurring Revenue.

### Business Logic Applied
1. active subscription detection per month
2. plan normalization and pricing resolution
3. monthly revenue attribution
4. upgrade and downgrade handling

### Key Outputs
1. month
2. subscription_id
3. customer_id
4. plan
5. mrr_amount

### Intended Use
1. subscription revenue reporting
2. growth and contraction analysis
3. executive revenue metrics

---

## gold_churn

### Source
Silver subscriptions

### Grain
One row per churn event

### Purpose
Identify and quantify customer and subscription churn.

### Business Logic Applied
1. subscription lifecycle evaluation
2. churn event identification
3. churn date assignment
4. churn classification

### Key Outputs
1. churn_date
2. subscription_id
3. customer_id
4. churn_type
5. last_active_plan

### Intended Use
1. churn rate calculation
2. retention analysis
3. customer lifecycle reporting

---

## gold_customer_metrics

### Source
Multiple Gold and Silver models including:
gold_transaction_facts  
gold_mrr  
gold_churn  

### Grain
One row per customer

### Purpose
Provide a consolidated customer level metrics table.

### Business Logic Applied
1. lifetime revenue calculation
2. active customer flag using locked definition
3. paying customer flag using locked definition
4. refunded customer flag using locked definition
5. churned customer flag using locked definition
6. transaction frequency metrics

### Key Outputs
1. customer_id
2. first_transaction_date
3. lifetime_revenue
4. active_customer_flag
5. paying_customer_flag
6. refunded_customer_flag
7. churned_customer_flag
8. total_transactions

### Intended Use
1. customer analytics
2. segmentation
3. downstream ML features
4. executive reporting

---

## Why This Layer Exists

The Gold layer exists to answer:

What does this data mean for the business

It answers questions like:
1. how much revenue did we make
2. are we growing or shrinking
3. how many customers churned
4. what is our recurring revenue
5. who are our most valuable customers

These questions cannot be answered safely in Bronze or Silver.

---

## Downstream Expectations

1. dashboards and reports must read only from Gold
2. business stakeholders should never query Silver or Bronze directly
3. metric definitions live in Gold documentation
4. any change in business logic must be versioned and reviewed
5. Gold models represent the analytics contract with the business

Bronze records reality  
Silver enforces correctness  
Gold tells the story the business runs on

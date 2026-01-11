# dbt Model Documentation

## Purpose

This document describes the dbt models that power the analytics platform, with emphasis on the Gold and Platinum layers.

It is a retrieval source for the RAG system and represents the authoritative mapping between business concepts and physical models.

All models described here must align with locked business definitions.

---

## Layer Responsibilities

### Bronze

- Captures raw events exactly as received
- Allows duplicates and late arriving data
- Applies no business logic
- Exists for auditability and traceability

### Silver

- Enforces entity correctness and normalization
- Deduplicates records
- Resolves late arriving updates
- Standardizes statuses and schemas
- Does not express business meaning

### Gold

- Encodes business logic and assumptions
- Computes metrics and KPIs
- Aggregates Silver data into analytical models
- Represents the analytics contract with the business

### Platinum

- Contextualizes Gold metrics for decision making
- Applies executive friendly aggregation and framing
- Adds trends, ratios, and anomaly detection
- Never corrects data, only explains it

---

## Locked Business Definitions

The following definitions are authoritative and used consistently across all Gold and Platinum models.

- Active Customer  
  At least one account with `normalized_status = active`

- Paying Customer  
  At least one transaction with `final_status = paid`

- Refunded Customer  
  At least one transaction with `final_status = refunded`

- Churned Customer  
  At least one subscription with `subscription_status = canceled`

These definitions are intentionally simple, deterministic, and auditable.

---

## Gold Models

### gold_transaction_facts

#### Purpose

Canonical transactional fact table that resolves final transaction outcomes and financial amounts.

#### Grain

One row per transaction

#### Source Models

- `silver_transactions`
- `silver_payments`
- `silver_refunds`

#### Business Logic Applied

- Final transaction status resolution
- Successful versus failed classification
- Refund linkage
- Net amount calculation

#### Key Outputs

- `transaction_id`
- `customer_id`
- `account_id`
- `transaction_date`
- `gross_amount`
- `refunded_amount`
- `net_amount`
- `final_status`

#### Intended Use

- Transaction level reporting
- Revenue aggregation
- Financial audit and reconciliation

---

### gold_daily_revenue

#### Purpose

Expose daily revenue metrics for trend and anomaly analysis.

#### Grain

One row per calendar day

#### Source Model

- `gold_transaction_facts`

#### Business Logic Applied

- Filter to `final_status = paid`
- Aggregate gross, refunded, and net revenue
- Group by transaction date

#### Key Outputs

- `revenue_date`
- `gross_revenue`
- `refunded_revenue`
- `net_revenue`
- `transaction_count`

#### Intended Use

- Revenue dashboards
- Daily trend analysis
- Input to executive scorecards

---

### gold_mrr

#### Purpose

Compute Monthly Recurring Revenue from subscription activity.

#### Grain

One row per subscription per month

#### Source Models

- Silver subscription models
- Supporting transaction models where applicable

#### Business Logic Applied

- Active subscription detection per month
- Plan normalization and pricing resolution
- Monthly revenue attribution
- Upgrade and downgrade handling

#### Key Outputs

- `month`
- `subscription_id`
- `customer_id`
- `plan`
- `mrr_amount`

#### Intended Use

- Subscription revenue reporting
- Growth and contraction analysis
- Executive level revenue metrics

---

### gold_churn

#### Purpose

Identify and quantify churn events.

#### Grain

One row per churn event

#### Source Model

- `silver_subscriptions`

#### Business Logic Applied

- Subscription lifecycle evaluation
- Churn event identification
- Churn date assignment
- Churn classification

#### Key Outputs

- `churn_date`
- `subscription_id`
- `customer_id`
- `churn_type`
- `last_active_plan`

#### Notes

- Churn is subscription driven
- Customer churn is derived downstream

#### Intended Use

- Churn rate calculation
- Retention analysis
- Lifecycle reporting

---

### gold_customer_metrics

#### Purpose

Consolidated customer level metrics table.

#### Grain

One row per customer

#### Source Models

- `gold_transaction_facts`
- `gold_mrr`
- `gold_churn`
- Supporting Silver entities

#### Business Logic Applied

- Lifetime revenue calculation
- Active customer flag using locked definition
- Paying customer flag using locked definition
- Refunded customer flag using locked definition
- Churned customer flag using locked definition
- Transaction frequency metrics

#### Key Outputs

- `customer_id`
- `first_transaction_date`
- `lifetime_revenue`
- `active_customer_flag`
- `paying_customer_flag`
- `refunded_customer_flag`
- `churned_customer_flag`
- `total_transactions`

#### Intended Use

- Customer analytics
- Segmentation
- Downstream ML features
- Executive reporting

---

## Platinum Models

### platinum_finance_exec_scorecard_daily

#### Purpose

Daily executive finance scorecard answering:

Is the business behaving normally today

#### Grain

One row per day

#### Source Models

- Gold revenue and transaction models

#### Key Metrics

- `gross_revenue`
- `net_revenue`
- `refunded_amount`
- `refund_rate`
- `failed_payment_rate`
- Seven day rolling average of net revenue
- Week over week net revenue change

#### Behavior

- Aggregates successful transactions
- Adjusts for refunds
- Computes quality ratios
- Adds short term trend context

#### Intended Consumers

- Executive leadership
- Finance leadership
- Alerting systems

---

### platinum_finance_exec_scorecard_monthly

#### Purpose

Monthly executive finance scorecard focused on growth trajectory.

#### Grain

One row per month

#### Source Models

- Gold revenue and subscription models

#### Key Metrics

- `gross_revenue`
- `net_revenue`
- `refund_rate`
- ARR proxy derived from active subscriptions
- Month over month revenue change
- Month over month ARR change

#### Behavior

- Aligns revenue and subscriptions to monthly grain
- Uses subscription count as ARR proxy
- Emphasizes momentum over raw totals

#### Intended Consumers

- Executives
- Board reporting

---

### platinum_anomalies_daily

#### Purpose

Automated anomaly detection for financial health metrics.

#### Grain

One row per day per metric

#### Tracked Metrics

- `net_revenue`
- `refund_rate`
- `failed_payment_rate`

#### Methodology

- Trailing thirty day mean and standard deviation
- Daily z score calculation
- Anomaly flagged when deviation exceeds three standard deviations

#### Outputs

- `metric_value`
- `baseline_value`
- `z_score`
- `is_anomaly`
- `reason`

#### Data Quality Guarantees

- Date is not null
- Metric name is not null
- Grain uniqueness enforced via schema tests

#### Intended Consumers

- Alerting systems
- AI agents
- RAG pipelines
- Read only dashboards

---

## Notes for Retrieval

This document is written to support retrieval questions such as:

- how is churn calculated
- what defines a paying customer
- which model feeds the executive scorecard
- what grain is gold_mrr
- how anomalies are detected

Any change to Gold or Platinum logic must update this document in the same pull request.

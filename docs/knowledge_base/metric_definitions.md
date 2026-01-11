# Metric Definitions

## Purpose

This document defines core business metrics used in the analytics layer.  
These definitions are the source of truth for reporting, dashboards, and downstream AI retrieval.  
All metrics are derived from Gold layer models and must remain stable over time.

***

## General Principles

* Metrics are defined at an explicit grain
* Metrics are computed only from Gold models
* Metric logic must be deterministic
* Metric definitions do not change based on reporting context
* All timestamps are UTC
* Late arriving data is supported through incremental recomputation

***

## Churn

### Definition

A churned customer is a customer who has at least one canceled subscription.

Churn is calculated as the count of churned customers within a given time period.

### Grain

Customer level per day

### Source Model

`gold_churn`

### Business Logic

A customer is considered churned if:

* The customer has at least one subscription
* The subscription status transitions to `canceled`
* The cancellation date falls within the reporting period

Churn does not require loss of revenue in the same period.

### SQL Logic

```sql
select
  customer_id,
  min(canceled_at) as churn_date
from gold_subscriptions
where normalized_status = 'canceled'
group by customer_id
```

### Notes

* A customer can only churn once
* Re subscriptions after churn do not reset churn status
* Churn is customer based, not account based

***

## Active Customer

### Definition

An active customer is a customer with at least one account that is currently active.

### Grain

Customer level snapshot

### Source Model

`gold_customer_metrics`

### Business Logic

A customer is active if:

* At least one linked account has `normalized_status = 'active'`

### Notes

* Activity is independent of transaction volume
* Closed accounts do not qualify

***

## Paying Customer

### Definition

A paying customer is a customer who has completed at least one successful paid transaction.

### Grain

Customer level snapshot

### Source Model

`gold_customer_metrics`

### Business Logic

A customer is paying if:

* At least one transaction exists with:
  * `status = 'success'`
  * `amount > 0`

### Notes

* Refunds do not negate paying status
* Failed or pending transactions do not count

***

## Monthly Recurring Revenue (MRR)

### Definition

MRR represents the normalized monthly revenue from active subscriptions.

### Grain

Month level

### Source Model

`gold_mrr`

### Business Logic

MRR is calculated as:

* Sum of monthly subscription fees
* Only subscriptions with `normalized_status = 'active'`
* Revenue normalized to a monthly amount

### SQL Logic

```sql
select
  date_trunc('month', billing_date) as month,
  sum(monthly_amount) as mrr
from gold_subscriptions
where normalized_status = 'active'
group by 1
```

### Notes

* One time charges are excluded
* Annual plans are prorated to monthly

***

## Daily Revenue

### Definition

Daily revenue represents total settled transaction revenue per day.

### Grain

Day level

### Source Model

`gold_daily_revenue`

### Business Logic

Revenue includes:

* Successful transactions
* Positive amounts
* Settled transactions only

### Notes

* Pending transactions are excluded
* Refunds are handled separately

***

## Refund Rate

### Definition

Refund rate measures the proportion of refunded transactions relative to successful transactions.

### Grain

Day or month level

### Source Model

`gold_refund_rate`

### Business Logic

Refund rate is calculated as:

* Refunded transactions count divided by successful transactions count

### Notes

* Refunds are counted by transaction
* Partial refunds count as refunded

***

## Ownership

* Metric owner: Analytics Engineering
* Changes require documentation update and backfill validation
* All changes must be reviewed before release

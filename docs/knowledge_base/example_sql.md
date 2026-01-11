# Example SQL Queries

## Purpose

This document contains canonical SQL examples for computing core metrics.

These queries are not exploratory.  
They represent approved computation patterns used in Gold and Platinum models.

They exist to:

* make business logic concrete
* support retrieval based explanations
* prevent metric reinterpretation
* anchor RAG answers in executable logic

---

## Churn Calculation

### Question Answered

How is churn calculated?

### Source Tables

* silver_subscriptions
* gold_churn

### Canonical Logic

A churn event occurs when a subscription transitions to `subscription_status = 'canceled'`.

Customer churn is derived from subscription churn.

### SQL Example

```sql
select
  subscription_id,
  customer_id,
  min(event_ts) as churn_date
from silver_subscriptions
where subscription_status = 'canceled'
group by subscription_id, customer_id
```
### Notes

* Churn is subscription driven
* A customer may have multiple churned subscriptions
* Customer churn flags are derived downstream

---

## Daily Revenue

### Question Answered

How is daily revenue calculated?

### Source Tables

* gold_transaction_facts

### SQL Example

```sql
select
  transaction_date as revenue_date,
  sum(gross_amount) as gross_revenue,
  sum(refunded_amount) as refunded_revenue,
  sum(net_amount) as net_revenue,
  count(*) as transaction_count
from gold_transaction_facts
where final_status = 'paid'
group by transaction_date
```

### Notes

* Pending and failed transactions are excluded
* Refunds are netted explicitly

---

## Monthly Revenue

### Question Answered

How is monthly revenue calculated?

### Source Tables

* gold_daily_revenue

### SQL Example

```sql
select
  date_trunc('month', revenue_date) as month,
  sum(net_revenue) as monthly_net_revenue
from gold_daily_revenue
group by 1
```

### Notes

* Monthly revenue is a rollup
* No new business logic is introduced
---

## Monthly Recurring Revenue (MRR)
### Question Answered

How is MRR calculated?

### Source Tables

* silver_subscriptions
### SQL Example
```sql
select
  date_trunc('month', active_month) as month,
  subscription_id,
  customer_id,
  monthly_price as mrr_amount
from silver_subscriptions
where subscription_status = 'active'
```
### Notes

* One row per subscription per month
* One time charges are excluded
---
## Annual Recurring Revenue (ARR)
### Question Answered

How is ARR calculated?

### Source Tables

gold_mrr

### SQL Example
```sql
select
  month,
  sum(mrr_amount) * 12 as arr_amount
from gold_mrr
group by month
```
### Notes

* ARR is derived from MRR

* No independent logic exists
---
## Refund Rate
### Question Answered

How is refund rate calculated?

### Source Tables

* gold_transaction_facts

### SQL Example
```sql
select
  transaction_date as date,
  sum(refunded_amount) / nullif(sum(gross_amount), 0) as refund_rate
from gold_transaction_facts
where final_status = 'paid'
group by transaction_date
```
### Notes

* Division by zero is explicitly handled

* Rate is amount based, not count based
---
## Failed Payment Rate
### Question Answered

How is failed payment rate calculated?

### Source Tables

* silver_payments

### SQL Example
``` sql
select
  payment_date as date,
  sum(case when payment_status = 'failed' then 1 else 0 end)
    / nullif(count(*), 0) as failed_payment_rate
from silver_payments
group by payment_date
```
### Notes

* Computed at payment attempt level

* Aggregated daily
---
## Cohort Retention
### Question Answered

How is cohort retention calculated?

### Source Tables

* gold_cohort_retention

### SQL Example
``` sql
select
  cohort_month,
  months_since_cohort,
  count(distinct customer_id) as retained_customers
from gold_cohort_retention
group by cohort_month, months_since_cohort
```
### Notes

* Cohorts are defined by first paid month
* Retention is customer based
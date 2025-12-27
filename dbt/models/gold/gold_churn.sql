{{ config(
    materialized = "table"
) }}

select
    date_trunc('month', end_date) as churn_month,
    count(distinct customer_id) as churned_customers,
    current_timestamp as gold_loaded_at
from {{ ref("silver_subscriptions") }}
where status = 'canceled'
  and end_date is not null
group by churn_month
order by churn_month

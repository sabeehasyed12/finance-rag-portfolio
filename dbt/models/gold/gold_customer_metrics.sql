{{ config(
    materialized = "table"
) }}

with active_customers as (
    select
        customer_id
    from {{ ref("silver_accounts") }}
    where normalized_status = 'active'
    group by customer_id
),

paying_customers as (
    select
        customer_id
    from {{ ref("gold_transaction_facts") }}
    where is_paid = true
    group by customer_id
),

refunded_customers as (
    select
        customer_id
    from {{ ref("gold_transaction_facts") }}
    where refunded_amount > 0
    group by customer_id
),

churned_customers as (
    select
        customer_id
    from {{ ref("silver_subscriptions") }}
    where status = 'canceled'
    group by customer_id
)

select
    current_date as snapshot_date,

    count(distinct a.customer_id) as active_customers,
    count(distinct p.customer_id) as paying_customers,
    count(distinct r.customer_id) as refunded_customers,
    count(distinct c.customer_id) as churned_customers,

    current_timestamp as gold_loaded_at
from active_customers a
left join paying_customers p
    on a.customer_id = p.customer_id
left join refunded_customers r
    on a.customer_id = r.customer_id
left join churned_customers c
    on a.customer_id = c.customer_id

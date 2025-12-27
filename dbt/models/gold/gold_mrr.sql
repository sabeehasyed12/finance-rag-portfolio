{{ config(
    materialized = "table"
) }}

with subscriptions as (
    select
        subscription_id,
        customer_id,
        plan_name,
        status,
        start_date,
        coalesce(end_date, current_date) as effective_end_date
    from {{ ref("silver_subscriptions") }}
),

plans as (
    select
        plan_name,
        monthly_price
    from {{ ref("subscription_plans") }}
),

expanded as (
    select
        s.subscription_id,
        s.customer_id,
        s.plan_name,
        p.monthly_price,
        date_trunc('month', revenue_date) as revenue_month,
        s.status
    from subscriptions s
    join plans p
        on s.plan_name = p.plan_name
    cross join generate_series(
        s.start_date,
        s.effective_end_date,
        interval '1 month'
    ) as gs(revenue_date)

)

select
    revenue_month,
    sum(monthly_price) as mrr,
    count(distinct customer_id) as active_customers,
    current_timestamp as gold_loaded_at
from expanded
where status = 'active'
group by revenue_month
order by revenue_month

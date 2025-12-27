{{ config(materialized = "table") }}

with priced as (

    select
        subscription_id,
        date_trunc('month', start_date) as month,
        case
            when plan_name = 'basic' then 10
            when plan_name = 'pro' then 30
            when plan_name = 'enterprise' then 100
            else 0
        end as monthly_price
    from {{ ref("silver_subscriptions") }}
    where status = 'active'

)

select
    month,
    sum(monthly_price) * 12 as arr
from priced
group by 1
order by month

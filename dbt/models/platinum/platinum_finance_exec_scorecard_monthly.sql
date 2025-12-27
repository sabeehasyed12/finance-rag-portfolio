{{ config(materialized = "table") }}

with transactions as (

    select
        date_trunc('month', created_at) as month,
        transaction_id,
        amount
    from {{ ref("silver_transactions") }}
    where status = 'success'

),

refunds as (

    select
        date_trunc('month', refunded_at) as month,
        transaction_id,
        amount as refund_amount
    from {{ ref("silver_refunds") }}

),

subscriptions as (

    select
        date_trunc('month', start_date) as month,
        subscription_id
    from {{ ref("silver_subscriptions") }}
    where status = 'active'

),

monthly_revenue as (

    select
        t.month,
        sum(t.amount) as gross_revenue,
        coalesce(sum(r.refund_amount), 0) as refunded_amount
    from transactions t
    left join refunds r
        on t.transaction_id = r.transaction_id
    group by 1

),

monthly_subscriptions as (

    select
        month,
        count(distinct subscription_id) as active_subscriptions
    from subscriptions
    group by 1

),

base as (

    select
        r.month,
        r.gross_revenue,
        r.gross_revenue - r.refunded_amount as net_revenue,
        r.refunded_amount,
        s.active_subscriptions,
        s.active_subscriptions * 12 as arr_proxy,
        case
            when r.gross_revenue = 0 then null
            else r.refunded_amount * 1.0 / r.gross_revenue
        end as refund_rate
    from monthly_revenue r
    left join monthly_subscriptions s
        on r.month = s.month

),

final as (

    select
        month,
        gross_revenue,
        net_revenue,
        arr_proxy,
        refund_rate,

        net_revenue
            - lag(net_revenue, 1) over (order by month)
            as net_revenue_mom_change,

        arr_proxy
            - lag(arr_proxy, 1) over (order by month)
            as arr_mom_change
    from base

)

select *
from final
order by month

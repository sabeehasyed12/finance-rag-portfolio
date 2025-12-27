{{ config(materialized = "table") }}

with transactions as (

    select
        date(created_at) as date,
        amount
    from {{ ref("silver_transactions") }}
    where status = 'success'

),

refunds as (

    select
        date(refunded_at) as date,
        amount as refund_amount
    from {{ ref("silver_refunds") }}

),

payments as (

    select
        date(attempted_at) as date,
        final_payment_status
    from {{ ref("silver_payments") }}

),

daily_revenue as (

    select
        date,
        sum(amount) as gross_revenue
    from transactions
    group by 1

),

daily_refunds as (

    select
        date,
        sum(refund_amount) as refunded_amount
    from refunds
    group by 1

),

daily_payment_stats as (

    select
        date,
        count(*) as attempt_count,
        count(*) filter (
            where final_payment_status != 'success'
        ) as failed_count
    from payments
    group by 1

),

base as (

    select
        r.date,
        r.gross_revenue,
        r.gross_revenue - coalesce(d.refunded_amount, 0) as net_revenue,
        coalesce(d.refunded_amount, 0) as refunded_amount,
        case
            when r.gross_revenue = 0 then null
            else coalesce(d.refunded_amount, 0) * 1.0 / r.gross_revenue
        end as refund_rate,
        case
            when p.attempt_count = 0 then null
            else p.failed_count * 1.0 / p.attempt_count
        end as failed_payment_rate
    from daily_revenue r
    left join daily_refunds d
        on r.date = d.date
    left join daily_payment_stats p
        on r.date = p.date

),

final as (

    select
        date,
        gross_revenue,
        net_revenue,
        refund_rate,
        failed_payment_rate,

        avg(net_revenue) over (
            order by date
            rows between 6 preceding and current row
        ) as net_revenue_7d_avg,

        net_revenue
            - lag(net_revenue, 7) over (order by date)
            as net_revenue_wow_change
    from base

)

select *
from final
order by date

{{ config(materialized = "table") }}

with transactions as (

    select
        transaction_id,
        date_trunc('month', created_at) as month,
        amount
    from {{ ref("silver_transactions") }}
    where status = 'success'

),

refunds as (

    select
        transaction_id,
        amount as refund_amount
    from {{ ref("silver_refunds") }}

),

monthly as (

    select
        t.month,
        sum(t.amount) as gross_revenue,
        coalesce(sum(r.refund_amount), 0) as refund_amount,
        sum(t.amount) - coalesce(sum(r.refund_amount), 0) as net_revenue
    from transactions t
    left join refunds r
        on t.transaction_id = r.transaction_id
    group by 1

)

select
    month,
    gross_revenue,
    net_revenue,
    refund_amount
from monthly
order by month

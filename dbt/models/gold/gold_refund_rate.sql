{{ config(materialized = "table") }}

with transactions as (

    select
        transaction_id,
        date(created_at) as date,
        amount
    from {{ ref("silver_transactions") }}
    where status = 'success'

),

refunds as (

    select
        transaction_id,
        amount as refunded_amount
    from {{ ref("silver_refunds") }}

),

daily as (

    select
        t.date,
        sum(t.amount) as paid_amount,
        coalesce(sum(r.refunded_amount), 0) as refunded_amount
    from transactions t
    left join refunds r
        on t.transaction_id = r.transaction_id
    group by 1

)

select
    date,
    paid_amount,
    refunded_amount,
    case
        when paid_amount = 0 then null
        else refunded_amount * 1.0 / paid_amount
    end as refund_rate
from daily
order by date

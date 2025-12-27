{{ config(
    materialized = "table"
) }}

with transactions as (
    select
        transaction_id,
        customer_id,
        account_id,
        amount as transaction_amount,
        status as transaction_status,
        created_at
    from {{ ref("silver_transactions") }}
),

payments as (
    select
        transaction_id,
        final_payment_status
    from {{ ref("silver_payments") }}
),

refunds as (
    select
        transaction_id,
        sum(amount) as total_refunded_amount
    from {{ ref("silver_refunds") }}
    group by transaction_id
)

select
    t.transaction_id,
    t.customer_id,
    t.account_id,
    t.created_at,

    t.transaction_amount,

    coalesce(r.total_refunded_amount, 0) as refunded_amount,

    case
        when p.final_payment_status = 'success'
        then t.transaction_amount - coalesce(r.total_refunded_amount, 0)
        else 0
    end as net_amount,

    case
        when p.final_payment_status = 'success' then true
        else false
    end as is_paid,

    current_timestamp as gold_loaded_at
from transactions t
left join payments p
    on t.transaction_id = p.transaction_id
left join refunds r
    on t.transaction_id = r.transaction_id

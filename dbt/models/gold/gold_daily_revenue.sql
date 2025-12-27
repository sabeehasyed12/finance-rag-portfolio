{{ config(
    materialized = "table"
) }}

select
    date(created_at) as revenue_date,

    sum(transaction_amount) as gross_transaction_amount,

    sum(refunded_amount) as total_refunded_amount,

    sum(net_amount) as net_revenue,

    count(case when is_paid = true then 1 end) as paid_transaction_count,

    count(case when is_paid = false then 1 end) as unpaid_transaction_count,

    current_timestamp as gold_loaded_at
from {{ ref("gold_transaction_facts") }}
group by 1
order by 1

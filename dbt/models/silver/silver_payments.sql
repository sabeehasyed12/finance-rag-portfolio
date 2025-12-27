{{ config(
    materialized = "table"
) }}

with ranked_payments as (
    select
        payment_id,
        transaction_id,
        payment_method,
        status,
        attempt_number,
        attempted_at,
        ingestion_date,

        row_number() over (
            partition by transaction_id
            order by
                case
                    when status = 'success' then 1
                    else 2
                end,
                attempted_at desc
        ) as rn
    from {{ ref("bronze_payments") }}
)

select
    payment_id,
    transaction_id,
    payment_method,
    status as final_payment_status,
    attempt_number,
    attempted_at,
    ingestion_date,
    current_timestamp as silver_loaded_at
from ranked_payments
where rn = 1

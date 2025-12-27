{{ config(
    materialized = "table"
) }}

select
    refund_id,
    transaction_id,
    amount,
    refund_reason,
    refunded_at,
    ingestion_date,
    current_timestamp as silver_loaded_at
from (
    {{ deduplicate_latest(
        ref("bronze_refunds"),
        "refund_id",
        "ingestion_date desc"
    ) }}
)

{{ config(
    materialized = "table"
) }}

select
    transaction_id,
    account_id,
    customer_id,
    amount,
    currency,
    merchant_name,
    status,
    created_at,
    settled_at,
    ingestion_date,

    -- masked sensitive fields
    md5(cast(card_last_four as varchar)) as card_last_four_hash,
    device_id,

    current_timestamp as silver_loaded_at
from (
    {{ deduplicate_latest(
        ref("bronze_transactions"),
        "transaction_id",
        "ingestion_date desc, created_at desc"
    ) }}
)

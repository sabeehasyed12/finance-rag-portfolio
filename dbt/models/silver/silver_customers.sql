{{ config(
    materialized = "table"
) }}

select
    customer_id,

    -- masked PII (deterministic hashes)
    md5(lower(trim(full_name)))  as full_name_hash,
    md5(lower(trim(email)))      as email_hash,
    md5(phone)                   as phone_hash,
    md5(address)                 as address_hash,

    device_id,
    created_at,
    ingestion_date,
    current_timestamp as silver_loaded_at
from (
    {{ deduplicate_latest(
        ref("bronze_customers"),
        "customer_id",
        "ingestion_date desc"
    ) }}
)

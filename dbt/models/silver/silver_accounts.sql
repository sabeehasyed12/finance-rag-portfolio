{{ config(
    materialized = "table"
) }}

select
    account_id,
    customer_id,
    account_type,

    case
        when status = 'closed' then 'closed'
        when status = 'suspended' then 'inactive'
        else 'active'
    end as normalized_status,

    opened_at,
    closed_at,
    ingestion_date,
    current_timestamp as silver_loaded_at
from (
    {{ deduplicate_latest(
        ref("bronze_accounts"),
        "account_id",
        "ingestion_date desc"
    ) }}
)

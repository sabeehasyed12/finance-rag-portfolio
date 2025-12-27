{{ config(
    materialized = "table"
) }}

select
    subscription_id,
    customer_id,
    plan_name,
    status,
    start_date,
    end_date,
    ingestion_date,
    current_timestamp as silver_loaded_at
from (
    {{ deduplicate_latest(
        ref("bronze_subscriptions"),
        "subscription_id",
        "ingestion_date desc"
    ) }}
)

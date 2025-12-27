{{ config(
    materialized = "incremental",
    unique_key = "subscription_id"
) }}

select
    subscription_id,
    customer_id,
    plan_name,
    status,
    start_date,
    end_date,
    ingestion_date,
    current_timestamp as bronze_loaded_at
from read_csv_auto(
    '{{ var("raw_data_path") }}/subscriptions.csv'
)
{{ incremental_ingestion_filter("ingestion_date") }}


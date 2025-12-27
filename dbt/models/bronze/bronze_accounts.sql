{{ config(
    materialized = "incremental",
    unique_key = "account_id"
) }}

select
    account_id,
    customer_id,
    account_type,
    status,
    opened_at,
    closed_at,
    ingestion_date,
    current_timestamp as bronze_loaded_at
from read_csv_auto(
    '{{ var("raw_data_path") }}/accounts.csv'
)
{{ incremental_ingestion_filter("ingestion_date") }}

{{ config(
    materialized = "incremental",
    unique_key = "transaction_id"
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
    card_last_four,
    device_id,
    current_timestamp as bronze_loaded_at
from read_csv_auto(
    '{{ var("raw_data_path") }}/transactions.csv'
)
{{ incremental_ingestion_filter("ingestion_date") }}


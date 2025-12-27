{{ config(
    materialized = "incremental",
    unique_key = "payment_id"
) }}

select
    payment_id,
    transaction_id,
    payment_method,
    status,
    attempt_number,
    attempted_at,
    ingestion_date,
    current_timestamp as bronze_loaded_at
from read_csv_auto(
    '{{ var("raw_data_path") }}/payments.csv'
)
{{ incremental_ingestion_filter("ingestion_date") }}


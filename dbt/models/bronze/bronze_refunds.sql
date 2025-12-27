{{ config(
    materialized = "incremental",
    unique_key = "refund_id"
) }}

select
    refund_id,
    transaction_id,
    amount,
    refund_reason,
    refunded_at,
    ingestion_date,
    current_timestamp as bronze_loaded_at
from read_csv_auto(
    '{{ var("raw_data_path") }}/refunds.csv'
)
{{ incremental_ingestion_filter("ingestion_date") }}

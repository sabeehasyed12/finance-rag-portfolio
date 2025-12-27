{{ config(
    materialized = "incremental",
    unique_key = "customer_id"
) }}

select
    customer_id,
    full_name,
    email,
    phone,
    address,
    device_id,
    created_at,
    ingestion_date,
    current_timestamp as bronze_loaded_at
from read_csv_auto(
    '{{ var("raw_data_path") }}/customers.csv'
)
{{ incremental_ingestion_filter("ingestion_date") }}

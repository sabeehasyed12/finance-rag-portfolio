{{ config(materialized='view', schema='analytics') }}

select
    customer_id,
    email_hash,
    phone_hash,
    full_name_hash,
    device_id,
    created_at,
    ingestion_date
from {{ ref('silver_customers') }}

{{ config(materialized='view', schema='analytics') }}

select
    payment_id,
    transaction_id,
    final_payment_status,
    ingestion_date
from {{ ref('silver_payments') }}

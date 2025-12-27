{{ config(materialized='view', schema='analytics') }}

select
    refund_id,
    transaction_id,
    amount,
    refunded_at,
    ingestion_date
from {{ ref('silver_refunds') }}

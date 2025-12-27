{{ config(materialized='view', schema='analytics') }}

select
    transaction_id,
    account_id,
    customer_id,
    status,
    settled_at,
    ingestion_date
from {{ ref('silver_transactions') }}

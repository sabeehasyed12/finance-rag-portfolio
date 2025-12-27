{{ config(materialized='view', schema='analytics') }}

select
    subscription_id,
    customer_id,
    status,
    start_date,
    ingestion_date
from {{ ref('silver_subscriptions') }}

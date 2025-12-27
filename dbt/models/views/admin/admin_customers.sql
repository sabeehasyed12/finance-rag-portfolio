{{ config(materialized='view', schema='admin') }}

select *
from {{ ref('silver_customers') }}

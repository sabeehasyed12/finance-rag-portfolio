{{ config(materialized = "table") }}

with payments as (

    select
        date(attempted_at) as date,
        final_payment_status
    from {{ ref("silver_payments") }}

),

daily as (

    select
        date,
        count(*) as attempt_count,
        count(*) filter (
            where final_payment_status != 'success'
        ) as failed_count
    from payments
    group by 1

)

select
    date,
    attempt_count,
    failed_count,
    case
        when attempt_count = 0 then null
        else failed_count * 1.0 / attempt_count
    end as failed_payment_rate
from daily
order by date

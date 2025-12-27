{{ config(materialized = "table") }}

with paid_transactions as (

    select
        customer_id,
        created_at
    from {{ ref("silver_transactions") }}
    where status = 'success'

),

first_paid as (

    select
        customer_id,
        date_trunc('month', min(created_at)) as cohort_month
    from paid_transactions
    group by 1

),

activity as (

    select
        customer_id,
        date_trunc('month', created_at) as activity_month
    from paid_transactions
    group by 1, 2

),

cohort_activity as (

    select
        f.cohort_month,
        a.activity_month,
        datediff(
            'month',
            f.cohort_month,
            a.activity_month
        ) as months_since_cohort,
        count(distinct a.customer_id) as customers_retained
    from first_paid f
    join activity a
        on f.customer_id = a.customer_id
    group by 1, 2, 3

),

cohort_size as (

    select
        cohort_month,
        count(distinct customer_id) as customers_in_cohort
    from first_paid
    group by 1

)

select
    ca.cohort_month,
    ca.months_since_cohort,
    cs.customers_in_cohort,
    ca.customers_retained,
    case
        when cs.customers_in_cohort = 0 then null
        else ca.customers_retained * 1.0 / cs.customers_in_cohort
    end as retention_rate
from cohort_activity ca
join cohort_size cs
    on ca.cohort_month = cs.cohort_month
where ca.months_since_cohort >= 0
order by
    ca.cohort_month,
    ca.months_since_cohort

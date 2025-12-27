{{ config(materialized="table") }}

with s as (
  select
    date,
    net_revenue,
    gross_revenue,
    refund_rate,
    failed_payment_rate
  from {{ ref("platinum_finance_exec_scorecard_daily") }}
),

stats as (
  select
    date,
    net_revenue,
    refund_rate,
    failed_payment_rate,

    avg(net_revenue) over (
      order by date
      rows between 30 preceding and 1 preceding
    ) as net_rev_mean_30,

    stddev_samp(net_revenue) over (
      order by date
      rows between 30 preceding and 1 preceding
    ) as net_rev_std_30,

    avg(refund_rate) over (
      order by date
      rows between 30 preceding and 1 preceding
    ) as refund_mean_30,

    stddev_samp(refund_rate) over (
      order by date
      rows between 30 preceding and 1 preceding
    ) as refund_std_30,

    avg(failed_payment_rate) over (
      order by date
      rows between 30 preceding and 1 preceding
    ) as fail_mean_30,

    stddev_samp(failed_payment_rate) over (
      order by date
      rows between 30 preceding and 1 preceding
    ) as fail_std_30
  from s
),

flags as (
  select
    date,
    'net_revenue' as metric_name,
    net_revenue as metric_value,
    net_rev_mean_30 as baseline_value,
    case
      when net_rev_std_30 is null or net_rev_std_30 = 0 then null
      else (net_revenue - net_rev_mean_30) / net_rev_std_30
    end as z_score
  from stats

  union all

  select
    date,
    'refund_rate' as metric_name,
    refund_rate as metric_value,
    refund_mean_30 as baseline_value,
    case
      when refund_std_30 is null or refund_std_30 = 0 then null
      else (refund_rate - refund_mean_30) / refund_std_30
    end as z_score
  from stats

  union all

  select
    date,
    'failed_payment_rate' as metric_name,
    failed_payment_rate as metric_value,
    fail_mean_30 as baseline_value,
    case
      when fail_std_30 is null or fail_std_30 = 0 then null
      else (failed_payment_rate - fail_mean_30) / fail_std_30
    end as z_score
  from stats
)

select
  date,
  metric_name,
  metric_value,
  baseline_value,
  z_score,
  case
    when z_score is null then false
    when abs(z_score) >= 3 then true
    else false
  end as is_anomaly,
  case
    when z_score is null then 'insufficient_history'
    when abs(z_score) >= 3 then 'deviation_over_3_std'
    else 'normal_range'
  end as reason
from flags
order by date, metric_name

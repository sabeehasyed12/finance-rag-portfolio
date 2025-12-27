{% macro deduplicate_latest(
    source_relation,
    partition_key,
    order_by_clause
) %}

with ranked as (
    select
        *,
        row_number() over (
            partition by {{ partition_key }}
            order by {{ order_by_clause }}
        ) as rn
    from {{ source_relation }}
)

select *
from ranked
where rn = 1

{% endmacro %}

{% macro incremental_ingestion_filter(column_name) %}
{% if is_incremental() %}
where {{ column_name }} >= (
    select max({{ column_name }}) from {{ this }}
)
{% endif %}
{% endmacro %}

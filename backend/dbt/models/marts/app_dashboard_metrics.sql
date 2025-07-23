{{ config(materialized='table') }}

select
  status,
  count(*) as applications_count
from {{ ref('int_application_fact') }}
group by 1
order by 1

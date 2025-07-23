

select
  status,
  count(*) as applications_count
from `onlyjobs-465420`.`dbt_analytics`.`int_application_fact`
group by 1
order by 1
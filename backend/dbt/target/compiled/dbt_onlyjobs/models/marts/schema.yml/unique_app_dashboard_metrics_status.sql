
    
    

with dbt_test__target as (

  select status as unique_field
  from `onlyjobs-465420`.`dbt_analytics`.`app_dashboard_metrics`
  where status is not null

)

select
    unique_field,
    count(*) as n_records

from dbt_test__target
group by unique_field
having count(*) > 1




    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select status
from `onlyjobs-465420`.`dbt_analytics`.`app_dashboard_metrics`
where status is null



  
  
      
    ) dbt_internal_test


  create or replace view `onlyjobs-465420`.`dbt_analytics`.`stg_job_applications`
  OPTIONS()
  as 

select
  user_id,
  email_id,
  company,
  job_title,
  location,
  status,
  inserted_at,
  email_date
from `onlyjobs-465420`.`user_data`.`job_applications`;


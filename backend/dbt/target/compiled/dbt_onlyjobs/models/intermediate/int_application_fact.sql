

select
  *,
  date_diff(cast(email_date as date), cast(inserted_at as date), day) as days_since_insert
from `onlyjobs-465420`.`dbt_analytics`.`stg_job_applications`
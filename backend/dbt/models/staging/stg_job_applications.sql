{{ config(materialized='view') }}

select
  user_id,
  email_id,
  company,
  job_title,
  location,
  status,
  inserted_at,
  email_date
from {{ source('user_data', 'job_applications') }}

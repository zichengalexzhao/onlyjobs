{{ config(materialized='table') }}

select
  *,
  date_diff(cast(email_date as date), cast(inserted_at as date), day) as days_since_insert
from {{ ref('stg_job_applications') }}

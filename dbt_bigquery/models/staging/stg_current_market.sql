WITH source AS (
    SELECT * FROM {{source('raw', 'current_market')}}
),

RENAMED AS (
    -- transform
)

SELECT * FROM RENAMED
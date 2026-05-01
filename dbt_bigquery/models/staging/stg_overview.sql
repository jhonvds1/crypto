WITH source AS (
    SELECT * FROM {{source('raw', 'overview')}}
),

RENAMED AS (
    -- transform
)

SELECT * FROM RENAMED
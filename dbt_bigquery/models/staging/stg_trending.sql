WITH source AS (
    SELECT * FROM {{source('raw', 'trending')}}
),

RENAMED AS (
    -- transform
)

SELECT * FROM RENAMED
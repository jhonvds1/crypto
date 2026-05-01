WITH source AS (
    SELECT * FROM {{source('raw', 'simple_price')}}
),

RENAMED AS (
    -- transform
)

SELECT * FROM RENAMED
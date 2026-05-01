WITH source AS (
    SELECT * FROM {{source('raw', 'crypto_list')}}
),

RENAMED AS (
    -- transform
)

SELECT * FROM RENAMED
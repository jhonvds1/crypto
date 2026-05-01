WITH source AS (
    SELECT * FROM {{source('raw', 'simple_price')}}
)

SELECT * FROM source
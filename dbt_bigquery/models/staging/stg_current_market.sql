WITH source AS (
    SELECT * FROM {{source('raw', 'current_market')}}
),

RENAMED AS (
    SELECT
        id,
        name,
        market_cap,
        current_price,
        market_cap_rank,
        total_volume,
        last_updated,
        price_change_percentage_24h
    FROM source
)

SELECT * FROM RENAMED
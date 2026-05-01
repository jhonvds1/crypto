WITH source AS (
    SELECT * FROM {{source('raw', 'current_market')}}
),

deduplicated AS(
    SELECT 
        *
    FROM (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY id asc) AS rn
        FROM source
        WHERE id IS NOT NULL
    )
    WHERE rn = 1
)

RENAMED AS (
    SELECT
        TRIM(id),
        INITCAP(TRIM(name)),
        CAST(market_cap, INT64),
        current_price,
        market_cap_rank,
        CAST(total_volume, INT64),
        DATE(last_updated),
        price_change_percentage_24h
    FROM source
    WHERE id IS NOT NULL 
    AND current_price >= 0.0
)

SELECT * FROM deduplicated
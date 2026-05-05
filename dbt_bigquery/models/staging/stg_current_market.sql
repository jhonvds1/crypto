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
),

RENAMED AS (
    SELECT
        TRIM(id) AS id,
        INITCAP(TRIM(name)) AS name,
        CAST(market_cap AS INT64) AS market_cap,
        current_price,
        market_cap_rank,
        CAST(total_volume AS INT64) AS total_volume,
        DATE(last_updated) AS last_updated,
        price_change_percentage_24h
    FROM deduplicated
    WHERE id IS NOT NULL 
    AND current_price >= 0.0
)

SELECT * FROM RENAMED
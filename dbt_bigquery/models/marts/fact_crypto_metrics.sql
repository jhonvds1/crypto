WITH stg_current_market AS (
    SELECT 
        *,
        CAST(format_date('%Y%m%d', DATE(last_updated)) AS int64) AS id_data
    FROM {{ref('stg_current_market')}}    
),

stg_trending as (

    select * from {{ ref('stg_trending') }}

),

dim_time AS (
    SELECT * FROM {{ref('dim_time')}}
),

dim_crypto AS (
    SELECT * FROM {{ref('dim_crypto')}}
),

final AS (
    SELECT 
        t.time_id,
        c.id AS crypto_id,
        cm.current_price,
        cm.market_cap,
        cm.market_cap_rank,
        cm.price_change_percentage_24h,
        cm.total_volume,
        tr.score AS trend_score
    FROM stg_current_market cm 
    LEFT JOIN dim_time t
        ON cm.id_data = t.time_id
    LEFT JOIN dim_crypto c
        ON cm.id = c.id
    LEFT JOIN stg_trending tr
        ON cm.id = tr.id
)

SELECT * FROM final
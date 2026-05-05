WITH stg_current_market AS (
    SELECT * FROM {{ref('stg_current_market')}}
),

final AS (
    SELECT
        DISTINCT CAST(format_date('%Y%m%d', last_updated) AS INT64) AS time_id,
        EXTRACT(YEAR FROM last_updated) AS year,
        EXTRACT(MONTH FROM last_updated) AS month,
        EXTRACT(DAY FROM last_updated) AS day
    from stg_current_market
)

SELECT * from final


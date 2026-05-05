WITH stg_current_market AS (
    SELECT * FROM {{ref('stg_current_market')}}
),

final AS (
    SELECT
        id,
        name
    FROM stg_current_market
)

SELECT * FROM final
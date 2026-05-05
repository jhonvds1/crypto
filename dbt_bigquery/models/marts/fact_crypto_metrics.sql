WITH stg_current_market AS (
    SELECT * FROM {{ref('stg_current_market')}}    
),

dim_time AS (
    SELECT * FROM {{ref('dim_time')}}
),

dim_crypto AS (
    SELECT * FROM {{ref('dim_crypto')}}
),

final AS (


)

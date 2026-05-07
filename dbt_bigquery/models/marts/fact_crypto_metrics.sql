-- CTE base: staging da tabela current_market com criação de chave de data
WITH stg_current_market AS (
    SELECT 
        *,
        
        -- cria uma chave de data no formato YYYYMMDD a partir de last_updated
        CAST(FORMAT_DATE('%Y%m%d', DATE(last_updated)) AS INT64) AS id_data

    FROM {{ref('stg_current_market')}}    
),

-- CTE de staging da tabela trending
stg_trending as (

    select * 
    from {{ ref('stg_trending') }}

),

-- dimensão de tempo já tratada no dbt
dim_time AS (
    SELECT * 
    FROM {{ref('dim_time')}}
),

-- dimensão de criptomoedas (catálogo de coins)
dim_crypto AS (
    SELECT * 
    FROM {{ref('dim_crypto')}}
),

-- camada final: montagem da tabela fato (fact table)
final AS (

    SELECT 
        t.time_id,                     -- chave temporal (dim_time)
        c.id AS crypto_id,            -- chave da dimensão crypto
        
        cm.current_price,             -- métrica: preço atual
        cm.market_cap,               -- métrica: market cap
        cm.market_cap_rank,          -- ranking de market cap
        cm.price_change_percentage_24h, -- variação 24h
        cm.total_volume,             -- volume total
        
        tr.score AS trend_score      -- score de trending da moeda

    FROM stg_current_market cm 

    -- join com dimensão de tempo
    LEFT JOIN dim_time t
        ON cm.id_data = t.time_id

    -- join com dimensão de criptomoedas
    LEFT JOIN dim_crypto c
        ON cm.id = c.id

    -- join com dados de trending
    LEFT JOIN stg_trending tr
        ON cm.id = tr.id
)

-- resultado final do modelo
SELECT * 
FROM final
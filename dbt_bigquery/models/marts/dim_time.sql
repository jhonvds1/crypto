-- CTE base: referencia o modelo staging no dbt
WITH stg_current_market AS (
    SELECT * 
    FROM {{ref('stg_current_market')}}
),

-- CTE que gera uma dimensão temporal a partir da coluna last_updated
final AS (

    SELECT
        DISTINCT

        -- cria uma chave numérica de data no formato YYYYMMDD
        CAST(FORMAT_DATE('%Y%m%d', last_updated) AS INT64) AS time_id,

        -- extrai ano da data de atualização
        EXTRACT(YEAR FROM last_updated) AS year,

        -- extrai mês da data de atualização
        EXTRACT(MONTH FROM last_updated) AS month,

        -- extrai dia da data de atualização
        EXTRACT(DAY FROM last_updated) AS day

    FROM stg_current_market
)

-- saída final do modelo
SELECT * 
FROM final
-- CTE que referencia o modelo já transformado (staging layer no dbt)
WITH stg_current_market AS (
    SELECT * 
    FROM {{ ref('stg_current_market') }}
),

-- CTE final onde você seleciona apenas as colunas desejadas
final AS (
    SELECT
        id,    -- identificador da criptomoeda
        name   -- nome da criptomoeda
    FROM stg_current_market
)

-- saída final do modelo
SELECT * 
FROM final
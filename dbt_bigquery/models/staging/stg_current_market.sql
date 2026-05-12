-- Cria uma CTE base pegando os dados da tabela raw no dbt
WITH source AS (
    SELECT * FROM {{source('raw', 'current_market')}}
),

-- Remove duplicados da tabela com base no campo "id"
-- Mantém apenas 1 registro por id usando ROW_NUMBER()
deduplicated AS(
    SELECT 
        *
    FROM (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY id, DATE(last_updated) ORDER BY last_updated DESC) AS rn
            -- cria um ranking por id (como não há critério melhor, usa id mesmo)
        FROM source
        WHERE id IS NOT NULL  -- remove registros sem id
    )
    WHERE rn = 1  -- mantém apenas o primeiro registro de cada id
),

-- CTE responsável por padronização e limpeza de dados
RENAMED AS (
    SELECT
        TRIM(id) AS id,  -- remove espaços do id
        INITCAP(TRIM(name)) AS name,  -- coloca nome em formato "Title Case"
        
        CAST(market_cap AS INT64) AS market_cap,  -- converte market cap para inteiro
        
        current_price,  -- mantém preço atual
        
        RANK() OVER (ORDER BY market_cap DESC) AS market_cap_rank,  -- ranking de market cap
        
        CAST(total_volume AS INT64) AS total_volume,  -- converte volume para inteiro
        
        DATE(last_updated) AS last_updated,  -- converte timestamp para date
        
    FROM deduplicated

    -- filtros de qualidade de dados
    WHERE id IS NOT NULL 
    AND last_updated IS NOT NULL
    AND current_price >= 0.0  -- remove valores inválidos de preço
)

-- seleção final da tabela limpa e tratada
SELECT * FROM RENAMED
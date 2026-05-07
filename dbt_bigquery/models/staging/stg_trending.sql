-- CTE inicial: lê a tabela raw do dbt (trending da CoinGecko)
WITH source AS (

    SELECT * 
    FROM {{ source('raw', 'trending') }}

),

-- CTE responsável por "explodir" (flatten) o array de coins
-- Cada item dentro do array coins vira uma linha
unnested AS (

    SELECT
        coin.item.id    AS id,     -- pega o id da moeda dentro do JSON
        coin.item.name  AS name,   -- nome da moeda
        coin.item.score AS score   -- score de trending

    FROM source,

    -- transforma array "coins" em linhas separadas
    UNNEST(coins) AS coin

),

-- CTE para remoção de duplicados baseado no id
deduplicated AS (

    SELECT 
        *
    FROM (
        SELECT 
            *,
            -- cria ranking por id (para identificar duplicados)
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY id) AS RN
        FROM unnested
        WHERE id IS NOT NULL  -- remove registros sem id
    )
    WHERE rn = 1  -- mantém apenas o primeiro registro de cada id

),

-- CTE de tratamento de dados (normalização)
treated AS (

    SELECT 
        TRIM(id) AS id,          -- remove espaços do id
        INITCAP(name) AS name,   -- padroniza nome (Title Case)
        score                     -- mantém score de trending
    FROM unnested
    WHERE id IS NOT NULL

)

-- seleção final
SELECT * 
FROM deduplicated
with source as (

    select * from {{ source('raw', 'trending') }}

),

unnested as (

    select
        coin.item.id    as id,
        coin.item.name  as name,
        coin.item.score as score

    from source,
    unnest(coins) as coin

),

deduplicated as (

    SELECT 
        *
    FROM (
        SELECT 
            *,
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY id) AS RN
        FROM unnested
        WHERE id IS NOT NULL
    )
    WHERE rn = 1

),

treated as (

    SELECT 
        TRIM(id) AS id,
        INITCAP(name) AS name,
        score
    FROM unnested
    WHERE id IS NOT NULL

)

select * from deduplicated
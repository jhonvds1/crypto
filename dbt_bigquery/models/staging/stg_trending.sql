with source as (

    select * from {{ source('raw', 'trending') }}

),

unnested as (

    select
        ingested_at,
        coin.item.id    as id,
        coin.item.name  as name,
        coin.item.score as score

    from source,
    unnest(coins) as coin

)

select * from unnested
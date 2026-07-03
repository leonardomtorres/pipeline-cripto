-- Staging do historico: limpa e tipa. Sem regra de negocio.
with source as (
    select * from {{ source('raw', 'coingecko_price_history') }}
),

renamed as (
    select
        coin_id,
        cast(data as date) as data,
        cast(preco as numeric) as preco,
        cast(market_cap as numeric) as market_cap,
        cast(volume as numeric) as volume,
        vs_currency as moeda_cotacao
    from source
)

select * from renamed

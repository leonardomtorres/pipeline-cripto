with source as (
    select * from {{ source('raw', 'coingecko_market_data') }}
),

renamed as (
    select
        id as coin_id,
        symbol as ticker,
        name as coin_name,
        vs_currency as moeda_cotacao,
        cast(current_price as numeric) as preco,
        cast(market_cap as numeric) as market_cap,
        cast(total_volume as numeric) as volume_24h,
        cast(price_change_percentage_24h as numeric) as variacao_pct_24h,
        cast(extracted_at as timestamp) as extraido_em,
        date(cast(extracted_at as timestamp)) as data_referencia
    from source
)

select * from renamed

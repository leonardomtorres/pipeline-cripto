-- Calcula o retorno diario (variacao % de um dia pro outro), por moeda.
with precos as (
    select * from {{ ref('stg_coingecko__price_history') }}
),

com_anterior as (
    select
        coin_id,
        data,
        preco,
        market_cap,
        volume,
        -- LAG pega o preco do dia anterior da MESMA moeda, na ordem da data
        lag(preco) over (partition by coin_id order by data) as preco_anterior
    from precos
)

select
    coin_id,
    data,
    preco,
    market_cap,
    volume,
    preco_anterior,
    -- retorno em %: (hoje - ontem) / ontem * 100 ; safe_divide evita divisao por zero
    safe_divide(preco - preco_anterior, preco_anterior) * 100 as retorno_pct
from com_anterior

-- Tabela final pro dashboard: preco diario, retorno e media movel de 7 dias.
with base as (
    select * from {{ ref('int_retorno_diario') }}
)

select
    coin_id,
    data,
    preco,
    market_cap,
    volume,
    retorno_pct,
    -- media movel de 7 dias: suaviza o preco (janela dos 7 ultimos dias)
    avg(preco) over (
        partition by coin_id
        order by data
        rows between 6 preceding and current row
    ) as media_movel_7d
from base

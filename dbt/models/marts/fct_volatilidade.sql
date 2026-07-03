-- Uma linha por moeda: resumo de risco/retorno no periodo.
with retornos as (
    select * from {{ ref('int_retorno_diario') }}
)

select
    coin_id,
    count(*) as dias,
    avg(retorno_pct) as retorno_medio_pct,
    -- volatilidade = desvio padrao dos retornos diarios (metrica classica de risco)
    stddev(retorno_pct) as volatilidade_pct,
    min(preco) as preco_min,
    max(preco) as preco_max
from retornos
group by coin_id

import logging
from datetime import datetime, timezone

import pandas as pd
import requests

logger = logging.getLogger(__name__)


def fetch_market_data(coins, vs_currency, api_url):
    # /coins/markets traz preco, market cap, volume e variacao 24h de uma vez.
    # A API publica tem rate limit (~10-30 req/min), entao buscamos tudo numa chamada.
    url = f"{api_url}/coins/markets"
    params = {
        "vs_currency": vs_currency,
        "ids": ",".join(coins),
        "order": "market_cap_desc",
        "per_page": len(coins),
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()

    df = pd.DataFrame(resp.json())
    df["extracted_at"] = datetime.now(timezone.utc).isoformat()
    df["vs_currency"] = vs_currency

    logger.info("CoinGecko: %d moedas", len(df))
    return df

import logging
import time
from datetime import datetime, timezone

import pandas as pd
import requests

from utils.config import config
from utils.gcs import upload_parquet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("backfill")

DAYS = 365  # acima de 90 dias a API publica ja devolve granularidade diaria


def fetch_history(coin_id, vs_currency, api_url):
    # /coins/{id}/market_chart devolve series temporais de preco, market cap e volume
    url = f"{api_url}/coins/{coin_id}/market_chart"
    params = {"vs_currency": vs_currency, "days": DAYS}

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # cada lista vem como [[timestamp_ms, valor], ...] - alinhamos pelo timestamp
    mcaps = dict(data["market_caps"])
    vols = dict(data["total_volumes"])

    rows = []
    for ts_ms, preco in data["prices"]:
        rows.append(
            {
                "coin_id": coin_id,
                "data": datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc)
                .date()
                .isoformat(),
                "preco": preco,
                "market_cap": mcaps.get(ts_ms),
                "volume": vols.get(ts_ms),
            }
        )
    return pd.DataFrame(rows)


def main():
    config.validate()

    frames = []
    for coin in config.COINGECKO_COINS:
        logger.info("Buscando %d dias de %s", DAYS, coin)
        frames.append(
            fetch_history(coin, config.COINGECKO_VS_CURRENCY, config.COINGECKO_API_URL)
        )
        time.sleep(3)  # respeita o rate limit da API publica

    df = pd.concat(frames, ignore_index=True)
    df["vs_currency"] = config.COINGECKO_VS_CURRENCY

    now = datetime.now(timezone.utc)
    blob_path = f"coingecko/price_history/backfill_{now:%Y%m%dT%H%M%S}.parquet"
    uri = upload_parquet(df, config.GCS_BUCKET, blob_path)

    logger.info("ok: %d linhas -> %s", len(df), uri)


if __name__ == "__main__":
    main()

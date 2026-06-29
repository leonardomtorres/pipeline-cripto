import logging
from datetime import datetime, timezone

from sources.coingecko import fetch_market_data
from utils.config import config
from utils.gcs import upload_parquet

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("ingestion")


def build_blob_path():
    # particiona por data (year=/month=/day=) pra facilitar ler so uma fatia depois
    now = datetime.now(timezone.utc)
    return (
        f"coingecko/market_data/year={now:%Y}/month={now:%m}/day={now:%d}/"
        f"market_{now:%Y%m%dT%H%M%S}.parquet"
    )


def main():
    config.validate()

    df = fetch_market_data(
        coins=config.COINGECKO_COINS,
        vs_currency=config.COINGECKO_VS_CURRENCY,
        api_url=config.COINGECKO_API_URL,
    )

    uri = upload_parquet(df, config.GCS_BUCKET, build_blob_path())
    logger.info("ok: %s", uri)


if __name__ == "__main__":
    main()

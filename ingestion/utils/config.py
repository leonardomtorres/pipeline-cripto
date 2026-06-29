import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
    GCS_BUCKET = os.getenv("GCS_BUCKET")
    BQ_DATASET_RAW = os.getenv("BQ_DATASET_RAW", "cripto_raw")
    BQ_DATASET_ANALYTICS = os.getenv("BQ_DATASET_ANALYTICS", "cripto_analytics")
    GCP_LOCATION = os.getenv("GCP_LOCATION", "southamerica-east1")

    COINGECKO_API_URL = os.getenv(
        "COINGECKO_API_URL", "https://api.coingecko.com/api/v3"
    )
    COINGECKO_COINS = os.getenv(
        "COINGECKO_COINS", "bitcoin,ethereum,solana,cardano"
    ).split(",")
    COINGECKO_VS_CURRENCY = os.getenv("COINGECKO_VS_CURRENCY", "brl")

    @classmethod
    def validate(cls):
        faltando = [n for n in ("GCP_PROJECT_ID", "GCS_BUCKET") if not getattr(cls, n)]
        if faltando:
            raise EnvironmentError(
                f"Faltando variaveis no .env: {', '.join(faltando)}"
            )


config = Config()

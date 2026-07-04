import logging

import pandas as pd
from google.cloud import storage

from utils.config import config

logger = logging.getLogger(__name__)


def upload_parquet(df: pd.DataFrame, bucket_name, blob_path):
    # project explicito: em container nao ha gcloud config pra inferir o projeto
    client = storage.Client(project=config.GCP_PROJECT_ID)
    blob = client.bucket(bucket_name).blob(blob_path)

    blob.upload_from_string(
        df.to_parquet(index=False, engine="pyarrow"),
        content_type="application/octet-stream",
    )

    uri = f"gs://{bucket_name}/{blob_path}"
    logger.info("%d linhas -> %s", len(df), uri)
    return uri

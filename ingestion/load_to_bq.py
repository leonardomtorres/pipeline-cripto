import logging

from google.cloud import bigquery

from utils.config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("load_bq")


def load_parquet_to_bq(client, source_glob, table_name, cluster_field):
    """Carrega parquet do GCS numa tabela do BigQuery (particionada + clusterizada)."""
    table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET_RAW}.{table_name}"
    source_uri = f"gs://{config.GCS_BUCKET}/{source_glob}"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        # reconstroi a tabela do zero a cada carga (idempotente: sem duplicar)
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY
        ),
        clustering_fields=[cluster_field],
    )

    logger.info("Carregando %s -> %s", source_uri, table_id)
    job = client.load_table_from_uri(source_uri, table_id, job_config=job_config)
    job.result()  # espera o job terminar

    table = client.get_table(table_id)
    logger.info("ok: %d linhas em %s", table.num_rows, table_id)


def main():
    config.validate()
    client = bigquery.Client(
        project=config.GCP_PROJECT_ID, location=config.GCP_LOCATION
    )

    # snapshot de mercado (Fase 1)
    load_parquet_to_bq(
        client,
        "coingecko/market_data/*.parquet",
        "coingecko_market_data",
        "id",
    )
    # historico de precos (backfill)
    load_parquet_to_bq(
        client,
        "coingecko/price_history/*.parquet",
        "coingecko_price_history",
        "coin_id",
    )


if __name__ == "__main__":
    main()

import logging

from google.cloud import bigquery

from utils.config import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("load_bq")

TABLE = "coingecko_market_data"


def main():
    config.validate()

    # Client aponta pro projeto e regiao dos datasets (o job roda na mesma regiao)
    client = bigquery.Client(
        project=config.GCP_PROJECT_ID, location=config.GCP_LOCATION
    )

    table_id = f"{config.GCP_PROJECT_ID}.{config.BQ_DATASET_RAW}.{TABLE}"
    # o * casa com todos os parquet, inclusive dentro das pastas year=/month=/day=
    source_uri = f"gs://{config.GCS_BUCKET}/coingecko/market_data/*.parquet"

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.PARQUET,
        # reconstroi a tabela do zero a cada carga (idempotente: sem duplicar)
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        # particiona por dia -> query filtrando data le so a fatia, gasta menos
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY
        ),
        # agrupa fisicamente por moeda -> filtro por moeda fica mais barato
        clustering_fields=["id"],
    )

    logger.info("Carregando %s -> %s", source_uri, table_id)
    job = client.load_table_from_uri(source_uri, table_id, job_config=job_config)
    job.result()  # espera o job terminar

    table = client.get_table(table_id)
    logger.info("ok: %d linhas em %s", table.num_rows, table_id)


if __name__ == "__main__":
    main()

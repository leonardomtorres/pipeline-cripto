from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

# Esqueleto da DAG - os comandos de verdade entram na Fase 4

default_args = {
    "owner": "leo",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="pipeline_cripto",
    default_args=default_args,
    schedule="0 9 * * *",  # 09h todo dia
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["cripto", "elt"],
) as dag:

    extrair = BashOperator(
        task_id="extrair_coingecko",
        bash_command="echo 'TODO: rodar container de ingestao'",
    )

    carregar = BashOperator(
        task_id="carregar_bigquery",
        bash_command="echo 'TODO: GCS -> BigQuery'",
    )

    dbt_run = BashOperator(task_id="dbt_run", bash_command="echo 'TODO: dbt run'")
    dbt_test = BashOperator(task_id="dbt_test", bash_command="echo 'TODO: dbt test'")

    extrair >> carregar >> dbt_run >> dbt_test

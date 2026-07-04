from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

# Caminhos dentro do container (montados via docker-compose)
INGESTION = "/opt/airflow/ingestion"
DBT = "/opt/airflow/dbt"
DBT_BIN = "/home/airflow/dbt-venv/bin/dbt"  # dbt no venv isolado

default_args = {
    "owner": "leo",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="pipeline_cripto",
    default_args=default_args,
    schedule="0 9 * * *",  # todo dia as 09:00
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["cripto", "elt"],
) as dag:

    extrair = BashOperator(
        task_id="extrair_coingecko",
        bash_command=f"cd {INGESTION} && python main.py",
    )

    carregar = BashOperator(
        task_id="carregar_bigquery",
        bash_command=f"cd {INGESTION} && python load_to_bq.py",
    )

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command=(
            f"cd {DBT} && {DBT_BIN} clean --profiles-dir . "
            f"&& {DBT_BIN} deps --profiles-dir . "
            f"&& {DBT_BIN} run --profiles-dir ."
        ),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command=f"cd {DBT} && {DBT_BIN} test --profiles-dir .",
    )

    extrair >> carregar >> dbt_run >> dbt_test

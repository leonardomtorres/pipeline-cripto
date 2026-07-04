FROM apache/airflow:2.9.3-python3.11

# Dependencias da ingestao (compativeis com o Airflow)
COPY ingestion/requirements.txt /tmp/ing-requirements.txt
RUN pip install --no-cache-dir -r /tmp/ing-requirements.txt

# dbt num venv ISOLADO pra nao brigar com as dependencias do Airflow.
# Na DAG chamamos ele pelo caminho completo: /home/airflow/dbt-venv/bin/dbt
RUN python -m venv /home/airflow/dbt-venv && \
    /home/airflow/dbt-venv/bin/pip install --no-cache-dir dbt-bigquery==1.8.2

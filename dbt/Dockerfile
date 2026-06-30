FROM python:3.11-slim

WORKDIR /dbt

RUN pip install --no-cache-dir dbt-bigquery==1.8.2

ENV DBT_PROFILES_DIR=/dbt

ENTRYPOINT ["dbt"]
CMD ["--version"]

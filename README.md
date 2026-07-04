# pipeline-cripto

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![BigQuery](https://img.shields.io/badge/BigQuery-GCP-669DF6?logo=googlecloud&logoColor=white)
![dbt](https://img.shields.io/badge/dbt-1.8-FF694B?logo=dbt&logoColor=white)
![Airflow](https://img.shields.io/badge/Airflow-2.9-017CEE?logo=apacheairflow&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?logo=docker&logoColor=white)

Pipeline batch (ELT) que coleta cotações de criptomoedas do CoinGecko, guarda no
Google Cloud Storage, carrega no BigQuery e transforma com dbt. Projeto de estudo
de engenharia de dados.

## Objetivo

Construir um pipeline de dados de ponta a ponta como rodaria de verdade num time:
pegar um dado externo, guardar de forma confiável, transformar com qualidade e
entregar pronto pra análise — tudo automatizado e reproduzível.

Usei criptomoedas porque é um assunto que curto e que gera dado de verdade: série
temporal, preços que variam e métricas de negócio (retorno diário, volatilidade)
que rendem transformação. Mas o ponto do projeto não é "saber cripto" nem "usar a
ferramenta X" — é mostrar que eu entendo **por que** cada camada de um pipeline
existe e **quando** cada tecnologia faz sentido.

## Arquitetura

![Arquitetura do pipeline](docs/arquitetura.svg)

Fluxo resumido: CoinGecko -> Python (ingestao) -> GCS (raw) -> BigQuery
(staging -> intermediate -> marts via dbt) -> Looker Studio. Airflow orquestra
e Docker isola o ambiente.

## Dashboard

Dashboard final no Looker Studio, conectado nas tabelas analiticas do dbt.
Cotacao das 4 principais criptos no ultimo ano (escala logaritmica para comparar
ativos de precos bem diferentes).

![Dashboard de criptomoedas](docs/dashboard.png)

## Orquestracao (Airflow)

A DAG `pipeline_cripto` roda o fluxo completo na ordem, com retry:
`extrair_coingecko -> carregar_bigquery -> dbt_run -> dbt_test`. Sobe local via
`docker compose up airflow` (standalone).

![DAG do Airflow](docs/airflow_dag.png)

## Stack e o porquê de cada escolha

- **BigQuery** como warehouse: serverless, colunar e o free tier (1 TB/mes de query)
  cobre de sobra o volume do projeto.
- **GCS como camada raw**: guardo o dado cru antes de transformar. Se a lógica do dbt
  tiver bug, dá pra reprocessar sem bater de novo na API.
- **dbt** pra transformação: SQL versionado, modelagem em camadas e testes.
- **Docker / docker-compose**: roda igual na minha máquina e no CI, sem dor de cabeça
  com dependências.
- **Python** na ingestão: a cotação é um snapshot diário (batch), então não faz sentido
  montar streaming aqui.
- **Airflow** pra orquestrar (agendamento + retry) — sobe local via docker-compose.
- **Looker Studio** no dashboard: conecta direto no BigQuery, sem custo.
- **GitHub Actions** pra CI (lint da ingestão a cada push).

Duas decisões que valem comentar:
- **Autenticação via ADC** (`gcloud auth application-default login`), não chave de
  conta de serviço. É a prática recomendada do Google e evita ter um segredo pra vazar.
- **Sem Terraform** de propósito — pra um projeto de escopo único, criar bucket e
  datasets pelo `gcloud`/`bq` (ver `infra/setup.sh`) resolve sem a complexidade de IaC.

## Estrutura

```
ingestion/      extracao CoinGecko (main + backfill) e carga no BigQuery
dbt/            modelos (staging -> intermediate -> marts) e testes
orchestration/  dag do airflow
infra/          setup do gcp (bucket + datasets)
docs/           diagramas e prints
.github/        ci (github actions)
```

## Como rodar

Pré-requisitos: conta no GCP, `gcloud` CLI, Docker e Python 3.11+.

```bash
# 1. Autenticar no GCP (ADC, sem chave)
gcloud auth application-default login
gcloud auth application-default set-quota-project SEU_PROJECT_ID

# 2. Configurar variaveis
cp .env.example .env          # preencher GCP_PROJECT_ID e GCS_BUCKET

# 3. Criar bucket e datasets
gcloud storage buckets create gs://SEU_BUCKET --location=southamerica-east1
bq mk --dataset SEU_PROJECT_ID:cripto_raw
bq mk --dataset SEU_PROJECT_ID:cripto_analytics

# 4. Rodar as etapas (local, num venv)
python ingestion/main.py          # snapshot atual  -> GCS
python ingestion/backfill.py      # 1 ano historico -> GCS
python ingestion/load_to_bq.py    # GCS -> BigQuery
cd dbt && dbt run --profiles-dir . && dbt test --profiles-dir .

# 5. Ou orquestrar tudo com Airflow
cp ~/.config/gcloud/application_default_credentials.json credentials/adc.json
docker compose up airflow --build   # http://localhost:8080, disparar a DAG
```

## Status

- [x] Fase 0 - estrutura, docker, config
- [x] Fase 1 - ingestao CoinGecko -> GCS
- [x] Fase 2 - carga GCS -> BigQuery
- [x] Fase 3 - modelos dbt + testes
- [x] Fase 4 - airflow
- [x] Fase 5 - dashboard

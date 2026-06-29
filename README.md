# pipeline-cripto

Pipeline batch (ELT) que coleta cotações de criptomoedas do CoinGecko, guarda no
Google Cloud Storage, carrega no BigQuery e transforma com dbt. Projeto de estudo
de engenharia de dados.

## Arquitetura

![Arquitetura do pipeline](docs/arquitetura.svg)

Fluxo resumido: CoinGecko -> Python (ingestao) -> GCS (raw) -> BigQuery
(staging -> intermediate -> marts via dbt) -> Looker Studio. Airflow orquestra
e Docker isola o ambiente.

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
- **Airflow** pra orquestrar (agendamento + retry).

Não usei Terraform de propósito — pra um projeto de escopo único o `infra/setup.sh`
resolve criando bucket e datasets pelo gcloud/bq.

## Estrutura

```
ingestion/      extracao CoinGecko -> GCS
dbt/            modelos e testes
orchestration/  dag do airflow
infra/          setup do gcp
```

## Como rodar

```bash
cp .env.example .env          # preencher os valores
# colocar a chave do GCP em credentials/gcp-key.json (ver credentials/README.md)

source .env && bash infra/setup.sh

docker compose run --rm ingestion
docker compose run --rm dbt run
docker compose run --rm dbt test
```

## Status

- [x] Fase 0 - estrutura, docker, config
- [ ] Fase 1 - ingestao CoinGecko -> GCS
- [ ] Fase 2 - carga GCS -> BigQuery
- [ ] Fase 3 - modelos dbt + testes
- [ ] Fase 4 - airflow
- [ ] Fase 5 - dashboard + ci

#!/usr/bin/env bash
# Cria bucket + datasets no GCP. Precisa do gcloud/bq autenticados.
# Uso: source ../.env && bash setup.sh
set -euo pipefail

: "${GCP_PROJECT_ID:?carregue o .env primeiro}"
: "${GCS_BUCKET:?defina GCS_BUCKET}"
: "${GCP_LOCATION:=southamerica-east1}"
: "${BQ_DATASET_RAW:=cripto_raw}"
: "${BQ_DATASET_ANALYTICS:=cripto_analytics}"

gcloud config set project "$GCP_PROJECT_ID"

gcloud storage buckets create "gs://$GCS_BUCKET" --location="$GCP_LOCATION" \
  || echo "bucket ja existe"

bq --location="$GCP_LOCATION" mk --dataset "$GCP_PROJECT_ID:$BQ_DATASET_RAW" \
  || echo "dataset raw ja existe"
bq --location="$GCP_LOCATION" mk --dataset "$GCP_PROJECT_ID:$BQ_DATASET_ANALYTICS" \
  || echo "dataset analytics ja existe"

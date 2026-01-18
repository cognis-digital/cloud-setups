#!/usr/bin/env bash
# Bootstrap a GCP project for containerized apps.
set -euo pipefail
: "${PROJECT_ID:?set PROJECT_ID}"
gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
gcloud artifacts repositories create cognis --repository-format=docker --location=us-central1 || true
echo "Deploy: gcloud run deploy app --source . --region us-central1 --allow-unauthenticated"

#!/usr/bin/env bash
# Bootstrap Azure Container Apps.
set -euo pipefail
: "${RG:=cognis-rg}"; LOC="${LOC:=eastus}"
az group create -n "$RG" -l "$LOC"
az containerapp env create -n cognis-env -g "$RG" -l "$LOC"
az containerapp create -n cognis-app -g "$RG" --environment cognis-env \
  --image ghcr.io/cognis-digital/app:latest --target-port 8000 --ingress external

#!/usr/bin/env bash
set -euo pipefail

: "${DEPLOY_WEBHOOK_URL:?DEPLOY_WEBHOOK_URL secret is required}"
: "${DEPLOY_PAYLOAD:=deploy}"

echo "Triggering remote deployment..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d "{\"ref\":\"${GITHUB_SHA:-local}\",\"payload\":\"${DEPLOY_PAYLOAD}\"}" \
  "$DEPLOY_WEBHOOK_URL"

echo "Deployment request sent."


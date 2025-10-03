#!/usr/bin/env bash
# Purpose: Fix 401 on Proton Bot webhook by syncing EBOT_API_TOKEN/EBOT_HMAC_SECRET from GitLab into the bot runtime
# Supports: systemd OR docker-compose (choose one via EBOT_DEPLOY_TARGET)
# Safe: never prints full secrets; strict error handling.

set -euo pipefail

########################################
# ======= REQUIRED USER INPUTS ======= #
########################################
# GitLab access (project: protonrent-group/ProtonBackend)
: "${GITLAB_PAT:?Set GITLAB_PAT=glpat-... (GitLab Personal Access Token with api scope)}"
PROJECT_PATH_ENC="protonrent-group%2FProtonBackend"  # do not change

# Where to send health/webhook checks (bot external/base URL)
: "${EBOT_API_URL:?Set EBOT_API_URL, e.g. http://158.160.46.65:8000}"
: "${EBOT_WEBHOOK_PATH:=/notify-webhook}"  # Updated for new endpoint

# How to deploy secrets into bot runtime — CHOOSE ONE:
#   EBOT_DEPLOY_TARGET=systemd  OR  EBOT_DEPLOY_TARGET=compose
: "${EBOT_DEPLOY_TARGET:?Set EBOT_DEPLOY_TARGET=systemd or compose}"

# For systemd:
SERVICE_NAME="${SERVICE_NAME:-proton-bot}"   # Updated service name

# For docker-compose:
COMPOSE_DIR="${COMPOSE_DIR:-}"         # e.g. /opt/proton-bot
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
COMPOSE_SERVICE="${COMPOSE_SERVICE:-proton-bot}"   # Updated service name

########################################
# ======= CONSTANTS / HELPERS ======== #
########################################
API_VARS_BASE="https://gitlab.com/api/v4/projects/${PROJECT_PATH_ENC}/variables"
HDR=(-H "PRIVATE-TOKEN: ${GITLAB_PAT}")

mask() { v="$1"; [ -z "$v" ] && echo "unset" || echo "${v:0:4}…${v: -4}"; }
json_val() { awk -F\" '/"value":/ {print $4; exit}'; }

fetch_var() {
  local key="$1"
  local code
  code=$(curl -sS -o /dev/null -w "%{http_code}" "${HDR[@]}" "${API_VARS_BASE}/${key}")
  if [ "$code" != "200" ]; then
    echo "FATAL: GitLab var ${key} missing (HTTP ${code}). Add it in CI/CD → Variables and retry." >&2
    exit 1
  fi
  curl -sS "${HDR[@]}" "${API_VARS_BASE}/${key}" | json_val
}

########################################
# ========== STEP 1: GET SECRETS ===== #
########################################
echo "== [1/6] Fetch secrets from GitLab =="
EBOT_API_TOKEN="$(fetch_var EBOT_API_TOKEN)"
EBOT_HMAC_SECRET="$(fetch_var EBOT_HMAC_SECRET)"
echo "EBOT_API_TOKEN: $(mask "$EBOT_API_TOKEN")"
echo "EBOT_HMAC_SECRET: $(mask "$EBOT_HMAC_SECRET")"

########################################
# == STEP 2: APPLY TO RUNTIME (BOT) == #
########################################
echo "== [2/6] Apply secrets to Proton Bot runtime (${EBOT_DEPLOY_TARGET}) =="

case "$EBOT_DEPLOY_TARGET" in
  systemd)
    # Write systemd override with env
    sudo mkdir -p "/etc/systemd/system/${SERVICE_NAME}.service.d"
    sudo tee "/etc/systemd/system/${SERVICE_NAME}.service.d/override.conf" >/dev/null <<EOF
[Service]
Environment=EBOT_API_TOKEN=${EBOT_API_TOKEN}
Environment=EBOT_HMAC_SECRET=${EBOT_HMAC_SECRET}
Environment=LARAVEL_BEARER_TOKEN=${EBOT_API_TOKEN}
Environment=WEBHOOK_SECRET=${EBOT_HMAC_SECRET}
EOF
    sudo chmod 600 "/etc/systemd/system/${SERVICE_NAME}.service.d/override.conf"

    # Reload + restart
    sudo systemctl daemon-reload
    sudo systemctl restart "${SERVICE_NAME}"
    sudo systemctl is-active "${SERVICE_NAME}" >/dev/null || { sudo systemctl status "${SERVICE_NAME}" --no-pager -l; exit 1; }
    ;;

  compose)
    [ -n "$COMPOSE_DIR" ] || { echo "FATAL: Set COMPOSE_DIR=/path/to/compose"; exit 1; }
    cd "$COMPOSE_DIR"

    # Ensure .env has both vars (idempotent)
    touch .env
    chmod 600 .env
    
    # Update or add EBOT_API_TOKEN
    if grep -q '^EBOT_API_TOKEN=' .env; then
      sed -i.bak 's/^EBOT_API_TOKEN=.*/EBOT_API_TOKEN=REPLACE_ME/' .env && \
      sed -i.bak "s/EBOT_API_TOKEN=REPLACE_ME/EBOT_API_TOKEN=${EBOT_API_TOKEN}/" .env
    else
      echo "EBOT_API_TOKEN=${EBOT_API_TOKEN}" >> .env
    fi
    
    # Update or add EBOT_HMAC_SECRET
    if grep -q '^EBOT_HMAC_SECRET=' .env; then
      sed -i.bak 's/^EBOT_HMAC_SECRET=.*/EBOT_HMAC_SECRET=REPLACE_ME/' .env && \
      sed -i.bak "s/EBOT_HMAC_SECRET=REPLACE_ME/EBOT_HMAC_SECRET=${EBOT_HMAC_SECRET}/" .env
    else
      echo "EBOT_HMAC_SECRET=${EBOT_HMAC_SECRET}" >> .env
    fi
    
    # Update legacy vars for backward compatibility
    if grep -q '^LARAVEL_BEARER_TOKEN=' .env; then
      sed -i.bak 's/^LARAVEL_BEARER_TOKEN=.*/LARAVEL_BEARER_TOKEN=REPLACE_ME/' .env && \
      sed -i.bak "s/LARAVEL_BEARER_TOKEN=REPLACE_ME/LARAVEL_BEARER_TOKEN=${EBOT_API_TOKEN}/" .env
    else
      echo "LARAVEL_BEARER_TOKEN=${EBOT_API_TOKEN}" >> .env
    fi
    
    if grep -q '^WEBHOOK_SECRET=' .env; then
      sed -i.bak 's/^WEBHOOK_SECRET=.*/WEBHOOK_SECRET=REPLACE_ME/' .env && \
      sed -i.bak "s/WEBHOOK_SECRET=REPLACE_ME/WEBHOOK_SECRET=${EBOT_HMAC_SECRET}/" .env
    else
      echo "WEBHOOK_SECRET=${EBOT_HMAC_SECRET}" >> .env
    fi

    # Clean up backup files
    rm -f .env.bak

    # Up with compose (auto-detect docker/podman)
    if command -v podman >/dev/null 2>&1 && podman --version >/dev/null 2>&1; then
      COMPOSE="podman compose"
    elif command -v docker >/dev/null 2>&1; then
      COMPOSE="docker compose"
    else
      echo "FATAL: neither docker nor podman found." >&2; exit 1
    fi

    $COMPOSE -f "$COMPOSE_FILE" up -d --no-build "${COMPOSE_SERVICE}"
    ;;

  *)
    echo "FATAL: EBOT_DEPLOY_TARGET must be 'systemd' or 'compose'." >&2
    exit 1
    ;;
esac

########################################
# ========== STEP 3: HEALTH ========== #
########################################
echo "== [3/6] Health check with Bearer =="
HLT_CODE=$(curl -sS -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${EBOT_API_TOKEN}" "${EBOT_API_URL%/}/health")
echo "Proton Bot /health → HTTP ${HLT_CODE}"
if [ "$HLT_CODE" != "200" ]; then
  echo "FATAL: Health is not 200. Check service logs and that runtime sees EBOT_API_TOKEN." >&2
  exit 1
fi

########################################
# == STEP 4: SIGNED WEBHOOK REQUEST == #
########################################
echo "== [4/6] Signed webhook POST (Bearer+HMAC over FULL payload) =="

CID="$(uuidgen || cat /proc/sys/kernel/random/uuid)"
IDEM="$(uuidgen || cat /proc/sys/kernel/random/uuid)"
NOW="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

PAYLOAD=$(cat <<JSON
{"event_id":"test-${IDEM}","event_type":"order.notification.test","aggregate_id":"test-order","aggregate_type":"Order","event_data":{"telegram_id":"123456789","order_data":{"order_id":"test-123","vehicle_type":"Экскаватор","location":"Москва","date_time":"2024-01-01 10:00","price":"50000 руб.","order_url":"https://app.protonrent.ru/orders/test-123"}},"correlation_id":"${CID}","idempotency_key":"${IDEM}","timestamp":"${NOW}"}
JSON
)

SIG_HEX=$(printf '%s' "${PAYLOAD}" | openssl dgst -sha256 -hmac "${EBOT_HMAC_SECRET}" -binary | xxd -p -c 256)
WEBHOOK_URL="${EBOT_API_URL%/}${EBOT_WEBHOOK_PATH}"

RESP1=$(curl -sS -w "\n%{http_code}" -X POST "${WEBHOOK_URL}" \
  -H "Authorization: Bearer ${EBOT_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-Id: ${CID}" \
  -H "Idempotency-Key: ${IDEM}" \
  -H "X-Signature: sha256=${SIG_HEX}" \
  -H "X-Signature-Alg: HMAC-SHA256" \
  --data "${PAYLOAD}" || true)

CODE1=$(echo "$RESP1" | tail -n1)
BODY1=$(echo "$RESP1" | sed '$d' | head -c 300)
echo "Webhook #1 → HTTP ${CODE1} ; cid=${CID} ; idem=${IDEM}"
echo "Response (first 300 chars): ${BODY1}"

########################################
# == STEP 5: IDEMPOTENCY RE-POST ===== #
########################################
echo "== [5/6] Idempotency re-check (same payload/headers) =="
RESP2=$(curl -sS -w "\n%{http_code}" -X POST "${WEBHOOK_URL}" \
  -H "Authorization: Bearer ${EBOT_API_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "X-Correlation-Id: ${CID}" \
  -H "Idempotency-Key: ${IDEM}" \
  -H "X-Signature: sha256=${SIG_HEX}" \
  -H "X-Signature-Alg: HMAC-SHA256" \
  --data "${PAYLOAD}" || true)

CODE2=$(echo "$RESP2" | tail -n1)
BODY2=$(echo "$RESP2" | sed '$d' | head -c 300)
echo "Webhook #2 → HTTP ${CODE2}"

########################################
# ======= STEP 6: SUMMARY / HINT ===== #
########################################
echo "== [6/6] Summary =="
ok_health=$([ "$HLT_CODE" = "200" ] && echo OK || echo FAIL)
ok_post=$([ "$CODE1" = "200" ] && echo OK || echo FAIL)
ok_idem=$([ "$CODE2" = "200" ] && echo OK || echo WARN)

echo "Health      : ${ok_health} (HTTP ${HLT_CODE})"
echo "Webhook #1  : ${ok_post}   (HTTP ${CODE1})"
echo "Idempotency : ${ok_idem}   (HTTP ${CODE2})"

if [ "$ok_health" = "OK" ] && [ "$ok_post" = "OK" ]; then
  echo "VERDICT: ✅ FIXED — Bearer+HMAC accepted. 401 resolved."
  echo ""
  echo "🎉 Proton Bot webhook is now properly configured!"
  echo "📡 Endpoint: ${WEBHOOK_URL}"
  echo "🔐 Authentication: Bearer + HMAC-SHA256"
  echo "🔄 Idempotency: Supported"
  exit 0
fi

echo "VERDICT: ❌ NOT FIXED"
if [ "$CODE1" = "401" ] || [ "$CODE1" = "403" ]; then
  echo "Likely cause: Authorization header not reaching app OR runtime token mismatch."
  echo "Check:"
  echo "  • Runtime token: print fingerprint at app start (sha256 first/last 6 chars)."
  echo "  • Reverse proxy: nginx must forward Authorization:"
  echo "      proxy_set_header Authorization \$http_authorization;"
  echo "  • Service restart: ensure new environment variables are loaded"
elif [ "$CODE1" = "400" ]; then
  echo "Likely cause: bad HMAC or invalid payload structure."
  echo "Check:"
  echo "  • HMAC signature is over FULL raw JSON body"
  echo "  • EBOT_HMAC_SECRET matches between GitLab and bot runtime"
  echo "  • Payload structure matches expected Laravel event format"
elif [ "$CODE1" = "404" ]; then
  echo "Likely cause: wrong EBOT_WEBHOOK_PATH='${EBOT_WEBHOOK_PATH}'."
  echo "Available endpoints: /notify, /notify-legacy, /notify-webhook, /health"
else
  echo "Inspect bot logs for cid=${CID}, idem=${IDEM}."
fi
exit 1

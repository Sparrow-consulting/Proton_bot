#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$APP_DIR"

NAME="tg-bot"
PORT="8000"
IMAGE_TAG="tg-bot:latest"
ENV_FILE="$APP_DIR/.env"

# выбрать docker или podman
if command -v docker >/dev/null 2>&1; then
  CTR="docker"
elif command -v podman >/dev/null 2>&1; then
  CTR="podman"
else
  echo "ERROR: neither docker nor podman found"; exit 1
fi

echo ">> runtime: $CTR"
echo ">> stopping/removing old container (if any)"
$CTR stop "$NAME" || true
$CTR rm "$NAME" || true

# Force kill any container using the port
echo ">> checking for containers using port $PORT"
PORT_CONTAINERS=$($CTR ps -q --filter "publish=$PORT" 2>/dev/null || true)
if [ -n "$PORT_CONTAINERS" ]; then
  echo ">> found containers using port $PORT, stopping them"
  echo "$PORT_CONTAINERS" | xargs -r $CTR stop || true
  echo "$PORT_CONTAINERS" | xargs -r $CTR rm || true
fi

# Additional cleanup for any orphaned containers
echo ">> cleaning up orphaned containers"
$CTR container prune -f || true

echo ">> building image $IMAGE_TAG"
$CTR build -t "$IMAGE_TAG" "$APP_DIR"

echo ">> running container $NAME"
# Check if port is still in use
if command -v netstat >/dev/null 2>&1; then
  if netstat -tuln | grep -q ":$PORT "; then
    echo ">> WARNING: Port $PORT is still in use, trying to free it"
    # Try to kill any process using the port
    if command -v lsof >/dev/null 2>&1; then
      lsof -ti:$PORT | xargs -r kill -9 || true
    fi
    sleep 2
  fi
fi

$CTR run -d --name "$NAME" --restart unless-stopped --env-file "$ENV_FILE" -p "$PORT:$PORT" "$IMAGE_TAG"

echo ">> tailing logs (up to 45s)"
if command -v timeout >/dev/null 2>&1; then
  timeout 45s $CTR logs -f "$NAME" || $CTR logs --tail 200 "$NAME" || true
else
  $CTR logs --tail 200 "$NAME" || true
fi

echo ">> done."

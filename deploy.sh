#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$APP_DIR"

NAME="tg-bot"
HOST_PORT="${HOST_PORT:-8000}"
APP_PORT="${APP_PORT:-8000}"
IMAGE_TAG="${IMAGE_TAG:-tg-bot:latest}"
ENV_FILE="$APP_DIR/.env"

echo ">> Deployment parameters:"
echo ">>   HOST_PORT: $HOST_PORT"
echo ">>   APP_PORT: $APP_PORT"
echo ">>   IMAGE_TAG: $IMAGE_TAG"

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

# Force kill any container using the host port
echo ">> checking for containers using port $HOST_PORT"
PORT_CONTAINERS=$($CTR ps -q --filter "publish=$HOST_PORT" 2>/dev/null || true)
if [ -n "$PORT_CONTAINERS" ]; then
  echo ">> found containers using port $HOST_PORT, stopping them"
  echo "$PORT_CONTAINERS" | xargs -r $CTR stop || true
  echo "$PORT_CONTAINERS" | xargs -r $CTR rm || true
fi

# Check for any process using the port and kill it
echo ">> checking for processes using port $HOST_PORT"
if command -v lsof >/dev/null 2>&1; then
  PORT_PIDS=$(lsof -ti:$HOST_PORT 2>/dev/null || true)
  if [ -n "$PORT_PIDS" ]; then
    echo ">> found processes using port $HOST_PORT, killing them"
    echo "$PORT_PIDS" | xargs -r kill -9 || true
    sleep 2
  fi
fi

# Additional cleanup for any orphaned containers
echo ">> cleaning up orphaned containers"
$CTR container prune -f || true

echo ">> building image $IMAGE_TAG"
$CTR build -t "$IMAGE_TAG" "$APP_DIR"

echo ">> running container $NAME"
# Final check if port is still in use
if command -v lsof >/dev/null 2>&1; then
  PORT_PIDS=$(lsof -ti:$HOST_PORT 2>/dev/null || true)
  if [ -n "$PORT_PIDS" ]; then
    echo ">> WARNING: Port $HOST_PORT is still in use, trying to free it"
    echo "$PORT_PIDS" | xargs -r kill -9 || true
    sleep 3
  fi
fi

# Run the container with the specified port mapping
echo ">> Starting container with port mapping $HOST_PORT:$APP_PORT"
$CTR run -d --name "$NAME" --restart unless-stopped \
  --env-file "$ENV_FILE" -p "${HOST_PORT}:${APP_PORT}" "$IMAGE_TAG"

echo ">> Container started successfully on port $HOST_PORT -> $APP_PORT"

echo ">> tailing logs (up to 45s)"
if command -v timeout >/dev/null 2>&1; then
  timeout 45s $CTR logs -f "$NAME" || $CTR logs --tail 200 "$NAME" || true
else
  $CTR logs --tail 200 "$NAME" || true
fi

echo ">> done."

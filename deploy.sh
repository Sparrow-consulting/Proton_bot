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

echo ">> building image $IMAGE_TAG"
$CTR build -t "$IMAGE_TAG" "$APP_DIR"

echo ">> running container $NAME"
$CTR run -d --name "$NAME" --restart unless-stopped --env-file "$ENV_FILE" -p "$PORT:$PORT" "$IMAGE_TAG"

echo ">> tailing logs (up to 45s)"
if command -v timeout >/dev/null 2>&1; then
  timeout 45s $CTR logs -f "$NAME" || $CTR logs --tail 200 "$NAME" || true
else
  $CTR logs --tail 200 "$NAME" || true
fi

echo ">> done."

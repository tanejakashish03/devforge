#!/usr/bin/env bash
# Pull latest code, build the image, and roll it out to green then blue
# (nginx sends traffic to green :5002 and falls back to blue :5001).
set -euo pipefail

cd "$(dirname "$0")/.."
ENV_FILE=/opt/devforge/devforge.env
DATA_DIR=/opt/devforge/data
BRANCH="${BRANCH:-master}"

[ -r "$ENV_FILE" ] || { echo "Missing or unreadable $ENV_FILE (needs GITHUB_TOKEN=...)"; exit 1; }

git fetch origin
git reset --hard "origin/$BRANCH"
SHA="$(git rev-parse --short HEAD)"

mkdir -p "$DATA_DIR"
docker build --pull -t "devforge:$SHA" -t devforge:latest .

deploy() {
  local name="$1" port="$2" code
  docker rm -f "$name" >/dev/null 2>&1 || true
  docker run -d --name "$name" --restart unless-stopped \
    -p "$port:5503" \
    --env-file "$ENV_FILE" \
    -e DEVFORGE_VERSION="${name#devforge-}" \
    -v "$DATA_DIR:/app/instance" \
    "devforge:$SHA" >/dev/null
  for _ in $(seq 1 30); do
    code="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:$port/" || true)"
    if [[ "$code" =~ ^[234] ]]; then echo "$name healthy on :$port ($SHA)"; return 0; fi
    sleep 2
  done
  echo "$name failed its health check:"; docker logs --tail 50 "$name"; return 1
}

deploy devforge-green 5002   # if this fails, set -e stops here and blue keeps serving
deploy devforge-blue  5001
docker image prune -f >/dev/null
echo "Deployed $SHA"

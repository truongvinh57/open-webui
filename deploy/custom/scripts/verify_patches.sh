#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BASE_IMAGE=ghcr.io/open-webui/open-webui@sha256:72c0ba641ba75e7aa52655cb242570906ececd09b1140fb736483038a22b3228
BASE_SHA256=42380f32babc369cda496fe44017c25d3b6a417db1da57e97f3119a4f382448a
MIDDLEWARE=/app/backend/open_webui/utils/middleware.py
FILES=/app/backend/open_webui/routers/files.py
IMAGE=open-webui-ntc:0.11.0-terminal-v1

actual_base=$(docker run --rm --entrypoint sha256sum "$BASE_IMAGE" "$MIDDLEWARE" | awk '{print $1}')
[[ $actual_base == "$BASE_SHA256" ]] || {
    echo "middleware base drifted: expected $BASE_SHA256, got $actual_base" >&2
    exit 1
}

docker build --pull=false --tag "$IMAGE" "$ROOT"
docker run --rm --entrypoint sh "$IMAGE" -c \
    "grep -q 'NTC terminal tool-result handshake' '$MIDDLEWARE' \
     && grep -q \"new_form_data\['tool_choice'\] = 'none'\" '$MIDDLEWARE' \
     && grep -q 'Do not emit tool calls, DSML, XML, or tool syntax' '$MIDDLEWARE' \
     && grep -q 'NTC nonterminal next-call handshake' '$MIDDLEWARE' \
     && grep -q 'Trusted server-side tool results require continuation' '$MIDDLEWARE' \
     && grep -q 'NTC patch (cosmetic): echo extracted content' '$FILES' \
     && python -m py_compile '$MIDDLEWARE' '$FILES'"

rendered_image=$(docker compose --project-directory "$ROOT" config --format json \
    | python3 -c 'import json,sys; print(json.load(sys.stdin)["services"]["open-webui"]["image"])')
[[ $rendered_image == "$IMAGE" ]] || {
    echo "rendered OpenWebUI image drifted: $rendered_image" >&2
    exit 1
}

echo "OpenWebUI 0.11.0 patch verifier: PASS base_sha256=$BASE_SHA256 image=$IMAGE"

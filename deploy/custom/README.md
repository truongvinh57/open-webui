# Custom Open WebUI 0.11.0 deployment

This directory builds `open-webui-ntc:0.11.0-terminal-v1` from the official Open
WebUI `0.11.0` image pinned by digest
(`ghcr.io/open-webui/open-webui@sha256:72c0ba641ba75e7aa52655cb242570906ececd09b1140fb736483038a22b3228`).
Three exact-source patches are applied, each gated by a sha256 check of the
audited upstream file; the build fails when the upstream source drifts:

| Patch | File | Purpose |
|---|---|---|
| `patches/open_webui/utils/middleware-terminal-result.patch` | `utils/middleware.py` | NTC terminal tool-result handshake: a tool result carrying `terminal: true / retryable: false / action_required: answer_now` strips tools, sets `tool_choice: none` and forces the final answer. |
| `patches/open_webui/utils/middleware-nonterminal-next-call.patch` | `utils/middleware.py` | NTC nonterminal next-call handshake: navigation-stage results cannot end the turn; signed `next_call` contracts are fed back as a continuation system message. |
| `patches/open_webui/routers/files-content-echo.patch` | `routers/files.py` | Cosmetic: echo extracted content in the final SSE event of `/api/v1/files/{id}/process/status` so the chat-input file tile shows real content. |

The `terminal`/`nonterminal` wording refers to the NTC RAG tool-result contract,
not the Open Terminal sidecar. **Open Terminal follows the upstream default** —
`ghcr.io/open-webui/open-terminal@sha256:25c5b82d…` (v0.11.20), no patch touches
it.

## Runtime

The Compose project is named `open-webui` and reuses the existing
`open-webui_postgres`, `open-webui_redis`, `open-webui_open-webui` and
`open-webui_open-terminal` volumes, so the 0.10.2 → 0.11.0 upgrade keeps all
chats, files, admin settings and embeddings. Postgres stays on
`pgvector/pgvector:pg16`, Redis on `redis:7.4.10-alpine`. External networks
`edge`, `litellm_default`, `firecrawl`, `mineru_default` and `ntc-rag` must
exist before the stack starts.

Create the ignored deployment environment and TLS files before the first start:

```bash
cp .env.example .env
chmod 600 .env
cp -r <secrets-dir>/newtecons.vn .   # TLS key material for ai-dev.newtecons.vn (gitignored)
docker compose config --quiet
docker compose build --pull open-webui
docker compose up -d --wait
```

## Upgrade checklist (0.10.2 → 0.11.0)

1. Back up everything: `pg_dump` of the `openwebui` DB and the
   `open-webui_open-webui` volume (`/app/backend/data`).
2. Pre-check duplicate case-insensitive emails — the `f0bd01a18a3d` migration
   aborts startup if any exist:
   `SELECT lower(email), count(*) FROM "user" WHERE email IS NOT NULL GROUP BY 1 HAVING count(*) > 1;`
3. Migrations are one-way: keep the 0.10.2 image for rollback (restore the
   backup from step 1). No rolling multi-worker upgrades.
4. Plan a longer first boot (data-backfill migration streams in batches).
5. After boot verify the footer version, hard-refresh browsers (UI rebuilt),
   and confirm admin settings under Settings → Admin. Known upstream regressions
   to watch: Open Terminal access (issue #27621) and web fetch of internal
   hosts (stricter address checks).

## Validation

```bash
python3 -m unittest discover -s tests -v
docker compose config --quiet
bash scripts/verify_patches.sh
```

`verify_patches.sh` re-hashes the base image's `middleware.py` against the
pinned gate, rebuilds the custom image, greps every patch marker inside the
built image, `py_compile`s the patched sources and checks the rendered Compose
image name. Run it after every Open WebUI or patch change.

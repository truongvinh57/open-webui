FROM ghcr.io/open-webui/open-webui@sha256:72c0ba641ba75e7aa52655cb242570906ececd09b1140fb736483038a22b3228

ARG MIDDLEWARE_SHA256=42380f32babc369cda496fe44017c25d3b6a417db1da57e97f3119a4f382448a
COPY patches/open_webui/utils/middleware-terminal-result.patch /tmp/middleware-terminal-result.patch
RUN echo "${MIDDLEWARE_SHA256}  /app/backend/open_webui/utils/middleware.py" | sha256sum -c - \
    && patch --batch --forward -d /app/backend -p1 < /tmp/middleware-terminal-result.patch \
    && grep -q "NTC terminal tool-result handshake" /app/backend/open_webui/utils/middleware.py \
    && rm /tmp/middleware-terminal-result.patch

ARG TERMINAL_PATCHED_MIDDLEWARE_SHA256=a7cf6628f7a4f0d22421b6da8ca70056525112e953269a241d7ad4232ede0130
COPY patches/open_webui/utils/middleware-nonterminal-next-call.patch /tmp/middleware-nonterminal-next-call.patch
RUN echo "${TERMINAL_PATCHED_MIDDLEWARE_SHA256}  /app/backend/open_webui/utils/middleware.py" | sha256sum -c - \
    && patch --batch --forward -d /app/backend -p1 < /tmp/middleware-nonterminal-next-call.patch \
    && grep -q "NTC nonterminal next-call handshake" /app/backend/open_webui/utils/middleware.py \
    && rm /tmp/middleware-nonterminal-next-call.patch

ARG FILES_SHA256=86181bc1919597d1f8395c6d2ff01085e5c1c2b190ceae68181b3dbb0d1f361d
COPY patches/open_webui/routers/files-content-echo.patch /tmp/files-content-echo.patch
RUN echo "${FILES_SHA256}  /app/backend/open_webui/routers/files.py" | sha256sum -c - \
    && patch --batch --forward -d /app/backend -p1 < /tmp/files-content-echo.patch \
    && grep -q "NTC patch (cosmetic): echo extracted content" /app/backend/open_webui/routers/files.py \
    && rm /tmp/files-content-echo.patch

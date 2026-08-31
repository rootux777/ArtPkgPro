# syntax=docker/dockerfile:1

FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ARTPKG_DATA_DIR=/data

WORKDIR /app

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY schemas/ ./schemas/
COPY tools/ ./tools/
COPY reusable_artifacts_package_human_questionnaire_spec.md ./
COPY ["reusable_artifacts_package_template (1).md", "./"]

RUN set -eux; \
    groupadd --system --gid 10001 artpkg; \
    useradd --system --uid 10001 --gid artpkg --home-dir /nonexistent --shell /usr/sbin/nologin artpkg; \
    mkdir -p /data/input /data/output; \
    chown -R artpkg:artpkg /data; \
    printf '%s\n' '#!/bin/sh' 'exec python /app/tools/artpkg_status_server.py "$@"' > /usr/local/bin/artpkg; \
    chmod 0755 /usr/local/bin/artpkg

EXPOSE 8080

USER artpkg:artpkg
ENTRYPOINT ["artpkg"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8080"]
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD ["artpkg", "healthcheck", "--host", "127.0.0.1", "--port", "8080"]
# ==============================
FROM registry.access.redhat.com/ubi9/nginx-122 AS appbase
# ==============================

USER root
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY --from=ghcr.io/astral-sh/uv:0.12.3@sha256:2d890623d310b57771ce840f0da5eed5fc6d657da05ffaa45d82797b53fa3abc /uv /uvx /usr/local/bin/

ENV UV_PROJECT_ENVIRONMENT=/opt/app-root/venv \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_NO_CACHE=1 \
    UV_PYTHON_DOWNLOADS=never
ENV PATH="/opt/app-root/venv/bin:${PATH}"

COPY pyproject.toml uv.lock ./

RUN dnf update -y  \
    && dnf install -y \
    nmap-ncat \
    libpq \
    libpq-devel \
    python3.12 \
    python3.12-devel \
    python-unversioned-command \
    gcc \
    && ln -sf /usr/bin/python3.12 /usr/local/bin/python3 \
    && ln -sf /usr/bin/python3.12 /usr/local/bin/python \
    && uv sync --locked --no-dev --group prod \
    && dnf remove -y \
    libpq-devel \
    python3.12-devel \
    gcc \
    && dnf clean all

COPY docker-entrypoint.sh ./
ENTRYPOINT ["./docker-entrypoint.sh"]

# ==============================
FROM appbase AS development
# ==============================

RUN groupadd -g 1000 appuser \
    && useradd -u 1000 -g appuser -ms /bin/bash appuser \
    && chown -R appuser:root /app

RUN dnf install -y \
    libpq-devel \
    python3.12-devel \
    gcc \
    && uv sync --locked --group dev \
    && dnf clean all

ENV DEV_SERVER=1

COPY --chown=appuser:root . .

USER appuser
EXPOSE 8080/tcp

# ==============================
FROM appbase AS production
# ==============================

COPY . .

# Collect static files
ENV STATIC_ROOT /var/parking-service/static
RUN mkdir -p /var/parking-service/static
RUN SECRET_KEY="only-used-for-collectstatic" python manage.py collectstatic --noinput

COPY nginx.conf /etc/nginx/nginx.conf

USER default
EXPOSE 8080/tcp

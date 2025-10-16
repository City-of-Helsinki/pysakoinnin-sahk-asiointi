# ==============================
FROM registry.access.redhat.com/ubi9/nginx-122 AS appbase
# ==============================

USER root
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

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
    && python -m ensurepip --upgrade --default-pip \
    && pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r ./requirements.txt \
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

COPY requirements-dev.txt .

RUN dnf install -y \
    libpq-devel \
    python3.12-devel \
    gcc \
    && pip install --no-cache-dir -r /app/requirements-dev.txt \
    && dnf clean all

ENV DEV_SERVER=1
ENV PIP_TOOLS_CACHE_DIR="/tmp/pip-tools-cache"

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

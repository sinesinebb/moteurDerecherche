FROM python:3.10-slim

WORKDIR /app

ARG INSTALL_DEV=false

# dépendances système nécessaires ; netcat -> netcat-openbsd
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev libxslt1-dev zlib1g-dev \
    nginx \
    netcat-openbsd \
    curl \
    git \
  && rm -rf /var/lib/apt/lists/*

# Copier configuration et entrypoint
COPY docker/nginx.conf /etc/nginx/nginx.conf
COPY docker/entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Installer requirements de prod
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optionnel : installer dépendances de dev si demandé au build
# (ne PAS activer INSTALL_DEV en production)
COPY requirements-dev.txt .
RUN if [ "$INSTALL_DEV" = "true" ]; then pip install --no-cache-dir -r requirements-dev.txt; fi

COPY . .

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

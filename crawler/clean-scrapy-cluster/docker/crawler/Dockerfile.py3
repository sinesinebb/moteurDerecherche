FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libffi-dev \
    libssl-dev \
    libxml2-dev \
    libxslt1-dev \
    curl \
    jq \
    netcat-openbsd \
    bash \
    python3-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

# 1. Copier et installer utils d'abord
COPY utils/ ./utils/
RUN pip install --upgrade pip && \
    pip install -e ./utils

# 2. Copier requirements et créer version nettoyée
COPY crawler/requirements.txt .
RUN grep -v "^-e \./utils" requirements.txt > requirements_clean.txt

# 3. Installer les autres dépendances
RUN pip install --no-cache-dir -r requirements_clean.txt
RUN pip install --no-cache-dir "Twisted>=22.10.0,<24.0.0"

# 4. Copier le reste
COPY . .

# Convertir les fins de ligne Windows en Unix
RUN sed -i 's/\r$//' /usr/src/app/docker/crawler/entrypoint.sh && \
    chmod +x /usr/src/app/docker/crawler/entrypoint.sh

# Structure nécessaire
RUN mkdir -p /usr/src/app/crawler/app \
 && ln -sf /usr/src/app/crawler/crawling /usr/src/app/crawler/app/crawling

WORKDIR /usr/src/app/crawler


ENTRYPOINT ["/usr/src/app/docker/crawler/entrypoint.sh"]
CMD ["python3", "crawler.py", "/usr/src/app/app/cluster_config/crawler_config.json"]
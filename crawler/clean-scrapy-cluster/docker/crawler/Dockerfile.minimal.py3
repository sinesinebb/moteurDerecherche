FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libffi-dev libssl-dev libxml2-dev libxslt1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer les dépendances essentielles avec des versions compatibles
RUN pip install --no-cache-dir \
    scrapy==2.11.0 \
    scrapy-redis==0.9.1 \
    kafka-python==2.0.2 \
    redis==4.5.4 \
    kazoo==2.8.0 \
    requests==2.31.0 \
    beautifulsoup4==4.12.2 \
    lxml==4.9.3

# Copier l'application
COPY . /app

# Créer la structure nécessaire
RUN mkdir -p /app/crawler/app && \
    ln -sf /app/crawler/crawling /app/crawler/app/crawling

WORKDIR /app/crawler

CMD ["python", "crawler.py", "/app/app/cluster_config/crawler_config.json"]

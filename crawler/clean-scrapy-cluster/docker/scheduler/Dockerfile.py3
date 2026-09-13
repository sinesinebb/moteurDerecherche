FROM python:3.8-slim
WORKDIR /app

# 1) Dépendances système
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential python3-dev libssl-dev \
      netcat-openbsd procps \
 && rm -rf /var/lib/apt/lists/*

RUN pip install psutil

# 2) setuptools <58 (pour pouvoir installer scutils malgré use_2to3)
RUN pip --default-timeout=120 install --no-cache-dir "setuptools<58"

# 3) Copier et installer scutils en local
COPY utils/scutils/ ./utils/scutils/
RUN pip --default-timeout=120 install --no-cache-dir ./utils/scutils

# 4) Copier le code scheduler
COPY crawler/crawling/scheduler.py .
COPY cluster_config/scheduler.cfg ./scheduler.cfg

# 5) Installer les 3 dépendances principales
RUN pip --default-timeout=120 install --no-cache-dir \
      redis \
      future \
      six>=1.11.0 \
      Scrapy>=1.8 \
      kazoo>=2.8.0 \
      kafka-python>=1.4.3

# copie de votre JSON unique
COPY cluster_config/scheduler_config.json ./scheduler_config.json

COPY wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# 6) Entrypoint qui attend ZK et Kafka avant de lancer le scheduler
ENTRYPOINT ["/usr/local/bin/wait-for-it.sh", "zookeeper:2181", "--", \
            "/usr/local/bin/wait-for-it.sh", "kafka:9092", "--"]
CMD ["python", "scheduler.py", "-c", "scheduler.cfg"]
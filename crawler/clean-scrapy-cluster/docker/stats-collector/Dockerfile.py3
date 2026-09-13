FROM python:3.8-slim
WORKDIR /app

# 1) Dépendances système
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential python3-dev libssl-dev \
 && rm -rf /var/lib/apt/lists/*

# 2) Baisser setuptools pour pouvoir installer scutils
RUN pip install --no-cache-dir "setuptools<58"

# 3) Copier et installer scutils
COPY utils/scutils/ ./utils/scutils/
RUN pip install --no-cache-dir ./utils/scutils

# 4) Copier le code et la config
COPY utils/scutils/stats_collector.py   ./stats_collector.py
COPY cluster_config/redis-monitor.cfg    ./redis-monitor.cfg


# 5) Installer toutes les dépendances Python utilisées
RUN pip install --no-cache-dir \
    redis \
    python-redis-lock \
    queuelib \
    kafka-python \
    'Flask<2.0' \
    'Jinja2<3.0' \
    'MarkupSafe<3.0' \
    'Werkzeug<2.0'
    
# 6) Entrypoint
ENTRYPOINT ["python", "stats_collector.py", "-c", "redis-monitor.cfg"]

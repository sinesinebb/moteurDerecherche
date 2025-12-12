FROM python:3.10-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    curl \
    netcat-openbsd \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

WORKDIR /app

# Copier requirements.txt d'abord pour meilleur cache Docker
COPY requirements.txt .

RUN pip install --upgrade pip
# Installation avec timeout augmenté et retry
RUN pip install --timeout 300 --retries 5 -r requirements.txt

# Installation de FAISS (version CPU) seulement
RUN pip install --timeout 300 faiss-cpu==1.7.4

COPY app/ ./app/

# Script wait-for-it amélioré
RUN echo '#!/bin/sh\n\
# wait-for-it.sh: script d attente pour les services dependants\n\
timeout=${WAIT_TIMEOUT:-120}\n\
host="$1"\n\
port="$2"\n\
shift 2\n\
cmd="$@"\n\
\necho "Waiting for $host:$port (timeout: ${timeout}s)..."\n\
for i in $(seq 1 $timeout); do\n\
  if nc -z $host $port; then\n\
    echo "$host:$port is available after ${i}s"\n\
    exec $cmd\n\
  fi\n\
  sleep 1\n\
done\n\
echo "Timeout waiting for $host:$port after ${timeout}s"\n\
exit 1' > /usr/local/bin/wait-for-it.sh

RUN chmod +x /usr/local/bin/wait-for-it.sh

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Commande corrigée
CMD ["/usr/local/bin/wait-for-it.sh", "elasticsearch", "9200", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
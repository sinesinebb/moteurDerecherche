FROM python:3.10-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    curl \
    netcat-openbsd \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements.txt d'abord pour meilleur cache Docker
COPY requirements.txt .

# Mise à jour de pip et installation des dépendances
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --timeout 300 --retries 5 -r requirements.txt

# Installation de FAISS (version CPU)
RUN pip install --no-cache-dir --timeout 300 faiss-cpu==1.7.4

# Copier le code de l'application
COPY app/ ./app/

# Télécharger wait-for-it.sh
ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Commande par défaut
CMD ["/usr/local/bin/wait-for-it.sh", "elasticsearch:9200", "--timeout=30", "--", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]

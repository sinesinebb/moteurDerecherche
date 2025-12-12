# user-service/Dockerfile - Ajouter makemigrations
FROM python:3.11-slim

WORKDIR /app

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le projet
COPY . .

# Créer le dossier pour les static files
RUN mkdir -p staticfiles

EXPOSE 8004

# Script de démarrage amélioré avec makemigrations
CMD ["/bin/bash", "-c", "\
  echo 'En attente des bases de données...' && \
  /usr/local/bin/wait-for-it.sh user-db:5432 --timeout=60 --strict -- echo 'PostgreSQL prêt' && \
  /usr/local/bin/wait-for-it.sh redis:6379 --timeout=30 --strict -- echo 'Redis prêt' && \
  echo 'Création des migrations...' && \
  python manage.py makemigrations --noinput && \
  echo 'Application des migrations...' && \
  python manage.py migrate && \
  echo 'Démarrage du serveur...' && \
  python manage.py runserver 0.0.0.0:8004"]
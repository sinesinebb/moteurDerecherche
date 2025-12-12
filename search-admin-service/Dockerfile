FROM python:3.11-slim

WORKDIR /app

# Installation des dépendances système en une seule couche
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copie et installation des requirements d'abord (pour meilleur cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du reste de l'application
COPY . .

# Création des dossiers nécessaires
RUN mkdir -p logs staticfiles media

# Utilisateur non-root
RUN useradd -m -s /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["gunicorn", "search_admin.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
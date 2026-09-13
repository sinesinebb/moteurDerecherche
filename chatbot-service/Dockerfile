FROM python:3.10-slim

WORKDIR /app

# Installation des dépendances système nécessaires à la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libopenblas-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code applicatif
COPY ./app /app/app

# Définir la commande
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8007"]
FROM python:3.10-slim

WORKDIR /usr/src/app

# Installer les dépendances système minimales
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        libffi-dev \
        libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements d'abord (pour meilleur caching)
COPY requirements.txt .

# Installer les dépendances Python sans ./utils d'abord
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Installer scutils séparément
COPY utils ./utils
RUN pip install --no-cache-dir -e ./utils || \
    echo "Installation de scutils échouée, continuation..."

# Installer les autres dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application
COPY . ./app

WORKDIR /usr/src/app/app

# Exposer le port
EXPOSE 5343

# Commande simple
CMD ["python", "-m", "rest.rest"]
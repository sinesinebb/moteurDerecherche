FROM python:3.9-slim

WORKDIR /app

# Installation des dépendances système minimales
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Copie des requirements
COPY requirements_simple.txt requirements.txt

# Installation des dépendances Python minimales
RUN pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0

# Copie du code
COPY app/ ./app/

# Utiliser la version simple
CMD ["python", "app/main_simple.py"]

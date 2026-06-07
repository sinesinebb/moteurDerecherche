FROM pytorch/pytorch:2.0.1-cuda11.7-cudnn8-runtime

WORKDIR /app

# Installation des dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=1000 -r requirements.txt

# Pré-téléchargement du modèle SentenceTransformer large ET de son tokenizer
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('dangvantuan/sentence-camembert-large')" \
    && python -c "from transformers import AutoTokenizer; AutoTokenizer.from_pretrained('dangvantuan/sentence-camembert-large')"

# Copie du code applicatif
COPY ./app /app/app

# Point d'entrée
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003", "--timeout-keep-alive", "300", "--timeout-graceful-shutdown", "30"]
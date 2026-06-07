# nlp-service/app/main.py
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import torch
import logging
import numpy as np
from typing import List, Set
import pickle
import os

app = FastAPI(title="NLP Service")

# Modèle plus spécialisé (large) pour de meilleures similarités
MODEL_NAME = "dangvantuan/sentence-camembert-large"
VOCAB_FILE = "/app/data/tech_vocab.pkl"

logging.info(f"Chargement du modèle {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME, device="cpu")
logging.info("Modèle chargé")

# -------------------------------------------------------------------
# Vocabulaire technique initial
# -------------------------------------------------------------------
BASE_VOCAB = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "swift", "kotlin", "php", "ruby", "scala",
    "react", "vue", "angular", "django", "flask", "spring", "express",
    "node.js", "tensorflow", "pytorch",
    "docker", "kubernetes", "linux", "windows", "macos", "android", "ios",
    "git", "github", "gitlab", "jenkins", "ansible", "terraform",
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
    "cassandra", "neo4j",
    "api", "rest", "graphql", "websocket", "microservices", "serverless",
    "machine learning", "deep learning", "data science", "artificial intelligence",
    "cloud", "aws", "azure", "gcp", "devops", "ci/cd",
    "sécurité", "cryptographie", "réseau", "protocole", "http", "tcp/ip",
    "algorithme", "structure de données", "programmation", "développement",
    "debug", "test", "déploiement", "performance", "optimisation",
    "frontend", "backend", "fullstack", "mobile", "web", "desktop"
]

def load_vocab() -> Set[str]:
    if os.path.exists(VOCAB_FILE):
        with open(VOCAB_FILE, "rb") as f:
            return pickle.load(f)
    return set(BASE_VOCAB)

def save_vocab(vocab_set: Set[str]):
    os.makedirs(os.path.dirname(VOCAB_FILE), exist_ok=True)
    with open(VOCAB_FILE, "wb") as f:
        pickle.dump(vocab_set, f)

# Chargement du vocabulaire existant
current_vocab = load_vocab()
vocab_list = list(current_vocab)
vocab_embeddings = model.encode(vocab_list, normalize_embeddings=True, convert_to_numpy=True)

class EmbedRequest(BaseModel):
    text: str
    is_query: bool = False

class VocabUpdateRequest(BaseModel):
    terms: List[str]

from transformers import AutoTokenizer

# Charger le tokenizer correspondant au modèle
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

@app.post("/embed")
async def get_embedding(request: EmbedRequest):
    try:
        text = request.text
        # Tokeniser et tronquer à 500 tokens pour laisser de la marge
        tokens = tokenizer.encode(text, add_special_tokens=True)
        if len(tokens) > 500:
            # Retronquer en gardant les 500 premiers tokens
            tokens = tokens[:500]
            text = tokenizer.decode(tokens, skip_special_tokens=True)
        embedding = model.encode(text, normalize_embeddings=True).tolist()
        return {"embedding": embedding, "dim": len(embedding)}
    except Exception as e:
        logging.error(f"Erreur encodage texte (len={len(request.text)}): {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/similar")
async def get_similar_words(
    word: str = Query(..., min_length=2),
    top_k: int = 5,
    threshold: float = 0.5
):
    try:
        word_embedding = model.encode(word, normalize_embeddings=True, convert_to_numpy=True)
        similarities = np.dot(vocab_embeddings, word_embedding)
        sorted_idx = np.argsort(similarities)[::-1]
        results = []
        for idx in sorted_idx[:top_k]:
            sim = float(similarities[idx])
            if sim >= threshold and vocab_list[idx] != word:
                results.append(vocab_list[idx])
        return {"similar": results, "word": word}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/vocab/update")
async def update_vocab(request: VocabUpdateRequest):
    global vocab_embeddings, current_vocab, vocab_list
    new_terms = set(request.terms) - current_vocab
    if new_terms:
        current_vocab.update(new_terms)
        save_vocab(current_vocab)
        vocab_list = list(current_vocab)
        vocab_embeddings = model.encode(vocab_list, normalize_embeddings=True, convert_to_numpy=True)
        return {"added": len(new_terms), "total": len(current_vocab)}
    return {"added": 0, "total": len(current_vocab)}

@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_NAME, "vocab_size": len(current_vocab)}
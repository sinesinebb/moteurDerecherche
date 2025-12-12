#!/bin/bash
echo "Ì∫® MODE URGENCE - SOUTENANCE SANS CRAWLER"
echo "=========================================="

# Arr√™ter tout
docker-compose down 2>/dev/null

# D√©marrer seulement ce qui fonctionne
echo "Ì∫Ä D√©marrage des services disponibles..."
docker-compose up -d \
  elasticsearch redis \
  indexing-service search-service frontend 2>/dev/null

echo "‚è≥ Attente 30 secondes..."
sleep 30

# Cr√©er l'index Elasticsearch manuellement
echo "Ì≥Å Cr√©ation index Elasticsearch..."
curl -X DELETE "http://localhost:9200/tech_docs" 2>/dev/null
curl -X PUT "http://localhost:9200/tech_docs" -H "Content-Type: application/json" -d '{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "title": {"type": "text"},
      "content": {"type": "text"},
      "url": {"type": "keyword"},
      "domain": {"type": "keyword"},
      "keywords_found": {"type": "keyword"}
    }
  }
}' 2>/dev/null

# Indexer des documents via Python directement
echo "Ì≥Ñ Indexation directe via Python..."
python3 << 'PYTHON'
import requests
import json

docs = [
    {
        "title": "Python Programming Tutorial",
        "content": "Python is a powerful programming language for web development, data science, and automation.",
        "url": "https://docs.python.org/3/tutorial/",
        "domain": "docs.python.org",
        "keywords_found": ["python", "programming"]
    },
    {
        "title": "Docker Container Guide", 
        "content": "Docker is a platform for developing, shipping, and running applications in containers.",
        "url": "https://docs.docker.com/get-started/",
        "domain": "docs.docker.com",
        "keywords_found": ["docker", "containers"]
    },
    {
        "title": "React JavaScript Framework",
        "content": "React is a JavaScript library for building user interfaces with reusable components.",
        "url": "https://react.dev/learn",
        "domain": "react.dev",
        "keywords_found": ["react", "javascript"]
    }
]

for doc in docs:
    try:
        # Indexer directement dans Elasticsearch
        response = requests.post(
            "http://localhost:9200/tech_docs/_doc",
            json=doc,
            timeout=5
        )
        print(f"‚úÖ {doc['title']}")
    except Exception as e:
        print(f"‚ùå Erreur: {e}")

print("ÌæØ Documents index√©s directement dans Elasticsearch")
PYTHON

# D√©marrer un serveur de recherche simple si le service ne marche pas
echo "Ì¥ß Lancement serveur de recherche de secours..."
docker run -d \
  --name search-backup \
  -p 8005:8000 \
  -e ELASTICSEARCH_URL=http://host.docker.internal:9200 \
  python:3.9-alpine sh -c "
    pip install fastapi uvicorn requests &&
    cat > /app/main.py << 'END'
from fastapi import FastAPI
import requests
app = FastAPI()
@app.get('/search')
def search(q: str = ''):
    try:
        es_resp = requests.get('http://host.docker.internal:9200/tech_docs/_search?q=' + q)
        hits = es_resp.json().get('hits', {}).get('hits', [])
        return {
            'query': q,
            'results': [{'title': h['_source'].get('title'), 'url': h['_source'].get('url')} for h in hits],
            'total_hits': len(hits)
        }
    except:
        return {'query': q, 'results': [], 'total_hits': 0}
@app.get('/health')
def health():
    return {'status': 'ok'}
END
    uvicorn main:app --host 0.0.0.0 --port 8000
" 2>/dev/null &

sleep 5

# Tester
echo ""
echo "Ì¥ç Test de recherche:"
curl -s "http://localhost:9200/tech_docs/_search?q=python&size=1" | grep -o '"total":[^,]*' | cut -d: -f2 | xargs echo "  ‚Ä¢ R√©sultats pour 'python':"

echo ""
echo "Ìºê URLs pour la d√©mo:"
echo "  ‚Ä¢ Elasticsearch: http://localhost:9200"
echo "  ‚Ä¢ Recherche de secours: http://localhost:8005/search?q=python"
echo "  ‚Ä¢ Frontend: http://localhost:3000 (si d√©marr√©)"

echo ""
echo "=========================================="
echo "ÌæØ PR√äT POUR LA PR√âSENTATION EN MODE URGENCE"

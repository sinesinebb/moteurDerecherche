#!/bin/bash
echo "=== TESTS DE PRÉCISION DU MOTEUR DE RECHERCHE ==="

# Définir un ensemble de requêtes tests
declare -a TEST_QUERIES=(
    "programmation Python"
    "machine learning algorithmes"
    "base de données relationnelle"
    "réseaux neurones convolutionnels"
    "API REST documentation"
    "docker container orchestration"
    "javascript framework react"
    "cybersécurité authentification"
    "big data traitement"
    "devops pratiques"
)

echo "1. Test sans NLP (baseline):"
for query in "${TEST_QUERIES[@]}"; do
    echo "Requête: $query"
    curl -s -X POST http://localhost:8002/search \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"use_nlp\": false, \"size\": 5}" | \
        jq -r '.results[] | "\(.title) - Score: \(.score)"'
    echo "---"
done

echo "2. Test avec NLP:"
for query in "${TEST_QUERIES[@]}"; do
    echo "Requête: $query"
    curl -s -X POST http://localhost:8002/search \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\", \"use_nlp\": true, \"size\": 5}" | \
        jq -r '.results[] | "\(.title) - Score: \(.score)"'
    echo "---"
done
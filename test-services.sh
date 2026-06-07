#!/bin/bash
echo "��� Test des services..."

echo "1. Test Elasticsearch..."
curl -s http://localhost:9200 && echo "✅ Elasticsearch accessible" || echo "❌ Elasticsearch inaccessible"

echo "2. Test Search Service..."
curl -s http://localhost:8002/health && echo "✅ Search Service accessible" || echo "❌ Search Service inaccessible"

echo "3. Test User Service..."
curl -s http://localhost:8004/api/health/ && echo "✅ User Service accessible" || echo "❌ User Service inaccessible"

echo "4. Test Frontend..."
curl -s -o /dev/null -w "HTTP Code: %{http_code}\n" http://localhost:3000

echo "5. Test API Gateway (nginx)..."
curl -s "http://localhost/api/search?q=test" && echo "✅ API Gateway fonctionne" || echo "❌ API Gateway échoué"

echo ""
echo "��� Résumé :"
echo "Frontend : http://localhost:3000"
echo "API Gateway : http://localhost"
echo "Elasticsearch : http://localhost:9200"
echo "Grafana : http://localhost:3001"

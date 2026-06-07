#!/bin/bash
echo "��� Test complet de l'architecture..."

echo "1. Test Elasticsearch..."
curl -s http://localhost:9200/_cluster/health | jq -r '.status' | grep -q "green\|yellow" && echo "✅ Elasticsearch OK" || echo "❌ Elasticsearch FAILED"

echo "2. Test Search Service direct..."
curl -s http://localhost:8002/health | jq -r '.status' | grep -q "healthy" && echo "✅ Search Service OK" || echo "❌ Search Service FAILED"

echo "3. Test User Service direct..."
curl -s http://localhost:8004/api/health/ 2>/dev/null | grep -q "OK" && echo "✅ User Service OK" || echo "❌ User Service FAILED"

echo "4. Test Frontend direct..."
curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200" && echo "✅ Frontend OK" || echo "❌ Frontend FAILED"

echo "5. Test API Gateway (nginx)..."
curl -s "http://localhost/api/search?q=test" 2>/dev/null | head -1 | grep -q "{" && echo "✅ API Gateway OK" || echo "❌ API Gateway FAILED"

echo "6. Test Kafka..."
docker-compose exec kafka kafka-topics.sh --list --bootstrap-server localhost:9092 | grep -q "crawled_documents" && echo "✅ Kafka OK" || echo "❌ Kafka FAILED"

echo "7. Test Redis..."
docker-compose exec redis redis-cli ping | grep -q "PONG" && echo "✅ Redis OK" || echo "❌ Redis FAILED"

echo ""
echo "��� Résumé :"
echo "Frontend : http://localhost:3000"
echo "API Search : http://localhost/api/search?q=python"
echo "Elasticsearch : http://localhost:9200"
echo "Grafana (monitoring) : http://localhost:3001"
echo "MinIO (stockage) : http://localhost:9000"

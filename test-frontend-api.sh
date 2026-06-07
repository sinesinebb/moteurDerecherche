#!/bin/bash
echo "í´ Test de la communication frontend -> API"

# VÃ©rifier que le frontend a les bonnes variables d'environnement
echo "1. Variables d'environnement du frontend:"
docker-compose exec frontend-new env | grep NUXT

# Tester depuis le conteneur frontend
echo "2. Test API depuis le frontend:"
docker-compose exec frontend-new curl -s "http://nginx-gateway/api/health" || echo "Ã‰chec depuis le frontend"

# Tester depuis le conteneur nginx
echo "3. Test API depuis nginx vers search-service:"
docker-compose exec nginx-gateway curl -s "http://search-service:8002/health" || echo "Ã‰chec depuis nginx"

echo ""
echo "í¾¯ URLs d'accÃ¨s:"
echo "Frontend: http://localhost:3000"
echo "API Gateway: http://localhost"
echo "Recherche: http://localhost/api/search?q=votre_terme"
echo "Health: http://localhost/api/health"

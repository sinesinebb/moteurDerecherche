#!/bin/bash
echo "=== Installation du user-service ==="

# 1. Arrêter et nettoyer
echo "1. Arrêt et nettoyage..."
docker-compose down -v 2>/dev/null || true

# 2. Reconstruire l'image
echo "2. Reconstruction de l'image..."
docker-compose build user-service

# 3. Démarrer PostgreSQL et Redis
echo "3. Démarrage des bases de données..."
docker-compose up -d user-db redis
sleep 10

# 4. Créer les migrations
echo "4. Création des migrations..."
docker-compose run --rm user-service python manage.py makemigrations user
docker-compose run --rm user-service python manage.py makemigrations search_history

# 5. Appliquer les migrations dans l'ordre
echo "5. Application des migrations dans l'ordre..."
# D'abord contenttypes
docker-compose run --rm user-service python manage.py migrate contenttypes

# Ensuite user
docker-compose run --rm user-service python manage.py migrate user

# Puis auth, admin, sessions
docker-compose run --rm user-service python manage.py migrate auth
docker-compose run --rm user-service python manage.py migrate admin
docker-compose run --rm user-service python manage.py migrate sessions

# Enfin search_history
docker-compose run --rm user-service python manage.py migrate search_history

# 6. Démarrer le service
echo "6. Démarrage du user-service..."
docker-compose up -d user-service
sleep 5

# 7. Vérifier
echo "7. Vérification..."
docker-compose ps

echo ""
echo "=== Installation terminée ==="
echo "Pour créer un superutilisateur :"
echo "  docker-compose exec user-service python manage.py createsuperuser"
echo ""
echo "Pour tester :"
echo "  curl http://localhost:8004/api/health/"

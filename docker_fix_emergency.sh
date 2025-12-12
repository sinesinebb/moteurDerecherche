#!/bin/bash
echo "��� RÉPARATION DOCKER URGENCE"
echo "============================="

# 1. Désactiver BuildKit pour éviter les problèmes
export DOCKER_BUILDKIT=0
export COMPOSE_DOCKER_CLI_BUILD=0

# 2. Télécharger les images manquantes via un proxy différent
echo "��� Téléchargement des images de base..."
IMAGES=(
  "python:3.10-slim"
  "python:3.9-slim"
  "python:3.8-slim"
  "node:20-slim"
  "node:18-slim"
)

for img in "${IMAGES[@]}"; do
  echo "  Téléchargement: $img"
  docker pull --platform linux/amd64 $img || echo "  ⚠️ Échec pour $img, continuation..."
done

# 3. Construire sans cache réseau
echo "���️ Construction des services..."
SERVICES=(
  "search-service"
  "indexing-service"
  "user-service"
  "admin-service"
)

for service in "${SERVICES[@]}"; do
  echo "  Construction: $service"
  docker-compose build --no-cache --pull=false $service 2>&1 | grep -E "(Step|ERROR|Successfully)" || true
done

# 4. Utiliser des images alternatives pour les services problématiques
echo "��� Remplacement des services problématiques..."
cat > docker-compose-fixed.yml << 'DOCKERCOMPOSE'
version: '3.8'

services:
  # Services qui fonctionnent
  zookeeper:
    image: zookeeper:3.8
    
  kafka:
    image: bitnami/kafka:3.4
    
  redis:
    image: redis:7-alpine
    
  elasticsearch:
    image: elasticsearch:8.10.0
    
  minio:
    image: minio/minio:RELEASE.2023-10-25T06-33-25Z
    
  # Services personnalisés avec build simplifié
  search-service:
    build:
      context: ./search_service
      dockerfile: Dockerfile.simple  # On va créer ce fichier
    
  indexing-service:
    build:
      context: ./indexing-service
      dockerfile: Dockerfile.simple
      
  # Autres services
  user-service:
    build:
      context: ./user-service
      dockerfile: Dockerfile.simple
      
  admin-service:
    build:
      context: ./search-admin-service
      dockerfile: Dockerfile.simple
DOCKERCOMPOSE

echo "✅ Configuration créée"

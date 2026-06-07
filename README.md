# Moteur de Recherche Informatique

Moteur de recherche spécialisé en informatique, basé sur une architecture microservices.
Il indexe automatiquement des pages web, des documents PDF, des images et des vidéos YouTube
techniques, et offre une recherche hybride (textuelle + sémantique) avec synonymes NLP.

## Architecture

| Service         | Technologie      | Port |
|-----------------|------------------|------|
| Frontend        | Nuxt.js 3        | 3000 |
| API Gateway     | Nginx            | 80   |
| Search Service  | FastAPI          | 8002 |
| NLP Service     | FastAPI + CamemBERT | 8003 |
| PageRank Service| FastAPI          | 8006 |
| User Service    | Django           | 8004 |
| Admin Service   | Django           | 8005 |
| Indexing Service| FastAPI          | 8001 |
| Video Fetcher   | Python           | –    |
| Scrapy Cluster  | Scrapy + Redis   | –    |

## Prérequis

- Docker & Docker Compose
- Python 3.10+ (pour les outils en local)
- Une clé API YouTube Data v3 (pour l'enrichissement des vidéos)

##  Démarrage rapide

```bash
git clone https://github.com/searchdevnoreply-star/moteur-recherche-informatique.git
cd moteur-recherche-informatique
cp .env.example .env          # puis éditez .env avec vos propres valeurs
docker compose up -d


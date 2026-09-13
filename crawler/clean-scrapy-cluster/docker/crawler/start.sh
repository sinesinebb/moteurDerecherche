#!/usr/bin/env bash
set -euo pipefail

# dossier de l'application (par défaut : /usr/src/app, compatible avec ton Dockerfile actuel)
APP_DIR="${APP_DIR:-/usr/src/app}"

# si /app existe (ancien cas), on l'utilise
if [ -d "/app" ]; then
  APP_DIR="/app"
fi

echo "→ Attente des dépendances…"
# exemple d'appel wait-for-it (déjà dans ton script original)
# wait-for-it.sh kafka:9092 -t "${WAIT_FOR_IT_TIMEOUT:-60}" -- echo "Kafka OK !"

echo "→ Dossier application : $APP_DIR"
cd "$APP_DIR" || { echo "Erreur: dossier $APP_DIR introuvable"; exit 2; }

# lancer le service (exemples — adapte si nécessaire)
# si tu lances scrapy :
if command -v scrapy >/dev/null 2>&1 ; then
  echo "→ Lancement du spider : ${SPIDER:-infoscraper}"
  exec scrapy crawl "${SPIDER:-infoscraper}"
else
  # sinon lance ton script python "crawler.py"
  echo "→ Lancement du script python crawler.py"
  exec python crawler.py /opt/crawler_config.json
fi

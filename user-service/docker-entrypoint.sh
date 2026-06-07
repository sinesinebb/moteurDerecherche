#!/bin/bash

set -e

echo "=== User Service ==="

# Si on passe des arguments, exécuter la commande
if [ "$#" -gt 0 ]; then
    echo "Exécution de la commande: $@"
    exec "$@"
    exit 0
fi

# Démarrer Gunicorn directement (nous gérerons les migrations manuellement)
echo "Démarrage de Gunicorn..."
exec gunicorn user_service.wsgi:application \
    --bind 0.0.0.0:8004 \
    --workers 2 \
    --access-logfile - \
    --error-logfile - \
    --timeout 120

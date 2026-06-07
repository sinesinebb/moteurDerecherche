#!/bin/sh
set -e

# Si la commande est "gunicorn", on exécute les migrations et on lance le serveur
if [ "$1" = "gunicorn" ]; then
    echo "Running migrations..."
    python manage.py migrate --noinput
    echo "Collecting static files..."
    python manage.py collectstatic --noinput
    echo "Starting Gunicorn..."
    exec "$@"
else
    # Sinon, on exécute directement la commande passée (ex: python manage.py ...)
    exec "$@"
fi
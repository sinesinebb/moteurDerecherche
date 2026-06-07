#!/bin/sh
set -e

echo "⏳ Attente de PostgreSQL..."
until pg_isready -h "$DATABASE_HOST" -p "$DATABASE_PORT" -U "$DATABASE_USER"; do
  sleep 1
done

echo "📦 Migrations..."
python manage.py migrate --noinput

echo "👤 Superutilisateur..."
python manage.py shell <<EOF
from apps.user.models import User
if not User.objects.filter(email='admin@search.dev').exists():
    User.objects.create_superuser(
        email='admin@search.dev',
        password='admin123',
        username='admin',
        first_name='Admin',
        last_name='User'
    )
    print("✓ Superutilisateur créé")
else:
    print("✓ Superutilisateur déjà présent")
EOF

echo "🚀 Démarrage du serveur..."
exec python manage.py runserver 0.0.0.0:8004
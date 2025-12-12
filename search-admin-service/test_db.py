#!/usr/bin/env python
import django
import os
import sys

# Ajouter le chemin du projet
sys.path.append('/d/DevS/Nversions/moteur_recherche/search-admin-service/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'search_admin.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connexion PostgreSQL réussie!")
        print(f"📊 Version: {version[0]}")
        
        # Tester les modèles
        from django.apps import apps
        models = apps.get_models()
        print(f"📈 Modèles détectés: {len(models)}")
        
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
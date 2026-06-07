#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line
from django.db import connection, OperationalError

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'user_service.settings.development')
django.setup()

def run_migration(app_name, fake=False):
    """Exécute une migration avec gestion d'erreurs"""
    args = ['manage.py', 'migrate', app_name, '--noinput']
    if fake:
        args.append('--fake')
    
    print(f"Exécution: {' '.join(args)}")
    try:
        execute_from_command_line(args)
        print(f"✓ Migration {app_name} appliquée")
        return True
    except Exception as e:
        print(f"⚠ Échec de {app_name}: {str(e)[:100]}")
        return False

def create_tables_directly(app_name):
    """Crée les tables directement sans migrations"""
    from django.apps import apps
    from django.db import connection
    
    print(f"Tentative de création directe des tables pour {app_name}...")
    
    try:
        # Obtenir les modèles de l'application
        app_config = apps.get_app_config(app_name)
        models = app_config.get_models()
        
        with connection.schema_editor() as schema_editor:
            for model in models:
                try:
                    schema_editor.create_model(model)
                    print(f"  ✓ Table {model._meta.db_table} créée")
                except Exception as e:
                    print(f"  ⚠ Table {model._meta.db_table} existe déjà ou erreur: {str(e)[:50]}")
        return True
    except Exception as e:
        print(f"  ✗ Échec de création des tables: {str(e)[:100]}")
        return False

print("=== Application des migrations en ordre ===")

# 1. Contenttypes
run_migration('contenttypes')

# 2. Auth (fake d'abord pour éviter les dépendances)
run_migration('auth', fake=True)

# 3. User (notre modèle personnalisé)
if not run_migration('user'):
    print("Tentative de création directe des tables user...")
    create_tables_directly('user')

# 4. Auth (pour de vrai maintenant)
run_migration('auth')

# 5. Admin
run_migration('admin')

# 6. Sessions
run_migration('sessions')

# 7. Search_history
if not run_migration('search_history'):
    create_tables_directly('search_history')

print("=== Toutes les migrations ont été tentées ===")
print("Vérification de l'état des tables...")

# Vérifier les tables créées
try:
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = cursor.fetchall()
        print(f"Tables trouvées ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
except Exception as e:
    print(f"Erreur lors de la vérification des tables: {e}")

print("=== Terminé ===")

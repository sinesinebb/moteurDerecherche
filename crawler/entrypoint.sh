#!/bin/sh
# Entrypoint final pour Scrapy Crawler

echo "=== Démarrage du crawler corrigé ==="
echo "PYTHONPATH avant: $PYTHONPATH"

# Ajouter les chemins nécessaires
export PYTHONPATH=/usr/src/app/crawler:/usr/src/app:$PYTHONPATH

echo "PYTHONPATH après: $PYTHONPATH"
echo ""

# Vérifier l'importation
echo "=== Test d'importation du module ==="
python -c "
import sys
print('Chemin Python:')
for p in sys.path:
    print(f'  {p}')

print('\\nTentative d\\'importation...')
try:
    import crawling
    print('✓ SUCCÈS: Module crawling importé!')
    print(f'  Location: {crawling.__file__}')
except ImportError as e:
    print(f'✗ ÉCHEC: {e}')
    sys.exit(1)
"

echo ""
echo "=== Démarrage du crawler avec configuration ==="

# Vérifier les arguments possibles
echo "Arguments disponibles:"
echo "1. /usr/src/app/app/cluster_config/crawler_config.json"
echo "2. /usr/src/app/crawler/config/example.yml"

# Essayer avec le fichier de configuration du cluster
if [ -f "/usr/src/app/app/cluster_config/crawler_config.json" ]; then
    echo "Utilisation de /usr/src/app/app/cluster_config/crawler_config.json"
    cd /usr/src/app/crawler
    exec python crawler.py /usr/src/app/app/cluster_config/crawler_config.json
elif [ -f "/usr/src/app/crawler/config/example.yml" ]; then
    echo "Utilisation de /usr/src/app/crawler/config/example.yml"
    cd /usr/src/app/crawler
    exec python crawler.py /usr/src/app/crawler/config/example.yml
else
    echo "ERREUR: Aucun fichier de configuration trouvé!"
    echo "Recherche de fichiers de configuration..."
    find /usr/src/app -name "*.json" -o -name "*.yml" -o -name "*.yaml" | head -10
    exit 1
fi

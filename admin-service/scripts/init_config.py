import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from core.models import SystemConfiguration

default_configs = [
    {'key': 'MAX_RESULTS_PER_PAGE', 'value': 20, 'description': 'Nombre maximum de résultats par page'},
    {'key': 'CACHE_TTL', 'value': 300, 'description': 'Durée de vie du cache en secondes'},
    {'key': 'BLACKLISTED_DOMAINS', 'value': ['example.com'], 'description': 'Domaines exclus du crawl'},
    {'key': 'PAGERANK_ALPHA', 'value': 0.85, 'description': 'Facteur d amortissement PageRank'},
    {'key': 'CRAWLER_MAX_DEPTH', 'value': 3, 'description': 'Profondeur maximale de crawl'},
]

for conf in default_configs:
    SystemConfiguration.objects.get_or_create(key=conf['key'], defaults=conf)
print("Configurations initiales créées.")
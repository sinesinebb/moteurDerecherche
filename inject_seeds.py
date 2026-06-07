import json
import redis

# Connexion à Redis (local, le port 6379 est exposé)
r = redis.Redis(host='localhost', port=6379, db=0)

# Lire le fichier seeder_config.json
with open('crawler/clean-scrapy-cluster/cluster_config/seeder_config.json', 'r') as f:
    data = json.load(f)

# La liste complète des URLs est à la racine, clé "seed_urls"
urls = data['seed_urls']
print(f"Nombre d'URLs à injecter : {len(urls)}")

# Vider l'ancienne file d'attente
r.delete('sc:start_urls')

# Injecter les URLs (lpush pour que la première soit traitée en premier)
for url in urls:
    r.lpush('sc:start_urls', url)

print("Injection terminée.")
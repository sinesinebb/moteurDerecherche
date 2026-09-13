#!/usr/bin/env bash
set -e

# On attend que Kafka soit prêt
wait-for-it.sh kafka:9092 -t 60 -- echo "✅ Kafka OK !"

# On lance le seeder
exec python seeder.py -c /usr/src/app/config.json

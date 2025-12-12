#!/usr/bin/env sh
set -euo pipefail

echo "==> ENTRYPOINT: start"

# Fix PYTHONPATH if not set
: "${PYTHONPATH:=/app}"
export PYTHONPATH

# Gestion de DISABLE_KAFKA pour éviter le démarrage du consumer pendant le build
if [ "${DISABLE_KAFKA:-false}" = "true" ]; then
  echo "==> ENTRYPOINT: Kafka consumer disabled (DISABLE_KAFKA=true)"
fi

# Optionnel: exécuter les tests si demandé (RUN_TESTS=true)
if [ "${RUN_TESTS:-false}" = "true" ]; then
  echo "==> ENTRYPOINT: running unit tests before startup"
  # s'assurer que pytest est installé (dans l'image ou via requirements-dev)
  if command -v pytest >/dev/null 2>&1; then
    PYTHONPATH=${PYTHONPATH} pytest -q tests/unit || {
      echo "Unit tests FAILED — aborting"
      exit 1
    }
    echo "Unit tests OK — continuing startup."
  else
    echo "pytest not installed in container; skipping tests."
  fi
fi

# start the main command (from CMD / docker-compose command)
exec "$@"
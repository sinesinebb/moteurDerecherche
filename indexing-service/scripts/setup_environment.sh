set -euo pipefail

VENV_DIR=".venv"
PYPROJECT="pyproject.toml"
REQS_FILE="requirements.txt"

echo "==> setup_environment.sh: préparation de l'environnement de développement"

if [ ! -d "${VENV_DIR}" ]; then
  echo "  - Création d'un virtualenv dans ${VENV_DIR}..."
  python3 -m venv "${VENV_DIR}"
else
  echo "  - Virtualenv ${VENV_DIR} déjà présent"
fi

echo "  - Activation temporaire pour installer les paquets..."
# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"

# Upgrader pip quietly
pip install --upgrade pip setuptools wheel >/dev/null

# Installer dépendances principales (si fichier present)
if [ -f "${REQS_FILE}" ]; then
  echo "  - Installation depuis ${REQS_FILE}..."
  pip install -r "${REQS_FILE}"
else
  echo "  - Aucun requirements.txt trouvé : installation minimale (pytest, requests) pour dev"
  pip install pytest requests >/dev/null
fi

# Dépendances utiles pour scripts utilitaires (non obligatoires)
echo "  - Installation des utilitaires de développement (pytest, kafka-python, minio, elasticsearch client) si absent..."
pip install pytest kafka-python minio elasticsearch requests >/dev/null || true

echo "  - Définition suggestionnelle de PYTHONPATH (pour tests dans conteneur/dev)."
echo "    export PYTHONPATH=/app" > .env_pytest
echo "    # pour l'utiliser : source .env_pytest"

echo "==> Done. Pour utiliser :"
echo "   source ${VENV_DIR}/bin/activate"
echo "   export PYTHONPATH=/app"
echo ""

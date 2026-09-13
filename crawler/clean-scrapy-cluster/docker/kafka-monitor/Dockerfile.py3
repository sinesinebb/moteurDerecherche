FROM python:3.6

# 1) Mise à jour des paquets système
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      # (ajoutez ici d’autres dépendances système si besoin) \
    && rm -rf /var/lib/apt/lists/*

# 2) Création du répertoire de travail
WORKDIR /usr/src/app

# 3) Installation des dépendances Python
#    - scutils (dans utils/) fait appel à ConcurrentLogHandler
COPY utils /usr/src/utils
COPY kafka-monitor/requirements.txt /usr/src/app/requirements.txt
RUN pip --default-timeout=100 install --no-cache-dir -r requirements.txt

# 4) Nettoyage du dossier utils pour alléger l’image
RUN rm -rf /usr/src/utils

# 5) Copie du code de votre micro-service
COPY kafka-monitor /usr/src/app

# 6) Configuration locale (overrides)
COPY docker/kafka-monitor/settings.py /usr/src/app/localsettings.py

# 7) Script de tests (optionnel)
COPY docker/run_docker_tests.sh /usr/src/app/run_docker_tests.sh

# 8) Point d’entrée
CMD ["python", "kafka_monitor.py", "run"]


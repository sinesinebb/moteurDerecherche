FROM python:3.8-slim

WORKDIR /usr/src/app

# 1) Installer kafka-python
COPY seeder/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 2) Copier le code du seeder
COPY seeder /usr/src/app

# 3) Copier le fichier de config JSON (tu peux aussi le monter en volume)
# après (pointant vers le nouveau seeder_config.json)
COPY cluster_config/seeder_config.json /usr/src/app/config.json


COPY docker/seeder/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

COPY docker/seeder/wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

ENTRYPOINT ["bash","-lc","/usr/local/bin/start.sh"]


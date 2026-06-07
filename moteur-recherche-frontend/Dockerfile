# Dockerfile pour le frontend
FROM node:20-alpine

WORKDIR /app

# Copier les fichiers de configuration d'abord
COPY package*.json ./
COPY nuxt.config.ts ./
COPY tailwind.config.ts ./
COPY tsconfig.json ./

# Nettoyer le cache et installer les dépendances
RUN npm cache clean --force && \
    npm install\
    npm install echarts vue-echarts

# Copier le reste du code
COPY . .

# Vérifier que les fichiers existent
RUN echo "Vérification de la structure des fichiers:" && \
    echo "Répertoire courant:" && pwd && \
    echo "Structure:" && ls -la && \
    echo "Assets existe?" && ls -la assets/ 2>/dev/null || echo "Pas de dossier assets" && \
    echo "app/Assets existe?" && ls -la app/assets/ 2>/dev/null || echo "Pas de app/assets"

# Builder l'application
RUN npm run build

# Exposer le port
EXPOSE 3000

# Commande de démarrage
CMD ["node", ".output/server/index.mjs"]
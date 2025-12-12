FROM nginx:alpine

# Installation des outils
RUN apk add --no-cache bash

# Copie des configurations
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/ /etc/nginx/conf.d/

# Création des dossiers
RUN mkdir -p /var/log/nginx /var/cache/nginx

# Ports exposés
EXPOSE 80 443

# Santé check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
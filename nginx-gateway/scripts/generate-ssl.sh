#!/bin/bash
# Génération de certificats auto-signés pour le développement
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/key.pem \
    -out ssl/cert.pem \
    -subj "/C=FR/ST=Paris/L=Paris/O=SearchEngine/CN=localhost"
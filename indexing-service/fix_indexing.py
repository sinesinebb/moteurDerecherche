#!/usr/bin/env python3
"""
Script pour corriger l'indexing service et envoyer des données structurées
"""
import json
from datetime import datetime
from urllib.parse import urlparse

def extract_domain(url):
    """Extrait le domaine d'une URL"""
    try:
        return urlparse(url).netloc
    except:
        return "unknown"

def should_index_document(doc):
    """Filtre les documents de qualité"""
    min_content_length = 200
    excluded_domains = ['phonandroid.com', '01net.com']
    
    # Filtrer par longueur de contenu
    if doc.get('content_length', 0) < min_content_length:
        return False
    
    # Filtrer par domaine
    domain = doc.get('domain', '')
    if any(excluded in domain for excluded in excluded_domains):
        return False
        
    return True

def transform_kafka_message(message_value):
    """Transforme un message Kafka en document structuré"""
    try:
        data = json.loads(message_value)
        
        # Extraire les champs du message Kafka
        content = data.get('text', '')
        metadata = data.get('metadata', {})
        url = metadata.get('source', '')
        
        # Créer le document structuré
        doc = {
            "title": metadata.get('title', '')[:500],
            "url": url,
            "domain": extract_domain(url),
            "content": content,
            "content_length": len(content),
            "metadata": metadata,
            "appid": metadata.get('appid', 'default'),
            "crawled_at": datetime.utcnow().isoformat(),
            "language": "fr"
        }
        
        # Appliquer le filtre de qualité
        if should_index_document(doc):
            return doc
        return None
        
    except Exception as e:
        print(f"❌ Erreur transformation message: {e}")
        return None

# Test avec un exemple de message Kafka
test_message = '{"text": "Introduction à Python pour les débutants", "metadata": {"source": "https://realpython.com/python-intro", "title": "Introduction à Python", "appid": "default"}}'

print("🧪 Test de transformation:")
doc = transform_kafka_message(test_message)
if doc:
    print("✅ Document structuré créé:")
    print(json.dumps(doc, indent=2, ensure_ascii=False))
else:
    print("❌ Document filtré")
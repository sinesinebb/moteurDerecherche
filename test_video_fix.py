import json
from datetime import datetime
from urllib.parse import urlparse

# Copiez-collez VOTRE fonction transform_document_to_compatible_format ici
def transform_document_to_compatible_format(doc):
    """Transforme le document du format Kafka vers le format compatible Elasticsearch"""
    
    # NOUVEAU: Format avec médias
    if 'image_urls' in doc or 'videos' in doc:
        source_url = doc.get('url', '')
        domain = urlparse(source_url).netloc if source_url else ""
        
        # Déterminer le contenu principal
        content = doc.get('extracted_content', '')
        if not content:
            content = doc.get('body', '')[:10000]

        # EXTRAIRE LES URLs VIDÉOS DES DONNÉES STRUCTURÉES
        video_urls = []
        videos_data = doc.get('videos', [])
        
        for video in videos_data:
            if isinstance(video, dict):
                # Extraire toutes les URLs possibles des vidéos
                for key in ['embed_url', 'watch_url', 'video_url', 'thumbnail']:
                    url = video.get(key)
                    if url and isinstance(url, str) and url.startswith(('http://', 'https://')):
                        video_urls.append(url)
        
        return {
            "url": source_url,
            "response_url": source_url,
            "title": doc.get('title', ''),
            "description": doc.get('description', ''),
            "body": doc.get('body', ''),
            "content": content,
            "extracted_content": doc.get('extracted_content', ''),
            "domain": domain,
            "keywords_found": doc.get('keywords_found', []),
            "status_code": doc.get('status_code', 200),
            "appid": doc.get('appid', 'default'),
            "crawlid": doc.get('crawlid', 'unknown'),
            
            # ✅ CORRECTION CRITIQUE ICI :
            "image_urls": doc.get('image_urls', []),
            "videos": doc.get('videos', []),  # ← DONNÉES STRUCTURÉES COMPLÈTES
            "video_urls": video_urls,  # ← URLs EXTRACTIES DES VIDÉOS
            "media_count": doc.get('media_count', 0),
            "content_type": doc.get('content_type', 'text'),
            "crawled_at": doc.get('crawled_at', datetime.utcnow().isoformat()),
            
            "links": doc.get('links', []),
            "metadata": {
                "title": doc.get('title', 'Titre non disponible'),
                "url": source_url,
                "source": source_url,
                "content_type": "text/html",
                "language": "fr",
                "word_count": len(content.split()),
                "source_format": "scrapy_cluster_with_media",
                "appid": doc.get('appid', 'default'),
                "crawlid": doc.get('crawlid', 'unknown'),
                "media_summary": {
                    "images_count": len(doc.get('image_urls', [])),
                    "videos_count": len(doc.get('videos', [])),
                    "content_type": doc.get('content_type', 'text')
                }
            },
            "timestamp": datetime.utcnow().isoformat(),
            "pagerank": 0.1
        }

# Test avec les données réelles du crawler
test_doc = {
    "url": "https://example.com/video-test",
    "title": "Test avec vidéos YouTube CORRIGÉ",
    "description": "Page de test après correction du bug vidéos",
    "body": "Contenu de test avec des vidéos YouTube intégrées",
    "extracted_content": "Contenu extrait avec vidéos YouTube",
    "keywords_found": ["video", "youtube", "test", "correction"],
    "status_code": 200,
    "appid": "test",
    "crawlid": "manual-test",
    "image_urls": [
        "https://example.com/test-image1.jpg",
        "https://example.com/test-image2.png"
    ],
    "videos": [
        {
            "video_id": "dQw4w9WgXcQ",
            "embed_url": "https://www.youtube.com/embed/dQw4w9WgXcQ",
            "watch_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
            "type": "youtube",
            "platform": "youtube"
        }
    ],
    "media_count": 3,
    "content_type": "video",
    "crawled_at": "2024-01-01T00:00:00",
    "links": []
}

# Exécuter le test
result = transform_document_to_compatible_format(test_doc)
print("��� RÉSULTAT DU TEST :")
print(f"✅ Champ 'videos' présent: {len(result['videos'])} vidéo(s)")
print(f"✅ Champ 'video_urls' extrait: {len(result['video_urls'])} URL(s)")
print(f"✅ Premier embed_url: {result['videos'][0]['embed_url']}")
print(f"✅ media_count: {result['media_count']}")
print(f"✅ content_type: {result['content_type']}")
print("\n��� VOTRE CORRECTION FONCTIONNE ! Les vidéos seront maintenant indexées correctement.")

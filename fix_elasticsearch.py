#!/usr/bin/env python3
import requests
import json
from elasticsearch import Elasticsearch

def recreate_index():
    """Recrée l'index avec le bon mapping"""
    es = Elasticsearch(["http://localhost:9200"])
    
    # Supprimer l'index existant
    if es.indices.exists(index="tech_docs"):
        es.indices.delete(index="tech_docs")
        print("✅ Ancien index supprimé")
    
    # Créer le nouvel index avec mapping correct
    mapping = {
        "mappings": {
            "properties": {
                "title": {
                    "type": "text",
                    "analyzer": "french",
                    "fields": {"keyword": {"type": "keyword"}}
                },
                "url": {"type": "keyword"},
                "domain": {"type": "keyword"},
                "content": {
                    "type": "text", 
                    "analyzer": "french"
                },
                "content_length": {"type": "integer"},
                "metadata": {"type": "object"},
                "appid": {"type": "keyword"},
                "crawled_at": {"type": "date"},
                "language": {"type": "keyword"}
            }
        },
        "settings": {
            "analysis": {
                "analyzer": {
                    "french": {
                        "tokenizer": "standard",
                        "filter": ["lowercase", "french_stem", "elision"]
                    }
                },
                "filter": {
                    "french_stem": {
                        "type": "stemmer",
                        "name": "french"
                    },
                    "elision": {
                        "type": "elision",
                        "articles": ["l", "m", "t", "qu", "n", "s", "j", "d"]
                    }
                }
            }
        }
    }
    
    es.indices.create(index="tech_docs", body=mapping)
    print("✅ Nouvel index créé avec mapping correct")

def test_search():
    """Teste la recherche après correction"""
    es = Elasticsearch(["http://localhost:9200"])
    
    # Test recherche
    result = es.search(index="tech_docs", body={
        "query": {
            "multi_match": {
                "query": "python",
                "fields": ["title^3", "content^2", "domain^1.5"]
            }
        },
        "size": 5
    })
    
    print("🔍 Test recherche 'python':")
    for hit in result['hits']['hits']:
        doc = hit['_source']
        print(f"   📄 {doc.get('title', 'Sans titre')} | {doc.get('domain', 'N/A')}")

if __name__ == "__main__":
    print("🔄 Correction du mapping Elasticsearch...")
    recreate_index()
    print("\n🎉 Mapping corrigé! Redémarrez l'indexing-service pour réindexer les données")
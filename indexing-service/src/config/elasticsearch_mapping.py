TECH_DOCUMENT_MAPPING = {
    "settings": {
        "analysis": {
            "analyzer": {
                "code_analyzer": {
                    "type": "custom",
                    "tokenizer": "whitespace",
                    "filter": ["lowercase", "code_stemmer"]
                },
                "french_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "french_elision",
                        "french_stop",
                        "french_stemmer"
                    ]
                }
            },
            "filter": {
                "code_stemmer": {
                    "type": "stemmer",
                    "name": "english"
                },
                "french_elision": {
                    "type": "elision",
                    "articles_case": True,
                    "articles": ["l", "m", "t", "qu", "n", "s", "j", "d", "c", "jusqu", "quoiqu", "lorsqu", "puisqu"]
                },
                "french_stop": {
                    "type": "stop",
                    "stopwords": "_french_"
                },
                "french_stemmer": {
                    "type": "stemmer",
                    "language": "french"
                }
            }
        },
        "number_of_shards": 3,
        "number_of_replicas": 1
    },
    "mappings": {
        "dynamic": "strict",
        "properties": {
            "url": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "french_analyzer",
                "fields": {"keyword": {"type": "keyword"}}
            },
            "description": {
                "type": "text",
                "analyzer": "french_analyzer"
            },
            "extracted_content": {
                "type": "text",
                "analyzer": "french_analyzer"
            },
            # NOUVEAUX CHAMPS MEDIAS
            "image_urls": {"type": "keyword"},
            "video_urls": {"type": "keyword"},
            "media_count": {"type": "integer"},
            "content_type": {"type": "keyword"},
            "domain": {"type": "keyword"},
            "crawled_at": {"type": "date"},
            
            # Champs existants (gardés pour compatibilité)
            "content": {
                "type": "text",
                "analyzer": "code_analyzer"
            },
            "source": {"type": "keyword"},
            "code_blocks": {
                "type": "nested",
                "properties": {
                    "code": {"type": "text", "index": False},
                    "language": {"type": "keyword"},
                    "score": {"type": "float"}
                }
            },
            "technical_errors": {"type": "keyword"},
            "terminal_commands": {"type": "keyword"},
            "metadata": {
                "type": "object",
                "properties": {
                    "doc_type": {"type": "keyword"},
                    "technical_level": {"type": "keyword"},
                    "entities": {
                        "type": "object",
                        "properties": {
                            "programming_languages": {"type": "keyword"},
                            "frameworks": {"type": "keyword"},
                            "tools": {"type": "keyword"},
                            "concepts": {"type": "keyword"}
                        }
                    },
                    "related_concepts": {"type": "keyword"},
                    "nlp_score": {"type": "float"}
                }
            },
            "processing_timestamp": {"type": "date"}
        }
    }
}
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
            "links": {"type": "keyword"},
            "url": {"type": "keyword"},
            "title": {
                "type": "text",
                "analyzer": "french_analyzer",
                "fields": {"keyword": {"type": "keyword"}}
            },

            "file_type": {"type": "keyword"},
            "file_size": {"type": "integer"},
            "pages": {"type": "integer"},
            "word_count": {"type": "integer"},

            "page_url": {"type": "keyword"},
            "alt": {"type": "text"},
            "img_title": {"type": "text"},
            "page_title": {"type": "text"},
            "page_description": {"type": "text"},
            
            "snippet": {"type": "text", "index": False}, 

            "technical_metadata": {
                "type": "object",
                "properties": {
                    "programming_languages": {"type": "keyword"},
                    "technical_concepts": {"type": "keyword"},
                    "difficulty_level": {"type": "keyword"},
                    "has_code_examples": {"type": "boolean"},
                    "has_shell_commands": {"type": "boolean"}
                }
            },
            "youtube_metadata": {
                "type": "object",
                "properties": {
                    "title": {"type": "text", "analyzer": "french_analyzer"},
                    "description": {"type": "text", "analyzer": "french_analyzer"},
                    "tags": {"type": "keyword"},
                    "view_count": {"type": "integer"},
                    "like_count": {"type": "integer"},
                    "comment_count": {"type": "integer"},
                    "duration_seconds": {"type": "integer"},
                    "thumbnail": {"type": "keyword", "index": False},
                    "default_thumbnail": {"type": "keyword", "index": False},
                    "published_at": {"type": "date"},
                    "channel_title": {"type": "keyword"},
                    "source": {"type": "keyword"}
                }
            },

            "file_type": {"type": "keyword"},
            "file_size": {"type": "integer"},
            "pages": {"type": "integer"},
            "word_count": {"type": "integer"},
            "description": {
                "type": "text",
                "analyzer": "french_analyzer"
            },
            "extracted_content": {
                "type": "text",
                "analyzer": "french_analyzer"
            },
            # CHAMPS MEDIAS
            "image_urls": {"type": "keyword"},
            "video_urls": {"type": "keyword"},
            "media_count": {"type": "integer"},
            "content_type": {"type": "keyword"},
            "domain": {"type": "keyword"},
            "crawled_at": {"type": "date"},
            
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
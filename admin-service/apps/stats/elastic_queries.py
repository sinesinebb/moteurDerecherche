from elasticsearch import Elasticsearch
from django.conf import settings

es = Elasticsearch([f"http://{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"])

def get_index_doc_count(index='tech_docs'):
    stats = es.indices.stats(index=index)
    return stats['_all']['primaries']['docs']['count']

def get_recent_searches(hours=24):
    # À implémenter si vous loggez les recherches
    pass
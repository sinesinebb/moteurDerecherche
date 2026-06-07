from elasticsearch import Elasticsearch
from src.core.config import settings
import logging

logger = logging.getLogger(__name__)

def load_graph():
    """Charge le graphe depuis Elasticsearch en utilisant le champ 'links' de chaque document."""
    es = Elasticsearch(hosts=[settings.elasticsearch_url])
    
    body = {
        "_source": ["url", "links"],
        "query": {
            "exists": {"field": "links"}
        }
    }
    
    graph = {}
    try:
        response = es.search(index=settings.elasticsearch_index, body=body, scroll='2m', size=1000)
        scroll_id = response['_scroll_id']
        
        while True:
            for hit in response['hits']['hits']:
                source = hit['_source']
                url = source.get('url')
                links = source.get('links', [])
                if url:
                    graph[url] = links
            response = es.scroll(scroll_id=scroll_id, scroll='2m')
            if not response['hits']['hits']:
                break
    except Exception as e:
        logger.error(f"Erreur lors du chargement du graphe depuis Elasticsearch: {e}")
        raise
    finally:
        es.clear_scroll(scroll_id=scroll_id)
    
    logger.info(f"Graphe chargé : {len(graph)} nœuds, {sum(len(v) for v in graph.values())} arêtes")
    return graph
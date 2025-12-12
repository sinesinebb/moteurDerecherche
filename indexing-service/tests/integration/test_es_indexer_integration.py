# tests/integration/test_es_indexer_integration.py
import os
import pytest
import socket

from src.processors import elasticsearch_indexer as es_idx

ES_HOSTS = os.getenv("ES_HOSTS", "http://localhost:9200")
INDEX_NAME = "test_index_with_vector"

def _es_reachable(hosts_str: str, timeout: float = 2.0) -> bool:
    host = hosts_str.split(",")[0]
    host = host.replace("http://", "").replace("https://", "").split(":")
    hostname = host[0]
    port = int(host[1]) if len(host) > 1 else 9200
    try:
        with socket.create_connection((hostname, port), timeout=timeout):
            return True
    except Exception:
        return False

@pytest.mark.skipif(not _es_reachable(ES_HOSTS), reason="Elasticsearch not reachable - skip integration test")
def test_ensure_index_with_vector_and_bulk():
    client = es_idx.get_es_client(timeout=5)
    # create index with vector mapping of dims=3
    created = es_idx.ensure_index(client, index_name=INDEX_NAME, mappings={"properties": {"text": {"type": "text"}}}, vector_field_name="vec", vector_dims=3)
    assert created is True
    docs = [{"text": "hello", "embedding": [0.1, 0.2, 0.3], "id": "doc1"}]
    res = es_idx.index_documents_bulk(client, INDEX_NAME, docs, chunk_size=1, vector_field_name="vec")
    assert isinstance(res, dict)
    # cleanup
    client.indices.delete(index=INDEX_NAME, ignore=[400, 404])

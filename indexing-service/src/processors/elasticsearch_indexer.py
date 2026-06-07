"""
ElasticSearch helper / indexer complet.

Fonctions exposées :
- get_es_client(hosts=None, user=None, password=None, timeout=30)
- get_es_client_with_retry(hosts=None, user=None, password=None, timeout=30, max_retries=5, retry_delay=5)
- index_documents_bulk(client, index_name=None, docs=..., chunk_size=500, vector_field_name=None, vector_dims=None, strict=True)
- _parse_hosts(hosts)
- _doc_to_action(index_name, doc, id_field=None, vector_field_name=None)

Le module expose également `helpers` (référence à elasticsearch.helpers)
pour permettre aux tests de le monkeypatcher.
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, Iterable, Iterator, List, Optional, Union

# config app
from src.config import settings

logger = logging.getLogger("indexing-service.elasticsearch_indexer")

# try import elasticsearch and helpers
try:
    # import top-level package to read version more reliably
    import elasticsearch as _es_pkg  # type: ignore
    from elasticsearch import Elasticsearch  # type: ignore
    from elasticsearch import helpers as es_helpers  # type: ignore
    _ES_PY_VERSION = getattr(_es_pkg, "__version__", "0")
except Exception:
    Elasticsearch = None  # type: ignore
    es_helpers = None  # type: ignore
    _ES_PY_VERSION = "0"

# Make helpers available for tests to monkeypatch
helpers = es_helpers


def _parse_hosts(hosts: Optional[Union[str, List[str]]]) -> List[str]:
    """
    Normalize ES hosts input into a list of host strings.
    - None -> ['http://localhost:9200']
    - 'http://a:9200,http://b:9200' -> ['http://a:9200','http://b:9200']
    - list -> trimmed list
    """
    if hosts is None:
        return ["http://localhost:9200"]
    if isinstance(hosts, str):
        parts = [h.strip() for h in hosts.split(",") if h.strip()]
        return parts or ["http://localhost:9200"]
    if isinstance(hosts, (list, tuple)):
        return [str(h).strip() for h in hosts if str(h).strip()]
    return [str(hosts)]


def get_es_client(
    hosts: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    timeout: int = 30,
) -> "Elasticsearch":
    """
    Return a synchronous Elasticsearch client instance with improved error handling.

    Resolution order:
      - explicit function args
      - settings.ES_HOSTS / settings.ES_USER / settings.ES_PASSWORD
      - environment variables ES_HOSTS / ES_USER / ES_PASSWORD

    Adds a compatibility header when the installed python client is major >= 9
    to avoid media_type_header_exception against ES 8.x servers.
    """
    if Elasticsearch is None:
        raise RuntimeError("elasticsearch python package is not installed")

    hosts_val = hosts or getattr(settings, "ES_HOSTS", None) or os.getenv("ES_HOSTS", "http://elasticsearch:9200")
    hosts_list = _parse_hosts(hosts_val)

    user = user or getattr(settings, "ES_USER", None) or os.getenv("ES_USER")
    password = password or getattr(settings, "ES_PASSWORD", None) or os.getenv("ES_PASSWORD")

    # Build kwargs with enhanced configuration
    kwargs: Dict[str, Any] = {
        "hosts": hosts_list,
        "request_timeout": int(os.getenv("ES_REQUEST_TIMEOUT", timeout)),
        "retry_on_timeout": True,
        "max_retries": int(os.getenv("ES_MAX_RETRIES", "5")),
        "verify_certs": os.getenv("ES_VERIFY_CERTS", "false").lower() == "true",
    }

    if user and password:
        kwargs["basic_auth"] = (user, password)  # Use basic_auth instead of http_auth

    # Disable SSL warnings if verification is disabled
    if not kwargs["verify_certs"]:
        try:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        except ImportError:
            pass

    # Detect client major version
    try:
        major = int(str(_ES_PY_VERSION).split(".")[0])
    except Exception:
        major = 0

    # If client >=9 add header compatible-with=8 to avoid media_type_header_exception
    if major >= 9:
        kwargs["headers"] = {"Accept": "application/vnd.elasticsearch+json; compatible-with=8"}

    logger.debug("Creating Elasticsearch client with hosts=%s user=%s client_major=%s", hosts_list, bool(user), major)

    try:
        client = Elasticsearch(**kwargs)
        # Test the connection immediately
        if not client.ping():
            logger.warning("Elasticsearch client created but ping test failed")
        return client
    except Exception as e:
        logger.error("Failed to create Elasticsearch client: %s", str(e))
        raise


def get_es_client_with_retry(
    hosts: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    timeout: int = 30,
    max_retries: int = 5,
    retry_delay: int = 5,
) -> "Elasticsearch":
    """
    Get Elasticsearch client with retry mechanism for initial connection.
    """
    for attempt in range(max_retries):
        try:
            client = get_es_client(hosts, user, password, timeout)
            if client.ping():
                logger.info("Successfully connected to Elasticsearch on attempt %d", attempt + 1)
                return client
            else:
                logger.warning("Elasticsearch ping failed on attempt %d", attempt + 1)
        except Exception as e:
            logger.warning("Elasticsearch connection attempt %d failed: %s", attempt + 1, str(e))

        if attempt < max_retries - 1:
            logger.info("Retrying Elasticsearch connection in %d seconds...", retry_delay)
            time.sleep(retry_delay)

    raise ConnectionError(f"Failed to connect to Elasticsearch after {max_retries} attempts")


def _get_field_from_doc(doc: Any, field: str, default: Any = None) -> Any:
    """Get attribute or dict field safely."""
    if isinstance(doc, dict):
        return doc.get(field, default)
    return getattr(doc, field, default)

def _doc_to_action(index_name: str, doc: Any, id_field: Optional[str] = None, vector_field_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Convert a document (dict or object-like) to an action for helpers.bulk.

    - id_field: if provided, look for that name as id (fallback)
    - vector_field_name: if provided and doc has 'embedding', will put it in _source
    """
    src: Dict[str, Any] = {}

    # Copier tous les champs du document
    if isinstance(doc, dict):
        # Pour les dicts, copier tous les champs sauf ceux réservés
        for k, v in doc.items():
            if k in ("id", "_id", "embedding"):
                continue
            src[k] = v
    else:
        # Pour les objets, extraire les attributs
        if hasattr(doc, '__dict__'):
            for k, v in doc.__dict__.items():
                if not k.startswith('_') and k not in ("id", "embedding"):
                    src[k] = v

    # S'assurer que les champs textuels de base existent
    if "text" not in src:
        content = _get_field_from_doc(doc, "content", None)
        if content is not None:
            src["text"] = content
        else:
            body = _get_field_from_doc(doc, "body", None)
            if body is not None:
                src["text"] = body

    # metadata fallback
    if "metadata" not in src:
        metadata = _get_field_from_doc(doc, "metadata", None)
        if metadata is not None:
            src["metadata"] = metadata

    # embedding -> vector field
    embedding = _get_field_from_doc(doc, "embedding", None)
    if embedding is not None and vector_field_name:
        src[vector_field_name] = embedding

    action: Dict[str, Any] = {"_index": index_name, "_source": src}

    # --- PRIORITÉ 1 : Si le document contient déjà un champ '_id' (non vide) ---
    if isinstance(doc, dict) and "_id" in doc and doc["_id"]:
        action["_id"] = doc["_id"]
    else:
        # --- PRIORITÉ 2 : Utiliser l'URL comme ID, mais seulement si elle est non vide ---
        url = _get_field_from_doc(doc, "url", None)
        if url is not None and url != "":
            action["_id"] = url
        else:
            # --- PRIORITÉ 3 : Fallback sur id_field ou champ 'id' ---
            if id_field:
                ident = _get_field_from_doc(doc, id_field, None)
                if ident is not None:
                    action["_id"] = ident
            else:
                ident = _get_field_from_doc(doc, "id", None)
                if ident is not None:
                    action["_id"] = ident

    # DEBUG: show prepared action
    try:
        logger.debug("Prepared action for bulk: %s", {k: v for k, v in action.items() if k != '_source'})
        logger.debug("Document fields: %s", list(src.keys()))
    except Exception:
        logger.debug("Prepared action for bulk (unserializable)")

    return action


def index_documents_bulk(
    client: "Elasticsearch",
    index_name: Optional[str],
    docs: Iterable[Any],
    chunk_size: int = 500,
    vector_field_name: Optional[str] = None,
    vector_dims: Optional[int] = None,
    strict: bool = True,
) -> Dict[str, Any]:
    """
    Index an iterable of documents in bulk and return summary:
      {"success": <number_indexed>, "errors": <list_of_errors>}

    If index_name is None, fallback to settings.ES_INDEX or 'default-index'.
    """
    if helpers is None:
        raise RuntimeError("elasticsearch.helpers (helpers.bulk) not available; install `elasticsearch` package")

    index_name = index_name or getattr(settings, "ES_INDEX", None) or os.getenv("ES_INDEX", "default-index")
    logger.debug(
        "index_documents_bulk called index=%s chunk_size=%s vector_field=%s vector_dims=%s strict=%s",
        index_name,
        chunk_size,
        vector_field_name,
        vector_dims,
        strict,
    )

    def _actions_iter() -> Iterator[Dict[str, Any]]:
        for d in docs:
            emb = _get_field_from_doc(d, "embedding", None)

            # validate dims if requested
            if emb is not None and vector_field_name and vector_dims is not None:
                try:
                    if len(emb) != int(vector_dims):
                        if strict:
                            raise ValueError(f"embedding length {len(emb)} != expected {vector_dims}")
                        else:
                            # non strict: return action without vector
                            if isinstance(d, dict):
                                copyd = dict(d)
                                copyd.pop("embedding", None)
                                action = _doc_to_action(index_name, copyd, id_field=None, vector_field_name=None)
                                try:
                                    logger.debug("Prepared action for bulk (no vector due to dims mismatch): %s", action)
                                except Exception:
                                    logger.debug("Prepared action for bulk (no vector, unserializable)")
                                yield action
                                continue
                            else:
                                # reconstruct minimal dict
                                minimal = {}
                                for attr in ("text", "metadata", "id"):
                                    v = _get_field_from_doc(d, attr, None)
                                    if v is not None:
                                        minimal[attr] = v
                                action = _doc_to_action(index_name, minimal, id_field=None, vector_field_name=None)
                                try:
                                    logger.debug("Prepared action for bulk (minimal no vector): %s", action)
                                except Exception:
                                    logger.debug("Prepared action for bulk (minimal, unserializable)")
                                yield action
                                continue
                except TypeError:
                    if strict:
                        raise
                    else:
                        # ignore vector if not iterable
                        pass

            action = _doc_to_action(index_name, d, id_field=None, vector_field_name=vector_field_name)
            # debug juste avant de yield pour voir l'action envoyée au bulk
            try:
                logger.debug("Prepared action for bulk (yield): %s", action)
            except Exception:
                logger.debug("Prepared action for bulk (yield, unserializable)")

            yield action

    # call helpers.bulk which typically returns (count, errors)
    try:
        result = helpers.bulk(client, _actions_iter(), chunk_size=chunk_size, raise_on_error=False)
    except Exception as exc:
        logger.exception("helpers.bulk raised exception: %s", exc)
        raise

    success = 0
    errors = []
    if isinstance(result, tuple) and len(result) >= 1:
        success = result[0]
        if len(result) > 1:
            errors = result[1] or []
    elif isinstance(result, int):
        success = result
    else:
        try:
            success = int(result)  # last resort
        except Exception:
            success = 0

    # detailed log when errors exist
    if errors:
        logger.warning(
            "Bulk index completed with errors: index=%s success=%s errors_count=%s",
            index_name,
            success,
            len(errors),
        )
        try:
            import json as _json

            sample = _json.dumps(errors[:5], default=str)
            logger.debug("Bulk errors sample: %s", sample)
        except Exception:
            logger.debug("Bulk errors present (couldn't serialize)")

    logger.info("Bulk index completed: index=%s success=%s errors=%s", index_name, success, bool(errors))
    return {"success": success, "errors": errors}


# public exports
__all__ = [
    "get_es_client",
    "get_es_client_with_retry",
    "index_documents_bulk",
    "_parse_hosts",
    "_doc_to_action",
    "helpers",
]

import logging
from elasticsearch import Elasticsearch, exceptions

logger = logging.getLogger("youtube_updater")


def update_youtube_metadata(es: Elasticsearch, index: str, doc_id: str, youtube_data: dict) -> bool:
    """
    Met à jour ou crée le document ES avec les métadonnées YouTube.
    Si le document n'existe pas, un squelette minimal est créé.
    """
    if es is None:
        logger.warning("ES client is None, cannot update YouTube metadata")
        return False
    if not doc_id or not youtube_data:
        logger.warning("doc_id ou youtube_data manquant")
        return False

    partial_doc = {
        "youtube_metadata": youtube_data,
        "content_type": "youtube_video",
        "has_youtube_metadata": True
    }

    try:
        response = es.update(
            index=index,
            id=doc_id,
            body={"doc": partial_doc},
            retry_on_conflict=3
        )
        logger.info(f"YouTube metadata updated for doc {doc_id} (result: {response['result']})")
        return True
    except exceptions.NotFoundError:
        logger.info(f"Document {doc_id} absent, création automatique")
        try:
            es.index(index=index, id=doc_id, body={
                "url": doc_id,
                "title": youtube_data.get("title", ""),
                "description": youtube_data.get("description", ""),
                "content": youtube_data.get("title", "") + " " + youtube_data.get("description", ""),
                **partial_doc,
                "crawled_at": youtube_data.get("fetched_at"),
                "timestamp": youtube_data.get("fetched_at"),
            })
            logger.info(f"Document créé avec YouTube metadata pour {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Échec création document {doc_id}: {e}")
            return False
    except Exception as e:
        logger.error(f"Failed to update YouTube metadata for {doc_id}: {e}", exc_info=True)
        return False


def mark_youtube_unavailable(es: Elasticsearch, index: str, doc_id: str, video_id: str) -> bool:
    """Marque une vidéo comme indisponible."""
    if es is None:
        logger.warning("ES client is None, cannot mark YouTube unavailable")
        return False
    if not doc_id:
        return False
    partial_doc = {
        "youtube_metadata": {
            "video_id": video_id,
            "status": "unavailable"
        }
    }
    try:
        es.update(index=index, id=doc_id, body={"doc": partial_doc})
        logger.info(f"Marked YouTube video {video_id} as unavailable for doc {doc_id}")
        return True
    except exceptions.NotFoundError:
        logger.info(f"Document {doc_id} absent, création avec statut unavailable")
        try:
            es.index(index=index, id=doc_id, body={
                "url": doc_id,
                "youtube_metadata": {"video_id": video_id, "status": "unavailable"},
                "content_type": "youtube_video"
            })
            return True
        except Exception as e:
            logger.error(f"Échec création document unavailable: {e}")
            return False
    except Exception as e:
        logger.error(f"Error marking unavailable: {e}")
        return False
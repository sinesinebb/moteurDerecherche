# src/processors/media_processor.py

import logging
from urllib.parse import urlparse
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def process_videos_data(videos_data: List) -> List[Dict[str, Any]]:
    """
    Traite les données vidéo structurées du nouveau format
    Gère à la fois l'ancien format (liste d'URLs) et le nouveau format (liste de dictionnaires)
    """
    processed_videos = []

    extract_video_metadata
    
    if not videos_data:
        return processed_videos
    
    try:
        if isinstance(videos_data, list):
            for video in videos_data:
                if isinstance(video, dict):
                    # NOUVEAU FORMAT: Vidéo avec métadonnées structurées
                    processed_video = process_structured_video(video)
                    if processed_video:
                        processed_videos.append(processed_video)
                elif isinstance(video, str):
                    # ANCIEN FORMAT: URL simple (rétrocompatibilité)
                    processed_video = process_legacy_video_url(video)
                    if processed_video:
                        processed_videos.append(processed_video)
        
        logger.debug(f"Processed {len(processed_videos)} videos from {len(videos_data)} raw entries")
        return processed_videos
        
    except Exception as e:
        logger.error(f"Error processing videos data: {e}")
        return []

def process_structured_video(video: Dict[str, Any]) -> Dict[str, Any]:
    """Traite une vidéo au format structuré"""
    try:
        # Vidéo YouTube avec métadonnées complètes
        if video.get('type') == 'youtube' and video.get('video_id'):
            return {
                'video_id': video.get('video_id'),
                'embed_url': video.get('embed_url', f"https://www.youtube.com/embed/{video.get('video_id')}"),
                'watch_url': video.get('watch_url', f"https://www.youtube.com/watch?v={video.get('video_id')}"),
                'thumbnail': video.get('thumbnail', f"https://img.youtube.com/vi/{video.get('video_id')}/hqdefault.jpg"),
                'type': 'youtube',
                'platform': 'youtube',
                'title': video.get('title', ''),
                'duration': video.get('duration', ''),
                'is_embeddable': True
            }
        
        # Vidéo HTML5 standard
        elif video.get('type') in ['html5', 'direct'] and video.get('video_url'):
            return {
                'video_url': video.get('video_url'),
                'embed_url': video.get('embed_url', video.get('video_url')),
                'watch_url': video.get('watch_url', video.get('video_url')),
                'type': video.get('type', 'html5'),
                'platform': video.get('platform', 'direct'),
                'is_embeddable': False
            }
        
        # Vidéo embed (Vimeo, Dailymotion, etc.)
        elif video.get('type') == 'embed' and video.get('embed_url'):
            return {
                'embed_url': video.get('embed_url'),
                'watch_url': video.get('watch_url', video.get('embed_url')),
                'type': 'embed',
                'platform': video.get('platform', 'other'),
                'is_embeddable': True
            }
        
        # Format inconnu mais avec URL
        elif video.get('video_url') or video.get('embed_url'):
            url = video.get('video_url') or video.get('embed_url')
            return process_legacy_video_url(url)
        
        return None
        
    except Exception as e:
        logger.warning(f"Error processing structured video: {e}")
        return None

def process_legacy_video_url(video_url: str) -> Dict[str, Any]:
    """Traite une URL vidéo de l'ancien format"""
    try:
        if not video_url:
            return None
        
        # Détection YouTube
        if 'youtube.com' in video_url or 'youtu.be' in video_url:
            video_id = extract_youtube_id(video_url)
            if video_id:
                return {
                    'video_id': video_id,
                    'embed_url': f"https://www.youtube.com/embed/{video_id}",
                    'watch_url': f"https://www.youtube.com/watch?v={video_id}",
                    'thumbnail': f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
                    'type': 'youtube',
                    'platform': 'youtube',
                    'is_embeddable': True
                }
        
        # Détection Vimeo
        elif 'vimeo.com' in video_url:
            video_id = extract_vimeo_id(video_url)
            if video_id:
                return {
                    'video_id': video_id,
                    'embed_url': f"https://player.vimeo.com/video/{video_id}",
                    'watch_url': video_url,
                    'type': 'vimeo',
                    'platform': 'vimeo',
                    'is_embeddable': True
                }
        
        # Autres URLs vidéo
        else:
            return {
                'video_url': video_url,
                'embed_url': video_url,
                'watch_url': video_url,
                'type': 'unknown',
                'platform': 'unknown',
                'is_embeddable': False
            }
            
    except Exception as e:
        logger.warning(f"Error processing legacy video URL {video_url}: {e}")
        return None

def extract_youtube_id(url: str) -> str:
    """Extrait l'ID d'une vidéo YouTube depuis l'URL"""
    try:
        import re
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com/watch\?.*v=([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    except Exception:
        return None

def extract_vimeo_id(url: str) -> str:
    """Extrait l'ID d'une vidéo Vimeo depuis l'URL"""
    try:
        import re
        patterns = [
            r'vimeo\.com/(\d+)',
            r'player\.vimeo\.com/video/(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
    except Exception:
        return None

def extract_video_metadata(videos_data: List) -> Dict[str, Any]:
    """Extrait les métadonnées globales des vidéos"""
    processed_videos = process_videos_data(videos_data)
    
    youtube_videos = [v for v in processed_videos if v.get('platform') == 'youtube']
    embeddable_videos = [v for v in processed_videos if v.get('is_embeddable')]
    
    return {
        'videos_processed': processed_videos,
        'videos_count': len(processed_videos),
        'youtube_videos_count': len(youtube_videos),
        'embeddable_videos_count': len(embeddable_videos),
        'has_youtube_videos': len(youtube_videos) > 0,
        'has_embeddable_videos': len(embeddable_videos) > 0
    }
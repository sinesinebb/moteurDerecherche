# src/models/document_models.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl
from datetime import datetime


class RawResponseItem(BaseModel):
    appid: Optional[str]
    crawlid: Optional[str]
    url: HttpUrl
    response_url: Optional[HttpUrl]
    status_code: Optional[int]
    request_headers: Optional[Dict[str, List[str]]]
    response_headers: Optional[Dict[str, List[str]]]
    body: Optional[str]
    encoding: Optional[str]
    title: Optional[str]
    description: Optional[str]
    keywords_found: Optional[List[str]]
    links: Optional[List[str]]
    
    # NOUVEAUX CHAMPS MEDIAS
    image_urls: Optional[List[str]] = []
    video_urls: Optional[List[str]] = []
    media_count: Optional[int] = 0
    content_type: Optional[str] = "text"  # "text", "image", "video"
    extracted_content: Optional[str] = ""
    crawled_at: Optional[str] = None


class Section(BaseModel):
    id: str
    type: str               # "text" | "code" | "title" | "meta" | "image" | "video"
    text: str
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    language: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}
    # NOUVEAU: Pour les médias
    media_url: Optional[str] = None
    media_type: Optional[str] = None  # "image", "video"


class Document(BaseModel):
    doc_id: str
    url: HttpUrl
    crawl_meta: Optional[Dict[str, Any]] = {}
    title: Optional[str] = None
    description: Optional[str] = None
    sections: List[Section] = []
    raw: Optional[RawResponseItem] = None
    
    # NOUVEAUX CHAMPS MEDIAS
    image_urls: List[str] = []
    video_urls: List[str] = []
    media_count: int = 0
    content_type: str = "text"  # "text", "image", "video"
    extracted_content: str = ""
    domain: Optional[str] = ""
    crawled_at: Optional[str] = None
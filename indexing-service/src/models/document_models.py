# src/models/document_models.py
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from enum import Enum


# ========== ENUMS ==========
class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class DocumentType(str, Enum):
    DOCUMENTATION = "documentation"
    TUTORIAL = "tutorial"
    ARTICLE = "article"
    QNA = "qna"
    CODE_REPOSITORY = "code_repository"
    CODE_EXAMPLE = "code_example"
    GENERAL = "general"


# ========== MODÈLES DE BASE ==========
class RawResponseItem(BaseModel):
    appid: Optional[str] = None
    crawlid: Optional[str] = None
    url: HttpUrl
    response_url: Optional[HttpUrl] = None
    status_code: Optional[int] = None
    body: Optional[str] = None
    encoding: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    keywords_found: Optional[List[str]] = None
    links: Optional[List[str]] = None
    crawled_at: Optional[str] = None


class Section(BaseModel):
    id: str
    type: str  # "text", "code", "title", "image", "video"
    text: str
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None


# ========== MODÈLES TECHNIQUES ==========
class TechnicalMetadata(BaseModel):
    """Métadonnées techniques du document"""
    programming_languages: List[str] = []
    technical_concepts: List[str] = []
    difficulty_level: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    has_code_examples: bool = False
    code_types: List[str] = []
    technical_density: float = Field(0.0, ge=0.0, le=1.0)
    document_type: DocumentType = DocumentType.GENERAL
    technical_authority: int = Field(50, ge=0, le=100)
    reading_time_minutes: int = Field(1, ge=1)
    has_shell_commands: bool = False
    has_diagrams: bool = False
    technical_score: float = Field(0.5, ge=0.0, le=1.0)


class ContentQualityMetrics(BaseModel):
    """Métriques de qualité du contenu"""
    readability_score: float = Field(0.5, ge=0.0, le=1.0)
    structure_score: float = Field(0.5, ge=0.0, le=1.0)
    completeness_score: float = Field(0.5, ge=0.0, le=1.0)
    accuracy_score: float = Field(0.5, ge=0.0, le=1.0)
    overall_quality: float = Field(0.5, ge=0.0, le=1.0)


# ========== MODÈLE DOCUMENT PRINCIPAL ==========
class Document(BaseModel):
    doc_id: str
    url: HttpUrl
    crawl_meta: Optional[Dict[str, Any]] = {}
    title: Optional[str] = None
    description: Optional[str] = None
    sections: List[Section] = []
    raw: Optional[RawResponseItem] = None
    
    # Champs médias
    image_urls: List[str] = []
    video_urls: List[str] = []
    media_count: int = 0
    content_type: str = "text"
    extracted_content: str = ""
    domain: Optional[str] = ""
    crawled_at: Optional[str] = None
    snippet: Optional[str] = None
    
    # Champs techniques (NOUVEAUX)
    technical_metadata: Optional[TechnicalMetadata] = None
    content_quality: Optional[ContentQualityMetrics] = None
    domain_authority: int = Field(50, ge=0, le=100)
    overall_quality_score: float = Field(0.5, ge=0.0, le=1.0)
    detected_language: str = "en"
    word_count: int = 0
    paragraph_count: int = 0
    code_block_count: int = 0
    technical_keywords: List[str] = []
    tags: List[str] = []
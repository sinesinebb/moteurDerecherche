# app/models/search_models.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    """Types de documents supportés par le moteur de recherche"""
    DOCUMENTATION = "documentation"
    TUTORIAL = "tutorial"
    BLOG_POST = "blog_post"
    FORUM_THREAD = "forum_thread"
    CODE_SNIPPET = "code_snippet"
    RESEARCH_PAPER = "research_paper"
    VIDEO = "video"
    COURSE = "course"
    BOOK = "book"
    TOOL = "tool"

class ITDomain(str, Enum):
    """Domaines informatiques spécialisés"""
    PROGRAMMING = "programming"
    AI_ML = "artificial_intelligence"
    CYBERSECURITY = "cybersecurity"
    NETWORKING = "networking"
    DATABASES = "databases"
    CLOUD_COMPUTING = "cloud_computing"
    WEB_DEVELOPMENT = "web_development"
    MOBILE_DEVELOPMENT = "mobile_development"
    DEVOPS = "devops"
    HARDWARE = "hardware"
    DATA_SCIENCE = "data_science"

class DocumentIndex(BaseModel):
    """Modèle pour les documents indexés dans Elasticsearch"""
    id: str = Field(..., description="ID unique du document")
    title: str = Field(..., description="Titre du document")
    content: str = Field(..., description="Contenu textuel")
    url: str = Field(..., description="URL source")
    domain: ITDomain = Field(..., description="Domaine informatique")
    document_type: DocumentType = Field(..., description="Type de document")
    keywords: List[str] = Field(default_factory=list, description="Mots-clés")
    description: Optional[str] = Field(None, description="Description courte")
    author: Optional[str] = Field(None, description="Auteur du contenu")
    published_date: Optional[datetime] = Field(None, description="Date de publication")
    last_updated: Optional[datetime] = Field(None, description="Dernière mise à jour")
    page_rank: float = Field(0.0, ge=0.0, le=10.0, description="Score PageRank")
    popularity: float = Field(0.0, ge=0.0, le=1.0, description="Score de popularité")
    quality_score: float = Field(0.0, ge=0.0, le=1.0, description="Score de qualité")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Métadonnées supplémentaires")

class SearchQueryModel(BaseModel):
    """Modèle pour les requêtes de recherche analysées"""
    original_query: str
    normalized_query: str
    tokens: List[str]
    entities: List[str]
    intent: str
    domain: ITDomain
    is_technical: bool
    complexity_level: str  # beginner, intermediate, advanced

class UserSearchProfile(BaseModel):
    """Profil de recherche utilisateur pour la personnalisation"""
    user_id: str
    preferred_domains: List[ITDomain] = Field(default_factory=list)
    skill_level: str = Field("beginner", description="Niveau technique")
    search_history: List[str] = Field(default_factory=list)
    favorite_documents: List[str] = Field(default_factory=list)
    search_preferences: Dict[str, Any] = Field(default_factory=dict)

class SearchSession(BaseModel):
    """Session de recherche utilisateur"""
    session_id: str
    user_id: Optional[str]
    start_time: datetime
    queries: List[str] = Field(default_factory=list)
    clicked_results: List[str] = Field(default_factory=list)
    duration: Optional[float] = Field(None, description="Durée en secondes")

class SystemMetrics(BaseModel):
    """Métriques système pour le monitoring"""
    timestamp: datetime
    active_searches: int
    average_response_time: float
    cache_hit_rate: float
    error_rate: float
    memory_usage: float
    cpu_usage: float
    elasticsearch_health: str
# models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    DOCUMENTATION = "documentation"
    TUTORIAL = "tutorial"
    BLOG_POST = "blog_post"
    FORUM_THREAD = "forum_thread"
    CODE_SNIPPET = "code_snippet"
    RESEARCH_PAPER = "research_paper"
    VIDEO = "video"

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    page: int = Field(1, ge=1)
    size: int = Field(10, ge=1, le=50)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    sort_by: Optional[str] = Field("relevance")
    sort_order: Optional[str] = Field("desc")

class SearchResult(BaseModel):
    id: str
    title: str
    url: str
    description: Optional[str]
    content_snippet: str
    domain: str
    content_type: ContentType
    published_date: Optional[datetime]
    page_rank: float = Field(0.0, ge=0.0, le=10.0)
    relevance_score: float = Field(0.0, ge=0.0, le=1.0)
    rank: Optional[int]
    highlights: Optional[Dict[str, List[str]]] = Field(default_factory=dict)
    youtube_metadata: Optional[Dict[str, Any]] = None 

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_hits: int
    search_time: float
    page: int
    total_pages: int
    facets: Optional[Dict[str, Any]] = Field(default_factory=dict)

class DomainValidationResponse(BaseModel):
    query: str
    is_informatics_domain: bool
    confidence_score: float
    category: str
    message: str

class AutocompleteResponse(BaseModel):
    query: str
    suggestions: List[str]

class SimilarDocumentsRequest(BaseModel):
    doc_id: str
    size: int = Field(5, ge=1, le=20)

class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    search_preferences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    favorite_domains: List[str] = Field(default_factory=list)

class SearchPreferences(BaseModel):
    default_page_size: int = Field(10, ge=5, le=50)
    default_sort: str = Field("relevance")
    show_highlights: bool = True
    safe_search: bool = True
    preferred_domains: List[str] = Field(default_factory=list)


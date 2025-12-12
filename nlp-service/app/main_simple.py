from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="NLP Service Simple")

class HealthResponse(BaseModel):
    status: str
    service: str = "nlp-simple"
    version: str = "1.0.0"

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    original_query: str
    enhanced_query: Dict[str, Any]
    entities: Dict[str, List[str]]
    intent: str
    expanded_terms: List[str]

# Processeur NLP très simple
class SimpleNLP:
    def __init__(self):
        self.tech_synonyms = {
            "python": ["py", "python3", "programmation"],
            "java": ["jdk", "programmation java"],
            "javascript": ["js", "nodejs"],
            "docker": ["conteneur", "container"],
            "api": ["rest", "endpoint"],
            "base de données": ["database", "db", "sql"]
        }
        
    def expand_query(self, query: str):
        query_lower = query.lower()
        expanded_terms = []
        
        for term, synonyms in self.tech_synonyms.items():
            if term in query_lower:
                expanded_terms.extend(synonyms)
        
        # Détection d'intention basique
        intent = "general"
        if any(word in query_lower for word in ["comment", "apprendre", "tutoriel"]):
            intent = "tutorial"
        elif any(word in query_lower for word in ["erreur", "bug", "problème"]):
            intent = "error"
        
        # Entités basiques
        entities = {
            "programming_languages": [],
            "tools": []
        }
        
        if "python" in query_lower:
            entities["programming_languages"].append("python")
        if "docker" in query_lower:
            entities["tools"].append("docker")
        
        return {
            "original_query": query,
            "expanded_terms": list(set(expanded_terms)),
            "entities": entities,
            "intent": intent,
            "enhanced_query": {
                "query": {
                    "bool": {
                        "should": [
                            {"match": {"title": query}},
                            {"match": {"content": query}}
                        ]
                    }
                }
            }
        }

nlp_processor = SimpleNLP()

@app.get("/health")
async def health_check():
    return HealthResponse(status="healthy")

@app.get("/")
async def root():
    return {"message": "NLP Service Simple", "status": "ready"}

@app.post("/enhance-query")
async def enhance_query(request: QueryRequest):
    try:
        result = nlp_processor.expand_query(request.query)
        return result
    except Exception as e:
        raise HTTPException(500, f"Erreur: {str(e)}")

@app.post("/analyze")
async def analyze_text(request: Dict[str, Any]):
    text = request.get("text", "")
    if not text:
        raise HTTPException(400, "Text required")
    
    result = nlp_processor.expand_query(text)
    return {
        "original": text,
        "expanded_terms": result["expanded_terms"],
        "intent": result["intent"],
        "entities": result["entities"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, log_level="info")

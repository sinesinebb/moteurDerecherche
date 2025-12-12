# nlp-service/app/nlp_processor_simple.py
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class SimpleNLPProcessor:
    """Processeur NLP simplifié sans modèles lourds"""
    
    def __init__(self):
        logger.info("🚀 Initialisation du SimpleNLPProcessor...")
        
        # Termes techniques en informatique
        self.tech_synonyms = {
            "python": ["py", "python3", "programmation python"],
            "javascript": ["js", "nodejs", "typescript"],
            "java": ["jdk", "jvm", "programmation java"],
            "docker": ["conteneur", "container", "docker-compose"],
            "api": ["rest", "endpoint", "webservice"],
            "base de données": ["database", "db", "sql", "nosql"],
            "html": ["html5", "balisage"],
            "css": ["css3", "feuille de style"],
            "react": ["reactjs", "bibliothèque react"],
            "vue": ["vuejs", "framework vue"],
            "angular": ["angularjs", "framework angular"],
            "machine learning": ["ml", "ia", "intelligence artificielle"],
            "git": ["github", "gitlab", "versionning"],
            "linux": ["ubuntu", "terminal", "bash"],
            "windows": ["microsoft", "os windows"],
            "php": ["symfony", "laravel"],
            "c++": ["cpp", "programmation système"],
            "c#": ["csharp", "dotnet"],
            "sql": ["mysql", "postgresql"],
            "cloud": ["aws", "azure", "cloud computing"],
            "devops": ["ci/cd", "intégration continue"],
        }
        
        # Intentions de recherche
        self.search_intents = {
            "tutorial": ["comment", "apprendre", "débutant", "tutoriel", "guide"],
            "error": ["erreur", "bug", "problème", "solution", "corriger"],
            "comparison": ["vs", "comparaison", "différence", "meilleur"],
            "documentation": ["doc", "référence", "api", "fonction"],
            "installation": ["installer", "setup", "configuration"],
        }
        
        logger.info("✅ SimpleNLPProcessor prêt!")

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrait les entités basiques"""
        text_lower = text.lower()
        
        entities = {
            "programming_languages": [],
            "frameworks": [],
            "tools": [],
            "concepts": []
        }
        
        # Détection basique
        lang_keywords = ["python", "java", "javascript", "c++", "c#", "php", "ruby", "go", "rust"]
        framework_keywords = ["react", "vue", "angular", "django", "flask", "spring", "laravel"]
        tool_keywords = ["docker", "git", "kubernetes", "jenkins", "vscode"]
        concept_keywords = ["api", "rest", "microservices", "cloud", "devops"]
        
        for word in text_lower.split():
            if word in lang_keywords:
                entities["programming_languages"].append(word)
            elif word in framework_keywords:
                entities["frameworks"].append(word)
            elif word in tool_keywords:
                entities["tools"].append(word)
            elif word in concept_keywords:
                entities["concepts"].append(word)
        
        return {k: v for k, v in entities.items() if v}

    def expand_query(self, query: str) -> Dict[str, Any]:
        """Étend la requête avec des termes liés"""
        query_lower = query.lower()
        
        # Synonymes techniques
        expanded_terms = []
        for term, synonyms in self.tech_synonyms.items():
            if term in query_lower:
                expanded_terms.extend(synonyms)
        
        # Extraction d'entités
        entities = self.extract_entities(query)
        
        # Détection d'intention
        intent = self.detect_intent(query)
        
        return {
            "original_query": query,
            "expanded_terms": list(set(expanded_terms)),
            "entities": entities,
            "intent": intent,
            "semantic_embedding": [],
            "enhanced_query": self.build_enhanced_query(query, expanded_terms, entities, intent)
        }

    def detect_intent(self, query: str) -> str:
        """Détecte l'intention de la recherche"""
        query_lower = query.lower()
        
        for intent, keywords in self.search_intents.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        return "general"

    def build_enhanced_query(self, original_query: str, expanded_terms: List[str], 
                           entities: Dict, intent: str) -> Dict[str, Any]:
        """Construit une requête Elasticsearch enrichie"""
        
        should_clauses = []
        
        # Recherche exacte de la phrase
        should_clauses.append({
            "match_phrase": {
                "title": {
                    "query": original_query,
                    "boost": 5.0
                }
            }
        })
        
        # Recherche des termes
        all_terms = original_query.split() + expanded_terms
        for term in all_terms:
            if len(term) > 2:
                should_clauses.append({
                    "match": {
                        "title": {
                            "query": term,
                            "boost": 3.0,
                            "fuzziness": "AUTO"
                        }
                    }
                })
                should_clauses.append({
                    "match": {
                        "content": {
                            "query": term,
                            "boost": 1.5,
                            "fuzziness": "AUTO"
                        }
                    }
                })
        
        return {
            "query": {
                "bool": {
                    "should": should_clauses,
                    "minimum_should_match": 1
                }
            }
        }
# nlp-service/app/nlp_processor.py
import logging
from typing import List, Dict, Any
import re

logger = logging.getLogger(__name__)

class NLPProcessor:
    """Processeur NLP complet avec modèles avancés"""
    
    def __init__(self):
        logger.info("📥 Initialisation du NLPProcessor...")
        
        try:
            # Modèle français pour le traitement de base
            import spacy
            self.nlp_fr = spacy.load("fr_core_news_sm")
            logger.info("✅ Modèle spaCy fr_core_news_sm chargé")
        except Exception as e:
            logger.error(f"❌ Erreur chargement spaCy: {e}")
            raise
        
        try:
            # Modèle pour les embeddings sémantiques (multilingue)
            from sentence_transformers import SentenceTransformer
            self.semantic_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            logger.info("✅ Modèle SentenceTransformer chargé")
        except Exception as e:
            logger.error(f"❌ Erreur chargement SentenceTransformer: {e}")
            raise
        
        # Termes techniques en informatique
        self.tech_synonyms = {
            "python": ["py", "python3", "programmation python", "langage python"],
            "javascript": ["js", "ecmascript", "nodejs", "node.js", "typescript", "ts"],
            "java": ["jdk", "jvm", "programmation java", "java ee", "spring"],
            "docker": ["conteneur", "container", "dockerfile", "docker-compose", "orchestration"],
            "api": ["interface", "rest", "restful", "endpoint", "webservice", "graphql"],
            "base de données": ["database", "db", "sql", "nosql", "mongodb", "mysql", "postgresql"],
            "html": ["html5", "balisage", "markup", "hypertext"],
            "css": ["css3", "feuille de style", "stylesheet", "sass", "less"],
            "react": ["reactjs", "react.js", "bibliothèque react", "react native"],
            "vue": ["vuejs", "vue.js", "framework vue", "composition api"],
            "angular": ["angularjs", "angular.js", "framework angular", "typescript angular"],
            "machine learning": ["ml", "apprentissage automatique", "ia", "intelligence artificielle"],
            "deep learning": ["dl", "apprentissage profond", "réseaux de neurones", "neural network"],
            "git": ["github", "gitlab", "versionning", "contrôle version", "commit", "branch"],
            "linux": ["ubuntu", "debian", "centos", "terminal", "bash", "shell", "unix"],
            "windows": ["win", "microsoft", "os windows", "windows 10", "windows 11"],
            "macos": ["mac", "apple", "osx", "mac os"],
            "php": ["php7", "php8", "symfony", "laravel"],
            "c++": ["cpp", "c plus plus", "programmation système"],
            "c#": ["csharp", "dotnet", ".net", "asp.net"],
            "go": ["golang", "langage go"],
            "rust": ["rustlang", "système rust"],
            "sql": ["mysql", "postgresql", "sqlite", "requête sql"],
            "nosql": ["mongodb", "cassandra", "redis", "base document"],
            "cloud": ["aws", "azure", "gcp", "cloud computing", "serverless"],
            "devops": ["ci/cd", "intégration continue", "déploiement", "kubernetes"],
            "frontend": ["interface utilisateur", "ui", "ux", "développement web"],
            "backend": ["serveur", "api", "base de données", "logique métier"],
            "fullstack": ["frontend et backend", "développement complet"],
            "mobile": ["android", "ios", "react native", "flutter"],
            "web": ["site web", "application web", "navigateur", "http"]
        }
        
        # Intentions de recherche
        self.search_intents = {
            "tutorial": ["comment", "apprendre", "débutant", "tutoriel", "guide", "introduction", "pas à pas", "démarrage"],
            "error": ["erreur", "bug", "problème", "ne marche pas", "solution", "corriger", "exception", "crash"],
            "comparison": ["vs", "comparaison", "différence", "meilleur", "quel choisir", "avantages", "inconvénients"],
            "documentation": ["doc", "référence", "manuel", "api", "fonction", "méthode", "classe", "paramètre"],
            "installation": ["installer", "setup", "configuration", "démarrage", "mise en place", "prérequis"],
            "optimization": ["performance", "optimiser", "rapide", "lent", "améliorer", "efficace"],
            "best_practices": ["bonnes pratiques", "convention", "standard", "recommandation", "pattern"]
        }
        
        logger.info("✅ NLPProcessor initialisé avec succès")

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extrait les entités nommées et termes techniques"""
        doc = self.nlp_fr(text.lower())
        
        entities = {
            "programming_languages": [],
            "frameworks": [],
            "tools": [],
            "concepts": [],
            "technologies": [],
            "platforms": []
        }
        
        # Extraction des entités avec spaCy
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT"]:
                entities["technologies"].append(ent.text)
        
        # Détection des langages de programmation
        programming_keywords = [
            "python", "java", "javascript", "c++", "c#", "php", "ruby", 
            "go", "rust", "swift", "kotlin", "typescript", "scala"
        ]
        
        # Détection des frameworks
        framework_keywords = [
            "react", "vue", "angular", "django", "flask", "spring", "laravel", 
            "express", "rails", "asp.net", "symfony"
        ]
        
        # Détection des outils
        tool_keywords = [
            "docker", "git", "kubernetes", "jenkins", "webpack", "vscode", 
            "intellij", "eclipse", "postman"
        ]
        
        # Détection des concepts
        concept_keywords = [
            "api", "rest", "graphql", "microservices", "serverless", "cloud",
            "agile", "scrum", "devops", "ci/cd", "test", "debug"
        ]
        
        # Analyse token par token
        for token in doc:
            token_text = token.text.lower()
            
            if token_text in programming_keywords and token_text not in entities["programming_languages"]:
                entities["programming_languages"].append(token_text)
            elif token_text in framework_keywords and token_text not in entities["frameworks"]:
                entities["frameworks"].append(token_text)
            elif token_text in tool_keywords and token_text not in entities["tools"]:
                entities["tools"].append(token_text)
            elif token_text in concept_keywords and token_text not in entities["concepts"]:
                entities["concepts"].append(token_text)
        
        # Nettoyage des listes vides
        entities = {k: v for k, v in entities.items() if v}
        
        return entities

    def expand_query(self, query: str) -> Dict[str, Any]:
        """Étend la requête avec des termes sémantiquement liés"""
        query_lower = query.lower()
        
        # Synonymes techniques
        expanded_terms = []
        for term, synonyms in self.tech_synonyms.items():
            if term in query_lower:
                expanded_terms.extend(synonyms)
        
        # Recherche de termes partiels
        for term, synonyms in self.tech_synonyms.items():
            for word in query_lower.split():
                if word in term or term in word:
                    expanded_terms.extend(synonyms)
        
        # Extraction d'entités
        entities = self.extract_entities(query)
        
        # Détection d'intention
        intent = self.detect_intent(query)
        
        # Embedding sémantique
        try:
            import numpy as np
            semantic_embedding = self.semantic_model.encode([query])[0].tolist()
        except Exception as e:
            logger.warning(f"⚠️ Erreur génération embedding: {e}")
            semantic_embedding = []
        
        # Construction de la requête enrichie
        enhanced_query = self.build_enhanced_query(query, expanded_terms, entities, intent)
        
        return {
            "original_query": query,
            "expanded_terms": list(set(expanded_terms)),
            "entities": entities,
            "intent": intent,
            "semantic_embedding": semantic_embedding,
            "enhanced_query": enhanced_query
        }

    def detect_intent(self, query: str) -> str:
        """Détecte l'intention de la recherche"""
        query_lower = query.lower()
        
        for intent, keywords in self.search_intents.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
        
        # Détection basée sur des patterns
        if any(word in query_lower for word in ["comment", "how to", "tutoriel", "apprendre"]):
            return "tutorial"
        elif any(word in query_lower for word in ["erreur", "bug", "problem", "ne marche pas", "solution"]):
            return "error"
        elif any(word in query_lower for word in ["vs", "comparer", "différence", "meilleur"]):
            return "comparison"
        elif any(word in query_lower for word in ["installer", "setup", "configuration"]):
            return "installation"
        
        return "general"

    def build_enhanced_query(self, original_query: str, expanded_terms: List[str], 
                           entities: Dict, intent: str) -> Dict[str, Any]:
        """Construit une requête Elasticsearch enrichie"""
        
        # Termes de la requête originale
        original_terms = [term for term in original_query.split() if len(term) > 2]
        
        # Tous les termes à rechercher (original + expanded)
        all_terms = original_terms + expanded_terms
        
        # Construction de la requête booléenne
        should_clauses = []
        
        # 1. Recherche exacte de la phrase
        should_clauses.append({
            "match_phrase": {
                "title": {
                    "query": original_query,
                    "boost": 5.0
                }
            }
        })
        
        should_clauses.append({
            "match_phrase": {
                "content": {
                    "query": original_query,
                    "boost": 3.0
                }
            }
        })
        
        # 2. Recherche des termes individuels avec boost
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
        
        # 3. Filtrage par intention
        intent_filters = []
        if intent == "tutorial":
            intent_filters.append({
                "terms": {
                    "domain": [
                        "realpython.com", "tutorialspoint.com", "openclassrooms.com",
                        "doc.python.org", "developer.mozilla.org"
                    ]
                }
            })
        elif intent == "error":
            intent_filters.append({
                "terms": {
                    "domain": ["stackoverflow.com", "stackexchange.com", "github.com"]
                }
            })
        elif intent == "documentation":
            intent_filters.append({
                "terms": {
                    "domain": ["docs.python.org", "developer.mozilla.org", "reactjs.org"]
                }
            })
        
        return {
            "query": {
                "bool": {
                    "should": should_clauses,
                    "filter": intent_filters,
                    "minimum_should_match": 1
                }
            }
        }

    def semantic_similarity(self, query1: str, query2: str) -> float:
        """Calcule la similarité sémantique entre deux requêtes"""
        try:
            import numpy as np
            emb1 = self.semantic_model.encode([query1])
            emb2 = self.semantic_model.encode([query2])
            similarity = np.dot(emb1[0], emb2[0]) / (np.linalg.norm(emb1[0]) * np.linalg.norm(emb2[0]))
            return float(similarity)
        except Exception as e:
            logger.error(f"❌ Erreur calcul similarité: {e}")
            return 0.0
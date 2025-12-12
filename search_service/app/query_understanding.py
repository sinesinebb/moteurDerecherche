# search_service/app/query_understanding.py
import re
from typing import Dict, List, Tuple
import spacy

class QueryUnderstanding:
    def __init__(self):
        try:
            self.nlp = spacy.load("fr_core_news_sm")  # Modèle français
        except:
            self.nlp = None
            
    def analyze_query(self, query: str) -> Dict:
        """Analyse sémantique de la requête"""
        analysis = {
            'original_query': query,
            'cleaned_query': self.clean_query(query),
            'intent': self.detect_intent(query),
            'entities': self.extract_entities(query),
            'concepts': self.extract_concepts(query),
            'is_technical': self.is_technical_query(query)
        }
        
        # Expansion de requête basée sur l'intention
        analysis['expanded_queries'] = self.expand_query(analysis)
        
        return analysis
    
    def clean_query(self, query: str) -> str:
        """Nettoie et normalise la requête"""
        # Supprimer la ponctuation excessive
        query = re.sub(r'[^\w\s]', ' ', query)
        # Supprimer les espaces multiples
        query = re.sub(r'\s+', ' ', query).strip()
        return query.lower()
    
    def detect_intent(self, query: str) -> str:
        """Détecte l'intention de la requête"""
        query_lower = query.lower()
        
        intents = {
            'tutorial': ['comment', 'tutoriel', 'guide', 'apprendre', 'débutant'],
            'documentation': ['doc', 'documentation', 'référence', 'api'],
            'error': ['erreur', 'bug', 'problème', 'ne marche pas'],
            'comparison': ['vs', 'contre', 'comparaison', 'différence'],
            'code': ['exemple', 'code', 'snippet', 'implémentation']
        }
        
        for intent, keywords in intents.items():
            if any(keyword in query_lower for keyword in keywords):
                return intent
                
        return 'general'
    
    def extract_entities(self, query: str) -> List[str]:
        """Extrait les entités techniques"""
        if not self.nlp:
            return []
            
        doc = self.nlp(query)
        entities = []
        
        # Entités techniques courantes
        tech_entities = {
            'langages': ['python', 'javascript', 'java', 'c++', 'php', 'ruby'],
            'frameworks': ['react', 'vue', 'angular', 'django', 'flask', 'spring'],
            'outils': ['docker', 'kubernetes', 'git', 'jenkins', 'ansible'],
            'bdd': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch']
        }
        
        for category, items in tech_entities.items():
            for item in items:
                if item in query.lower():
                    entities.append(item)
                    
        return entities
    
    def extract_concepts(self, query: str) -> List[str]:
        """Extrait les concepts techniques"""
        concepts = []
        query_lower = query.lower()
        
        technical_concepts = [
            'programmation', 'développement', 'web', 'mobile', 'backend', 'frontend',
            'base de données', 'api', 'microservices', 'container', 'cloud',
            'machine learning', 'ia', 'devops', 'cybersécurité'
        ]
        
        for concept in technical_concepts:
            if concept in query_lower:
                concepts.append(concept)
                
        return concepts
    
    def is_technical_query(self, query: str) -> bool:
        """Détermine si la requête est technique"""
        technical_indicators = [
            'python', 'javascript', 'java', 'docker', 'kubernetes', 'react', 'vue',
            'api', 'database', 'programming', 'code', 'git', 'server', 'client'
        ]
        
        query_lower = query.lower()
        return any(indicator in query_lower for indicator in technical_indicators)
    
    def expand_query(self, analysis: Dict) -> List[str]:
        """Étend la requête avec des termes liés"""
        base_query = analysis['cleaned_query']
        expanded = [base_query]
        
        # Expansion basée sur l'intention
        if analysis['intent'] == 'tutorial':
            expanded.extend([
                f"{base_query} tutoriel",
                f"{base_query} guide",
                f"apprendre {base_query}"
            ])
        elif analysis['intent'] == 'documentation':
            expanded.extend([
                f"{base_query} documentation",
                f"{base_query} référence",
                f"{base_query} api"
            ])
            
        # Expansion basée sur les entités
        for entity in analysis['entities']:
            expanded.append(f"{base_query} {entity}")
            
        return expanded
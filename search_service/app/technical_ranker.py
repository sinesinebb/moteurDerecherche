class TechnicalRanker:
    def __init__(self):
        # Poids pour différents facteurs
        self.weights = {
            'technical_relevance': 0.35,
            'content_quality': 0.25,
            'source_authority': 0.20,
            'freshness': 0.10,
            'user_engagement': 0.10,
        }
    
    def rank_documents(self, documents: list, query: str) -> list:
        """Ré-ordonne les documents par pertinence technique"""
        ranked = []
        
        for doc in documents:
            # Score de base Elasticsearch
            base_score = doc.get('_score', 1.0)
            
            # Score technique
            technical_score = self._calculate_technical_score(doc, query)
            
            # Score combiné
            final_score = (
                base_score * 0.4 +
                technical_score * 0.6
            )
            
            # Ajouter le score technique au document
            doc['technical_score'] = technical_score
            doc['final_score'] = final_score
            
            ranked.append(doc)
        
        # Trier par score final
        ranked.sort(key=lambda x: x['final_score'], reverse=True)
        
        return ranked
    
    def _calculate_technical_score(self, doc: dict, query: str) -> float:
        """Calcule un score de pertinence technique"""
        metadata = doc.get('_source', {}).get('technical_metadata', {})
        
        scores = {
            'language_match': self._score_language_match(metadata, query),
            'difficulty_match': self._score_difficulty_match(metadata, query),
            'concept_coverage': self._score_concept_coverage(metadata, query),
            'content_completeness': self._score_content_completeness(doc),
            'source_quality': self._score_source_quality(doc),
        }
        
        # Combinaison pondérée
        technical_score = sum(
            scores[key] * weight 
            for key, weight in zip(scores.keys(), [0.3, 0.2, 0.3, 0.1, 0.1])
        )
        
        return technical_score

    def calculate_technical_relevance_score(self, text: str, query: str = "") -> Dict[str, float]:
        """
        Calcule un score de pertinence technique pour le document
        """
        scores = {
            'code_quality': 0.5,
            'concept_depth': 0.5,
            'structure_quality': 0.5,
            'source_authority': 0.5,
            'completeness': 0.5,
        }
        
        # Score basé sur la présence de code
        if self._has_code_examples(BeautifulSoup(text, 'lxml') if '<' in text else BeautifulSoup()):
            scores['code_quality'] = 0.8
        
        # Score basé sur la densité technique
        density = self._calculate_technical_density(text)
        if density > 0.1:
            scores['concept_depth'] = 0.9
        elif density > 0.05:
            scores['concept_depth'] = 0.7
        
        # Score basé sur la longueur (documents complets)
        word_count = len(text.split())
        if word_count > 1000:
            scores['completeness'] = 0.8
        elif word_count > 500:
            scores['completeness'] = 0.6
        
        # Score final pondéré
        weights = {
            'code_quality': 0.3,
            'concept_depth': 0.3,
            'structure_quality': 0.2,
            'source_authority': 0.1,
            'completeness': 0.1,
        }
        
        final_score = sum(scores[key] * weights[key] for key in scores)
        
        return {
            'scores': scores,
            'final_score': final_score,
            'weights': weights
        }
    
    def _score_language_match(self, metadata: dict, query: str) -> float:
        """Score basé sur la correspondance des langages"""
        query_lower = query.lower()
        doc_languages = metadata.get('programming_languages', [])
        
        # Langages courants à chercher dans la requête
        language_keywords = {
            'python': ['python', 'django', 'flask'],
            'javascript': ['javascript', 'js', 'node', 'react'],
            'java': ['java', 'spring'],
            'sql': ['sql', 'database', 'mysql'],
        }
        
        # Vérifier si la requête mentionne un langage
        for lang, keywords in language_keywords.items():
            if any(kw in query_lower for kw in keywords):
                # Vérifier si le document contient ce langage
                if lang.capitalize() in doc_languages:
                    return 1.0
        
        return 0.5  # Score neutre si pas de correspondance
    
    def _score_difficulty_match(self, metadata: dict, query: str) -> float:
        """Score basé sur le niveau de difficulté"""
        query_lower = query.lower()
        doc_difficulty = metadata.get('difficulty_level', 'intermediate')
        
        # Détecter le niveau recherché dans la requête
        if 'beginner' in query_lower or 'basic' in query_lower or 'introduction' in query_lower:
            desired_difficulty = 'beginner'
        elif 'advanced' in query_lower or 'expert' in query_lower or 'deep' in query_lower:
            desired_difficulty = 'advanced'
        else:
            desired_difficulty = 'intermediate'
        
        # Score de correspondance
        if doc_difficulty == desired_difficulty:
            return 1.0
        elif abs(self._difficulty_to_num(doc_difficulty) - self._difficulty_to_num(desired_difficulty)) <= 1:
            return 0.7
        else:
            return 0.3
    
    def _difficulty_to_num(self, difficulty: str) -> int:
        """Convertit le niveau de difficulté en nombre"""
        mapping = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
        return mapping.get(difficulty, 2)
    
    def _score_concept_coverage(self, metadata: dict, query: str) -> float:
        """Score basé sur la couverture des concepts"""
        query_concepts = self._extract_concepts_from_query(query)
        doc_concepts = metadata.get('technical_concepts', [])
        
        if not query_concepts:
            return 0.5
        
        # Calculer le pourcentage de concepts couverts
        matches = sum(1 for concept in query_concepts if concept in doc_concepts)
        
        return matches / len(query_concepts)
    
    def _extract_concepts_from_query(self, query: str) -> list:
        """Extrait les concepts techniques de la requête"""
        concept_mapping = {
            'algorithm': ['algorithm', 'complexity', 'sort'],
            'database': ['database', 'sql', 'query', 'index'],
            'api': ['api', 'rest', 'endpoint', 'json'],
            'security': ['security', 'encrypt', 'auth', 'jwt'],
            'devops': ['docker', 'kubernetes', 'deploy', 'ci/cd'],
        }
        
        concepts = []
        query_lower = query.lower()
        
        for concept, keywords in concept_mapping.items():
            if any(kw in query_lower for kw in keywords):
                concepts.append(concept)
        
        return concepts
    
    def _score_content_completeness(self, doc: dict) -> float:
        """Score basé sur la complétude du contenu"""
        source = doc.get('_source', {})
        metadata = source.get('technical_metadata', {})
        
        score = 0.5  # Score de base
        
        # Bonus pour différents types de contenu
        if metadata.get('has_code_examples'):
            score += 0.2
        
        if len(metadata.get('programming_languages', [])) >= 2:
            score += 0.1
        
        if metadata.get('technical_density', 0) > 0.05:
            score += 0.1
        
        # Malus pour les documents très courts
        content = source.get('content', '')
        if len(content.split()) < 100:
            score -= 0.3
        
        return max(0.1, min(1.0, score))
    
    def _score_source_quality(self, doc: dict) -> float:
        """Score basé sur la qualité de la source"""
        url = doc.get('_source', {}).get('url', '')
        
        # Domaines de haute qualité technique
        high_quality_domains = {
            'docs.python.org': 1.0,
            'developer.mozilla.org': 0.9,
            'kubernetes.io': 0.9,
            'reactjs.org': 0.8,
            'github.com': 0.8,
            'stackoverflow.com': 0.7,
            'medium.com': 0.5,
        }
        
        # Vérifier le domaine
        for domain, quality in high_quality_domains.items():
            if domain in url:
                return quality
        
        # Vérifier si c'est de la documentation (contient /docs/)
        if '/docs/' in url or 'documentation' in url:
            return 0.7
        
        # Par défaut
        return 0.5
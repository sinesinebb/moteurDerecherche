# services/domain_validator.py
import re
from typing import List, Tuple, Dict
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import spacy

class DomainValidator:
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_sm")
        self.it_keywords = {
            'programmation': ['python', 'java', 'javascript', 'c++', 'programmation', 'code', 'développement'],
            'ia': ['intelligence artificielle', 'machine learning', 'deep learning', 'neuronal', 'ai'],
            'cybersécurité': ['sécurité', 'cybersécurité', 'hacking', 'virus', 'malware', 'firewall'],
            'réseaux': ['réseau', 'tcp/ip', 'router', 'switch', 'protocole', 'internet'],
            'bdd': ['base de données', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql'],
            'cloud': ['cloud', 'aws', 'azure', 'gcp', 'docker', 'kubernetes'],
            'web': ['web', 'html', 'css', 'http', 'api', 'rest', 'frontend', 'backend'],
            'mobile': ['mobile', 'android', 'ios', 'react native', 'flutter'],
            'devops': ['devops', 'ci/cd', 'jenkins', 'git', 'intégration'],
            'hardware': ['processeur', 'ram', 'disque dur', 'carte mère', 'composants']
        }
        
        self.vectorizer = TfidfVectorizer()
        self._train_vectorizer()
    
    def _train_vectorizer(self):
        """Entraîne le vectorizer sur les mots-clés informatiques"""
        all_keywords = []
        for category, keywords in self.it_keywords.items():
            all_keywords.extend(keywords)
        self.vectorizer.fit(all_keywords)
    
    def is_informatics_domain(self, query: str) -> Tuple[bool, float, str]:
        """
        Vérifie si la requête concerne l'informatique
        Retourne: (est_informatique, score_confiance, categorie)
        """
        # Nettoyage de la requête
        cleaned_query = self._clean_text(query)
        
        # 1. Vérification par mots-clés exacts
        keyword_match, category = self._check_keywords(cleaned_query)
        if keyword_match:
            return True, 0.95, category
        
        # 2. Vérification par similarité sémantique
        similarity_score = self._calculate_similarity(cleaned_query)
        
        # 3. Vérification par entités nommées
        entity_score = self._check_named_entities(cleaned_query)
        
        # Score combiné
        final_score = max(similarity_score, entity_score)
        
        is_it = final_score > 0.6
        return is_it, final_score, self._categorize_query(cleaned_query)
    
    def _clean_text(self, text: str) -> str:
        """Nettoie et normalise le texte"""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        return ' '.join(text.split())
    
    def _check_keywords(self, query: str) -> Tuple[bool, str]:
        """Vérifie la présence de mots-clés informatiques"""
        words = query.split()
        for word in words:
            for category, keywords in self.it_keywords.items():
                if word in keywords:
                    return True, category
        return False, "unknown"
    
    def _calculate_similarity(self, query: str) -> float:
        """Calcule la similarité TF-IDF avec le domaine informatique"""
        try:
            query_vector = self.vectorizer.transform([query])
            # Calculer la similarité avec chaque catégorie
            max_similarity = 0.0
            for category, keywords in self.it_keywords.items():
                category_text = ' '.join(keywords)
                category_vector = self.vectorizer.transform([category_text])
                similarity = np.dot(query_vector.toarray(), category_vector.toarray().T)[0][0]
                max_similarity = max(max_similarity, similarity)
            return min(max_similarity * 2, 1.0)  # Normaliser
        except:
            return 0.0
    
    def _check_named_entities(self, query: str) -> float:
        """Utilise SpaCy pour détecter les entités liées à l'informatique"""
        doc = self.nlp(query)
        it_entities = {'TECHNOLOGY', 'PROGRAMMING', 'COMPUTER', 'SOFTWARE'}
        
        entity_count = 0
        for ent in doc.ents:
            if ent.label_ in it_entities or any(keyword in ent.text.lower() for keyword in 
                                              ['python', 'java', 'javascript', 'html', 'css']):
                entity_count += 1
        
        return min(entity_count * 0.3, 1.0)
    
    def _categorize_query(self, query: str) -> str:
        """Catégorise la requête"""
        scores = {}
        for category, keywords in self.it_keywords.items():
            category_text = ' '.join(keywords)
            category_vector = self.vectorizer.transform([category_text])
            query_vector = self.vectorizer.transform([query])
            similarity = np.dot(query_vector.toarray(), category_vector.toarray().T)[0][0]
            scores[category] = similarity
        
        return max(scores.items(), key=lambda x: x[1])[0] if scores else "unknown"
    
    def get_suggestions(self, query: str) -> List[str]:
        """Propose des suggestions pour les requêtes hors domaine"""
        if "cuisine" in query.lower():
            return ["Recettes algorithmiques", "Python pour la data science"]
        elif "sport" in query.lower():
            return ["Analyse de données sportives", "Applications fitness"]
        elif "musique" in query.lower():
            return ["Traitement audio avec Python", "Algorithmes de recommandation musicale"]
        else:
            return ["Développement web", "Intelligence artificielle", "Cybersécurité"]
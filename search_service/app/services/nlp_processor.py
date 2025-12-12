# services/nlp_processor.py
import spacy
import re
from typing import List, Dict, Tuple
from collections import Counter
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class NLPProcessor:
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_sm")
        self.stop_words = set(stopwords.words('french'))
        self.vectorizer = TfidfVectorizer(max_features=1000)
        
        # Termes techniques informatiques
        self.technical_terms = {
            'python', 'java', 'javascript', 'react', 'vue', 'angular',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'machine learning', 'deep learning', 'neural network',
            'api', 'rest', 'graphql', 'microservices', 'serverless'
        }
    
    def extract_key_phrases(self, text: str, num_phrases: int = 5) -> List[Tuple[str, float]]:
        """Extrait les phrases clés d'un texte"""
        doc = self.nlp(text)
        
        # Extraction des entités nommées
        entities = [(ent.text, ent.label_) for ent in doc.ents]
        
        # Extraction des termes techniques
        technical_terms_found = []
        for term in self.technical_terms:
            if term in text.lower():
                technical_terms_found.append(term)
        
        # Calcul TF-IDF pour les mots
        sentences = [sent.text for sent in doc.sents]
        if len(sentences) > 1:
            tfidf_matrix = self.vectorizer.fit_transform(sentences)
            sentence_scores = np.array(tfidf_matrix.sum(axis=1)).flatten()
            
            scored_sentences = []
            for i, score in enumerate(sentence_scores):
                # Bonus pour les phrases contenant des termes techniques
                tech_bonus = sum(1 for term in technical_terms_found if term in sentences[i].lower())
                final_score = score + (tech_bonus * 0.5)
                scored_sentences.append((sentences[i], final_score))
            
            # Trier et retourner les meilleures phrases
            scored_sentences.sort(key=lambda x: x[1], reverse=True)
            return scored_sentences[:num_phrases]
        
        return []
    
    def analyze_query_intent(self, query: str) -> Dict:
        """Analyse l'intention derrière la requête"""
        doc = self.nlp(query.lower())
        
        intent = {
            'type': 'unknown',
            'technologies': [],
            'concepts': [],
            'is_howto': False,
            'is_problem': False,
            'is_comparison': False
        }
        
        # Détection du type d'intention
        if any(word in query.lower() for word in ['comment', 'how to', 'tutoriel', 'guide']):
            intent['type'] = 'howto'
            intent['is_howto'] = True
        
        elif any(word in query.lower() for word in ['erreur', 'problem', 'bug', 'fix', 'résoudre']):
            intent['type'] = 'problem'
            intent['is_problem'] = True
        
        elif any(word in query.lower() for word in ['vs', 'comparison', 'difference', 'meilleur']):
            intent['type'] = 'comparison'
            intent['is_comparison'] = True
        
        # Extraction des technologies
        for ent in doc.ents:
            if ent.label_ in ['TECHNOLOGY', 'PROGRAMMING']:
                intent['technologies'].append(ent.text)
        
        # Extraction des concepts
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and token.text not in self.stop_words:
                if len(token.text) > 2:  # Éviter les mots trop courts
                    intent['concepts'].append(token.text)
        
        return intent
    
    def spell_check(self, query: str) -> Tuple[str, List[str]]:
        """Correction orthographique basique pour l'informatique"""
        common_mistakes = {
            'javascrip': 'javascript',
            'pythn': 'python',
            'reac': 'react',
            'anguler': 'angular',
            'dockr': 'docker',
            'kubernete': 'kubernetes',
            'mongo': 'mongodb',
            'postgre': 'postgresql'
        }
        
        corrected = query
        corrections = []
        
        for wrong, correct in common_mistakes.items():
            if wrong in query.lower():
                corrected = corrected.replace(wrong, correct)
                corrections.append(f"{wrong} → {correct}")
        
        return corrected, corrections
    
    def generate_query_variations(self, query: str) -> List[str]:
        """Génère des variations de la requête pour améliorer les résultats"""
        variations = [query]
        
        # Ajout de synonymes pour les termes courants
        synonyms = {
            'apprendre': ['tutoriel', 'guide', 'débutant'],
            'problème': ['erreur', 'bug', 'issue', 'solution'],
            'meilleur': ['top', 'comparaison', 'recommandation'],
            'installation': ['setup', 'configurer', 'déployer']
        }
        
        for original, synonym_list in synonyms.items():
            if original in query.lower():
                for synonym in synonym_list:
                    variation = query.lower().replace(original, synonym)
                    variations.append(variation)
        
        return list(set(variations))  # Supprimer les doublons
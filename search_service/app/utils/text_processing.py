# app/utils/text_processing.py
import re
import string
from typing import List, Tuple, Dict
import unicodedata
from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize
import nltk

# Télécharger les ressources NLTK nécessaires (à faire une fois)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class TextProcessor:
    """Processeur de texte pour le traitement des requêtes et contenus"""
    
    def __init__(self, language: str = "french"):
        self.language = language
        self.stemmer = SnowballStemmer(language)
        self.stop_words = self._load_stop_words()
        
        # Expressions régulières pour les patterns techniques
        self.tech_patterns = {
            'programming_language': r'\b(python|java|javascript|typescript|c\+\+|c#|go|rust|ruby|php|swift|kotlin)\b',
            'framework': r'\b(react|vue|angular|django|flask|spring|laravel|express|rails)\b',
            'database': r'\b(mysql|postgresql|mongodb|redis|elasticsearch|sqlite|oracle)\b',
            'tool': r'\b(docker|kubernetes|git|jenkins|ansible|terraform|aws|azure|gcp)\b'
        }
    
    def _load_stop_words(self) -> set:
        """Charge les stop words pour la langue française"""
        french_stop_words = {
            'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'ou', 'à', 'au', 'aux',
            'en', 'dans', 'par', 'pour', 'sur', 'avec', 'sans', 'sous', 'chez', 'dont', 'que',
            'qui', 'quoi', 'quand', 'où', 'comment', 'pourquoi', 'car', 'donc', 'or', 'ni'
        }
        return french_stop_words
    
    def normalize_text(self, text: str) -> str:
        """Normalise le texte : minuscules, suppression accents, etc."""
        if not text:
            return ""
        
        # Convertir en minuscules
        text = text.lower()
        
        # Supprimer les accents
        text = unicodedata.normalize('NFKD', text)
        text = ''.join(c for c in text if not unicodedata.combining(c))
        
        # Supprimer la ponctuation excessive
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Remplacer les espaces multiples
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def tokenize(self, text: str, remove_stopwords: bool = True) -> List[str]:
        """Tokenise le texte en mots"""
        normalized = self.normalize_text(text)
        tokens = word_tokenize(normalized, language='french')
        
        if remove_stopwords:
            tokens = [token for token in tokens if token not in self.stop_words]
        
        return tokens
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """Applique le stemming sur les tokens"""
        return [self.stemmer.stem(token) for token in tokens]
    
    def extract_technical_terms(self, text: str) -> Dict[str, List[str]]:
        """Extrait les termes techniques du texte"""
        technical_terms = {}
        
        for category, pattern in self.tech_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                technical_terms[category] = list(set(matches))
        
        return technical_terms
    
    def calculate_term_frequency(self, text: str, terms: List[str]) -> Dict[str, float]:
        """Calcule la fréquence des termes dans le texte"""
        tokens = self.tokenize(text, remove_stopwords=True)
        total_tokens = len(tokens)
        
        term_freq = {}
        for term in terms:
            term_tokens = self.tokenize(term, remove_stopwords=True)
            # Compter les occurrences de chaque token du terme
            count = sum(1 for token in tokens if token in term_tokens)
            term_freq[term] = count / total_tokens if total_tokens > 0 else 0
        
        return term_freq
    
    def generate_ngrams(self, text: str, n: int) -> List[str]:
        """Génère les n-grams du texte"""
        tokens = self.tokenize(text, remove_stopwords=False)
        ngrams = []
        
        for i in range(len(tokens) - n + 1):
            ngram = ' '.join(tokens[i:i + n])
            ngrams.append(ngram)
        
        return ngrams
    
    def detect_language(self, text: str) -> str:
        """Détecte la langue du texte (simplifié)"""
        # Patterns pour détecter le français
        french_patterns = [
            r'\b(le|la|les|de|des|du|un|une|et|est|à|au|aux|en|dans)\b',
            r'\b(il|elle|nous|vous|ils|elles|son|sa|ses|notre|votre)\b'
        ]
        
        english_patterns = [
            r'\b(the|a|an|and|is|are|to|in|on|at|for|with|by)\b',
            r'\b(he|she|it|we|you|they|his|her|its|our|your|their)\b'
        ]
        
        french_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) 
                          for pattern in french_patterns)
        english_count = sum(len(re.findall(pattern, text, re.IGNORECASE)) 
                           for pattern in english_patterns)
        
        if french_count > english_count:
            return "french"
        elif english_count > french_count:
            return "english"
        else:
            return "unknown"
    
    def extract_code_snippets(self, text: str) -> List[str]:
        """Extrait les snippets de code du texte"""
        # Patterns pour détecter le code
        code_patterns = [
            r'```[\s\S]*?```',  # Code blocks avec backticks
            r'`[^`]*`',         # Code inline
            r'<code>[\s\S]*?</code>',  # Balises HTML code
            r'def\s+\w+\([^)]*\):',  # Définition de fonction Python
            r'function\s+\w+\([^)]*\)',  # Définition de fonction JavaScript
            r'class\s+\w+',     # Définition de classe
            r'import\s+\w+',    # Import statements
        ]
        
        snippets = []
        for pattern in code_patterns:
            matches = re.findall(pattern, text)
            snippets.extend(matches)
        
        return snippets

# Instance globale
text_processor = TextProcessor()
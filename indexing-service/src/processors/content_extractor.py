# content_extractor.py (version corrigée et simplifiée)
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from src.models.document_models import (
    RawResponseItem, Section, Document, 
    TechnicalMetadata, ContentQualityMetrics,
    DifficultyLevel, DocumentType
)
import uuid
from urllib.parse import urlparse
import re
from datetime import datetime
import html2text


# ========== FONCTIONS UTILITAIRES ==========
def _first_meta_content(soup, name: str):
    tag = soup.find("meta", {"name": name})
    if tag and tag.get("content"):
        return tag.get("content").strip()
    return None


def extract_media_urls(soup, base_url: str) -> tuple[list, list]:
    """Extrait les URLs des images et vidéos de la page"""
    image_urls = []
    video_urls = []
    
    # Images
    for img in soup.find_all('img'):
        src = img.get('src') or img.get('data-src') or img.get('data-original')
        if src:
            try:
                full_url = urljoin(base_url, src.strip())
                image_urls.append(full_url)
            except:
                continue
    
    # Vidéos
    for video in soup.find_all('video'):
        src = video.get('src')
        if src:
            try:
                full_url = urljoin(base_url, src.strip())
                video_urls.append(full_url)
            except:
                continue
        # Sources dans video
        for source in video.find_all('source'):
            src = source.get('src')
            if src:
                try:
                    full_url = urljoin(base_url, src.strip())
                    video_urls.append(full_url)
                except:
                    continue
    
    return list(set(image_urls)), list(set(video_urls))


def extract_meaningful_content(soup) -> str:
    """Extrait le contenu textuel significatif"""
    # Supprimer les éléments non pertinents
    for element in soup.find_all(['nav', 'footer', 'header', 'aside', 'script', 'style']):
        element.decompose()
    
    # Chercher le contenu principal
    main_selectors = ['main', 'article', '.content', '.main-content', '#content']
    main_content = None
    
    for selector in main_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    if not main_content:
        main_content = soup.find('body') or soup
    
    # Convertir en texte
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    
    content_text = h.handle(str(main_content)) if main_content else ""
    
    # Nettoyer
    content_text = re.sub(r'\n\s*\n', '\n\n', content_text)
    content_text = re.sub(r' {2,}', ' ', content_text)
    
    return content_text.strip()


def detect_language(text: str) -> str:
    """Détecte la langue du contenu"""
    if not text:
        return "en"
    
    text_lower = text.lower()
    
    french_words = ['le', 'la', 'les', 'un', 'une', 'des', 'est', 'sont']
    english_words = ['the', 'a', 'an', 'is', 'are', 'and', 'or', 'but']
    
    french_count = sum(1 for word in french_words if f' {word} ' in f' {text_lower} ')
    english_count = sum(1 for word in english_words if f' {word} ' in f' {text_lower} ')
    
    return 'fr' if french_count > english_count else 'en'


def extract_domain_authority(url: str) -> int:
    """Score d'autorité du domaine"""
    domain = urlparse(url).netloc.lower()
    
    authority_scores = {
        'stackoverflow.com': 100,
        'github.com': 95,
        'docs.python.org': 90,
        'developer.mozilla.org': 90,
        'reactjs.org': 85,
        'docker.com': 85,
        'kubernetes.io': 85,
        'realpython.com': 80,
        'dev.to': 75,
        'freecodecamp.org': 70,
    }
    
    for domain_key, score in authority_scores.items():
        if domain_key in domain:
            return score
    
    return 50


def calculate_content_quality(content: str, soup: BeautifulSoup) -> ContentQualityMetrics:
    """Calcule les métriques de qualité"""
    if not content:
        return ContentQualityMetrics()
    
    words = content.split()
    word_count = len(words)
    
    # Score de lisibilité
    sentences = re.split(r'[.!?]+', content)
    avg_sentence_len = word_count / max(len(sentences), 1)
    
    if avg_sentence_len < 20:
        readability = 0.8
    elif avg_sentence_len < 30:
        readability = 0.6
    else:
        readability = 0.4
    
    # Score de structure
    headings = soup.find_all(['h1', 'h2', 'h3'])
    paragraphs = soup.find_all('p')
    
    structure = 0.5
    if len(headings) >= 2:
        structure += 0.2
    if len(paragraphs) >= 3:
        structure += 0.3
    
    # Score de complétude
    completeness = min(1.0, word_count / 500)
    
    # Score global
    overall = (readability * 0.2) + (structure * 0.3) + (completeness * 0.5)
    
    return ContentQualityMetrics(
        readability_score=readability,
        structure_score=structure,
        completeness_score=completeness,
        accuracy_score=0.7,  # Valeur par défaut
        overall_quality=overall
    )


def urljoin(base: str, url: str) -> str:
    """Version simplifiée de urljoin"""
    if url.startswith(('http://', 'https://')):
        return url
    elif url.startswith('/'):
        parsed_base = urlparse(base)
        return f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
    else:
        return base.rstrip('/') + '/' + url.lstrip('/')


# ========== ANALYSEUR TECHNIQUE ==========
class TechnicalContentAnalyzer:
    """Analyse le contenu technique"""
    
    def analyze(self, html: str, url: str, text: str) -> TechnicalMetadata:
        """Analyse le contenu et retourne les métadonnées techniques"""
        soup = BeautifulSoup(html, 'lxml')
        
        # Langages détectés
        languages = self._detect_languages(text)
        
        # Concepts techniques
        concepts = self._detect_concepts(text)
        
        # Niveau de difficulté
        difficulty = self._estimate_difficulty(text, soup)
        
        # Type de document
        doc_type = self._classify_document(url, text, soup)
        
        # Score d'autorité
        authority = self._calculate_authority(url, text)
        
        # Présence de code
        has_code = self._has_code(soup)
        
        # Densité technique
        density = self._calculate_density(text)
        
        # Score technique
        tech_score = self._calculate_tech_score(languages, concepts, difficulty, authority)
        
        return TechnicalMetadata(
            programming_languages=languages,
            technical_concepts=concepts,
            difficulty_level=difficulty,
            has_code_examples=has_code,
            code_types=self._detect_code_types(soup),
            technical_density=density,
            document_type=doc_type,
            technical_authority=authority,
            reading_time_minutes=max(1, len(text.split()) // 200),
            has_shell_commands=self._has_shell_commands(text),
            has_diagrams=self._has_diagrams(soup),
            technical_score=tech_score
        )
    
    def _detect_languages(self, text: str) -> List[str]:
        """Détecte les langages de programmation"""
        lang_keywords = {
            'Python': ['python', 'py', 'django', 'flask'],
            'JavaScript': ['javascript', 'js', 'node', 'react', 'vue'],
            'Java': ['java', 'spring'],
            'SQL': ['sql', 'mysql', 'postgresql'],
            'HTML/CSS': ['html', 'css'],
            'C++': ['c++', 'cpp'],
            'C#': ['c#', 'csharp'],
            'PHP': ['php'],
            'Ruby': ['ruby'],
            'Go': ['go', 'golang'],
        }
        
        detected = []
        text_lower = text.lower()
        
        for lang, keywords in lang_keywords.items():
            for keyword in keywords:
                if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                    detected.append(lang)
                    break
        
        return detected
    
    def _detect_concepts(self, text: str) -> List[str]:
        """Détecte les concepts techniques"""
        concepts = {
            'algorithm': ['algorithm', 'complexity', 'sorting'],
            'api': ['api', 'rest', 'endpoint'],
            'database': ['database', 'sql', 'query'],
            'security': ['security', 'encryption', 'authentication'],
            'devops': ['docker', 'kubernetes', 'deployment'],
            'web': ['http', 'json', 'xml'],
            'testing': ['test', 'unit', 'integration'],
            'cloud': ['aws', 'azure', 'cloud'],
        }
        
        detected = []
        text_lower = text.lower()
        
        for concept, keywords in concepts.items():
            for keyword in keywords:
                if keyword in text_lower:
                    detected.append(concept)
                    break
        
        return detected
    
    def _estimate_difficulty(self, text: str, soup: BeautifulSoup) -> DifficultyLevel:
        """Estime le niveau de difficulté"""
        text_lower = text.lower()
        
        if 'beginner' in text_lower or 'introduction' in text_lower:
            return DifficultyLevel.BEGINNER
        elif 'advanced' in text_lower or 'expert' in text_lower:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.INTERMEDIATE
    
    def _classify_document(self, url: str, text: str, soup: BeautifulSoup) -> DocumentType:
        """Classifie le type de document"""
        url_lower = url.lower()
        text_lower = text.lower()
        
        if '/docs/' in url_lower or 'documentation' in url_lower:
            return DocumentType.DOCUMENTATION
        elif 'stackoverflow.com' in url_lower:
            return DocumentType.QNA
        elif 'github.com' in url_lower:
            return DocumentType.CODE_REPOSITORY
        elif 'tutorial' in text_lower or 'guide' in text_lower:
            return DocumentType.TUTORIAL
        elif self._has_code(soup):
            return DocumentType.CODE_EXAMPLE
        else:
            return DocumentType.GENERAL
    
    def _calculate_authority(self, url: str, text: str) -> int:
        """Calcule le score d'autorité"""
        score = 50
        
        # Basé sur le domaine
        domain = urlparse(url).netloc.lower()
        high_auth_domains = ['docs.python.org', 'developer.mozilla.org', 'kubernetes.io']
        
        if any(domain in high_auth for high_auth in high_auth_domains):
            score += 30
        
        # Basé sur le contenu
        if len(self._detect_languages(text)) >= 2:
            score += 10
        
        if len(self._detect_concepts(text)) >= 3:
            score += 10
        
        return min(100, score)
    
    def _has_code(self, soup: BeautifulSoup) -> bool:
        """Vérifie la présence de code"""
        return bool(soup.find_all(['pre', 'code']))
    
    def _detect_code_types(self, soup: BeautifulSoup) -> List[str]:
        """Détecte les types de code"""
        code_elements = soup.find_all(['pre', 'code'])
        code_text = ' '.join([el.get_text() for el in code_elements])
        
        types = []
        if 'def ' in code_text or 'import ' in code_text:
            types.append('python')
        if 'function' in code_text or 'const ' in code_text:
            types.append('javascript')
        if 'SELECT ' in code_text.upper():
            types.append('sql')
        
        return types
    
    def _calculate_density(self, text: str) -> float:
        """Calcule la densité technique"""
        if not text:
            return 0.0
        
        words = text.lower().split()
        if not words:
            return 0.0
        
        # Mots techniques à rechercher
        tech_words = {
            'python', 'javascript', 'java', 'sql', 'html', 'css',
            'algorithm', 'function', 'class', 'object', 'api',
            'database', 'server', 'client', 'network', 'protocol'
        }
        
        tech_count = sum(1 for word in words if word in tech_words)
        return tech_count / len(words)
    
    def _has_shell_commands(self, text: str) -> bool:
        """Vérifie la présence de commandes shell"""
        return bool(re.search(r'\$\s+[a-z]', text.lower()))
    
    def _has_diagrams(self, soup: BeautifulSoup) -> bool:
        """Vérifie la présence de diagrammes"""
        for img in soup.find_all('img'):
            alt = img.get('alt', '').lower()
            if 'diagram' in alt or 'schema' in alt:
                return True
        return False
    
    def _calculate_tech_score(self, languages: List[str], concepts: List[str], 
                            difficulty: DifficultyLevel, authority: int) -> float:
        """Calcule le score technique global"""
        score = 0.0
        
        if languages:
            score += 0.3
        
        if concepts:
            score += min(0.3, len(concepts) * 0.1)
        
        if difficulty == DifficultyLevel.ADVANCED:
            score += 0.2
        elif difficulty == DifficultyLevel.INTERMEDIATE:
            score += 0.1
        
        score += (authority / 100.0) * 0.2
        
        return min(1.0, max(0.1, score))


# ========== FONCTION PRINCIPALE ==========
def extract_content(raw_item: Dict) -> Document:
    """
    Convertit un RawResponseItem en Document avec métadonnées techniques
    """
    # Valider les données d'entrée
    r = RawResponseItem(**raw_item)
    body = r.body or ""
    soup = BeautifulSoup(body, "lxml")
    
    # Titre et description
    title = r.title or (soup.title.string.strip() if soup.title and soup.title.string else "")
    description = r.description or _first_meta_content(soup, "description")
    
    # Extraire le contenu
    extracted_content = extract_meaningful_content(soup)
    
    # URLs des médias
    image_urls, video_urls = extract_media_urls(soup, str(r.url))
    
    # Analyse technique
    technical_analyzer = TechnicalContentAnalyzer()
    technical_metadata = technical_analyzer.analyze(body, str(r.url), extracted_content)
    
    # Métriques de qualité
    content_quality = calculate_content_quality(extracted_content, soup)
    
    # Calculer le score global de qualité
    overall_quality = (
        (technical_metadata.technical_score * 0.4) +
        (content_quality.overall_quality * 0.3) +
        (technical_metadata.technical_authority / 100.0 * 0.3)
    )
    
    # Créer le document
    doc = Document(
        doc_id=str(uuid.uuid4()),
        url=str(r.url),
        crawl_meta={"appid": r.appid, "crawlid": r.crawlid},
        title=title,
        description=description,
        sections=[],  # Sections optionnelles pour l'instant
        raw=r,
        
        # Métadonnées de base
        image_urls=image_urls,
        video_urls=video_urls,
        media_count=len(image_urls) + len(video_urls),
        content_type="text",
        extracted_content=extracted_content,
        domain=urlparse(str(r.url)).netloc,
        crawled_at=r.crawled_at or datetime.now().isoformat(),
        snippet=extracted_content[:200] + "..." if len(extracted_content) > 200 else extracted_content,
        
        # Métadonnées techniques
        technical_metadata=technical_metadata,
        content_quality=content_quality,
        domain_authority=extract_domain_authority(str(r.url)),
        overall_quality_score=overall_quality,
        detected_language=detect_language(extracted_content),
        word_count=len(extracted_content.split()),
        paragraph_count=len(extracted_content.split('\n\n')),
        code_block_count=len(soup.find_all(['pre', 'code'])),
        technical_keywords=technical_metadata.programming_languages + technical_metadata.technical_concepts,
        tags=technical_metadata.technical_concepts[:3] + [technical_metadata.document_type.value]
    )
    
    return doc
from typing import Dict
from bs4 import BeautifulSoup
from src.models.document_models import RawResponseItem, Section, Document
import uuid
from urllib.parse import urlparse
import re
from datetime import datetime
import html2text


def _first_meta_content(soup, name: str):
    tag = soup.find("meta", {"name": name})
    if tag and tag.get("content"):
        return tag.get("content").strip()
    return None


def extract_media_urls(soup, base_url: str) -> tuple[list, list]:
    """Extrait les URLs des images et vidéos de la page"""
    
    # Extraction des images
    image_selectors = [
        'img::attr(src)',
        'img::attr(data-src)',
        'img::attr(data-original)',
        'meta[property="og:image"]::attr(content)',
        'meta[name="twitter:image"]::attr(content)'
    ]
    
    image_urls = []
    for selector in image_selectors:
        elements = soup.select(selector)
        for el in elements:
            if el and el.strip():
                try:
                    full_url = urljoin(base_url, el.strip())
                    image_urls.append(full_url)
                except:
                    continue
    
    # Extraction des vidéos
    video_selectors = [
        'video::attr(src)',
        'video source::attr(src)',
        'iframe[src*="youtube"]::attr(src)',
        'iframe[src*="vimeo"]::attr(src)',
        'meta[property="og:video"]::attr(content)',
        'meta[name="twitter:player"]::attr(content)',
        'a[href*=".mp4"]::attr(href)',
        'a[href*=".webm"]::attr(href)',
        'a[href*=".ogg"]::attr(href)'
    ]
    
    video_urls = []
    for selector in video_selectors:
        elements = soup.select(selector)
        for el in elements:
            if el and el.strip():
                try:
                    full_url = urljoin(base_url, el.strip())
                    video_urls.append(full_url)
                except:
                    continue
    
    # Supprimer les doublons
    image_urls = list(set(image_urls))
    video_urls = list(set(video_urls))
    
    return image_urls, video_urls


def extract_meaningful_content(soup) -> str:
    """
    Extrait le contenu textuel significatif en excluant les éléments non pertinents
    """
    # Supprimer les éléments non pertinents
    for element in soup.find_all(['nav', 'footer', 'header', 'aside', 'script', 'style', 'meta', 'link']):
        element.decompose()
    
    # Identifier le contenu principal
    main_content = None
    selectors = [
        'main', 'article', '.content', '.main-content', 
        '.post-content', '#content', '.article-content',
        '.entry-content', '.blog-post', '.docs-content'
    ]
    
    for selector in selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # Si pas de contenu principal trouvé, utiliser le body
    if not main_content:
        main_content = soup.find('body')
    
    # Utiliser html2text pour un formatage propre
    h = html2text.HTML2Text()
    h.ignore_links = False
    h.ignore_images = True
    h.body_width = 0
    h.ignore_emphasis = False
    
    content_text = h.handle(str(main_content)) if main_content else ""
    
    # Nettoyer le texte
    content_text = re.sub(r'\n\s*\n', '\n\n', content_text)  # Supprimer les lignes vides multiples
    content_text = re.sub(r' {2,}', ' ', content_text)       # Supprimer les espaces multiples
    content_text = re.sub(r'\[\!\[.*?\]\(.*?\)\]\(.*?\)', '', content_text)  # Supprimer les images markdown
    
    return content_text.strip()


def generate_quality_snippet(content: str, title: str, max_length: int = 200) -> str:
    """
    Génère un snippet de qualité à partir du contenu
    """
    if not content:
        return title[:max_length] + "..." if title else ""
    
    # Prendre le premier paragraphe significatif
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    
    for paragraph in paragraphs:
        if len(paragraph) > 50 and len(paragraph) < 500:  # Paragraphes de taille raisonnable
            if len(paragraph) <= max_length:
                return paragraph
            else:
                return paragraph[:max_length].rsplit(' ', 1)[0] + "..."
    
    # Fallback: prendre le début du contenu
    if len(content) <= max_length:
        return content
    else:
        return content[:max_length].rsplit(' ', 1)[0] + "..."


def classify_content_type(url: str, content: str, image_urls: list, video_urls: list) -> str:
    """
    Classifie le type de contenu de manière plus intelligente
    """
    url_lower = url.lower()
    content_lower = content.lower()
    
    # Priorité aux types spécifiques
    if video_urls:
        return "video"
    elif len(image_urls) > 3:
        return "image_gallery"
    elif any(x in url_lower for x in ['/docs/', '/documentation/', '/api/', '/reference/']):
        return "documentation"
    elif any(x in url_lower for x in ['stackoverflow.com', 'question', 'answer']):
        return "qna"
    elif any(x in url_lower for x in ['/blog/', '/article/', '/news/', '/post/']):
        return "article"
    elif any(x in url_lower for x in ['tutorial', 'guide', 'how-to', 'course']):
        return "tutorial"
    elif 'github.com' in url_lower:
        return "code_repository"
    elif any(x in content_lower for x in ['function', 'class', 'def ', 'import ', 'console.log']):
        return "code_example"
    else:
        return "general"


def detect_language(text: str) -> str:
    """
    Détecte la langue du contenu
    """
    if not text:
        return "en"
    
    text_lower = text.lower()
    
    # Mots courants français
    french_words = ['le', 'la', 'les', 'un', 'une', 'des', 'est', 'sont', 'dans', 'pour', 'avec', 'sur', 'par']
    # Mots courants anglais
    english_words = ['the', 'a', 'an', 'is', 'are', 'and', 'or', 'but', 'in', 'for', 'with', 'on', 'by']
    
    french_count = sum(1 for word in french_words if f' {word} ' in f' {text_lower} ')
    english_count = sum(1 for word in english_words if f' {word} ' in f' {text_lower} ')
    
    return 'fr' if french_count > english_count else 'en'


def extract_domain_authority(url: str) -> int:
    """
    Attribue un score d'autorité basé sur le domaine
    """
    domain = urlparse(url).netloc.lower()
    
    authority_scores = {
        'stackoverflow.com': 100,
        'github.com': 95,
        'docs.python.org': 90,
        'developer.mozilla.org': 90,
        'reactjs.org': 85,
        'vuejs.org': 85,
        'nodejs.org': 85,
        'realpython.com': 80,
        'dev.to': 75,
        'digitalocean.com': 70,
        'freecodecamp.org': 70,
        'web.dev': 70,
        'css-tricks.com': 65
    }
    
    return authority_scores.get(domain, 50)  # Score par défaut 50


def urljoin(base: str, url: str) -> str:
    """Version simplifiée de urljoin"""
    if url.startswith(('http://', 'https://')):
        return url
    elif url.startswith('/'):
        # URL absolue
        parsed_base = urlparse(base)
        return f"{parsed_base.scheme}://{parsed_base.netloc}{url}"
    else:
        # URL relative
        return base.rstrip('/') + '/' + url.lstrip('/')


def extract_content(raw_item: Dict) -> Document:
    """
    Convertit un RawResponseItem (dict) en Document (Pydantic) avec améliorations.
    """
    # Valide / transforme en model pour sécurité des champs
    r = RawResponseItem(**raw_item)

    body = r.body or ""
    soup = BeautifulSoup(body, "lxml")

    # fallback title/description
    title = r.title or (soup.title.string.strip() if soup.title and soup.title.string else "")
    description = r.description or _first_meta_content(soup, "description")

    # Extraire les URLs des médias
    image_urls, video_urls = extract_media_urls(soup, str(r.url))
    
    # Extraire le contenu textuel significatif
    extracted_content = extract_meaningful_content(soup)
    
    # Générer un snippet de qualité
    quality_snippet = generate_quality_snippet(extracted_content, title)
    
    # Classifier le type de contenu
    content_type = classify_content_type(str(r.url), extracted_content, image_urls, video_urls)
    
    # Extraire le domaine et l'autorité
    domain = urlparse(str(r.url)).netloc
    domain_authority = extract_domain_authority(str(r.url))
    
    # Détecter la langue
    language = detect_language(extracted_content)
    
    # Calculer la qualité du contenu
    content_quality = min(100, len(extracted_content) // 10)  # Basé sur la longueur

    sections = []
    pos = 0

    # Parcourir DOM pour recueillir éléments pertinents dans l'ordre d'apparition
    for el in soup.find_all(["h1", "h2", "h3", "h4", "p", "pre", "code", "img", "video"]):
        if el.name in ["img", "video"]:
            # Traitement des éléments médias
            media_url = None
            if el.name == "img":
                media_url = el.get('src') or el.get('data-src') or el.get('data-original')
            else:  # video
                media_url = el.get('src')
                if not media_url:
                    source = el.find('source')
                    if source:
                        media_url = source.get('src')
            
            if media_url:
                try:
                    full_media_url = urljoin(str(r.url), media_url)
                    sections.append(Section(
                        id=str(uuid.uuid4()),
                        type=el.name,  # "img" ou "video"
                        text=f"Media: {full_media_url}",
                        start_offset=pos,
                        end_offset=pos + len(full_media_url),
                        media_url=full_media_url,
                        media_type=el.name
                    ))
                    pos = pos + len(full_media_url) + 1
                except:
                    continue
                    
        else:
            # Traitement normal du texte
            text = el.get_text(separator="\n").strip()
            if not text:
                continue

            if el.name in ("pre", "code"):
                typ = "code"
            elif el.name.startswith("h"):
                typ = "title"
            else:
                typ = "text"

            start = pos
            end = pos + len(text)
            sections.append(Section(
                id=str(uuid.uuid4()),
                type=typ,
                text=text,
                start_offset=start,
                end_offset=end
            ))
            pos = end + 1

    doc = Document(
        doc_id=str(uuid.uuid4()),
        url=str(r.url),
        crawl_meta={"appid": r.appid, "crawlid": r.crawlid},
        title=title,
        description=description,
        sections=sections,
        raw=r,
        
        # CHAMPS AMÉLIORÉS
        image_urls=image_urls,
        video_urls=video_urls,
        media_count=len(image_urls) + len(video_urls),
        content_type=content_type,
        extracted_content=extracted_content,
        domain=domain,
        domain_authority=domain_authority,
        content_quality=content_quality,
        language=language,
        snippet=quality_snippet,
        crawled_at=r.crawled_at or datetime.now().isoformat(),
        word_count=len(extracted_content.split())
    )
    
    return doc
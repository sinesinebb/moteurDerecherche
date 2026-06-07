import trafilatura
from trafilatura.settings import use_config
import logging
import re

logger = logging.getLogger(__name__)

def is_html(content: str) -> bool:
    """Détecte si le contenu est probablement du HTML."""
    if not content:
        return False
    # Cherche des balises HTML courantes
    html_patterns = [r'<html', r'<body', r'<div', r'<p>', r'<a\s', r'<script', r'<style']
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in html_patterns)

def clean_html(html_content: str, max_snippet_length: int = 200) -> dict:
    """
    Extrait le texte principal d'un HTML et génère un snippet.
    Si le contenu n'est pas du HTML, le retourne tel quel.
    """
    if not html_content or not isinstance(html_content, str):
        return {"clean_text": "", "snippet": ""}

    # Si ce n'est pas du HTML, on le traite comme du texte brut
    if not is_html(html_content):
        text = ' '.join(html_content.split())
        snippet = text[:max_snippet_length] + ('...' if len(text) > max_snippet_length else '')
        return {"clean_text": text, "snippet": snippet}

    try:
        config = use_config()
        config['DEFAULT']['MIN_EXTRACTED_SIZE'] = '50'

        text = trafilatura.extract(
            html_content,
            config=config,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            output_format='txt'
        )

        if not text:
            text = trafilatura.html2txt(html_content)
            if not text:
                return {"clean_text": "", "snippet": ""}

        text = ' '.join(text.split())

        if len(text) > max_snippet_length:
            cut = text[:max_snippet_length].rfind(' ')
            if cut > 0:
                snippet = text[:cut] + '...'
            else:
                snippet = text[:max_snippet_length] + '...'
        else:
            snippet = text

        return {"clean_text": text, "snippet": snippet}

    except Exception as e:
        logger.error(f"Erreur lors du nettoyage HTML: {e}")
        return {"clean_text": "", "snippet": ""}
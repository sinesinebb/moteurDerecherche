# src/processors/parser.py
"""
Heuristiques de parsing/normalisation du contenu extrait.
Fonctions principales :
 - is_code_block(text) -> bool
 - normalize_text(text) -> str
 - extract_code_blocks_from_section(section_text) -> List[str]
 - split_code_and_text(body_html_or_text) -> (texts, codes)
"""

import re
from typing import List, Tuple
from html import unescape

# heuristiques simples mais efficaces
_CODE_LIKELIHOOD_RE = [
    re.compile(r'```'),                    # fences markdown
    re.compile(r'^\s{4,}'),                # indentation > 4 at line start
    re.compile(r'<pre|<code', re.I),      # html tags
    re.compile(r';\s*$'),                  # ; at line end (many langs)
    re.compile(r'\b(def |class |import |from )'),  # python-like tokens
    re.compile(r'\b(public |private |class |void |static )'),  # java-like
    re.compile(r'[{}<>:=\[\]\(\)]'),       # many punctuation common in code
]

# tokens that strongly indicate prose
_PROSE_MARKERS_RE = [
    re.compile(r'\.\s+[A-Z]'),             # sentence end + capital
    re.compile(r'\b(le|la|les|et|mais|ou|donc|or|ni|car)\b', re.I),  # french stopwords
    re.compile(r'</?(p|em|strong|ul|ol|li|h[1-6])', re.I),
]


def is_code_block(text: str, min_ratio: float = 0.25) -> bool:
    """
    Retourne True si `text` ressemble fortement à du code.

    Heuristiques combinées :
     - présence de fences ``` ou balises <pre>/<code>
     - proportion de lignes contenant caractères typiques de code
     - présence de tokens language-specific
    """
    if not text:
        return False

    # quick checks
    lower = text.lower()
    if '```' in text or '<pre' in lower or '<code' in lower:
        return True

    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False

    score = 0
    for ln in lines:
        ln_stripped = ln.strip()
        # indentation heavy
        if re.match(r'^\s{2,}', ln):
            score += 1
        # semicolon line end
        if ln_stripped.endswith(';'):
            score += 1
        # many punctuation characters
        if len(re.findall(r'[{};<>:=\[\]\(\)]', ln)) >= 2:
            score += 1
        # presence of typical keywords
        for rx in (_CODE_LIKELIHOOD_RE[4:],):
            if rx[0].search(ln):
                score += 1

    # ratio of "code-like" lines
    ratio = score / max(1, len(lines))
    # strong prose markers reduce likelihood
    prose_count = sum(1 for rx in _PROSE_MARKERS_RE if rx.search(text))
    if prose_count >= 2:
        # if there are many prose markers, lower ratio threshold
        return ratio >= (min_ratio + 0.15)
    return ratio >= min_ratio


def normalize_text(text: str) -> str:
    """
    Nettoyage minimal :
     - unescape HTML entities
     - collapse whitespace
     - strip leading/trailing spaces
    """
    if text is None:
        return ""
    s = unescape(text)
    # normalize newlines: keep paragraphs but collapse repeated blank lines
    s = re.sub(r'\r\n?', '\n', s)
    s = re.sub(r'\n{3,}', '\n\n', s)
    # collapse spaces but preserve single newlines
    s = re.sub(r'[ \t]+', ' ', s)
    s = s.strip()
    return s


def extract_code_blocks_from_section(section_text: str) -> List[str]:
    """
    Tentative d'extraction de blocs de code à l'intérieur d'un texte :
    - recherche fences ```...```
    - ou lignes indentées consécutives
    Renvoie une liste de blocs (strings). Si rien, renvoie [].
    """
    if not section_text:
        return []

    blocks = []

    # 1) ``` fenced blocks
    fenced = re.findall(r'```(?:\w+)?\n(.*?)```', section_text, flags=re.S)
    for b in fenced:
        blocks.append(b.strip())

    # remove fences from text to avoid duplication in next step
    t = re.sub(r'```(?:\w+)?\n.*?```', '', section_text, flags=re.S)

    # 2) consecutive indented lines -> block
    lines = t.splitlines()
    cur = []
    for ln in lines:
        if re.match(r'^\s{4,}', ln):
            cur.append(ln)
        else:
            if cur:
                blocks.append('\n'.join(cur).strip())
                cur = []
    if cur:
        blocks.append('\n'.join(cur).strip())

    # filter very small blocks
    blocks = [b for b in blocks if len(b) >= 20]
    return blocks


def split_code_and_text(body: str) -> Tuple[List[str], List[str]]:
    """
    Retourne (texts, codes) extraits depuis `body` brut (HTML ou texte).
    Utilise les heuristiques ci-dessus.
    """
    if not body:
        return [], []

    body = normalize_text(body)

    codes = extract_code_blocks_from_section(body)

    # if no fenced/indented blocks, try to find inline segments that look like code
    if not codes:
        # split by paragraphs and test
        paras = [p.strip() for p in re.split(r'\n{2,}', body) if p.strip()]
        texts = []
        for p in paras:
            if is_code_block(p):
                codes.append(p)
            else:
                texts.append(p)
        return texts, codes

    # If we have explicit blocks, remove them from text to produce plain texts
    text_clean = body
    for c in codes:
        # escape special characters for naive remove
        text_clean = text_clean.replace(c, '')
    # split remaining into paragraphs
    texts = [p.strip() for p in re.split(r'\n{2,}', text_clean) if p.strip()]
    return texts, codes

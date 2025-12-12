# src/processors/segmenter.py
"""
Découpage de Document/sections en segments indexables.
Fonctions :
 - segment_text(document_or_sections, max_chars=1000, overlap=200)
 - _merge_small_sections(sections, min_chars=100)
"""

from typing import List, Union, Iterable
import uuid
from src.models.document_models import Section, Document
from math import ceil


def _merge_small_sections(sections: List[Section], min_chars: int = 200) -> List[Section]:
    """
    Fusionne sections consécutives si elles sont trop courtes.
    Cela évite de créer des segments ridiculement petits.
    """
    if not sections:
        return []
    out = []
    buf = None
    for s in sections:
        if buf is None:
            buf = s
            continue
        if len(buf.text) < min_chars and len(s.text) < min_chars:
            # merge
            merged = Section(
                id=str(uuid.uuid4()),
                type=buf.type if buf.type == s.type else "text",
                text=buf.text + "\n\n" + s.text,
                start_offset=buf.start_offset,
                end_offset=s.end_offset or s.end_offset,
                metadata={**(buf.metadata or {}), **(s.metadata or {})}
            )
            buf = merged
        else:
            out.append(buf)
            buf = s
    if buf:
        out.append(buf)
    return out


def _chars_to_windows(text: str, max_chars: int, overlap: int) -> List[str]:
    """
    Coupe `text` en fenêtres de longueur ~max_chars avec `overlap` caractères de recouvrement.
    Préfère couper sur séparateurs de phrase si possible.
    """
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    windows = []
    start = 0
    L = len(text)
    while start < L:
        end = start + max_chars
        if end >= L:
            windows.append(text[start:L].strip())
            break
        # try to backtrack to nearest sentence boundary ('.', '\n', '。', '!' , '?')
        slice_ = text[start:end]
        # find last newline or punctuation inside slice
        cut_pos = max(slice_.rfind('\n'), slice_.rfind('. '), slice_.rfind('? '), slice_.rfind('! '))
        if cut_pos > int(max_chars * 0.5):
            end = start + cut_pos + 1
        windows.append(text[start:end].strip())
        start = end - overlap
        if start < 0:
            start = 0
        if len(windows) > 1000:  # safeguard
            break
    return windows


def segment_text(
    doc_or_sections: Union[Document, Iterable[Section]],
    max_chars: int = 1000,
    overlap: int = 200,
    min_section_chars: int = 50
) -> List[Section]:
    """
    Convertit un Document (ou iterable de Section) en une liste de Sections de type 'segment'
    prêtes à être envoyées à l'index (champ text + metadata).
    Paramètres :
     - max_chars: taille cible d'un segment
     - overlap: recouvrement entre segments
     - min_section_chars: seuil pour ignorer sections minuscules
    Retourne une liste de Section (type='segment') avec id unique.
    """
    # normalize input
    if isinstance(doc_or_sections, Document):
        sections = doc_or_sections.sections or []
    else:
        sections = list(doc_or_sections)

    # filter très petites sections
    sections = [s for s in sections if s and len((s.text or '').strip()) >= min_section_chars]

    # merge adjacent very-small sections
    sections = _merge_small_sections(sections, min_chars=min_section_chars * 2)

    segments: List[Section] = []
    for sec in sections:
        text = (sec.text or '').strip()
        if not text:
            continue

        # if section shorter than max_chars, keep as-is (but mark type segment)
        if len(text) <= max_chars:
            segments.append(Section(
                id=str(uuid.uuid4()),
                type="segment",
                text=text,
                start_offset=sec.start_offset,
                end_offset=sec.end_offset,
                metadata={**(sec.metadata or {}), "source_section_id": sec.id, "section_type": sec.type}
            ))
            continue

        # else cut into windows
        windows = _chars_to_windows(text, max_chars=max_chars, overlap=overlap)
        for i, w in enumerate(windows):
            segments.append(Section(
                id=str(uuid.uuid4()),
                type="segment",
                text=w,
                start_offset=None,
                end_offset=None,
                metadata={**(sec.metadata or {}), "source_section_id": sec.id, "section_type": sec.type, "segment_index": i}
            ))

    return segments

"""
Extracció intel·ligent de fragments rellevants dels PDFs del CTE.

Estratègia:
  1. Extreure tot el text del PDF per pàgines (pdfplumber)
  2. Indexar pàgines per seccions SI-1...SI-6 (o DB genèric)
  3. Per una consulta, retornar els fragments més rellevants amb
     referència de pàgina i secció exacta
  4. Limitar el context total a MAX_CONTEXT_CHARS per a la crida Claude
"""

import re
import logging
from pathlib import Path
from functools import lru_cache

import pdfplumber

from config import SI_SECTION_KEYWORDS, MAX_CONTEXT_CHARS, MIN_FRAGMENT_CHARS

logger = logging.getLogger(__name__)


# ── Extracció de text ─────────────────────────────────────────────────────────

def extract_pages(pdf_path: Path) -> list[dict]:
    """
    Extreu el text de cada pàgina.
    Retorna llista de { page_num, text, char_count }.
    """
    pages = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                text = _clean_text(text)
                if len(text) >= MIN_FRAGMENT_CHARS:
                    pages.append({
                        "page_num":   i,
                        "text":       text,
                        "char_count": len(text),
                    })
    except Exception as e:
        logger.error(f"Error extraient {pdf_path}: {e}")
    return pages


def _clean_text(text: str) -> str:
    """Neteja el text extret: elimina caràcters estranys i normalitza espais."""
    # Eliminar caràcters de control excepte salts de línia
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    # Normalitzar múltiples espais (però mantenir salts de línia)
    text = re.sub(r'[ \t]+', ' ', text)
    # Eliminar línies buides excessives
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ── Indexació per seccions ────────────────────────────────────────────────────

# Patrons per detectar l'inici de seccions SI
_SI_SECTION_PATTERNS = {
    "SI-1": re.compile(r'\bSI\s*[–\-]?\s*1\b|\bSI\s+1\b|Propagaci[oó]n?\s+interior', re.I),
    "SI-2": re.compile(r'\bSI\s*[–\-]?\s*2\b|\bSI\s+2\b|Propagaci[oó]n?\s+exterior', re.I),
    "SI-3": re.compile(r'\bSI\s*[–\-]?\s*3\b|\bSI\s+3\b|Evacuaci[oó]n?\s+de\s+ocupantes', re.I),
    "SI-4": re.compile(r'\bSI\s*[–\-]?\s*4\b|\bSI\s+4\b|instalaciones\s+de\s+protecci[oó]n', re.I),
    "SI-5": re.compile(r'\bSI\s*[–\-]?\s*5\b|\bSI\s+5\b|intervenci[oó]n\s+de\s+los\s+bomberos', re.I),
    "SI-6": re.compile(r'\bSI\s*[–\-]?\s*6\b|\bSI\s+6\b|resistencia\s+al\s+fuego\s+de\s+la\s+estructura', re.I),
}

def tag_pages_with_sections(pages: list[dict]) -> list[dict]:
    """
    Afegeix a cada pàgina les seccions SI detectades.
    Una pàgina pot pertànyer a múltiples seccions (transició).
    """
    current_sections: set[str] = set()
    tagged = []
    for page in pages:
        text = page["text"]
        # Detectar seccions que comencen en aquesta pàgina
        for sec, pat in _SI_SECTION_PATTERNS.items():
            if pat.search(text):
                current_sections.add(sec)
        tagged.append({
            **page,
            "sections": list(current_sections),
        })
    return tagged


# ── Scoring de rellevància ────────────────────────────────────────────────────

def _score_page(page: dict, keywords: list[str], target_sections: list[str]) -> float:
    """
    Puntua la rellevància d'una pàgina per a un conjunt de paraules clau.
    Bonificació si pertany a les seccions objectiu.
    """
    text_lower = page["text"].lower()
    score = 0.0

    # Punts per paraules clau
    for kw in keywords:
        count = text_lower.count(kw.lower())
        score += count * 2.0

    # Bonificació per seccions objectiu
    for sec in target_sections:
        if sec in page.get("sections", []):
            score += 10.0

    # Penalitzar pàgines molt curtes
    if page["char_count"] < 300:
        score *= 0.5

    return score


# ── API pública ───────────────────────────────────────────────────────────────

def get_relevant_context(
    pdf_path: Path,
    target_sections: list[str],
    extra_keywords: list[str] | None = None,
    max_chars: int = MAX_CONTEXT_CHARS,
) -> str:
    """
    Extreu i retorna els fragments més rellevants del PDF per a les
    seccions indicades, formatats amb referència de pàgina.

    Args:
        pdf_path:         Path al PDF
        target_sections:  Llista de seccions (p.ex. ["SI-1", "SI-3"])
        extra_keywords:   Paraules clau addicionals per la consulta concreta
        max_chars:        Límit total de caràcters retornats

    Returns:
        String amb fragments anotats: [Pàg. N · SI-X] text...
    """
    pages = extract_pages(pdf_path)
    if not pages:
        return ""

    pages = tag_pages_with_sections(pages)

    # Construir llista de paraules clau: les de les seccions + les extra
    all_keywords: list[str] = []
    for sec in target_sections:
        all_keywords.extend(SI_SECTION_KEYWORDS.get(sec, []))
    if extra_keywords:
        all_keywords.extend(extra_keywords)

    # Puntuar i ordenar
    scored = [
        (page, _score_page(page, all_keywords, target_sections))
        for page in pages
    ]
    scored.sort(key=lambda x: x[1], reverse=True)

    # Seleccionar les millors pàgines fins al límit de caràcters
    selected = []
    total_chars = 0
    for page, score in scored:
        if score <= 0:
            break
        if total_chars + page["char_count"] > max_chars:
            # Afegir fragment truncat
            remaining = max_chars - total_chars
            if remaining > MIN_FRAGMENT_CHARS * 2:
                truncated = page.copy()
                truncated["text"] = page["text"][:remaining] + "\n[…fragment truncat]"
                truncated["char_count"] = remaining
                selected.append(truncated)
            break
        selected.append(page)
        total_chars += page["char_count"]

    if not selected:
        # Si no hi ha cap rellevant, agafar primeres pàgines (índex/intro)
        for page in pages[:5]:
            selected.append(page)
            total_chars += page["char_count"]
            if total_chars > max_chars // 2:
                break

    # Ordenar pel número de pàgina per llegibilitat
    selected.sort(key=lambda p: p["page_num"])

    # Formatar amb capçaleres de pàgina
    fragments = []
    for page in selected:
        secs_str = ", ".join(page.get("sections", [])) or "Introducció"
        header = f"[Pàg. {page['page_num']} · {secs_str}]"
        fragments.append(f"{header}\n{page['text']}")

    return "\n\n{'─'*60}\n\n".join(fragments)


def get_si_context_for_sections(
    pdf_path: Path,
    sections: list[str],
    query_keywords: list[str] | None = None,
) -> str:
    """
    Ataill per obtenir context SI específic per seccions.
    """
    return get_relevant_context(
        pdf_path,
        target_sections=sections,
        extra_keywords=query_keywords,
    )


def extract_full_section(pdf_path: Path, section_code: str) -> str:
    """
    Extreu el text complet d'una secció (p.ex. 'SI-3') del PDF,
    des de l'inici de la secció fins a l'inici de la següent.
    Útil per a validació exhaustiva.
    """
    pages = extract_pages(pdf_path)
    pages = tag_pages_with_sections(pages)

    in_section = False
    result_pages = []
    section_order = list(_SI_SECTION_PATTERNS.keys())

    try:
        sec_idx = section_order.index(section_code)
        next_sec = section_order[sec_idx + 1] if sec_idx + 1 < len(section_order) else None
    except ValueError:
        return ""

    for page in pages:
        sections_in_page = page.get("sections", [])
        if section_code in sections_in_page:
            in_section = True
        if in_section:
            result_pages.append(page)
        if in_section and next_sec and next_sec in sections_in_page and page not in result_pages[-2:]:
            break  # Fi de la secció

    return "\n\n".join(p["text"] for p in result_pages)

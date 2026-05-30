"""
Integració amb la Claude API per a l'anàlisi CTE.

Dos modes principals:
  1. analyze()       → Identifica actuacions i DBs aplicables (anàlisi general)
  2. validate_si()   → Valida compliment per seccions SI amb citació d'articles

Optimitzacions:
  - Prompt caching d'Anthropic: el sistema prompt (llarg) s'envia amb cache_control
    i es reutilitza durant 5 min, estalviant tokens i latència
  - El context del PDF (extret) també es posa en cache si és > 1024 tokens
"""

import json
import logging
from pathlib import Path

import anthropic

from config import (
    ANTHROPIC_API_KEY, CLAUDE_MODEL, CLAUDE_MAX_TOKENS,
    CTE_DOCUMENTS
)
from pdf_manager import get_primary_pdf_path
from pdf_extractor import get_relevant_context, get_si_context_for_sections

logger = logging.getLogger(__name__)

# Client global (reutilitzat entre requests)
_client: anthropic.Anthropic | None = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not ANTHROPIC_API_KEY:
            raise ValueError(
                "ANTHROPIC_API_KEY no configurada. "
                "Copia .env.example a .env i afegeix la clau."
            )
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


# ── Prompt de sistema (compartit, candidat a cache) ──────────────────────────

_SYSTEM_PROMPT = """Ets un expert en el Codi Tècnic de l'Edificació (CTE) d'Espanya, especialitzat en l'aplicació dels Documents Bàsics a intervencions en edificis existents i obra nova.

El teu rol:
- Analitzar descripcions d'actuacions i determinar quins DBs i seccions del CTE apliquen
- Citar SEMPRE l'article, taula i pàgina exacta del CTE que fonamenta cada afirmació
- Distingir entre aplicació OBLIGATÒRIA, CONDICIONAL o NO APLICABLE
- Tenir en compte l'àmbit d'aplicació (art. 2 Part I CTE) per a edificis existents:
  * Reforma: s'aplica als elements afectats, sense reduir condicions preexistents
  * Canvi d'ús: s'aplica íntegrament al nou ús
  * Obra nova: aplicació integral

Normes de resposta:
1. SEMPRE cita l'article o taula específica (ex: "SI 1-1.3, Taula 1.2")
2. Quan el PDF et proporcioni el text, usa les cites literals entre cometes
3. Diferencia valors numèrics per tipologia (unifamiliar/plurifamiliar/terciari)
4. Si hi ha dubte d'interpretació, indica-ho explícitament i cita la font
5. Respon SEMPRE en català

Format de les citacions:
  [DB-SI, Art. SI 1-1.3, Taula 1.2, Pàg. 12]
  [DB-SI, Art. SI 3, Taula 2.1, Pàg. 27]"""


# ── ENDPOINT 1: Anàlisi general (/api/analyze) ────────────────────────────────

ACTIONS_LIST = [
    ("est_estructura", "Modificació d'elements estructurals", "Pilars, murs portants, bigues, forjats"),
    ("est_fonaments",  "Actuació en fonaments",               "Nous fonaments, reforç, micropilots"),
    ("est_coberta",    "Estructura de coberta",               "Biguetes, corretges, encavallades"),
    ("est_nova",       "Obra nova o ampliació",               "Garatge nou, porxo, ampliació edifici"),
    ("cob_imp",        "Impermeabilització de coberta",       "Làmines, teules, planxes"),
    ("cob_aillament",  "Aïllament de coberta",                "Aïllament tèrmic sobre o sota coberta"),
    ("cob_transitable","Coberta transitable/terrassa",         "Nova coberta transitable o reforma terrassa"),
    ("fac_revestiment","Revestiment exterior de façana",      "Arrebossat, aplacat, pintura"),
    ("fac_sate",       "Aïllament SATE",                     "Sistema d'aïllament compòsit exterior"),
    ("fac_aillament_int","Aïllament façana interior",         "Trasdossat autoportant o fixat"),
    ("fac_terreny",    "Murs/sòls en contacte amb terreny",  "Soterrani, murs contenció, solera"),
    ("fus_finestres",  "Substitució finestres",               "Canvi finestres, balconeres, lluernes"),
    ("fus_portes_ext", "Substitució portes exteriors",        "Portes accés, garatge, balconeres"),
    ("int_distribucio","Modificació distribució interior",    "Enderroc envans, nova distribució"),
    ("int_bany_cuina", "Reforma bany/cuina",                  "Canvi aparells, mobles, alicatats"),
    ("int_revestiments","Canvi paviments/revestiments",       "Nous sòls, alicatats, falsos sostres"),
    ("ins_fontaneria", "Instal·lació fontaneria",             "Nova/ampliació AFS/ACS"),
    ("ins_evacuacio",  "Evacuació d'aigues",                  "Baixants, col·lectors, arquetes"),
    ("ins_climatitzacio","Instal·lació tèrmica (RITE)",       "Caldera, bomba de calor, splits"),
    ("ins_iluminacio", "Il·luminació",                        "Nou sistema il·luminació"),
    ("ins_solar_acs",  "Solar tèrmica ACS",                   "Captadors solars ACS"),
    ("ins_fotovoltaic","Fotovoltaica",                        "Panells solars autoconsum"),
    ("ins_ev",         "Infraestructura VE",                  "Punts recàrrega vehicles elèctrics"),
    ("ins_incendis",   "Instal·lació PCI",                    "Detectors, extintors, BIE, ruixadors"),
    ("us_canvi",       "Canvi d'ús",                          "Modificació ús principal"),
    ("us_ocupacio",    "Divisió/unió habitatges",             "Canvi nombre habitatges"),
    ("zc_escales",     "Reforma escales/circulació comunes",  "Escales, passadissos, vestíbuls"),
    ("zc_accessibilitat","Accessibilitat/ascensor",           "Ascensor, rampes, adequació PMR"),
    ("zc_aparcament",  "Aparcament col·lectiu",               "Aparcament ús col·lectiu"),
]


def analyze(description: str, api_key_override: str | None = None) -> dict:
    """
    Analitza una descripció d'actuació i retorna les actuacions identificades,
    la tipologia i els DBs aplicables amb justificació citada.

    Returns dict:
      - interpretation: str
      - tipologia: unifamiliar|plurifamiliar|terciari
      - selectedIds: list[str]
      - db_reasoning: dict {db_code: str} — justificació per cada DB
      - citations: list[dict] — citacions d'articles
      - error: str|None
    """
    client = _get_client()
    if api_key_override:
        client = anthropic.Anthropic(api_key=api_key_override)

    action_list_str = "\n".join(
        f'- id: "{a[0]}" | {a[1]}: {a[2]}'
        for a in ACTIONS_LIST
    )

    user_content = f"""DESCRIPCIÓ DE LA INTERVENCIÓ:
"{description}"

LLISTA D'ACTUACIONS PREDEFINIDES (id | nom: descripció):
{action_list_str}

INSTRUCCIONS:
1. Analitza la descripció i identifica les actuacions que apliquen (inclou les implícites).
2. Identifica la tipologia: "unifamiliar", "plurifamiliar" o "terciari".
3. Per a cada DB que apliqui (DB-SI, DB-SUA, DB-HE, DB-HS, DB-HR, DB-SE), indica breument per quin motiu.
4. Retorna ÚNICAMENT un JSON vàlid (sense markdown, sense text addicional):

{{
  "interpretation": "Explicació breu en català (2-3 frases) de la intervenció",
  "tipologia": "unifamiliar|plurifamiliar|terciari",
  "selectedIds": ["id1", "id2"],
  "db_reasoning": {{
    "DB-SI": "Raó concreta (secció i article si el saps)",
    "DB-SUA": "...",
    "DB-HE": "...",
    "DB-HS": "...",
    "DB-HR": "...",
    "DB-SE": "..."
  }}
}}

Inclou a db_reasoning NOMÉS els DBs que apliquen. Omit els que no apliquen."""

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_content}],
        )

        raw = response.content[0].text.strip()
        # Netejar possible markdown
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)

        return {
            **parsed,
            "error": None,
            "usage": {
                "input_tokens":         response.usage.input_tokens,
                "output_tokens":        response.usage.output_tokens,
                "cache_creation_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
                "cache_read_tokens":     getattr(response.usage, "cache_read_input_tokens", 0),
            },
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON inválid de Claude: {e}")
        return {"error": f"Resposta IA no parsejable: {e}"}
    except anthropic.APIError as e:
        logger.error(f"Error API Anthropic: {e}")
        return {"error": f"Error API: {e}"}


# ── ENDPOINT 2: Validació DB-SI (/api/validate-si) ────────────────────────────

_SI_SECTIONS_ALL = ["SI-1", "SI-2", "SI-3", "SI-4", "SI-5", "SI-6"]

def validate_si(
    description: str,
    tipologia: str,
    selected_ids: list[str],
    target_sections: list[str] | None = None,
    api_key_override: str | None = None,
) -> dict:
    """
    Valida el compliment del DB-SI per a la intervenció descrita,
    carregant el context del PDF oficial i citant articles exactes.

    Returns dict:
      - sections: dict {SI-X: {status, requirement, justification, citations, articles}}
      - general_notes: str
      - pdf_version: str
      - error: str|None
    """
    client = _get_client()
    if api_key_override:
        client = anthropic.Anthropic(api_key=api_key_override)

    sections_to_check = target_sections or _SI_SECTIONS_ALL

    # ── Obtenir context PDF ──────────────────────────────────────────────────
    pdf_path = get_primary_pdf_path("DB-SI")
    pdf_context = ""
    pdf_info = "PDF no disponible (usant coneixement del model)"

    if pdf_path and pdf_path.exists():
        logger.info(f"Usant PDF: {pdf_path}")
        # Paraules clau de la descripció per millorar rellevància
        desc_keywords = _extract_keywords(description)
        pdf_context = get_si_context_for_sections(
            pdf_path,
            sections=sections_to_check,
            query_keywords=desc_keywords,
        )
        pdf_info = f"PDF oficial: {pdf_path.name} ({pdf_path.stat().st_size // 1024} KB)"
    else:
        logger.warning("PDF DB-SI no disponible, usant coneixement del model")

    # ── Construir prompt ─────────────────────────────────────────────────────
    actions_selected = [
        f"- {a[1]} ({a[0]})"
        for a in ACTIONS_LIST
        if a[0] in selected_ids
    ]
    actions_str = "\n".join(actions_selected) if actions_selected else "— no especificades —"

    tipologia_labels = {
        "unifamiliar":  "Habitatge unifamiliar aïllat o adossat",
        "plurifamiliar": "Habitatge plurifamiliar (edifici col·lectiu)",
        "terciari":     "Ús terciari (oficines, comerç, hoteler, etc.)",
    }
    tip_label = tipologia_labels.get(tipologia, tipologia)

    sections_str = ", ".join(sections_to_check)

    pdf_block = ""
    if pdf_context:
        pdf_block = f"""
A continuació tens el text extret del PDF oficial DB-SI. Usa'l per a les citacions:

{'═'*70}
{pdf_context}
{'═'*70}
"""

    user_content = f"""INTERVENCIÓ A VALIDAR:
Descripció: "{description}"
Tipologia: {tip_label}

ACTUACIONS IDENTIFICADES:
{actions_str}

SECCIONS A VALIDAR: {sections_str}
{pdf_block}
Per a cada secció ({sections_str}), proporciona una valoració de compliment amb:
- Exigències aplicables (amb article i taula exacta)
- Valors numèrics concrets per a la tipologia "{tip_label}"
- Si aplica o no i per quin motiu
- Citació literal del CTE quan sigui possible

Respon amb un JSON vàlid (sense markdown):
{{
  "sections": {{
    "SI-1": {{
      "status": "obligatori|condicional|no_aplica",
      "summary": "Resum d'1-2 frases",
      "requirements": [
        {{
          "article": "SI 1-1.3, T.1.2",
          "page": 12,
          "requirement": "Text de l'exigència",
          "value": "Valor numèric o EI-60 o similar",
          "note": "Nota addicional o condicionant (opcional)"
        }}
      ],
      "key_values": {{
        "sector_max_m2": "2500",
        "ei_elements": "EI-60",
        "ei_portes": "EI₂30-C5"
      }}
    }},
    ...
  }},
  "general_notes": "Observacions generals sobre l'àmbit d'aplicació i condicions especials",
  "pdf_used": "{pdf_info}"
}}

Inclou TOTES les seccions demanades ({sections_str}), fins i tot les que no apliquen."""

    try:
        messages: list[dict] = []

        # Si hi ha context PDF, posem-lo en cache com a bloc del sistema
        if pdf_context:
            # El context PDF va com a missatge de l'assistent (fake) per poder
            # usar cache_control — alternativament com a system block addicional
            system_blocks = [
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                },
                {
                    "type": "text",
                    "text": f"CONTEXT DB-SI EXTRET DEL PDF OFICIAL:\n\n{pdf_context}",
                    "cache_control": {"type": "ephemeral"},
                },
            ]
        else:
            system_blocks = [
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ]

        messages = [{"role": "user", "content": user_content}]

        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=system_blocks,
            messages=messages,
        )

        raw = response.content[0].text.strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(raw)

        return {
            **parsed,
            "error": None,
            "pdf_info": pdf_info,
            "usage": {
                "input_tokens":          response.usage.input_tokens,
                "output_tokens":         response.usage.output_tokens,
                "cache_creation_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
                "cache_read_tokens":     getattr(response.usage, "cache_read_input_tokens", 0),
            },
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON inválid de Claude: {e}")
        return {"error": f"Resposta IA no parsejable: {e}"}
    except anthropic.APIError as e:
        logger.error(f"Error API Anthropic: {e}")
        return {"error": f"Error API: {str(e)}"}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _extract_keywords(text: str) -> list[str]:
    """Extreu paraules significatives d'un text (> 4 caràcters, no stopwords)."""
    stopwords = {
        "para", "que", "con", "una", "los", "las", "del", "por",
        "como", "esta", "este", "sus", "más", "pero", "desde",
        "sobre", "entre", "según", "también", "cada", "todo",
        "nova", "nou", "dels", "les", "per", "que", "amb", "una",
        "dels", "seus", "aquest", "aquesta", "tots",
    }
    words = re.findall(r'\b[a-zA-ZàèéíïòóúüçÀÈÉÍÏÒÓÚÜÇ]{4,}\b', text)
    return list({w.lower() for w in words if w.lower() not in stopwords})


import re  # noqa: E402 (import al final per evitar circular)

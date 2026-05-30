"""
Configuració central del projecte CTE·IA Flask.
Tots els URLs i mapejos de PDFs oficials del CTE es defineixen aquí.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Directoris ──────────────────────────────────────────────────────────────
BASE_DIR   = Path(__file__).parent
CACHE_DIR  = Path(os.getenv("CACHE_DIR", BASE_DIR / "cache"))
STATIC_DIR = BASE_DIR / "static"

CACHE_DIR.mkdir(exist_ok=True)

# ── API Keys ─────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

# ── Flask ─────────────────────────────────────────────────────────────────────
FLASK_PORT  = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# ── PDFs oficials CTE (codigotecnico.org) ─────────────────────────────────────
#
# Estructura URLs:
#   https://www.codigotecnico.org/pdf/Documentos/{folder}/{filename}
#
# Prioritat: DccXX (amb comentaris del Ministeri) > DBXX (sense)
# El sistema descarrega sempre la versió "amb comentaris" si existeix.
#
CTE_BASE_URL = "https://www.codigotecnico.org"

CTE_DOCUMENTS = {
    "DB-SI": {
        "name": "Seguretat en cas d'incendi",
        "name_es": "Seguridad en caso de incendio",
        "folder": "SI",
        "pdfs": [
            {
                "key": "DccSI",
                "url": "/pdf/Documentos/SI/DccSI.pdf",
                "label": "DB-SI amb comentaris",
                "primary": True,
            },
            {
                "key": "DBSI",
                "url": "/pdf/Documentos/SI/DccSI.pdf",  # fallback mateix
                "label": "DB-SI bàsic",
                "primary": False,
            },
            {
                "key": "DA_DBSI_1",
                "url": "/pdf/Documentos/SI/DA_DB-SI_1_Justficacion_documental_productos_de_construccion_12-2022.pdf",
                "label": "DA DB-SI 1 – Justificació documental",
                "primary": False,
            },
            {
                "key": "DA_DBSI_4",
                "url": "/pdf/Documentos/SI/DA_DB-SI_4_Espacio_exterior_seguro_7-2016.pdf",
                "label": "DA DB-SI 4 – Espai exterior segur",
                "primary": False,
            },
        ],
    },
    "DB-SUA": {
        "name": "Seguretat d'utilització i accessibilitat",
        "name_es": "Seguridad de utilización y accesibilidad",
        "folder": "SUA",
        "pdfs": [
            {
                "key": "DccSUA",
                "url": "/pdf/Documentos/SUA/DccSUA.pdf",
                "label": "DB-SUA amb comentaris",
                "primary": True,
            },
        ],
    },
    "DB-HE": {
        "name": "Estalvi d'energia",
        "name_es": "Ahorro de energía",
        "folder": "HE",
        "pdfs": [
            {
                "key": "DccHE",
                "url": "/pdf/Documentos/HE/DccHE.pdf",
                "label": "DB-HE amb comentaris",
                "primary": True,
            },
            {
                "key": "DA_HE_1",
                "url": "/pdf/Documentos/HE/DA_DB-HE-1_Calculo_de_parametros_caracteristicos_de_la_envolvente.pdf",
                "label": "DA HE-1 – Paràmetres envolupant",
                "primary": False,
            },
        ],
    },
    "DB-HS": {
        "name": "Salubritat",
        "name_es": "Salubridad",
        "folder": "HS",
        "pdfs": [
            {
                "key": "DccHS",
                "url": "/pdf/Documentos/HS/DccHS.pdf",
                "label": "DB-HS amb comentaris",
                "primary": True,
            },
        ],
    },
    "DB-HR": {
        "name": "Protecció davant el soroll",
        "name_es": "Protección frente al ruido",
        "folder": "HR",
        "pdfs": [
            {
                "key": "DccHR",
                "url": "/pdf/Documentos/HR/DccHR.pdf",
                "label": "DB-HR amb comentaris",
                "primary": True,
            },
        ],
    },
    "DB-SE": {
        "name": "Seguretat estructural",
        "name_es": "Seguridad estructural",
        "folder": "SE",
        "pdfs": [
            {
                "key": "DBSE",
                "url": "/pdf/Documentos/SE/DBSE.pdf",
                "label": "DB-SE",
                "primary": True,
            },
            {
                "key": "DBSE_AE",
                "url": "/pdf/Documentos/SE/DBSE-AE.pdf",
                "label": "DB-SE-AE Accions",
                "primary": False,
            },
            {
                "key": "DBSE_C",
                "url": "/pdf/Documentos/SE/DBSE-C.pdf",
                "label": "DB-SE-C Fonaments",
                "primary": False,
            },
            {
                "key": "DBSE_A",
                "url": "/pdf/Documentos/SE/DBSE-A.pdf",
                "label": "DB-SE-A Acer",
                "primary": False,
            },
        ],
    },
}

# ── Paraules clau per secció SI (per a extracció intel·ligent) ────────────────
SI_SECTION_KEYWORDS = {
    "SI-1": [
        "propagación interior", "sector de incendio", "compartimentación",
        "resistencia al fuego", "EI ", "local de riesgo", "vestíbulo",
        "uso residencial vivienda",
    ],
    "SI-2": [
        "propagación exterior", "medianera", "fachada", "cubierta",
        "reacción al fuego", "clase de reacción", "Euroclase",
    ],
    "SI-3": [
        "evacuación", "ocupación", "recorrido de evacuación", "salida",
        "escalera protegida", "dimensionado", "señalización",
    ],
    "SI-4": [
        "instalaciones de protección", "extintor", "boca de incendio",
        "columna seca", "rociador", "detección", "hidrant",
    ],
    "SI-5": [
        "intervención de los bomberos", "vial de aproximación",
        "espacio de maniobra", "fachada accesible",
    ],
    "SI-6": [
        "resistencia al fuego de la estructura", "R 30", "R 60", "R 90",
        "R 120", "elementos estructurales", "forjado", "pilar",
    ],
}

# ── Model Claude ──────────────────────────────────────────────────────────────
CLAUDE_MODEL        = "claude-sonnet-4-6"
CLAUDE_MAX_TOKENS   = 4096
CLAUDE_CACHE_TTL_S  = 300   # 5 min (TTL prompt cache Anthropic)

# ── Extracció PDF ─────────────────────────────────────────────────────────────
# Nombre màxim de caràcters de context CTE que s'envien a Claude
MAX_CONTEXT_CHARS = 40_000
# Longitud mínima d'un fragment per ser considerat rellevant
MIN_FRAGMENT_CHARS = 80

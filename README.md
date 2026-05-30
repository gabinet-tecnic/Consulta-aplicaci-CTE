# CTE · IA — Eina d'anàlisi i justificació del CTE

Aplicació web local que analitza descripcions d'actuacions en edificis, determina quins Documents Bàsics del CTE apliquen i genera fitxes justificatives editables per a cada DB.

## Requisits

- Python 3.11 o superior
- Connexió a internet (per descarregar PDFs i cridar la Claude API)
- Clau API d'Anthropic → [console.anthropic.com](https://console.anthropic.com)

## Instal·lació

```bash
# 1. Clona el repositori
git clone https://github.com/el-teu-usuari/cte-ia.git
cd cte-ia

# 2. Instal·la les dependències
pip install -r requirements.txt

# 3. Crea el fitxer de configuració
copy .env.example .env      # Windows
cp .env.example .env        # Mac / Linux

# 4. Edita .env i afegeix la teva clau API
# ANTHROPIC_API_KEY=sk-ant-...
```

## Ús

```bash
python app.py
```

Obre el navegador a **http://localhost:5000**

La primera execució descarrega automàticament els PDFs oficials del CTE des de `codigotecnico.org` (~5 MB). Es guarden a `cache/` i només es tornen a descarregar si el Ministeri publica una versió nova.

## Endpoints

| Mètode | URL | Descripció |
|--------|-----|------------|
| GET | `/` | Aplicació web |
| GET | `/api/health` | Estat del servidor |
| GET | `/api/cache-status` | PDFs en cache |
| POST | `/api/analyze` | Anàlisi IA de la descripció |
| POST | `/api/validate-si` | Validació DB-SI amb PDF oficial |
| POST | `/api/refresh-pdfs` | Força re-descàrrega de PDFs |

## Fitxes justificatives disponibles

| DB | Nom | Seccions |
|----|-----|----------|
| DB-SI | Seguretat en cas d'Incendi | SI-1 a SI-6 |
| DB-SUA | Seguretat d'Utilització i Accessibilitat | SUA-1,2,3/4,7/8,9 |
| DB-HE | Estalvi d'Energia | HE-0 a HE-5 |
| DB-HS | Salubritat | HS-1 a HS-6 |
| DB-HR | Protecció davant el Soroll | HR 1-4 (només obra nova + rehab. integral) |
| DB-SE | Seguretat Estructural | SE, SE-AE, SE-C, SE-A/F/M |

## Avís legal

Eina d'orientació tècnica basada en el model OCT del COAC. Els PDFs del CTE provenen de `codigotecnico.org` (font oficial del Ministeri, versió sempre vigent). **No substitueix el criteri del tècnic competent ni els textos oficials del CTE.** La responsabilitat professional de la documentació signada recau sempre en el tècnic redactor.

## Estructura del projecte

```
flask_app/
├── app.py              ← Servidor Flask
├── config.py           ← Configuració i URLs dels PDFs
├── pdf_manager.py      ← Descàrrega i cache de PDFs
├── pdf_extractor.py    ← Extracció de text dels PDFs
├── ai_analyzer.py      ← Integració Claude API
├── .env                ← La teva API key (NO es puja a GitHub)
├── .env.example        ← Plantilla de configuració
├── requirements.txt    ← Dependències Python
├── cache/              ← PDFs descarregats (NO es pugen a GitHub)
└── static/
    └── CTE_ia_validacio_SI.html
```

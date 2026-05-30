# CTE·IA Flask — Posada en marxa

## 1. Requisits previs
- Python 3.11 o superior
- Connexió a internet (per descarregar PDFs CTE i cridar Claude API)

## 2. Instal·lació (una sola vegada)

```bash
# Des de la carpeta flask_app/
pip install -r requirements.txt
```

## 3. Configurar la clau API

```bash
# Copia el fitxer d'exemple
copy .env.example .env

# Edita .env i posa la teva clau Anthropic:
# ANTHROPIC_API_KEY=sk-ant-...
```

## 4. Arrancar el servidor

```bash
python app.py
```

Veuràs:
```
  CTE·IA Flask Server
  URL: http://localhost:5000
  API key: ✓ configurada
  Comprovant PDF DB-SI...
  ✓ DB-SI disponible: DccSI.pdf
```

Obre el navegador a: **http://localhost:5000**

## 5. Primera execució

La primera vegada descarregarà automàticament el PDF oficial DB-SI
des de codigotecnico.org (~5MB). Triga ~10-20s.

Els PDFs queden guardats a `cache/` i **no es tornen a descarregar**
tret que el servidor oficial publiqui una nova versió.

## Endpoints disponibles

| Mètode | URL                   | Descripció                              |
|--------|-----------------------|-----------------------------------------|
| GET    | `/`                   | Aplicació web principal                 |
| GET    | `/api/health`         | Estat servidor + PDFs                   |
| GET    | `/api/cache-status`   | Llista PDFs en cache                    |
| POST   | `/api/analyze`        | Anàlisi IA de la descripció             |
| POST   | `/api/validate-si`    | Validació DB-SI amb PDF oficial         |
| POST   | `/api/refresh-pdfs`   | Forçar re-descàrrega PDFs               |

## Exemple de crida des de la consola

```bash
# Anàlisi
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d "{\"description\": \"Reforma coberta plana habitatge plurifamiliar amb nou aïllament i impermeabilització\"}"

# Validació SI
curl -X POST http://localhost:5000/api/validate-si \
  -H "Content-Type: application/json" \
  -d "{\"description\": \"Canvi d'ús de local a habitatge\", \"tipologia\": \"plurifamiliar\", \"selectedIds\": [\"us_canvi\", \"int_distribucio\"]}"

# Estat cache
curl http://localhost:5000/api/cache-status

# Forçar re-descàrrega
curl -X POST http://localhost:5000/api/refresh-pdfs \
  -H "Content-Type: application/json" \
  -d "{\"force\": true}"
```

## Estructura de fitxers

```
flask_app/
├── app.py              ← Servidor Flask (arrenca aquí)
├── config.py           ← URLs PDFs, configuració
├── pdf_manager.py      ← Descàrrega i cache de PDFs
├── pdf_extractor.py    ← Extracció text i seccions del PDF
├── ai_analyzer.py      ← Integració Claude API
├── .env                ← La teva API key (NO compartir)
├── .env.example        ← Plantilla
├── requirements.txt    ← Dependències Python
├── cache/              ← PDFs descarregats (auto-gestionat)
└── static/
    └── CTE_ia_validacio_SI.html  ← Aplicació web
```

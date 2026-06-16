# CTE·IA — Prompt per a la Próxima Fase (gstack)

**Data**: 2 juny 2026  
**Status**: ✅ Codi bàse completat i desplegat  
**Repository**: https://github.com/gabinet-tecnic/Consulta-aplicaci-CTE

---

## Context

L'app CTE·IA ja té:
- ✅ 6 DBs implementats (SI, SUA, HE, HS, HR, SE)
- ✅ Sistema PDF inteligent (descàrrega automàtica de codigotecnico.org)
- ✅ Validació en temps real
- ✅ Filtrat contextual per tipologia
- ✅ Deployment actiu a Render

**Link**: https://consulta-aplicaci-cte.onrender.com

---

## Objectiu de la Próxima Fase

**Millorar la qualitat i completesa de les fitxes justificatives**.

Les fitxes actuals són funcionals però esquemàtiques. L'objectiu és que siguin **tan detallades i completes com les fitxes de referència del COAC**, amb:

- ✓ Taules de valors (transmitàncies, cabals, etc.)
- ✓ Camps de valor del projecte editables
- ✓ Caselles de "Contemplat" per a cada requisit
- ✓ Referencias normatives exactes
- ✓ Notes de càlcul i criteri
- ✓ Seccions per tipologia ben diferenciades

---

## Tasques per Implementar

### 1. **Enriquir Contingut de les Fitxes** (PRINCIPAL)

**Abordatge**: Comparar fitxa per fitxa (app vs. COAC) i millorar-les:

#### Fase 1 (Pilot): DB-HS Secció HS-6 (Radó)
- [ ] Llegir fitxa COAC HS-6 (referència)
- [ ] Comparar amb fitxa actual de l'app
- [ ] Identifi car elements que falten (taules, valors, camps)
- [ ] Actualitzar fitxa app a l'estàndard COAC
- [ ] Validar amb PDFs oficials del CTE
- [ ] ✅ Confirmar que funciona correctament

#### Fase 2: Aplicar Mateix Nivell a Altres DBs
- [ ] DB-SI (SI-1 a SI-6)
- [ ] DB-SUA (SUA-1, SUA-2, SUA-3, etc.)
- [ ] DB-HE (HE-0 a HE-5)
- [ ] DB-HS (HS-1 a HS-5)
- [ ] DB-HR (HR-1 a HR-4)
- [ ] DB-SE (SE base + variants)

---

### 2. **Multiidioma (CA/ES)** — PREREQUISIT

**Estat**: Pendent d'implementar  
**Importancia**: ALTA (necessari per colegiats que treballen en ambdós idiomes)

#### Tasques:
- [ ] Crear sistema i18n simple (`i18n/ca.json`, `i18n/es.json`)
- [ ] Afegir toggle de llengua al header (bandera CA/ES)
- [ ] Traduir tots els strings de les fitxes a castellà
- [ ] Guardar preferència en localStorage
- [ ] Verificar que PDFs oficials usin terminologia consistent

**Diccionari Exemple**:
```json
{
  "ca": {
    "db-si": "Seguretat en cas d'incendi",
    "exigencia": "Exigència",
    "valor-exigit": "Valor exigit",
    "valor-projecte": "Valor projecte"
  },
  "es": {
    "db-si": "Seguridad en caso de incendio",
    "exigencia": "Exigencia",
    "valor-exigit": "Valor exigido",
    "valor-projecte": "Valor proyecto"
  }
}
```

---

## Enfocament Recomanat

### Per a Cada DB:

1. **Obrir COAC fitxa** (referència oficial)
2. **Obrir app fitxa** (versió actual)
3. **Comparar element a element**:
   - Títols de seccions
   - Taules de valors (amb zones climàtiques, tipologies, etc.)
   - Camps de "Valor projecte"
   - Caselles de "Contemplat"
   - Referencias a articles exactes (ex: "HE 1, T.3.1.1.a")
   - Notes i criteris de càlcul
4. **Actualitzar fitxa app** fins igualar qualitat
5. **Testejar** amb scenarios reals

### Pilot (HS-6):
- Esperat: 2-3 hores
- Resultat: Template/standard per aplicar a altres DBs
- Confirmació: Validar amb Nuria

---

## Informació de Suport

### PDF Oficials (Descarregats Automàticament)
- **DB-SI**: `/cache/DB_SI_DccSI.pdf`
- **DB-SUA**: `/cache/DB_SUA_DccSUA.pdf`
- **DB-HE**: `/cache/DB_HE_DccHE.pdf`
- **DB-HS**: `/cache/DB_HS_DccHS.pdf`
- **DB-HR**: `/cache/DB_HR_DccHR.pdf`
- **DB-SE**: `/cache/DB_SE_DBSE.pdf`

### Estructura de Fitxes (Actual)
**Ubicació**: `/flask_app/static/CTE_ia_validacio_SI.html`

**Funcions per DB**:
- `buildFitxaSI(tipologia)` → línea ~1563
- `buildFitxaSUA(tipologia)` → línea ~1803
- `buildFitxaHE(tipologia)` → línea ~1931
- `buildFitxaHS(tipologia)` → línea ~2226
- `buildFitxaHR(tipologia)` → línea ~2265
- `buildFitxaSE(tipologia)` → línea ~2428

### Utilitats
- `row()` function → Crea files de taula amb reqs per tipologia
- `changeTipologia()` → Funcionalitat de selector tipologia
- `validateProjectFields()` → Validació de camps crítics

---

## Testing

Per cada fitxa millorada:
1. Veure fitxa a l'app
2. Comparar visualment amb COAC
3. Provar tipologia switching (unifamiliar → plurifamiliar → terciari)
4. Provar validacions de camps crítics
5. Provar impressió
6. Confirmar que no hi ha errors JavaScript (devtools)

**Checklist**: `TESTING_CHECKLIST.md` (a la repo)

---

## Quality Standard Document

**IMPORTANT**: Read `FITXES_QUALITY_STANDARDS.md` at the root of the repository.

This document shows:
- ✅ Visual comparison: current app fitxa (HS-6) vs COAC reference
- ✅ All missing elements (50% of content is incomplete)
- ✅ Complete template of how HS-6 should look
- ✅ Quality checklist for all fitxes
- ✅ Specifications for gstack to follow

**Key insight**: Current app fitxes are ~50% incomplete. The goal is NOT perfectionionism, but replicating the existing COAC completeness level.

---

## Delivery Expected

**Commit message format**:
```
Enhance [DB-XX] fitxa to COAC standard completeness

- Add alternative solutions (zones, contexts)
- Add technical specifications and calculation fields
- Add numbered notes for complex requirements
- Expand project value fields per solution
- Add CTE article references (exact articles)
- Implement full multilingual support (CA/ES)
- Verify against FITXES_QUALITY_STANDARDS.md checklist
```

**Verification**: Each fitxa must pass the quality checklist in `FITXES_QUALITY_STANDARDS.md`

---

## Contact & Questions

**Nuria**: gabinet.tecnic@catgi.cat  
**Colegiats testejant**: feedback@consulta-aplicaci-cte.onrender.com

---

**¡Endavant! El codi base és robust. Vos toca enriquir els continguts al nivell del COAC.**


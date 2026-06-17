# CTE·IA Phase 2 — Per a gstack

**Data**: 17 de juny de 2026  
**Estat**: 🚀 Ready to start  
**Tasca**: Millorar les fitxes justificatives al nivell COAC

---

## Context Ràpid

L'app CTE·IA ja està **LIVE** a Render amb:
- ✅ Sistema multiidioma CA/ES
- ✅ Validacions en temps real
- ✅ Print funcional
- ✅ Lògica d'aplicació correcta

**Que falta**: Les fitxes justificatives són **50% incompletes** comparades amb la referència COAC.

---

## Tasca Principal

**Reescriure les 6 fitxes (SI, SUA, HE, HS, HR, SE) al nivell de qualitat COAC.**

Cada fitxa ha de tenir:
- ✅ Solucions alternatives (múltiples opcions, no una sola)
- ✅ Especificacions tècniques detallades (mm, m³/h, kPa, etc.)
- ✅ Camps de càlcul amb fórmules (si aplica)
- ✅ Notes numeradas amb aclaracions complexes
- ✅ Multiidioma perfecte (CA/ES)
- ✅ Referencias exactes al CTE (articles, taules)

---

## Documents de Referència

### 1. **FITXES_QUALITY_STANDARDS.md** (LLEGIR PRIMER)
Ubicació: `/flask_app/FITXES_QUALITY_STANDARDS.md`

Conté:
- Comparació visual: app actual vs COAC (captures incloses)
- Exemple detallat de HS-6 complet al nivell COAC
- Checklist per verificar qualitat de cada fitxa
- Template de com hauria de veure cada secció

**CRITICAL**: Llegeix-la sencera per entendre l'estàndard esperat.

### 2. **PROMPT_PROXIMA_FASE_gstack.md**
Ubicació: `/flask_app/PROMPT_PROXIMA_FASE_gstack.md`

Conté:
- Instruccions detallades per a cada DB
- Ordre de prioritat
- Format de commit esperat
- Verificació requerida

### 3. **TESTING_CHECKLIST.md**
Ubicació: `/flask_app/TESTING_CHECKLIST.md`

Com testejar les fitxes:
- Scenarios per cada DB
- Multiidioma validation
- Print testing
- Tipologia switching

---

## App en Vivo

**URL**: https://consulta-aplicaci-cte.onrender.com

Pots accedir a:
- Obrir fitxes actuals (per veure l'estructura base)
- Canviar idioma (CA/ES) amb botones al header
- Veure validacions en temps real
- Testejar print

---

## Ordre de Prioritat (per DB)

### 1. **HS-6** (Pilot — ja tens l'exemple complet)
Solucions: Barrera protecció, Espai contenció ventilat, Despressurització del terreny

### 2. **HS-1 a HS-5** (Mateixa estructura HS)
HS-1: Humitat, HS-2: Residus, HS-3: Ventilació, HS-4: Fontaneria, HS-5: Evacuació

### 3. **DB-SI** (6 seccions, més complex)
SI-1 a SI-6 amb múltiples opcions per zona

### 4. **DB-HE** (Molt llarg, molt tabulat)
HE-0 a HE-5 amb taules de zona climàtica

### 5. **DB-SUA, DB-HR, DB-SE**
Les més petites, però amb detalls específics

---

## Especificacions Tècniques

### Estructura Base per Fitxa:

```
FITXA [DB-XX] — [TÍTOL]
Article: [XX] · RD XXXX/XXXX

JUSTIFICACIÓ DEL COMPLIMENT DE L'EXIGÈNCIA

[Si aplica: diferenciació per zones, contextos, tipologia]

SOLUCIONS POSSIBLES:
  ☐ Solució 1 (descrivió)
  ☐ Solució 2 (descrivió)
  ☐ Solució 3 (descrivió)
  [etc.]

CARACTERÍSTIQUES DE LES SOLUCIONS TÈCNIQUES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ SOLUCIÓ 1 [NOM]

Ubicació: [on va]
Requisits:
• Especificació 1 (amb unitats: mm, m³/h, kPa, etc.)
• Especificació 2
• [etc.]

Camps de càlcul (si aplica):
  Formula: D = -10 m²/s
  Input: [campo editabil]

Valor projecte: [input] [unitat]  ☐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Més solucions...]

OBSERVACIONS I NOTES TÈCNIQUES:
¹ Nota 1 amb detalles
² Nota 2
[etc.]

DOCUMENTACIÓ DE REFERÈNCIA:
• CTE DB-[XX] (actualitzat 2020)
• RD XXXX/XXXX
• Norma UNE-EN-ISO XXXXX
```

### Multiidioma (CA/ES):
- Tots els labels humans (títols, "Solucions possibles", etc.) s'han de traduir
- Els valors del CTE (articles, normes) es mantenen com estan
- Usar la funció `t()` del sistema i18n existent (ja està implementat)

---

## Procés per a Cada Fitxa

1. **Obrir fitxa COAC de referència** (les que Nuria va compartir)
2. **Obrir fitxa app actual** → https://consulta-aplicaci-cte.onrender.com
3. **Comparar element a element**:
   - Solucions alternatives?
   - Especificacions tècniques?
   - Camps de càlcul?
   - Notes detallades?
4. **Actualitzar fitxa app** (`buildFitxa*()` function al HTML)
5. **Testejar**:
   - Multiidioma (CA/ES)
   - Tipologia switching (si aplica)
   - Print (https://consulta-aplicaci-cte.onrender.com)
   - Validacions
6. **Commit** amb format:
   ```
   Enhance [DB-XX] fitxa to COAC standard completeness
   
   - Add [solucions/especificacions/etc.]
   - Implement [feature]
   - Verify multiidioma support
   ```

---

## Verificació Final (Checklist)

Per cada fitxa completada, verifica:

- [ ] Títol i article CTE exactes
- [ ] Totes les solucions alternatives (no només 1-2)
- [ ] Especificacions numèriques completes (mm, m³/h, etc.)
- [ ] Camps de càlcul amb fórmules (si aplica al CTE)
- [ ] Camps "Valor projecte" editables per solució
- [ ] Checkboxes "Contemplat" correctes
- [ ] Notes numeradas amb aclaracions
- [ ] Documentació de referència (URLs si aplica)
- [ ] Multiidioma CA/ES funcional
- [ ] Print correcte
- [ ] Tipologia switching correcte (si aplica)
- [ ] Commit message clar i descriptiu

---

## Questions/Support

Si tens dubtes sobre:
- Estructura d'una fitxa → llegeix `FITXES_QUALITY_STANDARDS.md` (té l'exemple complet HS-6)
- Com testejar → `TESTING_CHECKLIST.md`
- Ordre o prioritats → aquest document

---

## Context Técnic

L'app està construïda amb:
- **Frontend**: HTML + JavaScript vanilla (2500+ línies)
- **Backend**: Flask (Python) + Anthropic Claude API
- **PDFs**: Descàrrega automàtica de codigotecnico.org
- **Multiidioma**: Sistema i18n amb `t()` function
- **Deployment**: Render.com (auto-deploy en push a main)

**Estructures clau:**
- `buildFitxa*()` functions (per DB) → generen HTML de fitxa
- `row()` helper → crea files de taula amb suport multiidioma
- `changeTipologia()` → canvia visualització per tipologia
- `t(key)` → tradueix strings CA/ES

---

## Getting Started

1. **Clone/pull** repo: `https://github.com/gabinet-tecnic/Consulta-aplicaci-CTE`
2. **Llegir** `FITXES_QUALITY_STANDARDS.md` completament
3. **Obrir** https://consulta-aplicaci-cte.onrender.com (app en vivo)
4. **Comença** per HS-6 (tens l'exemple complet)
5. **Commit + push** cada fitxa completada
6. **Auto-deploy** a Render en ~2 minuts

---

## Estimació

- HS-6 (pilot): 2-3 hores
- Cada altra fitxa: 1-2 hores (dependrà de complexitat)
- **Total**: 15-25 hores (distribuït en 3-5 dies de feina)

---

**Preguntes? Comencem!**


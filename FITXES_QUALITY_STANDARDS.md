# Estàndard de Qualitat per a les Fitxes Justificatives

**Data**: 16 de juny de 2026  
**Estat**: ⚠️ CRÍTICO — Fitxes actuals NO compleixen estàndard COAC  
**Per a**: gstack — Fase 2 de millora de fitxes

---

## El Problema

Les fitxes actuals a l'app són **massa simplificades** comparades amb les fitxes de referència del COAC.

**Exemple concret: HS-6 (Protecció enfront el radó)**

### Versió ACTUAL de l'app (INCOMPLETA):

```
HS-6 | Protecció enfront el radó

EXIGÈNCIA                          | REF. CTE  | VALOR EXIGIT              | VALOR PROJECTE           | CONTEMPLAT
─────────────────────────────────────────────────────────────────────────────────────────────────────
Zona de radó del solar             | HS 6-1    | Zona I o II               | [input]                  | ☐
Barrera de radó                    | HS 6-2    | Membrana ≥ 0,5 mm         | [input]                  | ☐
Ventilació del subsòl (Zona II)    | HS 6-2.2  | Sistema ventilació        | [input]                  | ☐
```

**Problemes:**
- ❌ Només 3 requisits vs 5+ del COAC
- ❌ NO diferencía entre ZONA I i ZONA II (solucions diferents)
- ❌ MANCA "JUSTIFICACIÓ DEL COMPLIMENT DE L'EXIGÈNCIA"
- ❌ MANCA detalls tècnics (especificacions de membrana, gruix, fórmules)
- ❌ MANCA camp de càlcul per a barrera ("D = -10 m²/s · 2 mm")
- ❌ MANCA les notes tècniques amb aclaracions complexes

---

### Versió COAC (COMPLETA — La referència):

```
JUSTIFICACIÓ DEL COMPLIMENT DE L'EXIGÈNCIA

Municipal*: [input]              Zona: [input ZONA I o II]

SOLUCIONS POSSIBLES:
───────────────────────────────────────────────────────────────

☐ ZONA I
  ☐ Barrera de protecció
  
☐ ZONA II (Múltiples opcions)
  ☑ Barrera de protecció        i també       ☐ Cambra d'aire ventilada
  ☑ Espai de contenció ventilat
  ☑ Sistema de despressurització del terreny

CARACTERÍSTIQUES DE LES SOLUCIONS TÈCNIQUES PREVISTES

✓ BARRERA DE PROTECCIÓ
  - Està col·locada entre el terreny i els locals habitables de l'edifici
  - Té continu: als juntes i les trobades amb elements que la travessen
  - No té fissures que permetin el pas del radó conveccio
  - [H] Un coeficient de difusió al radó (D) tal que l'exhalació limit (Sh,b)...
  - Calcular: D = -10 m²/s i d = 2 mm
  
  ESPECIFICACIONS DETALLADES:
  - Membrana polietilè ≥ 0,5 mm (o equivalent)
  - Segellat perimetral amb cinta d'estanqueïtat o cordó expansiu
  - Totes les penetracions (tubs, canalitzacions) segellades individualment

✓ ESPAI DE CONTENCIÓ VENTILAT
  - Cambra d'aire ventilada horizontal o vertical, connectada amb
  l'exterior mitjançant natural o mecànica
  - [especificacions de superfície de ventilació natural mínima: cm²]

✓ SISTEMA DE DESPRESSURITZACIÓ DEL TERRENY *
  - Està format per una sèrie d'elements de captació, instal·lats sobre
  el reflector granular, amb conductes [especificacions técniques]
  - El sistema de captació està connectat a un conducte d'extracció
  mecànica.

OBSERVACIONS:
- Caldrà comprovar l'eficàcia de la solució emprada mesurament la concentració
de radó a posteriori de la intervenció
```

---

## Diferències Clau (APP vs COAC)

| Element | APP Actual | COAC | Status |
|---------|-----------|------|--------|
| **Estructura "Justificació"** | ❌ No | ✅ Sí | FALTA |
| **Diferenciació Zona I / II** | ❌ No | ✅ Sí | FALTA |
| **Solucions alternatives** | ❌ 1-2 | ✅ 3+ | INCOMPLETA |
| **Detalls tècnics** | ❌ Genèric | ✅ Específic | FALTA |
| **Camps de càlcul** | ❌ No | ✅ Sí | FALTA |
| **Notes amb números** | ❌ No | ✅ Sí | FALTA |
| **Especificacions numèriques** | ❌ Partial | ✅ Completes | INCOMPLETA |

---

## Estàndard de Qualitat Esperat

Cada fitxa ha de tenir:

### 1. **Estructura Base**
```
Títol DB (ex: "HS-6 Protecció enfront el radó")
  ├── Descrició de l'àmbit
  ├── ZONA/CONTEXT (si aplica)
  │   ├── Zona I (solucions)
  │   └── Zona II (solucions)
  ├── Taula de seccions aplicables
  ├── JUSTIFICACIÓ DEL COMPLIMENT
  │   ├── Solucions possibles (opcions alternatives)
  │   └── Característiques de les solucions tècniques
  ├── Camps per a valor projecte
  ├── OBSERVACIONS i notes tècniques
  └── DOCUMENTACIÓ DE REFERÈNCIA
```

### 2. **Requisits per Solució**
- ✅ Cada solució ha de ser **independent i completa**
- ✅ Ha de detallar **especificacions numèriques** (gruix, dimensions, fórmules)
- ✅ Ha de tenir **camps de càlcul** si cal (ex: "D = -10 m²/s · d = 2 mm")
- ✅ Ha de indicar **què es contempla** amb checkboxes per opcions

### 3. **Qualitat de Detalles**
- ✅ Articles exactes del CTE citats (ex: "HS 6-2.2", no "HS 6")
- ✅ Especificacions tècniques concretes (ex: "≥ 0,5 mm", no "gruix mínim")
- ✅ Unitats de mesura clares (mm, m²/s, kPa, etc.)
- ✅ Notes amb números per a aclaracions complexes (¹, ², ³)

### 4. **Cobertura de Cases d'Ús**
- ✅ Obra nova vs reforma (si difereixen)
- ✅ Tipologia (unifamiliar, plurifamiliar, terciari)
- ✅ Zones/contextos específics (Zona I/II per radó, etc.)

---

## Exemple Concret: Com Hauria de Veure HS-6

### FITXA HS-6 Completa (Estàndard COAC):

```
┌─────────────────────────────────────────────────────────────┐
│ HS-6 · PROTECCIÓ ENFRONT EL RADÓ                           │
│ Art. HS 6 · RD 1029/2022                                    │
└─────────────────────────────────────────────────────────────┘

JUSTIFICACIÓ DEL COMPLIMENT DE L'EXIGÈNCIA

Municipal*: [________________]    Zona: ☐ Zona I  ☐ Zona II

SOLUCIONS POSSIBLES:

Per a ZONA I (concentració baixa):
  ☐ Barrera de radó contínua (solució bàsica)

Per a ZONA II (concentració mitjana/alta):
  ☐ Barrera de protecció (+ espai de contenció ventilat)
  ☐ Espai de contenció ventilat (+ barrera)
  ☐ Sistema de despressurització del terreny
  ☐ Sistema de despressurització activa

CARACTERÍSTIQUES DE LES SOLUCIONS TÈCNIQUES

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ BARRERA DE PROTECCIÓ

Ubicació: Entre el terreny i els locals habitables de l'edifici

Requisits:
• Membrana polietilè ≥ 0,5 mm (o equivalent continu)
• Continuïtat: en juntes, trobades i elements que la travessen
• Segellat perimetral: cinta d'estanqueïtat o cordó expansiu
• Penetracions: tubs, canalitzacions segellades individualment

Càlcul de l'eficàcia:
  D = -10 m²/s  (coeficient de difusió al radó)
  d = 2 mm      (gruix mínim de membrana)
  
  [Camp per calcular exhalació limit (Sh,b)]

Valor projecte: [________________] mm de gruix membrana ☐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ ESPAI DE CONTENCIÓ VENTILAT

Ubicació: Entre la barrera i els locals habitables

Requisits:
• Cambra d'aire: horizontal o vertical, comunicada amb l'exterior
• Ventilació natural mínima: obertures ≥ 1/500 de la superfície solera
• Ventilació mecànica: 120 m³/h com a mínim
• Permeabilitat natural: com a mínim [especificacions]

Valor projecte:
  Tipo de ventilació: ☐ Natural  ☐ Mecànica
  Superfície ventilació: [________________] cm²  ☐
  Potència ventilació: [________________] m³/h   ☐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ SISTEMA DE DESPRESSURITZACIÓ DEL TERRENY

Ubicació: Penetrant la solera i les parets en contacte amb terreny

Components:
• Xarxa de captació sobre reflector granular
• Conducte d'extracció (DN ≥ 100 mm recomanat)
• Ventilador (potència mínima: [________________] W)
• Conducte final: prolongació 1 m sobre coberta

Valor projecte:
  Potència ventilador: [________________] W  ☐
  Diàmetre conducte: [________________] mm   ☐

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

OBSERVACIONS I NOTES TÈCNIQUES:

¹ Zona de radó: Consultar mapa CSN (Consell Seguretat Nuclear)
  Accés: https://www.csn.es/

² Nivell de referència: 300 Bq/m³ — si es mesura superior, implementar
  sistema de despressurització activa adicional

³ Barrera de protecció: Caldrà comprovar-la post-construcció mitjançant
  mesurament de concentració de radó (test radon)

⁴ Compatibilitat: Els sistemes es poden combinar (ex: barrera +
  ventilació + despressurització per a Zona II alta)

DOCUMENTACIÓ DE REFERÈNCIA:
• CTE DB-HS (actualitzat 2020)
• RD 1029/2022 sobre protecció enfront el radó
• Mapa de zones CSN: https://www.csn.es/...
• Norma UNE-EN-ISO 11665-1: Mesurament de radó

───────────────────────────────────────────────────────────────

Signatura i segell del tècnic competent

[________________]    Data: [__/__/__]

───────────────────────────────────────────────────────────────

Fitxa d'orientació tècnica. Generada per CTE·IA amb base en el
model OCT del COAC. Verificar sempre amb els textos oficials del CTE
vigents i els mapes/normes actualitzats.
```

---

## Per a gstack: Com Procedir

### **Tasca Principal:**
Replicar aquest estàndard de qualitat per a TOTES les fitxes (SI, SUA, HE, HS, HR, SE).

### **Procés per cada DB:**

1. **Obrir fitxa COAC de referència** (la que tengo Nuria)
2. **Obrir fitxa app actual** 
3. **Identificar gaps:**
   - Estructura de "Justificació"?
   - Solucions alternatives?
   - Detalls tècnics?
   - Camps de càlcul?
   - Notes numeradas?
4. **Actualitzar fitxa app** fins igualar qualitat COAC
5. **Testejar** (changeTipologia, validacions, print, multiidioma)

### **Ordre de Prioritat:**
1. **HS-6** (ja analitzat, serveix com pilot)
2. **HS-1 a HS-5** (mateixa estructura HS)
3. **DB-SI** (més complex)
4. **DB-HE** (molt grans)
5. **DB-SUA, DB-HR, DB-SE**

---

## Checklist per gstack

Quan actualitzis una fitxa, verifica que té:

- [ ] Títol i referència CTE exacta
- [ ] Descripció de l'àmbit/context
- [ ] Diferenciació per zones o casos (si aplica)
- [ ] Taula de "Solucions possibles" (opcions alternatives)
- [ ] Secció "Característiques de les solucions tècniques"
- [ ] Especificacions numèriques detallades (mm, m³/h, kPa, etc.)
- [ ] Camps de càlcul amb fórmules (si aplica)
- [ ] Camps "Valor projecte" editables per cada opció
- [ ] Checkboxes "Contemplat" per opcions
- [ ] Notes numeradas amb aclaracions complexes
- [ ] Documentació de referència (URLs, normes, etc.)
- [ ] Signatura i data
- [ ] Disclaimer "Verificar sempre amb textos oficials"
- [ ] Funcionament correcte en multiidioma (CA/ES)

---

## Arxius Referència

- **Fitxa COAC HS-6**: Carpeta compartida (screenshot + PDF si tenim)
- **Fitxa APP actual HS-6**: URL https://consulta-aplicaci-cte.onrender.com (obrir HS → Context → marcar "soterrani" → obrir HS-6)
- **Estàndard de qualitat**: Aquest document

---

**Nota final:** L'estàndard no és perfeccionisme — és replicar la completesa del COAC. Si el COAC té 5 solucions, la fitxa app ha de tenir 5 solucions. Si el COAC té notes técnicas amb números, la fitxa app ha de tenir-les.


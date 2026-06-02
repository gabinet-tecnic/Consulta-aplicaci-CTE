# CTE · IA — Testing Checklist & QA Guidelines

**Versió**: 1.0  
**Data**: Juny 2026  
**Per a**: Colegiats testejant l'aplicació

---

## Introdució

Els errors detectats en la testejada inicial han estat documentats i corregits. Aquesta guia ajuda a validar que les fitxes funcionin correctament i evita que es cometin els mateixos errors.

### Errors Corregits

| Error | Solució Implementada | Com Verificar |
|-------|---------------------|---------------|
| **HE-0 no demana % envolupant** | Decision panel que pregunta tipus obra + % envolupant | Obrir HE → veure "Decisió HE-0" |
| **Impressió sempre mostra general** | Media print CSS específic per fitxes | Imprimir fitxa → veure només fitxa, no resultats generals |
| **HS preguntes inadequades** | Context panel per marcar soterrani/aparcament | Obrir HS → veure "Context" i marcar segons projecte |
| **HULC sense explicació** | Tooltips en mentions de HULC | Passar mouse sobre "HULC" → veure explicació |
| **Dades incorrectes en camps** | Validació real-time amb warnings | Omplir zona climàtica invàlida → veure border vermell |

---

## Per a Cada DB: Testing Scenarios

### **DB-SI: Seguretat en cas d'Incendi**

#### ✓ Scenario 1: Obra Nova (Tipologia Plurifamiliar)
1. Obrirfitxa SI
2. Cambiar tipologia a **Plurifamiliar** (botó active)
3. Omplir projecte: nom, data, RC cadastral, tècnic
4. Completar SI-1 a SI-6 segons proyecto
5. **Verificar:**
   - ✅ Tipologia **plurifamiliar** resalta les filas correctes
   - ✅ Valors per unifamiliar estan amagats
   - ✅ R-30 vs R-60 són correctes per tipologia

#### ✓ Scenario 2: Obra Nova Unifamiliar (Adossat)
1. Obrir fitxa SI
2. Cambiar a **Unifamiliar / Adossat**
3. **Verificar:**
   - ✅ SI-6 mostra R-30 (adossat) o R-60 (aïllat) correcte
   - ✅ Zones altes (E) mostren valors correctes

#### ✓ Scenario 3: Imprimir Fitxa SI
1. Omplir fitxa SI parcialment
2. Cliquar botó **"Imprimir fitxa"**
3. **Verificar:**
   - ✅ S'obri diàleg print amb NOMÉS la fitxa SI
   - ✅ NO apareix el document de resultats generals
   - ✅ Layout és legible (no tallat pels marges)

---

### **DB-HE: Estalvi d'Energia**

#### ✓ Scenario 1: Obra Nova → HE-0 Aplica
1. Obrir fitxa HE
2. Panel "Decisió HE-0":
   - Triar **Obra nova**
3. **Verificar:**
   - ✅ Resultat diu "HE-0 aplica a obra nova"
   - ✅ Secció HE-0 apareix
   - ✅ Camps "Consum energètic" i "Qualificació energètica" són editables

#### ✓ Scenario 2: Reforma > 25% Envolupant → HE-0 Aplica
1. Panel "Decisió HE-0":
   - Triar **Reforma**
   - Input % envolupant: **35%**
2. **Verificar:**
   - ✅ Input apareix quan "Reforma" és seleccionat
   - ✅ Resultat diu "HE-0 aplica: reforma > 25%"
   - ✅ HE-0 visible

#### ✓ Scenario 3: Reforma < 25% Envolupant + Instal·lacions → NO HE-0
1. Panel "Decisió HE-0":
   - Triar **Reforma**
   - Input: **15%**
   - Marcar ✓ "instal·lacions tèrmiques"
2. **Verificar:**
   - ✅ Resultat diu "HE-0 NO aplica" (< 25%)
   - ✅ Avís vermell visible
   - ✅ HE-0 **amagat**

#### ✓ Scenario 4: Validació Zona Climàtica
1. Campo "Zona climàtica CTE": escriure **"X5"** (invàlid)
2. **Verificar:**
   - ✅ Border vermell al camp
   - ✅ Warning diu "Format: C1-C3, D1-D3, E1-E2"
3. Corregir a **"D1"** (vàlid)
4. **Verificar:**
   - ✅ Border torna al normal
   - ✅ Warning desapareix

#### ✓ Scenario 5: HULC Tooltip
1. Buscar text "HULC" a la fitxa (ex: HE-0 o HE-1)
2. **Verificar:**
   - ✅ "HULC" té un icona `?` al costat
3. Posar mouse sobre icona
4. **Verificar:**
   - ✅ Tooltip explica "HULC = Herramienta Unificada..."

---

### **DB-HS: Salubritat**

#### ✓ Scenario 1: Sense Soterrani (Unifamiliar)
1. Obrir fitxa HS
2. Panel "Context del projecte":
   - **NO marcar** ✓ "soterrani"
3. **Verificar:**
   - ✅ Secció HS-1 mostra NOMÉS "Façana" i "Coberta"
   - ✅ Filas "Murs soterrani" i "Terres soterrani" són **amagades**
   - ✅ Secció HS-6 "Radó" és **amagada**

#### ✓ Scenario 2: Amb Soterrani (Plurifamiliar)
1. Obrir fitxa HS
2. Panel "Context":
   - Marcar ✓ "soterrani"
3. **Verificar:**
   - ✅ Filas "Murs soterrani" i "Terres soterrani" **apareixen**
   - ✅ Secció HS-6 **visible**
   - ✅ Poder omplir impermeabilització del soterrani

#### ✓ Scenario 3: Amb Aparcament (Plurifamiliar)
1. Obrir fitxa HS
2. Panel "Context":
   - Marcar ✓ "aparcament col·lectiu"
3. Ir a **HS-3 Ventilació**
4. **Verificar:**
   - ✅ Tabla de cabals: fila "Aparcament col·lectiu" **visible**
   - ✅ Shows "120 l/s·plaça"

#### ✓ Scenario 4: Validació Zona Pluviomètrica
1. Campo "Zona pluviomètrica": escriure **"VI"** (invàlid)
2. **Verificar:**
   - ✅ Border vermell
   - ✅ Warning: "Format: I, II, III, IV o V"
3. Corregir a **"III"**
4. **Verificar:**
   - ✅ Border normal, warning desapareix

---

### **DB-HR: Protecció davant el Soroll**

#### ✓ Scenario 1: Edifici Urbà (Ld = 70 dB)
1. Obrir fitxa HR
2. Campo "Ld façana": **70**
3. **Verificar:**
   - ✅ Es accepta com número vàlid (sense warning)
   - ✅ Poder omplir taules d'índex de reducció acústica

#### ✓ Scenario 2: Validació Ld Façana
1. Campo: escriure **"xyz"** (invàlid)
2. **Verificar:**
   - ✅ Border vermell
   - ✅ Warning: "Valor numèric en dB"
3. Corregir a **"50"**
4. **Verificar:**
   - ✅ Es accepta (50-85 dB és rang típic)

#### ✓ Scenario 3: Valor sospitosament alt (ex: 100 dB)
1. Campo: **100**
2. **Verificar:**
   - ✅ Border groc (warning, no error)
   - ✅ Permet guardar (pot ser correcte en casos estranys)

---

### **DB-SUA: Seguretat d'Utilització i Accessibilitat**

#### ✓ Scenario 1: Obra Nova Residencial
1. Obrir fitxa SUA
2. **Verificar:**
   - ✅ Seccions SUA-1, SUA-2, SUA-3 visibles
   - ✅ Taula de criteris accessible (es pot editar)
   - ✅ Tipologia selector funciona

#### ✓ Scenario 2: Cambiar Tipologia a Terciari
1. Cliquar **"Terciari / Altres usos"**
2. **Verificar:**
   - ✅ Continguts per SUA-1, SUA-3 es reajusten
   - ✅ Valors específics per terciari mostrats

---

### **DB-SE: Seguretat Estructural**

#### ✓ Scenario 1: Obra Nova (Calculi Estructural Requerit)
1. Obrir fitxa SE
2. **Verificar:**
   - ✅ Informació sobre càlcul estructural (accions, combinacions)
   - ✅ Camps per referenciars norma DB-SE, DB-SE-AE, etc.
   - ✅ Seccions per materials (acer, formigó, fusta, etc.)

---

## Procés General de Testing per Fitxa

### ✅ Before Opening
- [ ] Descripció del projecte clara (ex: "Reforma integral plurifamiliar")
- [ ] IA ha identificat correctament els DBs aplicables
- [ ] Resultat de l'anàlisi IA és coherent

### ✅ When Opening Fitxa
- [ ] Fitxa modal oberta sense errors JavaScript
- [ ] Botó de tipologia mostra l'opció actual
- [ ] Context panels (HE-0, HS context) disponibles (si aplicable)
- [ ] Camps de text son editables

### ✅ Filling Fields
- [ ] **Projecte / Obra**: Accepta text lliure
- [ ] **Data**: Datepicker funciona i mostra data actual
- [ ] **Zona climàtica / Pluviomètrica / Ld**: Validació en temps real
  - Veure warning si format invàlid
  - Veure border vermell si error
- [ ] Checkboxes (ex: "Aplica") funcionen
- [ ] Tables amb inputs multiples son editables

### ✅ Tipologia Switching
- [ ] Cliquar autre tipologia: filas amb "only-*" s'amagan/mostren
- [ ] Valors a columna "Valor exigit" canvien si hi ha variants tipologia
- [ ] No hi ha elements deixats "penjats" o mal posicionats

### ✅ Printing
- [ ] Botó "Imprimir fitxa" fa Ctrl+P amb class `print-fitxa`
- [ ] Dialog print mostra NOMÉS la fitxa, no el header/footer/resultats
- [ ] Layout legible a paper (no tallat, fonts llegibles)

### ✅ Closing
- [ ] Cliquar botó "Tancar" o X tanca la modal
- [ ] Torna a la vista de resultats DBs
- [ ] Dades omplidas es mantenen (si es guarden)

---

## Common Issues & Troubleshooting

| Problema | Causa | Solució |
|----------|-------|---------|
| **HE-0 apareix quan no hauria** | No s'ha determinat % envolupant | Veure Decision Panel, marcar % < 25% |
| **Print mostra tot, no fitxa alone** | Class `print-fitxa` no aplicat | Verificar que modal té `open` class |
| **HS-1 mostra soterrani sense soterrani** | Context panel no marcat | Marcar "El projecte inclou soterrani" |
| **Camps zone amb border vermell** | Format invàlid | Corregir format (HE: C1-C3, HS: I-V, HR: número) |
| **HULC sense icona info** | enhanceHULCReferences() no executat | Recarregar fitxa |
| **Valors exigits no canvien per tipologia** | Selector tipologia no registrat | Cliquar botó tipologia per renovar |

---

## Performance & Browser Compatibility

- ✅ Tested: Chrome 120+, Firefox 121+, Safari 17+, Edge 120+
- ⚠️ Print: Usar "Guardar com PDF" per millor resultat (alguns navegadors)
- 💾 Dades: NO es guarden automàticament — imprimir o guardar manualment

---

## Reportar Errors

Si detecteu un error:

1. **Descriure el scenario** (ex: "Obra nova, unifamiliar, emplir HE-0")
2. **Pasos to reproduce** (clicks i inputs en ordre)
3. **Comportament esperat vs actual**
4. **Screenshots si necessari**
5. **Navegador i versió**

Enviar a: **gabinet.tecnic@catgi.cat**

---

## Versions & Updates

| Versió | Data | Canvis |
|--------|------|--------|
| 1.0 | Juny 2026 | Testing checklist inicial, 5 errores corregits |


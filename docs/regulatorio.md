# Clasificación regulatoria

DataSteward es un asistente **interno** que ayuda a encontrar, describir y consultar datos según
el rol de quien pregunta. No decide sobre personas: no otorga crédito, no selecciona ni evalúa
empleados, no da acceso a servicios. Esa es la base de las dos clasificaciones.

## Perú

**Normas:** Ley N.º 31814, que promueve el uso de la inteligencia artificial, y su Reglamento,
aprobado por el Decreto Supremo N.º 115-2025-PCM (publicado el 9 de setiembre de 2025). Para los
datos personales, la Ley N.º 29733 de Protección de Datos Personales.

**Categorías del Reglamento (art. 22):** *uso indebido* (prohibido), *uso de riesgo alto*
(permitido con condiciones y controles) y *riesgo aceptable* (el resto).

**Clasificación de DataSteward: riesgo aceptable.**

- No encaja en ningún uso indebido del art. 23 (manipulación, vigilancia masiva, inferencia de
  datos sensibles a partir de biometría, etc.).
- No encaja en los usos de riesgo alto del art. 24.1: no evalúa crédito (literal g), no decide
  sobre selección, evaluación o cese de trabajadores (literal e) aunque pueda leer la planilla, ni
  opera un activo crítico de servicios esenciales (literal a).
- **Dónde cambiaría:** si se usara para decidir sobre trabajadores a partir de la planilla, pasaría
  al literal e); si se desplegara como parte de un activo crítico de una entidad bancaria,
  podría caer en el literal a). El producto se inspira en gobierno de datos de servicios
  financieros, por eso se deja anotado.

**Obligaciones que sí aplican:**

| Obligación | Referencia | Cómo la atiende el prototipo |
|---|---|---|
| Tratar los datos personales según la normativa de protección de datos | Art. 26; Ley 29733 | Datos sintéticos; en producción, enmascarado por rol y principio de finalidad |
| Políticas internas y capacitación del personal (sector privado) | Arts. 31.2 y 31.3 | Política de acceso por rol (`datos/corpus/politica_acceso_roles.md`) |
| Etiquetado o aviso de que se interactúa con IA, cuando sea relevante | Art. 25.2 | La interfaz se presenta como asistente de IA |
| Plazo de adecuación del sector privado | Primera disposición complementaria final | Comercio: 2 años desde setiembre de 2025; si se usara en el sector financiero, 1 año (ya vencido en setiembre de 2026) |

La evaluación de impacto es voluntaria en el sector privado (art. 32.1), y el registro de
funcionamiento y la supervisión humana (art. 31) solo son obligatorios en riesgo alto. El
producto los tiene de todos modos: registro encadenado y un humano que lee cada respuesta.

## Unión Europea

**Norma:** Reglamento (UE) 2024/1689 de Inteligencia Artificial (AI Act).

**Clasificación de DataSteward: riesgo limitado (obligaciones de transparencia).**

- No es una práctica prohibida del art. 5.
- No es de alto riesgo: no es componente de seguridad de un producto regulado (art. 6.1) ni está
  en los usos del anexo III. En particular no hace *scoring* crediticio (anexo III, 5.b) ni toma
  decisiones de empleo (anexo III, 4).
- Interactúa directamente con personas, así que aplica el **art. 50.1**: informar que se está
  hablando con un sistema de IA.
- Aplica a todos los sistemas el **art. 4** (alfabetización en IA del personal que lo usa).
- Las obligaciones de **modelos de propósito general** (arts. 53 y siguientes) recaen en el
  proveedor del modelo (Google, en modo Gemini), no en el grupo.
- El tratamiento de datos personales sigue el RGPD.

## Dónde divergen

| Aspecto | Perú (DS 115-2025-PCM) | UE (Reglamento 2024/1689) |
|---|---|---|
| Nivel del producto | Riesgo aceptable | Riesgo limitado |
| Transparencia frente al usuario | Etiquetado "cuando sea relevante" (art. 25.2) | Obligación expresa para todo sistema que interactúa con personas (art. 50.1) |
| Catálogo de riesgo alto | Incluye una cláusula general (art. 24.1 j) y los activos críticos de servicios esenciales, entre ellos la banca | Lista cerrada en el anexo III, modificable por la Comisión |
| Evaluación previa | Evaluación de impacto voluntaria en el sector privado | Evaluación de conformidad obligatoria para alto riesgo |
| Datos personales | Remite a la Ley 29733 y a la autoridad de datos personales | Remite al RGPD |
| Supervisión y sanciones | La SGTD de la PCM recibe denuncias y las traslada a la autoridad competente | Autoridades nacionales de vigilancia y multas propias del Reglamento |
| Plazos | Escalonados por sector, de 1 a 4 años desde setiembre de 2025 | Escalonados desde agosto de 2024; obligaciones de alto riesgo del anexo III desde agosto de 2026 (la Comisión propuso posponerlas; verificar estado) |

**En la práctica:** la divergencia que más pesa para DataSteward es la cláusula general peruana.
Un uso que en Europa queda claramente fuera del anexo III podría considerarse de riesgo alto en
Perú si la autoridad entiende que hay "alta dificultad de supervisión humana" sobre datos de
personas. El registro de eventos y los controles medidos sirven como evidencia en ambos casos.

## Fuentes

- [Decreto Supremo N.º 115-2025-PCM (texto oficial)](https://www.congreso.gob.pe/Docs/DGP/DIDP/files/ds_115-2025-pcm.pdf)
- [Gob.pe: Decreto Supremo N.º 115-2025-PCM](https://www.gob.pe/institucion/pcm/normas-legales/7133522-115-2025-pcm)
- [Cuatrecasas: ¿Qué establece el Reglamento de la Ley de Inteligencia Artificial?](https://www.cuatrecasas.com/es/latam/tecnologia-medios-digitales/art/que-establece-el-reglamento-de-la-ley-de-inteligencia-artificial)
- [Reglamento (UE) 2024/1689 (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

# Priorización

Cada amenaza recibe una nota de **explotabilidad** (E, qué tan fácil es llevarla a cabo) y de
**impacto** (I, qué pasa si funciona), ambas de 1 a 5. La prioridad ordena por E × I y, en
empate, por la tasa de éxito medida sin controles. Donde hay medición, E se ancla en ella.

Escala de explotabilidad: 5 = cualquier usuario del chat, sin conocimientos, con éxito medido
≥ 80% · 4 = requiere algo de conocimiento (SQL, nombres de tablas) o éxito medido 60-80% ·
3 = requiere acceso a un punto menos expuesto o éxito < 60% · 2 = requiere acceso al servidor ·
1 = requiere comprometer a un tercero.

Escala de impacto: 5 = credenciales o datos restringidos de muchas personas · 4 = PII o sueldos ·
3 = engaño a usuarios o fuga de configuración · 2 = degradación del servicio · 1 = molestia.

| Prioridad | ID | Amenaza | E | I | E × I | Éxito medido sin controles |
|---|---|---|---|---|---|---|
| 1 | T02 | Inyección indirecta por documento | 5 | 5 | 25 | 100% [0.85; 1.00] |
| 2 | T01 | Inyección directa de prompt | 5 | 5 | 25 | 91% [0.72; 0.97] |
| 3 | T04 | Escalamiento de rol por el chat | 4 | 5 | 20 | 64% [0.43; 0.80] |
| 4 | T07 | Suplantación de rol en la interfaz | 5 | 4 | 20 | no medida (trivial: un clic) |
| 5 | T05 | Evasión del clasificador | 4 | 4 | 16 | 95% [0.78; 0.99] |
| 6 | T06 | Fuga del prompt del sistema | 5 | 3 | 15 | 91% [0.72; 0.97] |
| 7 | T03 | SQL destructivo o apilado | 3 | 5 | 15 | 68% [0.47; 0.84] |
| 8 | T08 | Phishing por documento | 4 | 3 | 12 | incluido en T02 (A2-06, A2-07, A2-16) |
| 9 | T09 | Datos sensibles en el registro | 3 | 4 | 12 | — |
| 10 | T11 | Denegación de servicio | 4 | 2 | 8 | — |
| 11 | T10 | Manipulación del registro | 2 | 3 | 6 | — |
| 12 | T12 | Filtración de la llave de API | 2 | 3 | 6 | — |
| 13 | T13 | Resultados enviados al proveedor LLM | 2 | 3 | 6 | — |
| 14 | T14 | Envenenamiento del entrenamiento del clasificador | 2 | 3 | 6 | — |
| 15 | T15 | Dependencias comprometidas | 1 | 5 | 5 | — |

## Justificación de las cinco primeras

**1. T02, inyección indirecta (25).** Es la más explotable porque el atacante no necesita hablar
con el asistente: le basta con que un documento suyo entre al catálogo, algo normal en gobierno
de datos, donde muchos equipos escriben notas. La víctima hace una pregunta inocente
("¿qué dice la nota de migración?") y el agente ejecuta la orden. Sin controles funcionó en 21 de
21 intentos, incluida la nota envenenada que ya vive en el corpus base. El impacto es máximo
porque la orden apunta a `seguridad.credenciales_servicio`. Va primera, por delante de T01 con la
misma nota, porque su tasa medida es mayor y porque el usuario que la dispara no sabe que está
atacando, así que tampoco lo reporta.

**2. T01, inyección directa (25).** Cualquier usuario con acceso al chat puede intentarla y el
modelo cede ante encuadres simples ("ignora", "override", "soy admin"), en inglés o en base64:
91% de éxito sin controles. El impacto es el mismo que T02 (planilla y credenciales). La exige
un usuario interno, lo que la deja un poco por detrás.

**3. T04, escalamiento de rol (20).** Es una variante de T01 enfocada en el rol: el usuario
afirma ser administrador o auditor. Tuvo 64% de éxito sin controles. Baja un punto de
explotabilidad porque la alineación del modelo rechaza los pedidos que no traen encuadre
(8 de 22 fallaron por eso). El impacto es 5 porque el rol abre todo el Lakehouse.

**4. T07, suplantación de rol en la interfaz (20).** En el prototipo el rol se elige en un
selector, sin autenticación: elegir "admin" da acceso total con un clic. No se mide porque el
resultado es determinista (100%). Su impacto queda en 4 y no en 5 porque solo aplica a quien ya
tiene acceso a la máquina donde corre el prototipo; en un despliegue real el rol vendría de un
proveedor de identidad. Es la amenaza que ningún control implementado reduce.

**5. T05, evasión del clasificador (16).** Sin enmascarado, 21 de 22 consultas mostraron PII.
Con el clasificador que solo mira el nombre, renombrar la columna basta (73% de éxito). Requiere
saber SQL y los nombres de columnas, por eso E = 4. El impacto es 4: PII de clientes, no
credenciales.

## Por qué T06 y T03 quedan fuera del top 5

T06 (fuga del prompt) es muy fácil (91%), pero el prompt no contiene secretos operativos: revela
la política y el canario. T03 (SQL destructivo) tiene impacto máximo, pero el modelo rechaza el
SQL destructivo cuando no viene con encuadre y la técnica que sí pasa (sentencias apiladas)
requiere conocer SQL. Ambas se miden igual en la [evaluación](evaluacion.md).

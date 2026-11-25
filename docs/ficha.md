# Ficha del sistema

| Campo | Contenido |
|---|---|
| Nombre | DataSteward |
| Grupo | Por definir |
| Integrantes | Por definir (4 integrantes) |
| Tipo | Prototipo local (Streamlit en `localhost` o Colab). No se despliega en internet. |

## Para qué sirve y a quién

Los equipos de datos de Minka, una empresa de retail **ficticia** con tarjeta de tienda y
billetera, pierden tiempo buscando qué tabla usar, quién es su dueño y qué pueden ver. DataSteward
responde esas preguntas en lenguaje natural y, cuando hace falta, consulta el Lakehouse con SQL
de solo lectura respetando el rol de quien pregunta y enmascarando datos personales.

Usuarios previstos: analistas de datos, auditores internos y administradores de la plataforma.

## Componentes

1. **Asistente con recuperación (RAG).** Índice TF-IDF local sobre el corpus de gobierno de datos
   (`datos/corpus/`). Recupera los 3 fragmentos más parecidos y se los pasa al modelo.
2. **Modelo de lenguaje.** Dos modos: `simulado` (determinista, por defecto, sin llave; imita un
   LLM pequeño y obediente con debilidades documentadas) y `gemini` (API de Gemini, nivel gratuito,
   `gemini-2.5-flash`, llave en `.env`).
3. **Agente con herramientas.** `listar_tablas`, `describir_tabla` y `ejecutar_sql` sobre DuckDB.
4. **Clasificador ML clásico.** Regresión logística de scikit-learn con rasgos del nombre de la
   columna (n-gramas de caracteres) y de una muestra de valores (patrones de correo, DNI, teléfono,
   tarjeta, magnitud numérica…). Decide si una columna es PII, SENSIBLE o NO_SENSIBLE, y esa decisión
   activa el enmascarado.
5. **Registro de eventos.** `registros/eventos.jsonl`, una línea por consulta, encadenada con SHA-256.
6. **Cinco controles activables** en `config.yaml`: filtro de entrada, sanitizador de documentos,
   validador SQL, enmascarado y filtro de salida.

## Qué datos usa y de dónde vienen

| Dato | Origen | Clasificación |
|---|---|---|
| Lakehouse (10 tablas: clientes, transacciones, productos, planilla, KPI, calidad, credenciales) | `src/datasteward/lakehouse.py`, Faker con semilla `20261125` | Sintético: incluye PII y secretos **falsos** a propósito |
| Corpus (catálogo, diccionario, políticas, glosario, procedimiento, guía SQL, nota de migración) | Escrito por el grupo en `datos/corpus/` | Interno ficticio. `nota_migracion_crm.md` está **envenenado** para la demostración |
| Columnas de entrenamiento del clasificador | Generadas en `clasificador.py` (semillas 1, 2 y 3) | Sintético |
| Catálogo de ataques y consultas legítimas | `evaluacion/catalogo/*.jsonl` | Escrito por el grupo |

## Quién lo usa y con qué permisos

| Rol | Tablas que puede leer | PII |
|---|---|---|
| analista | `gold.*`, `silver.transacciones`, `silver.productos`, `silver.clientes` | Enmascarada |
| auditor | `gold.*`, `silver.*`, `bronze.*` | Enmascarada |
| admin | Todo, incluido `seguridad.*` | En claro |

Todos los roles: solo `SELECT`. El rol lo fija la sesión (en el prototipo, un selector en la barra
lateral, sin autenticación; ver amenaza T07). La fuente única de la política es
`src/datasteward/politicas.py`.

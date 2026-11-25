# DataSteward · Ciberseguridad de IA

Asistente de gobierno de datos para un Lakehouse **ficticio**, construido, atacado y defendido como
trabajo integrador del curso *Ciberseguridad de Inteligencia Artificial* (Maestría en Ciencia de
Datos, UNI).

📄 **Página del proyecto:** https://anthonyhuaccachia.github.io/DataStewardAI/

> **Datos 100% sintéticos.** La empresa (Minka), sus clientes, empleados y credenciales son
> inventados (Faker, semilla fija). Nada corresponde a personas, empresas ni sistemas reales.

## Qué es

- **RAG** sobre el catálogo, el diccionario y las políticas de acceso (índice TF-IDF local).
- **Agente** con herramientas `listar_tablas`, `describir_tabla` y `ejecutar_sql` sobre DuckDB
  (esquemas bronze, silver, gold y seguridad).
- **Clasificador ML clásico** (scikit-learn) que decide qué columnas son PII o sensibles y activa
  el enmascarado.
- **Registro de eventos** JSONL encadenado con SHA-256.
- **Cinco controles** activables: filtro de entrada, sanitizador de documentos, validador SQL,
  enmascarado y filtro de salida.
- **LLM:** simulado y determinista por defecto (reproducible sin llave) o la API de Gemini.

## Instalar y correr

```bash
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m src.datasteward.preparar                    # genera Lakehouse, índice y clasificador
streamlit run src/app.py                              # interfaz en http://localhost:8501
```

Gemini (opcional): `cp .env.example .env`, complete `GEMINI_API_KEY` y elija "gemini" en la barra
lateral o use `DATASTEWARD_LLM=gemini`.

## Evaluación adversarial (un comando)

```bash
python evaluacion/correr_evaluacion.py               # ~45 s, LLM simulado
python evaluacion/correr_evaluacion.py --llm gemini
```

Seis amenazas × 21-22 ataques y 30 consultas legítimas; sin controles, con el control principal y
con todos; intervalos de Wilson al 95% y falsos positivos por control. Resultados versionados en
`evaluacion/resultados/<fecha>_<llm>/`. Notebook para Colab: `evaluacion/evaluacion.ipynb`.

## Entregables

| # | Entregable | Archivo |
|---|---|---|
| 1 | Ficha del sistema | [docs/ficha.md](docs/ficha.md) |
| 2 | Arquitectura (Mermaid) | [docs/arquitectura.md](docs/arquitectura.md) |
| 3 | Modelo de amenazas | [docs/modelo-de-amenazas.md](docs/modelo-de-amenazas.md) |
| 4 | Priorización | [docs/priorizacion.md](docs/priorizacion.md) |
| 5 | Controles y riesgo residual | [docs/controles.md](docs/controles.md) y [controles/](controles/) |
| 6 | Evaluación adversarial | [docs/evaluacion.md](docs/evaluacion.md) y [evaluacion/](evaluacion/) |
| 7 | Clasificación regulatoria | [docs/regulatorio.md](docs/regulatorio.md) |
| 8 | Página | GitHub Pages, publicada desde `docs/` con MkDocs Material |

## Estructura

```
config.yaml            controles activables y rutas
src/app.py             interfaz Streamlit
src/datasteward/       agente, RAG, LLM, clasificador, registro, Lakehouse sintético
controles/             los cinco controles
datos/corpus/          documentos sintéticos (incluye uno envenenado para la demostración)
evaluacion/            catálogo, correr_evaluacion.py, notebook y resultados versionados
registros/             muestras del registro de una corrida de ataque
docs/                  documentación y fuente de la página
```

## Reglas

Solo datos sintéticos. Ninguna llave en el repositorio ni en su historial. Los ataques se ejecutan
solo contra este producto.

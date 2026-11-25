"""Prepara todo lo necesario para correr: Lakehouse, índice RAG y clasificador.

Uso:  python -m src.datasteward.preparar
"""
import json

from src.datasteward import clasificador, lakehouse
from src.datasteward.config import cargar_config, ruta
from src.datasteward.rag import Indice


def main() -> None:
    cfg = cargar_config()
    db = lakehouse.construir(ruta(cfg, "lakehouse"))
    print(f"[1/3] Lakehouse sintético creado en {db}")
    idx = Indice.desde_carpeta(ruta(cfg, "corpus"))
    idx.guardar(ruta(cfg, "indice"))
    print(f"[2/3] Índice RAG con {len(idx.fragmentos)} fragmentos")
    met = clasificador.entrenar_y_guardar(ruta(cfg, "modelo_clasificador"))
    print("[3/3] Clasificador entrenado:", json.dumps(met, ensure_ascii=False))


if __name__ == "__main__":
    main()

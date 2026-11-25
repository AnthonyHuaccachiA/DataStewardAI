"""Carga de configuración: config.yaml + variables de entorno (.env)."""
from __future__ import annotations

import copy
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parents[2]

# Nombres de los controles activables. El orden es el del flujo de una consulta.
CONTROLES = [
    "filtro_entrada",
    "sanitizador_documentos",
    "validador_sql",
    "enmascarado",
    "filtro_salida",
]


def cargar_config(ruta: str | Path | None = None) -> dict:
    load_dotenv(RAIZ / ".env")
    ruta = Path(ruta) if ruta else RAIZ / "config.yaml"
    with open(ruta, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    modo = os.getenv("DATASTEWARD_LLM")
    if modo:
        cfg["llm"]["modo"] = modo.strip().lower()
    return cfg


def con_controles(cfg: dict, activos: list[str] | set[str] | None) -> dict:
    """Copia de la configuración con solo los controles indicados activos."""
    nuevo = copy.deepcopy(cfg)
    activos = set(activos or [])
    for c in CONTROLES:
        nuevo["controles"][c] = c in activos
    return nuevo


def ruta(cfg: dict, clave: str) -> Path:
    return RAIZ / cfg["rutas"][clave]

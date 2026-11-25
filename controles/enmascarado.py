"""Control 4: enmascarado de resultados guiado por el clasificador ML.

Cada columna del resultado pasa por el clasificador (nombre + muestra de valores). Si es
PII o SENSIBLE y el rol de la sesión no puede verla en claro, los valores se reemplazan.
"""
from __future__ import annotations

import pandas as pd

from src.datasteward.politicas import VE_SENSIBLE_SIN_MASCARA


def enmascarar_valor(v) -> str:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return v
    s = str(v)
    return "***" + s[-2:] if len(s) > 4 else "***"


def aplicar(df: pd.DataFrame, rol: str, clasificador, umbral: float = 0.5):
    if VE_SENSIBLE_SIN_MASCARA.get(rol, False) or df.empty:
        return df, []
    df = df.copy()
    enmascaradas = []
    for col in df.columns:
        muestra = [v for v in df[col].head(20).tolist() if v is not None]
        etiqueta, p = clasificador.clasificar(str(col), muestra)
        if etiqueta != "NO_SENSIBLE" and p >= umbral:
            df[col] = df[col].map(enmascarar_valor)
            enmascaradas.append({"columna": str(col), "etiqueta": etiqueta, "p": round(p, 3)})
    return df, enmascaradas

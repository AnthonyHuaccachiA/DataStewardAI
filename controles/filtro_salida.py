"""Control 5: filtro de salida.

Revisa la respuesta final antes de mostrarla:
- si contiene el token canario del prompt del sistema o frases literales del prompt, la bloquea;
- para roles sin permiso, redacta patrones de PII (correo, tarjeta, DNI, cuentas, secretos).
"""
import re

from src.datasteward.politicas import VE_SENSIBLE_SIN_MASCARA

from . import Decision

PII = {
    "correo": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
    "tarjeta": re.compile(r"\b4000\d{12}\b"),
    "cuenta": re.compile(r"\bCTA-\d{6,}\b"),
    "secreto": re.compile(r"\bFAKE-[\w-]+"),
    "dni": re.compile(r"(?<![\d.])\d{8}(?![\d.])"),
}


def revisar(respuesta: str, rol: str, canario: str, frases_prompt: list[str]) -> tuple[str, Decision]:
    motivos = []
    if canario in respuesta or any(f in respuesta for f in frases_prompt):
        return ("No puedo compartir mi configuración interna.",
                Decision(True, ["fuga_prompt_sistema"]))
    if not VE_SENSIBLE_SIN_MASCARA.get(rol, False):
        for nombre, patron in PII.items():
            if patron.search(respuesta):
                motivos.append(f"pii_redactada:{nombre}")
                respuesta = patron.sub("[REDACTADO]", respuesta)
    return respuesta, Decision(False, motivos)


def revisar_tabla(df, rol: str):
    """Aplica la misma redacción de PII a las celdas de texto de una tabla de resultados."""
    if VE_SENSIBLE_SIN_MASCARA.get(rol, False) or df is None or df.empty:
        return df, []
    df = df.copy()
    motivos = set()
    for col in df.columns:
        serie = df[col].astype(str)
        for nombre, patron in PII.items():
            if serie.str.contains(patron).any():
                motivos.add(f"pii_redactada_tabla:{nombre}")
                serie = serie.str.replace(patron, "[REDACTADO]", regex=True)
        if any(m.startswith("pii_redactada_tabla") for m in motivos):
            df[col] = serie
    return df, sorted(motivos)

"""Control 1: filtro de entrada.

Lista de patrones (expresiones regulares) sobre la consulta del usuario. Bloquea intentos
evidentes de anular instrucciones, de reclamar otro rol, de extraer el prompt del sistema y
de pedir SQL destructivo. Es un control de firma: lo que no coincide con un patrón pasa.
"""
import re

from . import Decision
from ._texto import normalizar

PATRONES = {
    "anular_instrucciones": [
        r"\bignora(r|d)?\b.{0,30}\b(instrucciones|reglas|politicas?|indicaciones|restricciones)",
        r"\bolvida(r)?\b.{0,20}\b(instrucciones|reglas|politicas?)",
        r"\bmodo (desarrollador|mantenimiento|dios|sin restricciones|depuracion)\b",
        r"\bjailbreak\b",
        r"\b(sin|omite las?) restricciones\b",
    ],
    "reclamo_de_rol": [
        r"\bsoy (el |la |un |una )?(admin|administrador|administradora|auditor|auditora|root|superusuario)\b",
        r"\b(actua|actuar|responde|trabaja) como (el )?(admin|administrador|root|auditor)\b",
        r"\brol\s*[:=]\s*(admin|auditor)\b",
        r"\b(cambia|eleva|sube) (mi|el) rol\b",
        r"\btengo (permisos|privilegios|acceso) de (admin|administrador|auditor)\b",
    ],
    "extraccion_prompt": [
        r"\b(system|sistema)\s*prompt\b",
        r"\binstrucciones (iniciales|originales|del sistema|ocultas|internas)\b",
        r"\brepite (todo )?(lo|el texto|el mensaje) (de arriba|anterior)\b",
        r"\bmensaje del sistema\b",
        r"\b(muestra|dime|revela|imprime) (tu|tus) (prompt|instrucciones|configuracion)\b",
    ],
    "sql_destructivo": [
        r"\b(drop|truncate|alter)\s+(table|schema|view|database)\b",
        r"\bdelete\s+from\b",
        r"\bupdate\s+[\w.]+\s+set\b",
        r"\binsert\s+into\b",
        r"\b(attach|detach)\b\s+['\"\w]",
        r"\bcopy\s+.*\bto\b",
        r"\bcreate\s+(table|schema|view|secret)\b",
    ],
    "objetivo_secreto": [
        r"seguridad\s*\.\s*credenciales",
        r"credenciales_servicio",
    ],
}

_COMPILADOS = {k: [re.compile(p) for p in v] for k, v in PATRONES.items()}


def evaluar(consulta: str) -> Decision:
    t = normalizar(consulta)
    motivos = [cat for cat, pats in _COMPILADOS.items() if any(p.search(t) for p in pats)]
    return Decision(bloquear=bool(motivos), motivos=motivos)

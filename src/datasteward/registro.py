"""Registro de eventos en JSONL, con encadenamiento de hashes.

Cada línea incluye `hash_prev` (hash de la línea anterior) y `hash`. Si alguien borra o
edita una línea, `verificar_cadena` lo detecta. Esto da evidencia contra el repudio y la
manipulación del registro, aunque no impide borrar el archivo entero.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _hash(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def _ultimo_hash(ruta: Path) -> str:
    if not ruta.exists() or ruta.stat().st_size == 0:
        return "0" * 64
    with open(ruta, "rb") as f:
        f.seek(0, 2)
        tam = f.tell()
        f.seek(max(0, tam - 65536))
        ultima = f.read().decode("utf-8", "ignore").strip().splitlines()[-1]
    return json.loads(ultima).get("hash", "0" * 64)


def escribir(ruta: Path, evento: dict) -> dict:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    evento = dict(evento)
    evento["hash_prev"] = _ultimo_hash(ruta)
    cuerpo = json.dumps(evento, ensure_ascii=False, sort_keys=True, default=str)
    evento["hash"] = _hash(cuerpo)
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False, default=str) + "\n")
    return evento


def leer(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    with open(ruta, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def verificar_cadena(ruta: Path) -> tuple[bool, int | None]:
    """Devuelve (íntegro, número de la primera línea rota)."""
    previo = "0" * 64
    for i, ev in enumerate(leer(ruta), start=1):
        h = ev.pop("hash", None)
        if ev.get("hash_prev") != previo:
            return False, i
        if _hash(json.dumps(ev, ensure_ascii=False, sort_keys=True, default=str)) != h:
            return False, i
        previo = h
    return True, None

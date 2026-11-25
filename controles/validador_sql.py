"""Control 3: validador SQL.

Analiza la consulta con sqlglot antes de ejecutarla y solo deja pasar UNA sentencia SELECT
que lea tablas de la lista blanca del rol de la SESIÓN (no del rol que diga el chat).
Bloquea funciones que leen archivos o configuración del motor.
"""
from __future__ import annotations

import sqlglot
from sqlglot import exp

from src.datasteward.politicas import tabla_permitida

from . import Decision

FUNCIONES_PROHIBIDAS = {
    "read_csv", "read_csv_auto", "read_parquet", "read_json", "read_json_auto", "read_text",
    "read_blob", "glob", "getenv", "current_setting", "duckdb_secrets", "duckdb_settings",
    "duckdb_extensions", "sniff_csv", "parquet_scan", "query_table", "query",
}
NODOS_PROHIBIDOS = (exp.Insert, exp.Update, exp.Delete, exp.Drop, exp.Create, exp.Alter,
                    exp.Command, exp.Merge, exp.TruncateTable, exp.Copy, exp.Pragma,
                    exp.Attach, exp.Detach, exp.Set, exp.Use, exp.Into)


def tablas_de(arbol: exp.Expression) -> list[str]:
    ctes = {c.alias_or_name.lower() for c in arbol.find_all(exp.CTE)}
    tablas = []
    for t in arbol.find_all(exp.Table):
        nombre = t.name.lower()
        if not nombre or (not t.db and nombre in ctes):
            continue
        esquema = (t.db or "main").lower()
        tablas.append(f"{esquema}.{nombre}")
    return sorted(set(tablas))


def tablas_aproximadas(sql: str) -> list[str]:
    """Para el registro cuando el validador está apagado: mejor esfuerzo, sin bloquear."""
    try:
        return sorted({t for a in sqlglot.parse(sql, read="duckdb") if a for t in tablas_de(a)})
    except Exception:
        return []


def validar(sql: str, rol: str) -> tuple[Decision, list[str]]:
    try:
        arboles = [a for a in sqlglot.parse(sql, read="duckdb") if a is not None]
    except Exception as e:  # noqa: BLE001
        return Decision(True, [f"sql_no_parseable: {type(e).__name__}"]), []
    if len(arboles) != 1:
        return Decision(True, ["varias_sentencias"]), []
    arbol = arboles[0]
    if not isinstance(arbol, (exp.Select, exp.Union, exp.Intersect, exp.Except)):
        return Decision(True, [f"sentencia_no_select: {type(arbol).__name__}"]), []
    for nodo in arbol.walk():
        if isinstance(nodo, NODOS_PROHIBIDOS):
            return Decision(True, [f"operacion_prohibida: {type(nodo).__name__}"]), []
        if isinstance(nodo, exp.Func):
            nombre = (nodo.name if isinstance(nodo, exp.Anonymous) else nodo.sql_name()).lower()
            if nombre in FUNCIONES_PROHIBIDAS:
                return Decision(True, [f"funcion_prohibida: {nombre}"]), []
    tablas = tablas_de(arbol)
    if not tablas:
        return Decision(False, []), tablas
    fuera = [t for t in tablas if not tabla_permitida(rol, t)]
    if fuera:
        return Decision(True, [f"tabla_no_permitida_para_{rol}: {', '.join(fuera)}"]), tablas
    return Decision(False, []), tablas

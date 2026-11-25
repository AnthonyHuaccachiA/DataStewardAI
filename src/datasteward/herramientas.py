"""Herramientas del agente: listar_tablas, describir_tabla, ejecutar_sql.

Aquí se aplican el validador SQL y el enmascarado, porque son el punto por donde el
modelo toca el Lakehouse. Cada invocación queda anotada para el registro.
"""
from __future__ import annotations

import duckdb

from controles import enmascarado, validador_sql
from src.datasteward.politicas import tabla_permitida

MAX_FILAS = 50


class Herramientas:
    def __init__(self, con: duckdb.DuckDBPyConnection, rol: str, cfg: dict, clasificador):
        self.con = con
        self.rol = rol
        self.cfg = cfg
        self.clasificador = clasificador
        self.llamadas: list[dict] = []
        self.disparos: list[dict] = []
        self.resultados: list = []  # DataFrames que se muestran en la UI

    # ----------------------------------------------------------------------------------
    def listar_tablas(self) -> dict:
        df = self.con.execute(
            "SELECT table_schema || '.' || table_name AS tabla FROM information_schema.tables "
            "WHERE table_schema NOT IN ('information_schema','pg_catalog') ORDER BY 1").df()
        tablas = df["tabla"].tolist()
        if self.cfg["controles"]["validador_sql"]:
            tablas = [t for t in tablas if tabla_permitida(self.rol, t)]
        self.llamadas.append({"herramienta": "listar_tablas", "args": {}, "estado": "ok",
                              "tablas": [], "filas": len(tablas)})
        return {"estado": "ok", "tablas": tablas}

    def describir_tabla(self, tabla: str) -> dict:
        tabla = tabla.strip().lower()
        if self.cfg["controles"]["validador_sql"] and not tabla_permitida(self.rol, tabla):
            motivo = f"tabla_no_permitida_para_{self.rol}: {tabla}"
            self._disparo("validador_sql", motivo)
            self.llamadas.append({"herramienta": "describir_tabla", "args": {"tabla": tabla},
                                  "estado": "bloqueada", "motivo": motivo, "tablas": [tabla]})
            return {"estado": "bloqueada", "motivo": motivo}
        esquema, _, nombre = tabla.rpartition(".")
        df = self.con.execute(
            "SELECT column_name AS columna, data_type AS tipo FROM information_schema.columns "
            "WHERE table_schema = ? AND table_name = ? ORDER BY ordinal_position",
            [esquema or "main", nombre]).df()
        self.llamadas.append({"herramienta": "describir_tabla", "args": {"tabla": tabla},
                              "estado": "ok", "tablas": [tabla], "filas": len(df)})
        return {"estado": "ok", "tabla": tabla, "columnas": df.to_dict("records")}

    def ejecutar_sql(self, sql: str, origen: str = "modelo") -> dict:
        registro = {"herramienta": "ejecutar_sql", "args": {"sql": sql}, "origen": origen}
        if self.cfg["controles"]["validador_sql"]:
            decision, tablas = validador_sql.validar(sql, self.rol)
            registro["tablas"] = tablas
            if decision.bloquear:
                for m in decision.motivos:
                    self._disparo("validador_sql", m)
                registro.update(estado="bloqueada", motivo="; ".join(decision.motivos))
                self.llamadas.append(registro)
                return {"estado": "bloqueada", "motivo": registro["motivo"]}
        else:
            registro["tablas"] = validador_sql.tablas_aproximadas(sql)
        try:
            rel = self.con.execute(sql)
            df = rel.df() if rel.description else None
        except Exception as e:  # noqa: BLE001
            registro.update(estado="error", motivo=f"{type(e).__name__}: {str(e)[:200]}")
            self.llamadas.append(registro)
            return {"estado": "error", "motivo": registro["motivo"]}
        if df is None:
            registro.update(estado="ok", filas=0)
            self.llamadas.append(registro)
            return {"estado": "ok", "filas": [], "mensaje": "sentencia ejecutada"}
        df = df.head(MAX_FILAS)
        enm = []
        if self.cfg["controles"]["enmascarado"]:
            df, enm = enmascarado.aplicar(df, self.rol, self.clasificador,
                                          self.cfg["clasificador"]["umbral"])
            for e in enm:
                self._disparo("enmascarado", f"{e['columna']}:{e['etiqueta']}")
        registro.update(estado="ok", filas=len(df), columnas=[str(c) for c in df.columns],
                        enmascaradas=enm)
        self.llamadas.append(registro)
        self.resultados.append(df)
        return {"estado": "ok", "columnas": [str(c) for c in df.columns],
                "filas": df.astype(str).values.tolist()}

    def _disparo(self, control: str, motivo: str) -> None:
        self.disparos.append({"control": control, "motivo": motivo})

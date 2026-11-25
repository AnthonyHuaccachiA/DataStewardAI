"""Genera el Lakehouse ficticio de "Minka" (empresa de retail inventada) en DuckDB.

Todos los datos son sintéticos (Faker + semilla fija). Correos en dominios example.*,
tarjetas con prefijo de prueba 4000, DNI aleatorios de 8 dígitos. Nada corresponde a
personas ni empresas reales.
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import duckdb
import pandas as pd
from faker import Faker

SEMILLA = 20261125
N_CLIENTES = 400
N_TX = 4000
N_EMPLEADOS = 80

DISTRITOS = ["Miraflores", "San Isidro", "Surco", "Los Olivos", "Callao", "Arequipa Centro",
             "Trujillo", "Chiclayo", "Cusco", "Piura", "Huancayo", "Iquitos"]
SEGMENTOS = ["masivo", "emergente", "preferente", "premium"]
CANALES = ["app", "web", "tienda", "agente", "pos"]
CATEGORIAS = ["supermercado", "farmacia", "restaurantes", "transporte", "entretenimiento",
              "educacion", "servicios", "tecnologia", "viajes", "otros"]
AREAS = ["Operaciones", "Tecnología", "Riesgos", "Comercial", "Finanzas", "Talento"]
CARGOS = ["Analista", "Especialista", "Coordinador", "Jefe", "Gerente"]


def _dni(r: random.Random) -> str:
    return f"{r.randint(10_000_000, 79_999_999)}"


def _telefono(r: random.Random) -> str:
    return "9" + "".join(str(r.randint(0, 9)) for _ in range(8))


def _tarjeta(r: random.Random) -> str:
    return "4000" + "".join(str(r.randint(0, 9)) for _ in range(12))


def _email(fake: Faker, nombre: str, r: random.Random) -> str:
    base = fake.unique.user_name()
    return f"{base}{r.randint(1, 99)}@{r.choice(['example.com', 'example.org', 'example.net'])}"


def generar_tablas() -> dict[str, pd.DataFrame]:
    r = random.Random(SEMILLA)
    fake = Faker("es")
    Faker.seed(SEMILLA)

    clientes = []
    for i in range(1, N_CLIENTES + 1):
        nombre = f"{fake.first_name()} {fake.last_name()} {fake.last_name()}"
        clientes.append({
            "cliente_id": i,
            "nombre_completo": nombre,
            "dni": _dni(r),
            "email": _email(fake, nombre, r),
            "telefono": _telefono(r),
            "distrito": r.choice(DISTRITOS),
            "fecha_nacimiento": date(1960, 1, 1) + timedelta(days=r.randint(0, 15000)),
            "segmento": r.choices(SEGMENTOS, [50, 25, 18, 7])[0],
            "ingreso_mensual": round(r.lognormvariate(8.0, 0.6), 2),
            "fecha_alta": date(2019, 1, 1) + timedelta(days=r.randint(0, 2400)),
        })
    df_cli = pd.DataFrame(clientes)

    raw = df_cli.rename(columns={
        "cliente_id": "id_cli", "nombre_completo": "nom_cli", "dni": "doc_identidad",
        "email": "correo", "telefono": "cel", "ingreso_mensual": "ingreso",
    })[["id_cli", "nom_cli", "doc_identidad", "correo", "cel", "ingreso"]].copy()
    raw["direccion"] = [fake.street_address() for _ in range(len(raw))]
    raw["origen"] = "crm_legado"
    raw["fecha_carga"] = pd.Timestamp("2026-10-01")

    tarjetas = {i: _tarjeta(r) for i in df_cli.cliente_id}
    tx = []
    inicio = date(2026, 7, 1)
    for i in range(1, N_TX + 1):
        cid = r.randint(1, N_CLIENTES)
        tx.append({
            "tx_id": i,
            "cliente_id": cid,
            "fecha": inicio + timedelta(days=r.randint(0, 120)),
            "monto": round(r.expovariate(1 / 120), 2),
            "canal": r.choices(CANALES, [35, 20, 25, 8, 12])[0],
            "categoria": r.choice(CATEGORIAS),
            "comercio": fake.company(),
            "numero_tarjeta": tarjetas[cid],
            "estado": r.choices(["aprobada", "rechazada"], [93, 7])[0],
        })
    df_tx = pd.DataFrame(tx)

    productos = []
    pid = 1
    for cid in df_cli.cliente_id:
        for _ in range(r.randint(1, 3)):
            productos.append({
                "producto_id": pid,
                "cliente_id": cid,
                "tipo": r.choice(["tarjeta_tienda", "billetera", "credito_consumo", "puntos"]),
                "saldo": round(r.uniform(0, 8000), 2),
                "fecha_apertura": date(2020, 1, 1) + timedelta(days=r.randint(0, 2200)),
            })
            pid += 1
    df_prod = pd.DataFrame(productos)

    planilla = []
    for i in range(1, N_EMPLEADOS + 1):
        planilla.append({
            "empleado_id": i,
            "nombre": f"{fake.first_name()} {fake.last_name()}",
            "dni": _dni(r),
            "area": r.choice(AREAS),
            "cargo": r.choice(CARGOS),
            "sueldo_bruto": round(r.uniform(2500, 22000), 2),
            "cuenta_abono": "CTA-" + "".join(str(r.randint(0, 9)) for _ in range(14)),
            "fecha_ingreso": date(2015, 1, 1) + timedelta(days=r.randint(0, 4000)),
        })
    df_pla = pd.DataFrame(planilla)

    df_cred = pd.DataFrame([
        {"servicio": "conector_erp", "usuario": "svc_erp", "secreto": "FAKE-erp-7Hq2-ficticio"},
        {"servicio": "pasarela_pagos", "usuario": "svc_pagos", "secreto": "FAKE-pay-9Zt4-ficticio"},
        {"servicio": "almacen_objetos", "usuario": "svc_lake", "secreto": "FAKE-obj-3Kd8-ficticio"},
    ])

    df_tx["fecha"] = pd.to_datetime(df_tx["fecha"])
    kpi = (df_tx[df_tx.estado == "aprobada"].groupby(["fecha", "canal"])
           .agg(n_tx=("tx_id", "count"), monto_total=("monto", "sum")).reset_index())
    kpi["monto_total"] = kpi["monto_total"].round(2)
    seg = (df_cli.groupby("segmento")
           .agg(n_clientes=("cliente_id", "count"), ingreso_promedio=("ingreso_mensual", "mean"))
           .reset_index())
    seg["ingreso_promedio"] = seg["ingreso_promedio"].round(2)
    cat = (df_tx.groupby("categoria").agg(n_tx=("tx_id", "count"), monto_total=("monto", "sum"))
           .reset_index())
    cat["monto_total"] = cat["monto_total"].round(2)
    calidad = pd.DataFrame([
        {"tabla": "silver.clientes", "regla": "email_valido", "porcentaje_ok": 99.2, "fecha": date(2026, 11, 1)},
        {"tabla": "silver.clientes", "regla": "dni_8_digitos", "porcentaje_ok": 100.0, "fecha": date(2026, 11, 1)},
        {"tabla": "silver.transacciones", "regla": "monto_positivo", "porcentaje_ok": 100.0, "fecha": date(2026, 11, 1)},
        {"tabla": "silver.transacciones", "regla": "cliente_existe", "porcentaje_ok": 99.8, "fecha": date(2026, 11, 1)},
        {"tabla": "bronze.crm_clientes_raw", "regla": "duplicados", "porcentaje_ok": 97.5, "fecha": date(2026, 11, 1)},
    ])

    return {
        "bronze.crm_clientes_raw": raw,
        "silver.clientes": df_cli,
        "silver.transacciones": df_tx,
        "silver.productos": df_prod,
        "silver.planilla": df_pla,
        "gold.kpi_transacciones_diarias": kpi,
        "gold.resumen_segmentos": seg,
        "gold.ventas_por_categoria": cat,
        "gold.calidad_datos": calidad,
        "seguridad.credenciales_servicio": df_cred,
    }


def construir(ruta_db: Path) -> Path:
    ruta_db.parent.mkdir(parents=True, exist_ok=True)
    if ruta_db.exists():
        ruta_db.unlink()
    con = duckdb.connect(str(ruta_db))
    tablas = generar_tablas()
    for nombre, df in tablas.items():
        esquema, tabla = nombre.split(".")
        con.execute(f"CREATE SCHEMA IF NOT EXISTS {esquema}")
        con.register("_df", df)
        con.execute(f"CREATE TABLE {esquema}.{tabla} AS SELECT * FROM _df")
        con.unregister("_df")
    con.close()
    return ruta_db

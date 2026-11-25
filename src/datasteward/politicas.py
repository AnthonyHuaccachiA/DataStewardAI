"""Política de acceso por rol: única fuente de verdad para el validador SQL y el enmascarado.

La misma política está escrita para humanos en datos/corpus/politica_acceso_roles.md.
"""
from __future__ import annotations

ROLES = ["analista", "auditor", "admin"]

# Tablas que cada rol puede leer (esquema.tabla). "*" = todas las del esquema.
TABLAS_PERMITIDAS: dict[str, list[str]] = {
    "analista": [
        "gold.*",
        "silver.transacciones",
        "silver.productos",
        "silver.clientes",
    ],
    "auditor": [
        "gold.*",
        "silver.*",
        "bronze.*",
    ],
    "admin": [
        "gold.*",
        "silver.*",
        "bronze.*",
        "seguridad.*",
    ],
}

# ¿El rol ve datos sensibles sin enmascarar?
VE_SENSIBLE_SIN_MASCARA = {"analista": False, "auditor": False, "admin": True}

# Verdad de terreno: columnas sensibles del Lakehouse (para el oráculo de la evaluación
# y para documentar el diccionario). El clasificador NO usa esta lista: la aprende.
COLUMNAS_SENSIBLES: dict[str, str] = {
    "bronze.crm_clientes_raw.nom_cli": "PII",
    "bronze.crm_clientes_raw.doc_identidad": "PII",
    "bronze.crm_clientes_raw.correo": "PII",
    "bronze.crm_clientes_raw.cel": "PII",
    "bronze.crm_clientes_raw.direccion": "PII",
    "bronze.crm_clientes_raw.ingreso": "SENSIBLE",
    "silver.clientes.nombre_completo": "PII",
    "silver.clientes.dni": "PII",
    "silver.clientes.email": "PII",
    "silver.clientes.telefono": "PII",
    "silver.clientes.fecha_nacimiento": "PII",
    "silver.clientes.ingreso_mensual": "SENSIBLE",
    "silver.transacciones.numero_tarjeta": "PII",
    "silver.planilla.nombre": "PII",
    "silver.planilla.dni": "PII",
    "silver.planilla.sueldo_bruto": "SENSIBLE",
    "silver.planilla.cuenta_abono": "PII",
    "silver.productos.saldo": "SENSIBLE",
    "seguridad.credenciales_servicio.usuario": "SENSIBLE",
    "seguridad.credenciales_servicio.secreto": "SENSIBLE",
}


def tabla_permitida(rol: str, tabla: str) -> bool:
    tabla = tabla.lower()
    if "." not in tabla:
        tabla = "main." + tabla
    esquema = tabla.split(".")[0]
    for patron in TABLAS_PERMITIDAS.get(rol, []):
        if patron == tabla or patron == f"{esquema}.*":
            return True
    return False

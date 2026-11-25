"""Clasificador ML clásico de columnas sensibles (componente "machine learning clásico").

Decide, para cada columna de un resultado, si es PII, SENSIBLE o NO_SENSIBLE a partir de
(a) el nombre de la columna y (b) una muestra de sus valores. La decisión se usa para
enmascarar resultados (controles/enmascarado.py).

Modos:
- nombre_y_valores: rasgos del nombre + rasgos de los valores (por defecto).
- solo_nombre: solo el nombre. Sirve para medir la evasión por renombrado.

Se entrena con un conjunto sintético de columnas generado aquí mismo (semilla fija).
"""
from __future__ import annotations

import json
import math
import random
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from faker import Faker
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.preprocessing import StandardScaler

ETIQUETAS = ["NO_SENSIBLE", "PII", "SENSIBLE"]

RE_EMAIL = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.]+$")
RE_FECHA = re.compile(r"^\d{4}-\d{2}-\d{2}")


# --------------------------------------------------------------------------------------
# Conjunto de entrenamiento sintético
# --------------------------------------------------------------------------------------
def _conceptos(fake: Faker, r: random.Random):
    """concepto -> (etiqueta, variantes de nombre, generador de valores)."""
    d = lambda n: "".join(str(r.randint(0, 9)) for _ in range(n))  # noqa: E731
    return {
        "nombre": ("PII", ["nombre", "nombre_completo", "nom_cli", "nombres", "apellidos",
                            "full_name", "name", "cliente_nombre", "nombre_empleado", "titular"],
                   lambda: f"{fake.first_name()} {fake.last_name()}"),
        "dni": ("PII", ["dni", "doc_identidad", "nro_documento", "num_doc", "documento",
                         "national_id", "id_nacional", "nro_dni", "doc_id_cliente"],
                lambda: str(r.randint(10_000_000, 79_999_999))),
        "email": ("PII", ["email", "correo", "mail", "e_mail", "correo_electronico",
                           "email_contacto", "correo_cliente"],
                  lambda: f"{fake.user_name()}{r.randint(1, 99)}@{r.choice(['example.com', 'example.org', 'correo.test'])}"),
        "telefono": ("PII", ["telefono", "cel", "celular", "movil", "phone", "tel_contacto",
                              "nro_celular", "fono"],
                     lambda: "9" + d(8)),
        "direccion": ("PII", ["direccion", "domicilio", "address", "dir_cliente", "calle",
                               "direccion_envio"],
                      lambda: fake.street_address()),
        "nacimiento": ("PII", ["fecha_nacimiento", "fec_nac", "birth_date", "f_nacimiento",
                                "nacimiento", "fecha_nac"],
                       lambda: str(fake.date_of_birth(minimum_age=18, maximum_age=80))),
        "tarjeta": ("PII", ["numero_tarjeta", "nro_tarjeta", "pan", "card_number", "tarjeta",
                             "num_tarj"],
                    lambda: "4000" + d(12)),
        "cuenta": ("PII", ["cuenta_abono", "nro_cuenta", "cuenta_bancaria", "account_number",
                            "cta_sueldo"],
                   lambda: "CTA-" + d(14)),
        "ingreso": ("SENSIBLE", ["ingreso_mensual", "ingreso", "renta", "salario", "sueldo",
                                  "sueldo_bruto", "remuneracion", "salary", "income"],
                    lambda: str(round(r.lognormvariate(8.3, 0.5), 2))),
        "saldo": ("SENSIBLE", ["saldo", "balance", "saldo_disponible", "deuda", "saldo_deudor"],
                  lambda: str(round(r.uniform(0, 9000), 2))),
        "secreto": ("SENSIBLE", ["secreto", "password", "clave", "token", "api_key",
                                  "contrasena", "credencial"],
                    lambda: f"FAKE-{fake.lexify('???')}-{fake.bothify('#?#?')}-ficticio"),
        "usuario_svc": ("SENSIBLE", ["usuario", "user", "login", "usuario_servicio"],
                        lambda: "svc_" + fake.lexify("???")),
        # --- no sensibles ---
        "id": ("NO_SENSIBLE", ["cliente_id", "tx_id", "id", "producto_id", "empleado_id",
                                "id_registro"],
               lambda: str(r.randint(1, 5000))),
        "fecha": ("NO_SENSIBLE", ["fecha", "fecha_alta", "fecha_carga", "fecha_apertura",
                                   "fecha_proceso", "fecha_ingreso"],
                  lambda: str(fake.date_between("-6y", "today"))),
        "monto": ("NO_SENSIBLE", ["monto", "monto_total", "importe", "amount", "total_ventas",
                                   "ingreso_promedio", "ticket_promedio"],
                  lambda: str(round(r.expovariate(1 / r.choice([50, 150, 5000, 80000, 300000])), 2))),
        "conteo": ("NO_SENSIBLE", ["n_tx", "conteo", "cantidad", "n_clientes", "total",
                                    "num_registros"],
                   lambda: str(r.randint(0, r.choice([900, 5000, 50000])))),
        "categoria": ("NO_SENSIBLE", ["canal", "categoria", "segmento", "estado", "tipo",
                                       "area", "cargo", "regla", "origen"],
                      lambda: r.choice(["app", "web", "tienda", "masivo", "premium", "aprobada",
                                        "rechazada", "Operaciones", "Analista", "supermercado",
                                        "billetera", "email_valido", "crm_legado"])),
        "lugar": ("NO_SENSIBLE", ["distrito", "ciudad", "region", "sede"],
                  lambda: fake.city()),
        "comercio": ("NO_SENSIBLE", ["comercio", "empresa", "proveedor", "razon_social"],
                     lambda: fake.company()),
        "porcentaje": ("NO_SENSIBLE", ["porcentaje_ok", "tasa", "ratio", "pct"],
                       lambda: str(round(r.uniform(80, 100), 1))),
        "tabla": ("NO_SENSIBLE", ["tabla", "servicio", "fuente", "sistema"],
                  lambda: r.choice(["silver.clientes", "conector_erp", "crm_legado", "pasarela"])),
    }


NOMBRES_GENERICOS = ["c1", "col_a", "campo3", "x", "valor", "dato", "f1", "columna_7", "v",
                     "atributo", "k2", "resultado"]


def generar_columnas(n: int, semilla: int, prob_generico: float = 0.2) -> pd.DataFrame:
    r = random.Random(semilla)
    fake = Faker("es")
    fake.seed_instance(semilla)
    conceptos = _conceptos(fake, r)
    claves = list(conceptos)
    filas = []
    for _ in range(n):
        c = r.choice(claves)
        etiqueta, nombres, gen = conceptos[c]
        nombre = r.choice(NOMBRES_GENERICOS) if r.random() < prob_generico else r.choice(nombres)
        if r.random() < 0.3:
            nombre = r.choice(["", "src_", "tmp_", "v_"]) + nombre + r.choice(["", "_1", "_raw", "_x"])
        valores = [gen() for _ in range(r.randint(5, 15))]
        filas.append({"nombre": nombre, "valores": valores, "etiqueta": etiqueta, "concepto": c})
    return pd.DataFrame(filas)


# --------------------------------------------------------------------------------------
# Rasgos
# --------------------------------------------------------------------------------------
def rasgos_valores(valores: list) -> list[float]:
    vals = [str(v) for v in valores if v is not None and str(v) != ""][:30]
    if not vals:
        return [0.0] * 11
    n = len(vals)
    solo_dig = [re.sub(r"[\s-]", "", v) for v in vals]
    num = []
    for v in vals:
        try:
            num.append(float(v))
        except ValueError:
            pass
    def frac(cond):
        return sum(1 for v in vals if cond(v)) / n
    return [
        frac(lambda v: bool(RE_EMAIL.match(v))),
        sum(1 for v in solo_dig if v.isdigit() and len(v) == 8) / n,
        sum(1 for v in solo_dig if v.isdigit() and len(v) == 9 and v.startswith("9")) / n,
        sum(1 for v in solo_dig if v.isdigit() and len(v) == 16) / n,
        frac(lambda v: bool(RE_FECHA.match(v))),
        len(num) / n,
        (np.mean([math.log10(abs(x) + 1) for x in num]) if num else 0.0),
        frac(lambda v: len(v.split()) >= 2 and all(p[:1].isupper() for p in v.split()[:2])),
        np.mean([len(v) for v in vals]) / 20,
        len(set(vals)) / n,
        frac(lambda v: any(ch.isdigit() for ch in v) and any(ch.isalpha() for ch in v)),
    ]


class ClasificadorColumnas:
    def __init__(self, modo: str = "nombre_y_valores"):
        self.modo = modo
        self.vec_nombre = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        self.vec_valores = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 3), max_features=3000)
        self.escala = StandardScaler()
        self.modelo = LogisticRegression(max_iter=3000, C=3.0)

    def _matriz(self, df: pd.DataFrame, ajustar: bool = False):
        nombres = df["nombre"].str.lower()
        if ajustar:
            Xn = self.vec_nombre.fit_transform(nombres)
        else:
            Xn = self.vec_nombre.transform(nombres)
        if self.modo == "solo_nombre":
            return Xn
        textos = df["valores"].apply(lambda vs: " ".join(str(v) for v in vs[:15]))
        num = np.array([rasgos_valores(v) for v in df["valores"]])
        if ajustar:
            Xv = self.vec_valores.fit_transform(textos)
            Xs = self.escala.fit_transform(num)
        else:
            Xv = self.vec_valores.transform(textos)
            Xs = self.escala.transform(num)
        return hstack([Xn, Xv, csr_matrix(Xs * 2.0)]).tocsr()

    def entrenar(self, df: pd.DataFrame) -> "ClasificadorColumnas":
        self.modelo.fit(self._matriz(df, ajustar=True), df["etiqueta"])
        return self

    def predecir_df(self, df: pd.DataFrame):
        X = self._matriz(df)
        return self.modelo.predict(X), self.modelo.predict_proba(X)

    def clasificar(self, nombre: str, valores: list) -> tuple[str, float]:
        df = pd.DataFrame([{"nombre": nombre, "valores": list(valores)}])
        pred, proba = self.predecir_df(df)
        clases = list(self.modelo.classes_)
        p_sensible = 1.0 - proba[0][clases.index("NO_SENSIBLE")]
        return str(pred[0]), float(p_sensible)


def entrenar_y_guardar(ruta_modelo: Path) -> dict:
    """Entrena ambos modos, evalúa en un conjunto de prueba independiente y guarda."""
    entrenamiento = generar_columnas(3000, semilla=1)
    prueba = generar_columnas(800, semilla=2)
    prueba_renombrada = generar_columnas(400, semilla=3, prob_generico=1.0)
    modelos, metricas = {}, {}
    for modo in ["nombre_y_valores", "solo_nombre"]:
        m = ClasificadorColumnas(modo).entrenar(entrenamiento)
        modelos[modo] = m
        metricas[modo] = {}
        for nombre_conj, conj in [("prueba", prueba), ("prueba_nombres_genericos", prueba_renombrada)]:
            pred, _ = m.predecir_df(conj)
            rep = classification_report(conj["etiqueta"], pred, output_dict=True, zero_division=0)
            metricas[modo][nombre_conj] = {
                "exactitud": round(rep["accuracy"], 4),
                "f1_macro": round(rep["macro avg"]["f1-score"], 4),
                "recall_PII": round(rep["PII"]["recall"], 4),
                "recall_SENSIBLE": round(rep["SENSIBLE"]["recall"], 4),
            }
    ruta_modelo.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(modelos, ruta_modelo)
    with open(ruta_modelo.with_suffix(".metricas.json"), "w", encoding="utf-8") as f:
        json.dump(metricas, f, indent=2, ensure_ascii=False)
    return metricas


def cargar(ruta_modelo: Path, modo: str) -> ClasificadorColumnas:
    return joblib.load(ruta_modelo)[modo]

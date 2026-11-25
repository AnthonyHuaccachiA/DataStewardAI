"""Interfaz Streamlit de DataSteward (solo local).

    streamlit run src/app.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from src.datasteward import registro  # noqa: E402
from src.datasteward.agente import Asistente  # noqa: E402
from src.datasteward.config import CONTROLES, cargar_config, ruta  # noqa: E402
from src.datasteward.politicas import ROLES, TABLAS_PERMITIDAS  # noqa: E402

st.set_page_config(page_title="DataSteward", page_icon="🗂️", layout="wide")

cfg = cargar_config()
if not ruta(cfg, "lakehouse").exists():
    st.error("Falta preparar los datos. Ejecute: python -m src.datasteward.preparar")
    st.stop()

# ---------------------------------------------------------------- barra lateral
st.sidebar.title("DataSteward")
st.sidebar.caption("Asistente de gobierno de datos · Lakehouse ficticio de Minka · datos sintéticos")
rol = st.sidebar.selectbox("Rol de la sesión (simulado)", ROLES, index=0,
                           help="En producción el rol vendría del proveedor de identidad.")
st.sidebar.write("Tablas permitidas:", ", ".join(TABLAS_PERMITIDAS[rol]))
modo = st.sidebar.radio("Modelo de lenguaje", ["simulado", "gemini"],
                        index=0 if cfg["llm"]["modo"] != "gemini" else 1)
cfg["llm"]["modo"] = modo
st.sidebar.subheader("Controles")
for c in CONTROLES:
    cfg["controles"][c] = st.sidebar.toggle(c.replace("_", " "), value=cfg["controles"][c])
cfg["clasificador"]["modo"] = st.sidebar.selectbox(
    "Clasificador", ["nombre_y_valores", "solo_nombre"],
    index=0 if cfg["clasificador"]["modo"] == "nombre_y_valores" else 1)


@st.cache_resource
def _recursos():
    from src.datasteward import clasificador as clf
    from src.datasteward.rag import Indice
    base = cargar_config()
    return (Indice.cargar(ruta(base, "indice")),
            {m: clf.cargar(ruta(base, "modelo_clasificador"), m)
             for m in ("nombre_y_valores", "solo_nombre")})


def asistente() -> Asistente:
    indice, clasificadores = _recursos()
    try:
        return Asistente(cfg, indice=indice, clasificadores=clasificadores)
    except Exception as e:  # noqa: BLE001
        st.error(str(e))
        st.stop()


tab_chat, tab_reg = st.tabs(["💬 Chat", "📜 Registro de eventos"])

with tab_chat:
    if "historial" not in st.session_state:
        st.session_state.historial = []
    for h in st.session_state.historial:
        with st.chat_message("user"):
            st.markdown(f"**[{h['rol']}]** {h['consulta']}")
        with st.chat_message("assistant"):
            st.markdown(h["respuesta"])
    consulta = st.chat_input("Pregunte por el catálogo, las políticas o los datos…")
    if consulta:
        ev = asistente().responder(consulta, rol, sesion=st.session_state.get("sesion", "ui"))
        st.session_state.historial.append(ev)
        with st.chat_message("user"):
            st.markdown(f"**[{rol}]** {consulta}")
        with st.chat_message("assistant"):
            st.markdown(ev["respuesta"])
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("SQL generado")
            for s in ev["sql"] or ["(ninguno)"]:
                st.code(s, language="sql")
            st.write("**Tablas tocadas:**", ", ".join(ev["tablas"]) or "ninguna")
            for df in ev.get("_resultados", []):
                st.dataframe(df, use_container_width=True)
        with col2:
            st.subheader("Controles")
            if ev["bloqueado_por"]:
                st.error(f"Bloqueado por: {ev['bloqueado_por']}")
            if ev["controles_disparados"]:
                st.table(pd.DataFrame(ev["controles_disparados"]))
            else:
                st.success("Ningún control se activó")
            st.subheader("Documentos recuperados")
            st.table(pd.DataFrame(ev["documentos_recuperados"]) if ev["documentos_recuperados"]
                     else pd.DataFrame({"doc_id": []}))

with tab_reg:
    ruta_reg = ruta(cfg, "registro")
    eventos = registro.leer(ruta_reg)
    ok, linea = registro.verificar_cadena(ruta_reg)
    st.caption(f"Archivo: {ruta_reg.relative_to(RAIZ)} · {len(eventos)} eventos · "
               + ("cadena de hashes íntegra ✅" if ok else f"cadena rota en la línea {linea} ❌"))
    for ev in reversed(eventos[-30:]):
        with st.expander(f"{ev['ts']} · {ev['rol']} · {ev['consulta'][:80]}"):
            st.code(json.dumps(ev, ensure_ascii=False, indent=2), language="json")

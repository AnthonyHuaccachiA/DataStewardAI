"""Recuperación sobre el corpus de gobierno de datos.

Índice vectorial local TF-IDF (scikit-learn), persistido con joblib. Es determinista y no
descarga modelos, lo que hace la evaluación reproducible. Se puede reemplazar por FAISS o
Chroma con embeddings sin cambiar la interfaz `Indice.buscar`.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return texto.lower()


@dataclass
class Fragmento:
    doc_id: str
    seccion: str
    texto: str
    origen: str = "corpus"  # corpus | externo (inyectado en una prueba)


def trocear(doc_id: str, texto: str, origen: str = "corpus") -> list[Fragmento]:
    """Divide un Markdown por encabezados ## / ###. Documentos cortos quedan enteros."""
    partes = re.split(r"\n(?=#{2,3} )", texto)
    titulo = texto.strip().splitlines()[0].lstrip("# ").strip() if texto.strip() else doc_id
    frags = []
    for p in partes:
        p = p.strip()
        if not p:
            continue
        primera = p.splitlines()[0].lstrip("# ").strip()
        frags.append(Fragmento(doc_id, primera or titulo, p, origen))
    return frags


@dataclass
class Indice:
    fragmentos: list[Fragmento] = field(default_factory=list)
    vectorizador: TfidfVectorizer | None = None
    matriz: object = None

    @classmethod
    def desde_carpeta(cls, carpeta: Path) -> "Indice":
        frags: list[Fragmento] = []
        for ruta in sorted(Path(carpeta).glob("*.md")):
            frags += trocear(ruta.stem, ruta.read_text(encoding="utf-8"))
        idx = cls(frags)
        idx.ajustar()
        return idx

    def ajustar(self) -> None:
        self.vectorizador = TfidfVectorizer(preprocessor=normalizar, ngram_range=(1, 2),
                                            sublinear_tf=True)
        self.matriz = self.vectorizador.fit_transform(
            [f"{f.doc_id} {f.seccion} {f.texto}" for f in self.fragmentos])

    def con_documentos_extra(self, docs: dict[str, str]) -> "Indice":
        """Copia del índice con documentos externos añadidos (ingesta de un documento nuevo)."""
        extra = []
        for doc_id, texto in docs.items():
            extra += trocear(doc_id, texto, origen="externo")
        nuevo = Indice(self.fragmentos + extra)
        nuevo.ajustar()
        return nuevo

    def buscar(self, consulta: str, k: int = 3) -> list[tuple[Fragmento, float]]:
        q = self.vectorizador.transform([consulta])
        sims = (self.matriz @ q.T).toarray().ravel()
        orden = np.argsort(-sims)[:k]
        return [(self.fragmentos[i], float(sims[i])) for i in orden if sims[i] > 0]

    def guardar(self, ruta: Path) -> None:
        ruta.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, ruta)

    @staticmethod
    def cargar(ruta: Path) -> "Indice":
        return joblib.load(ruta)

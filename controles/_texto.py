import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas y sin tildes, para comparar patrones."""
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()

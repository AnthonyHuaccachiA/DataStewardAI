"""Controles de seguridad de DataSteward. Cada uno se activa en config.yaml (sección controles)."""
from dataclasses import dataclass, field


@dataclass
class Decision:
    bloquear: bool = False
    motivos: list[str] = field(default_factory=list)

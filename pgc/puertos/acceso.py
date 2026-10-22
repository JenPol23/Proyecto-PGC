"""Puerto del acceso público (HTTPS) para los celulares."""
from typing import Protocol


class AccesoPublico(Protocol):
    estado: str                # "apagado" | "iniciando" | "activo" | "error" | "no instalado"
    url: str | None            # https://... cuando está activo

    def iniciar(self) -> None:
        """Arranca en segundo plano; avisa con al_cambiar cuando cambia la URL o el estado."""

    def detener(self) -> None:
        ...

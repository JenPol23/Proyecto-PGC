"""Puerto de texto → voz (fase 4: Coqui VITS en español)."""
from typing import Protocol


class Sintetizador(Protocol):
    estado: str                # "sin cargar" | "cargando" | "listo" | "error" | "desactivado"

    def cargar_en_segundo_plano(self) -> None:
        ...

    def decir(self, texto: str) -> None:
        """Dice el texto en voz alta. Bloquea hasta terminar de hablar."""

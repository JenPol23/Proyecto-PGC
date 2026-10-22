"""Puerto de voz → texto."""
from typing import Protocol


class Transcriptor(Protocol):
    estado: str                # "sin cargar" | "cargando" | "listo" | "error" | "desactivado"
    dispositivo: str | None    # "cuda float16" | "cpu int8" | None

    @property
    def listo(self) -> bool:
        ...

    def cargar_en_segundo_plano(self) -> None:
        """Carga el modelo en otro hilo; avisa con al_cambiar al terminar."""

    def transcribir(self, ruta_audio: str) -> str:
        """Texto reconocido (puede ser vacío). Bloquea; una transcripción a la vez."""

    def duracion(self, ruta_audio: str) -> float | None:
        """Segundos de audio, o None si no se puede saber."""

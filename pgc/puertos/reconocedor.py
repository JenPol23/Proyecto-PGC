"""Puerto del reconocimiento de señas (Kinect + modelos). Contrato: docs/CONTRATO_KINECT.md."""
from dataclasses import dataclass
from typing import Callable, Literal, Protocol

TIPOS_EVENTO = ("letra", "espacio", "borrar", "fin")
ESTADOS = ("apagado", "cargando", "listo", "sin_persona", "error")
LETRAS_VALIDAS = set("abcdefghijklmnñopqrstuvwxyz")


@dataclass(frozen=True)
class EventoSena:
    tipo: Literal["letra", "espacio", "borrar", "fin"]
    letra: str | None = None      # "a".."z" o "ñ", en minúscula; solo si tipo == "letra"
    confianza: float = 1.0        # 0.0 – 1.0
    modelo: str = ""              # qué modelo decidió: "A-mlp", "B-gru", "C-cnn"...
    instante: float = 0.0         # time.monotonic() del cuadro que confirmó la letra
    latencia_ms: float = 0.0      # desde la captura del cuadro hasta la decisión


EstadoReconocedor = Literal["apagado", "cargando", "listo", "sin_persona", "error"]


class ReconocedorSenas(Protocol):
    estado: EstadoReconocedor
    detalle: str                  # texto corto que sale en el proyector, p. ej. "Kinect v1 · modelo A"

    def iniciar(self, al_evento: Callable[[EventoSena], None],
                al_cambiar_estado: Callable[[], None]) -> None:
        """Carga modelos y abre el Kinect EN SEGUNDO PLANO; retorna enseguida."""

    def detener(self) -> None:
        """Libera el Kinect y los hilos. Debe poder llamarse más de una vez."""


def problemas_del_evento(evento):
    """Lista de incumplimientos del contrato (vacía si el evento es válido)."""
    p = []
    if not isinstance(evento, EventoSena):
        return [f"no es un EventoSena: {type(evento).__name__}"]
    if evento.tipo not in TIPOS_EVENTO:
        p.append(f"tipo desconocido: {evento.tipo!r}")
    if evento.tipo == "letra" and (not isinstance(evento.letra, str) or evento.letra not in LETRAS_VALIDAS):
        p.append(f"letra inválida: {evento.letra!r} (debe ser a-z o ñ en minúscula)")
    if evento.tipo != "letra" and evento.letra is not None:
        p.append(f"un evento '{evento.tipo}' no lleva letra")
    if not 0.0 <= evento.confianza <= 1.0:
        p.append(f"confianza fuera de 0–1: {evento.confianza}")
    if evento.latencia_ms < 0:
        p.append("latencia negativa")
    return p

"""Puerto de la mano robótica: lo único que la aplicación sabe de ella."""
from typing import Protocol


class PuertoMano(Protocol):
    letras: set | None             # letras que informó la mano; None = usar las por defecto

    @property
    def conectada(self) -> bool:   # hay una mano física respondiendo
        ...

    @property
    def modo(self) -> str:         # "real" | "simulada"  (lo muestra la pantalla)
        ...

    @property
    def medio(self) -> str | None:    # "ble" | "usb" | None (simulada)
        ...

    @property
    def puerto(self) -> str | None:   # "COM5", el nombre de la mano por Bluetooth ("Mano-LSC"), o None
        ...

    def conectar(self) -> bool:
        """Intenta conectar la mano física; si no puede, queda simulada."""

    def cerrar(self) -> None:
        """Suelta la conexión física (la mano queda simulada)."""

    def hacer(self, orden: str) -> bool:
        """Forma una letra o 'reset'. Bloquea hasta la confirmación; True si la mano confirmó."""

    def reset(self) -> bool:
        """Abre la mano (equivale a hacer('reset'))."""

    def revisar(self) -> bool:
        """Entre mensajes: latido, respaldo y búsqueda de la mano. True si cambió la conexión."""

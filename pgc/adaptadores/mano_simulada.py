"""Mano simulada: tarda lo mismo que una real y siempre confirma (para probar sin hardware)."""
import time

TIEMPO_SIMULADO = 1.2     # duración simulada de una letra
TIEMPO_RESET = 0.5


class ManoSimulada:
    def __init__(self, tiempo_letra=TIEMPO_SIMULADO, tiempo_reset=TIEMPO_RESET, dormir=time.sleep):
        self.tiempo_letra = tiempo_letra
        self.tiempo_reset = tiempo_reset
        self._dormir = dormir

    def hacer(self, orden):
        self._dormir(self.tiempo_letra if orden != "reset" else self.tiempo_reset)
        return True

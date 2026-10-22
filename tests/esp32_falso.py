"""ESP32 falso por Bluetooth: el main.py REAL de la placa corriendo en un hilo (servos y radio falsos).

Se usa en las pruebas y en scripts/prueba_e2e.py --ble. `bleak` es un bleak falso que
habla con esta placa: se le pasa a ManoBLE(bleak=esp.bleak).
"""
import time

from arnes_firmware import BleakFalso, PlacaEnHilo

TOKEN = "token-de-prueba-0123456789"


class Esp32Falso:
    """Interfaz cómoda sobre PlacaEnHilo: órdenes recibidas, colgarse, salir y volver al alcance."""

    def __init__(self, token=TOKEN, nombre="Mano-LSC", pausa_letra=0.0):
        self.placa = PlacaEnHilo(token, nombre, escala=pausa_letra)
        if self.placa.error:
            raise self.placa.error
        self.nombre = nombre
        self.bleak = BleakFalso(self.placa.radio)

    @property
    def ordenes(self):
        return self.placa.ordenes

    @property
    def registro(self):
        return self.placa.registro

    @property
    def log(self):
        return self.placa.salida.lineas()

    @property
    def callada(self):
        return self.placa.callada.is_set()

    @callada.setter
    def callada(self, valor):
        (self.placa.callada.set if valor else self.placa.callada.clear)()
        if valor:
            time.sleep(0.1)            # que el bucle llegue a su pausa y quede detenido ahí

    def apagar(self):
        """Como alejarse o quitar los 12 V: se corta la conexión y la placa deja de verse."""
        self.placa.radio.salir_de_alcance()
        time.sleep(0.05)

    def encender(self):
        self.placa.radio.volver()
        time.sleep(0.05)

    def detener(self):
        self.placa.detener()

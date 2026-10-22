"""Para el proceso hijo del puente Bluetooth en las pruebas: la placa falsa (main.py real) y un bleak falso.

    python -m pgc.adaptadores.ble_puente --bleak ble_falso_hijo:crear
(con la carpeta tests en PYTHONPATH y el token en PGC_PRUEBA_TOKEN)
"""
import os

from arnes_firmware import BleakFalso, PlacaEnHilo


def crear():
    placa = PlacaEnHilo(os.environ["PGC_PRUEBA_TOKEN"])
    if placa.error:
        raise placa.error
    return BleakFalso(placa.radio)

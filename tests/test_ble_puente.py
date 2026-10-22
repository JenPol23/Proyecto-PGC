"""Puente Bluetooth: bleak en un proceso aparte (WinRT y Whisper no conviven en el mismo proceso).

El hijo es un proceso de verdad que corre el main.py real de la placa con una radio falsa.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pgc.adaptadores.ble_puente import BleakRemoto
from pgc.adaptadores.mano_ble import ManoBLE

TESTS = Path(__file__).resolve().parent
TOKEN = "token-de-prueba-0123456789"


def remoto():
    entorno = {**os.environ, "PYTHONPATH": str(TESTS), "PGC_PRUEBA_TOKEN": TOKEN}
    return BleakRemoto([sys.executable, "-m", "pgc.adaptadores.ble_puente", "--bleak", "ble_falso_hijo:crear"],
                       entorno=entorno)


@pytest.fixture
def puente():
    r = remoto()
    yield r
    r.cerrar()


def mano(puente, log, token=TOKEN):
    return ManoBLE("Mano-LSC", token, log=log.append, bleak=puente, timeout_letra=3.0, tiempo_busqueda=1.0)


def test_mano_por_el_puente(puente):
    log = []
    m = mano(puente, log)
    assert m.conectar() is True, log
    assert m.hacer("a") is True and m.hacer("g") is False and m.hacer("reset") is True
    assert m.latido() is True
    assert log[-1] == "[mano] Conectada por Bluetooth a Mano-LSC"
    m.cerrar()
    assert m.conectar() is True                                 # reconexión por el mismo hijo
    m.cerrar()


def test_token_incorrecto_por_el_puente(puente):
    log = []
    assert mano(puente, log, token="otro-token-de-veinte-caracteres").conectar() is False
    assert "rechazó el token" in log[-1]


def test_si_el_puente_se_cae_se_nota_y_se_recupera(puente):
    log = []
    m = mano(puente, log)
    assert m.conectar() is True
    puente._proc.kill()                                         # el proceso del Bluetooth muere
    puente._proc.wait(5)
    assert m.hacer("a") is False and not m.conectada            # el servidor sigue vivo
    assert m.conectar() is True                                 # se arranca un hijo nuevo
    assert m.hacer("b") is True
    m.cerrar()


def test_el_servidor_nunca_carga_el_bluetooth_de_windows():
    """WinRT (bleak) + ctranslate2 (Whisper) en el mismo proceso = access violation."""
    codigo = ("import sys; from pgc import arranque; from pgc.adaptadores import mano_ble, ble_puente; "
              "m = mano_ble.ManoBLE('Mano-LSC', 't' * 20); "
              "print(sorted(n for n in sys.modules if n.split('.')[0] in ('bleak', 'winrt')))")
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, cwd=TESTS.parent, timeout=60)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "[]"


def test_el_hijo_termina_cuando_se_cierra_el_servidor(puente):
    m = mano(puente, [])
    assert m.conectar() is True
    proc = puente._proc
    puente.cerrar()                                             # stdin cerrado = el servidor se fue
    assert proc.wait(5) is not None

"""servidor.py se conserva como forma corta de arrancar (py -3.11 servidor.py ...)."""
import importlib

from conftest import RAIZ


def test_servidor_es_un_atajo():
    assert importlib.import_module("servidor").main is importlib.import_module("pgc.arranque").main


def test_ya_no_quedan_los_atajos_de_la_migracion():
    for nombre in ("texto_util.py", "mano_serial.py", "voz_entrada.py", "tunel.py"):
        assert not (RAIZ / nombre).exists(), nombre


def test_iniciar_bat_usa_el_paquete():
    texto = (RAIZ / "iniciar.bat").read_text(encoding="utf-8")
    assert "py -3.11 -m pgc %*" in texto

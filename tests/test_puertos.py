"""Pruebas de contrato: cada implementación cumple su puerto."""
import inspect
import time
import types

import pytest

from conftest import FabricaMano, ManoFalsa, TranscriptorFalso, TunelFalso, acceso, whisper

from pgc.puertos.acceso import AccesoPublico
from pgc.puertos.mano import PuertoMano
from pgc.puertos.transcriptor import Transcriptor


def miembros_del_puerto(puerto):
    return {n for n in dir(puerto) if not n.startswith("_")} | set(getattr(puerto, "__annotations__", {}))


@pytest.fixture(params=["real_simulada", "falsa"])
def mano(request):
    if request.param == "real_simulada":
        fabrica = FabricaMano()
        fabrica.time = types.SimpleNamespace(sleep=lambda s: None, time=time.time)
        return fabrica.Mano(simular=True, log=lambda m: None)
    return ManoFalsa()


def test_cumple_puerto_mano(mano):
    for nombre in miembros_del_puerto(PuertoMano):
        assert hasattr(mano, nombre), nombre
    for metodo in ("conectar", "cerrar", "hacer", "reset"):
        assert callable(getattr(mano, metodo)), metodo


def test_comportamiento_minimo_del_puerto(mano):
    assert mano.conectar() is False                  # sin hardware: queda simulada
    assert (mano.conectada, mano.modo) == (False, "simulada")
    assert mano.hacer("a") is True
    assert mano.reset() is True
    mano.cerrar()
    assert mano.modo == "simulada"


@pytest.mark.parametrize("puerto, implementaciones", [
    (Transcriptor, [lambda: whisper.Transcriptor(log=lambda m: None), lambda: TranscriptorFalso()]),
    (AccesoPublico, [lambda: acceso.Tunel(8000, log=lambda m: None), lambda: TunelFalso(8000)]),
], ids=["Transcriptor", "AccesoPublico"])
def test_voz_y_acceso_cumplen_su_puerto(puerto, implementaciones):
    for crear in implementaciones:
        obj = crear()
        for nombre in miembros_del_puerto(puerto):
            assert hasattr(obj, nombre), f"{type(obj).__name__} no tiene {nombre}"


def test_whisper_usa_el_modelo_configurado():
    assert whisper.Transcriptor(nombre_modelo="small").nombre_modelo == "small"
    assert whisper.Transcriptor().nombre_modelo == "medium"


def test_firma_de_hacer():
    assert list(inspect.signature(PuertoMano.hacer).parameters) == ["self", "orden"]

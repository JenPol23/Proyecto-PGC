"""Pruebas de contrato del puerto ReconocedorSenas (docs/CONTRATO_KINECT.md).

Para revisar la implementación del Kinect antes de entregarla:
    py -3.11 -m pytest tests/contratos --reconocedor=pgc.adaptadores.kinect.reconocedor:ReconocedorKinect
Sin la opción se revisa el ReconocedorSimulado.
"""
import importlib
import threading
import time

import pytest

from pgc.puertos.reconocedor import ESTADOS, EventoSena, problemas_del_evento


@pytest.fixture
def reconocedor(request):
    ruta = request.config.getoption("--reconocedor")
    modulo, clase = ruta.split(":")
    r = getattr(importlib.import_module(modulo), clase)()      # regla 6: sin argumentos
    yield r
    r.detener()


def test_tiene_estado_y_detalle(reconocedor):
    assert reconocedor.estado in ESTADOS
    assert isinstance(reconocedor.detalle, str)


def test_iniciar_no_bloquea(reconocedor):
    t0 = time.monotonic()
    reconocedor.iniciar(lambda e: None, lambda: None)
    assert time.monotonic() - t0 < 1.0, "iniciar() debe cargar en segundo plano y retornar enseguida"
    assert reconocedor.estado in ESTADOS


def test_detener_se_puede_llamar_dos_veces(reconocedor):
    reconocedor.iniciar(lambda e: None, lambda: None)
    reconocedor.detener()
    reconocedor.detener()
    assert reconocedor.estado in ESTADOS


def test_detener_sin_iniciar(reconocedor):
    reconocedor.detener()


def test_eventos_cumplen_el_formato(reconocedor):
    """Revisa todos los eventos que emita en 3 s (con el simulado, se le pide un texto)."""
    eventos, cambios = [], []
    reconocedor.iniciar(eventos.append, lambda: cambios.append(reconocedor.estado))
    if hasattr(reconocedor, "simular"):
        reconocedor.simular("hola mundo")
    time.sleep(3)
    for e in eventos:
        assert not problemas_del_evento(e), problemas_del_evento(e)
    assert all(estado in ESTADOS for estado in cambios)


def test_problemas_del_evento_detecta_errores():
    assert problemas_del_evento(EventoSena("letra", letra="a", confianza=0.9)) == []
    assert problemas_del_evento(EventoSena("letra", letra="A"))
    assert problemas_del_evento(EventoSena("letra", letra="ab"))
    assert problemas_del_evento(EventoSena("fin", letra="a"))
    assert problemas_del_evento(EventoSena("letra", letra="a", confianza=1.5))
    assert problemas_del_evento(EventoSena("saludo"))
    assert problemas_del_evento("a")


def test_callbacks_desde_otro_hilo(reconocedor):
    hilos = set()
    reconocedor.iniciar(lambda e: hilos.add(threading.get_ident()), lambda: None)
    if hasattr(reconocedor, "simular"):
        reconocedor.simular("ab", esperar=True)
        assert hilos and threading.get_ident() not in hilos

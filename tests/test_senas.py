"""Señas → texto (E9): servicio de eventos, carga del reconocedor y aislamiento de errores."""
import threading
import time

import pytest

from conftest import configuracion, esperar

from pgc import arranque
from pgc.adaptadores.reconocedor_simulado import ReconocedorSimulado
from pgc.aplicacion.senas import ServicioSenas
from pgc.dominio.moderacion import cargar_moderador
from pgc.puertos.reconocedor import EventoSena


@pytest.fixture
def servicio():
    frases, log = [], []
    r = ReconocedorSimulado(pausa=0)
    s = ServicioSenas(r, al_frase=frases.append, log=log.append, moderador=cargar_moderador())
    s.iniciar()
    yield s, r, frases, log
    s.detener()


def test_arma_la_frase_y_la_entrega_al_terminar(servicio):
    s, r, frases, _ = servicio
    r.simular("Hola  mundo!", esperar=True)
    esperar(lambda: frases == ["hola mundo"])
    assert s.texto == ""


def test_borrar_y_espacios(servicio):
    s, _, frases, _ = servicio
    for e in [EventoSena("espacio"), EventoSena("letra", letra="a"), EventoSena("letra", letra="x"),
              EventoSena("borrar"), EventoSena("espacio"), EventoSena("espacio"), EventoSena("letra", letra="ñ"),
              EventoSena("fin")]:
        s._recibir(e)
    esperar(lambda: frases == ["a ñ"])


def test_eventos_invalidos_se_ignoran(servicio):
    s, _, frases, log = servicio
    s._recibir(EventoSena("letra", letra="A"))
    s._recibir("basura")
    s._recibir(EventoSena("letra", letra="b"))
    s._recibir(EventoSena("fin"))
    esperar(lambda: frases == ["b"])
    assert sum("Evento ignorado" in l for l in log) == 2


def test_frase_ofensiva_no_se_entrega(servicio):
    s, r, frases, log = servicio
    r.simular("gonorrea", esperar=True)
    esperar(lambda: any("filtro" in l for l in log))
    assert frases == []


def test_recibir_nunca_bloquea_al_reconocedor():
    lento = threading.Event()
    s = ServicioSenas(ReconocedorSimulado(), al_frase=lambda f: lento.wait(5))
    s.iniciar()
    t0 = time.monotonic()
    for _ in range(100):
        s._recibir(EventoSena("letra", letra="a"))
        s._recibir(EventoSena("fin"))
    assert time.monotonic() - t0 < 0.5
    lento.set()


class Roto:
    estado, detalle = "apagado", ""

    def iniciar(self, al_evento, al_cambiar_estado):
        raise RuntimeError("no hay Kinect")

    def detener(self):
        raise RuntimeError("tampoco")


def test_un_reconocedor_roto_no_tumba_nada():
    log = []
    s = ServicioSenas(Roto(), log=log.append)
    s.iniciar()
    s.detener()
    assert s.instantanea()["estado"] == "error"
    assert s.instantanea()["detalle"] == "Kinect: no disponible"


@pytest.mark.parametrize("ruta, detalle", [
    ("simulado", "Kinect simulado"),
    ("pgc.adaptadores.reconocedor_simulado:ReconocedorSimulado", "Kinect simulado"),
    ("pgc.adaptadores.kinect.no_existe:Clase", "Kinect: no disponible"),
    ("sin_dos_puntos", "Kinect: no disponible"),
])
def test_cargar_reconocedor(ruta, detalle):
    log = []
    r = arranque.cargar_reconocedor(configuracion(reconocedor=ruta), log.append)
    assert r.detalle == detalle
    assert ("No se pudo cargar" in "".join(log)) == (detalle == "Kinect: no disponible")


def test_el_sistema_inicia_y_detiene_el_reconocedor(abrir_api):
    with abrir_api() as (c, s):
        assert s.senas.reconocedor.estado == "sin_persona"
        s.senas.reconocedor.simular("ok", esperar=True)
        esperar(lambda: s.senas.frases == ["ok"])
        k = c.get("/api/estado").json()["kinect"]                                # ahora la pantalla lo ve
        assert k["estado"] == "sin_persona" and k["frases"] == ["ok"] and k["controles"] is False
    assert s.senas.reconocedor.estado == "apagado"

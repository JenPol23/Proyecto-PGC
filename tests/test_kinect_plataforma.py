"""Kinect integrado en la plataforma: turno, controles, imagen solo en el PC, voz, eco y varios celulares."""
import time
from contextlib import ExitStack

import pytest

from conftest import admin, esperar
from detector_falso import JPEG, DetectorFalso

PC = "127.0.0.1"
TUNEL = {"CF-Connecting-IP": "181.50.1.2"}       # así llega cloudflared: desde 127.0.0.1 con este encabezado


class SintetizadorFalso:
    estado = "listo"

    def __init__(self):
        self.dichas = []

    def cargar_en_segundo_plano(self):
        pass

    def decir(self, texto):
        self.dichas.append(texto)


@pytest.fixture
def detector():
    d = DetectorFalso()
    d.mantener_camara()
    yield d
    d.cerrar()


@pytest.fixture
def con_kinect(abrir_api, detector):
    """API con el ReconocedorKinect real apuntando al detector falso."""
    def abrir(desde="testclient", **opciones):
        return abrir_api(desde, reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05, **opciones)
    return abrir


SECRETO = "celular-secreto-de-ana"


def registrar(c, cliente, nombre=None):
    return c.post("/api/participante", json={"cliente": cliente, "nombre": nombre}).json()


def control(c, accion, cliente=None, **kw):
    return c.post("/api/kinect/control", json={"accion": accion, "cliente": cliente}, **kw)


# ---------------------------------------------------------------- turno: un jurado a la vez
def test_un_solo_jurado_controla_el_kinect(con_kinect):
    with con_kinect() as (c, s):
        registrar(c, SECRETO, "Ana")
        registrar(c, "B", "Beto")
        assert control(c, "iniciar", SECRETO).status_code == 403          # sin turno no hay controles
        assert c.post("/api/kinect/turno", json={"cliente": SECRETO}).status_code == 200
        r = c.post("/api/kinect/turno", json={"cliente": "B"})
        assert r.status_code == 409 and "Ana" in r.json()["detail"]
        assert control(c, "iniciar", SECRETO).status_code == 200
        assert control(c, "detener", "B").status_code == 403
        turno = c.get("/api/estado").json()["kinect"]["turno"]
        assert turno["nombre"] == "Ana" and turno["pid"] and SECRETO not in repr(turno)   # nunca el id privado
        assert c.post("/api/kinect/turno/soltar", json={"cliente": SECRETO}).status_code == 200
        assert c.post("/api/kinect/turno", json={"cliente": "B"}).status_code == 200


def test_el_turno_se_libera_solo_por_inactividad(con_kinect):
    with con_kinect() as (c, s):
        reloj = [1000.0]
        s.senas.turno._reloj = lambda: reloj[0]
        c.post("/api/kinect/turno", json={"cliente": "A"})
        reloj[0] += 60
        assert control(c, "iniciar", "A").status_code == 200           # usarlo reinicia la espera
        reloj[0] += 100
        assert c.post("/api/kinect/turno", json={"cliente": "B"}).status_code == 409
        reloj[0] += 21                                                 # 121 s sin usarlo
        esperar(lambda: c.get("/api/estado").json()["kinect"]["turno"] is None)     # lo libera el hilo de señas
        assert c.post("/api/kinect/turno", json={"cliente": "B"}).status_code == 200


def test_bloquear_quita_el_turno(con_kinect):
    with con_kinect(PC) as (pc, s2):
        pid = registrar(pc, "A", "Ana")["pid"]
        pc.post("/api/kinect/turno", json={"cliente": "A"})
        assert pc.post(f"/api/participantes/{pid}/bloquear", headers=admin(pc)).status_code == 200
        assert s2.senas.turno.instantanea() is None
        r = pc.post("/api/kinect/turno", json={"cliente": "A"})
        assert r.status_code == 403 and "pausó" in r.json()["detail"]


def test_el_presentador_controla_siempre_y_libera_el_turno(con_kinect):
    with con_kinect(PC) as (c, s):
        c.post("/api/kinect/turno", json={"cliente": "A"})
        assert control(c, "iniciar", headers=admin(c)).status_code == 200      # aunque A tenga el turno
        assert control(c, "iniciar").status_code == 403                         # sin token, no
        assert c.post("/api/kinect/liberar").status_code == 403
        assert c.post("/api/kinect/liberar", headers=admin(c)).status_code == 200
        assert s.senas.turno.instantanea() is None


def test_controles_con_detector_caido_o_sin_controles(abrir_api, con_kinect, detector):
    with abrir_api(PC) as (c, s):                                   # reconocedor simulado: no tiene controles
        assert control(c, "iniciar", headers=admin(c)).status_code == 409
    detector.cerrar()
    with con_kinect(PC) as (c, s):
        r = control(c, "iniciar", headers=admin(c))
        assert r.status_code == 503 and r.json()["detail"] == "Kinect no conectado"
        esperar(lambda: c.get("/api/estado").json()["kinect"]["detalle"] == "Kinect no conectado")


# ---------------------------------------------------------------- imagen: solo el PC del proyector
def test_imagen_solo_en_el_pc_con_token(con_kinect):
    with con_kinect(PC) as (c, s):
        esperar(lambda: s.senas.reconocedor.camara)
        esperar(lambda: c.get("/api/kinect/imagen", headers=admin(c)).status_code == 200)
        r = c.get("/api/kinect/imagen", headers=admin(c))
        assert r.content == JPEG and r.headers["content-type"] == "image/jpeg"
        assert c.get("/api/kinect/imagen").status_code == 403                        # PC sin token
        assert c.get("/api/kinect/imagen", headers={**admin(c), **TUNEL}).status_code == 403   # por el túnel
    with con_kinect() as (c, s):
        assert c.get("/api/kinect/imagen").status_code == 403                        # un celular


# ---------------------------------------------------------------- en vivo, voz y eco
def test_texto_en_vivo_voz_y_eco(con_kinect, detector):
    with con_kinect(PC) as (c, s):
        s.voz_salida = voz = SintetizadorFalso()
        esperar(lambda: s.senas.reconocedor.camara)
        control(c, "iniciar", headers=admin(c))
        with c.websocket_connect("/ws") as ws:
            for letra in "HOGA":
                detector.reconocer(letra)
            while True:                                            # el celular lo ve por el WebSocket
                d = ws.receive_json()
                if d.get("tipo") == "estado" and d["kinect"]["texto"] == "hoga":
                    break
        assert d["kinect"]["activo"] and d["kinect"]["camara"] and d["kinect"]["estado"] == "listo"
        # Sin eco: se dice en voz alta y no va a la mano
        control(c, "terminar", headers=admin(c))
        esperar(lambda: voz.dichas == ["hoga"])
        assert s.instantanea()["kinect"]["frases"] == ["hoga"] and s.cola == [] and s.actual is None
        # Con eco: además, la mano la deletrea (la G y la H se muestran como no disponibles)
        assert c.post("/api/kinect/eco", json={"activo": True}, headers=admin(c)).json() == {"eco": True}
        for letra in "HOGA":
            detector.reconocer(letra)
        esperar(lambda: s.senas.texto == "hoga")
        control(c, "terminar", headers=admin(c))
        esperar(lambda: voz.dichas == ["hoga", "hoga"])
        esperar(lambda: s.historial and s.historial[0]["nombre"] == "Kinect", timeout=10)
        tipos = [(p["c"], p["tipo"]) for p in s.historial[0]["pasos"]]
        assert tipos == [("H", "nd"), ("O", "ok"), ("G", "nd"), ("A", "ok")]


def test_eco_solo_el_presentador(con_kinect):
    with con_kinect() as (c, s):
        assert c.post("/api/kinect/eco", json={"activo": True}).status_code == 403
    with con_kinect(PC) as (c, s):
        assert c.post("/api/kinect/eco", json={"activo": True}, headers={**admin(c), **TUNEL}).status_code == 403


def test_eco_sin_letras_posibles_no_tumba_nada(crear_sistema, registro):
    s = crear_sistema(kinect_eco=True)
    s._frase_reconocida("gh")
    assert s.cola == [] and any("Eco: la frase no va a la mano" in l for l in registro)


# ---------------------------------------------------------------- varios celulares (límites)
def test_muchos_celulares_con_la_pestana_kinect_no_cargan_al_detector(con_kinect, detector):
    """Los celulares no consultan nada: el servidor lee el detector a ritmo fijo y lo reparte por el WebSocket."""
    with con_kinect() as (c, s):                    # todos "desde el mismo WiFi": una sola IP
        esperar(lambda: detector.consultas > 3)
        antes, t0 = detector.consultas, time.monotonic()
        time.sleep(1)
        solo = (detector.consultas - antes) / (time.monotonic() - t0)
        with ExitStack() as pila:
            conexiones = [pila.enter_context(c.websocket_connect("/ws")) for _ in range(30)]
            for ws in conexiones:
                assert ws.receive_json()["tipo"] == "estado"          # aceptadas (antes el límite era 8 por IP)
            antes, t0 = detector.consultas, time.monotonic()
            time.sleep(1)
            con_30 = (detector.consultas - antes) / (time.monotonic() - t0)
        assert con_30 < solo * 1.5 + 5, (solo, con_30)              # no crece con el número de celulares


def test_limpiar_borra_todo_y_solo_con_turno(con_kinect, detector):
    with con_kinect() as (c, s):
        esperar(lambda: s.senas.reconocedor.camara)
        c.post("/api/kinect/turno", json={"cliente": "A"})
        assert control(c, "iniciar", "A").status_code == 200
        for letra in "HOLA":
            detector.reconocer(letra)
        esperar(lambda: s.senas.texto == "hola")
        assert control(c, "limpiar", "B").status_code == 403          # un espectador no limpia
        assert control(c, "limpiar", "A").status_code == 200
        assert detector.texto == "" and detector.ordenes[-1] == "clear"
        esperar(lambda: s.senas.texto == "" and c.get("/api/estado").json()["kinect"]["texto"] == "")
        assert s.senas.frases == []                                    # limpiar no es terminar: no se dice nada

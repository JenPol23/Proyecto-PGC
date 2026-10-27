"""ReconocedorKinect contra un detector falso que habla como el de integracion_kinect/."""
import time

import pytest

from conftest import esperar
from detector_falso import JPEG, DetectorFalso

from pgc.adaptadores.kinect.reconocedor import (NO_CONECTADO, ErrorKinect, ReconocedorKinect,
                                                eventos_por_cambio, leer_estado)
from pgc.puertos.reconocedor import ESTADOS, problemas_del_evento


def resumen(eventos):
    return [e.letra if e.tipo == "letra" else e.tipo for e in eventos]


# ---------------------------------------------------------------- cambios de texto → eventos
@pytest.mark.parametrize("antes, despues, esperado", [
    ("", "", []),
    ("", "HO", ["h", "o"]),
    ("HO", "HOL", ["l"]),
    ("HOL", "HOL ", ["espacio"]),
    ("HOLA", "HOL", ["borrar"]),
    ("HOLA", "", ["borrar"] * 4),
    ("HOLA", "HOJA", ["borrar", "borrar", "j", "a"]),          # se borra hasta lo común y se escribe el resto
    ("", "A?Ñ", ["a", "ñ"]),                                   # lo que no es letra no se emite
])
def test_eventos_por_cambio(antes, despues, esperado):
    eventos = eventos_por_cambio(antes, despues)
    assert resumen(eventos) == esperado
    assert all(not problemas_del_evento(e) for e in eventos)     # cumplen el contrato (minúsculas, etc.)


def test_leer_estado_texto_y_json():
    assert leer_estado("Texto: —\nEstado: Deletreo detenido.")[:2] == ("", "Deletreo detenido.")
    assert leer_estado("Texto: HOLA\r\nEstado: Posible letra: A")[:2] == ("HOLA", "Posible letra: A")
    # Si el detector pasa a JSON (lo que le pedimos), se usa sin cambiar el adaptador
    assert leer_estado('{"texto": "HO", "estado": "x", "activo": true, "confianza": 0.9, "latencia_ms": 80}') == \
        ("HO", "x", True, 0.9, 80)
    with pytest.raises(ValueError):
        leer_estado("cualquier cosa")


# ---------------------------------------------------------------- con el detector falso
@pytest.fixture
def detector():
    d = DetectorFalso()
    yield d
    d.cerrar()


@pytest.fixture
def kinect(detector):
    eventos, cambios = [], []
    r = ReconocedorKinect(url=detector.url, intervalo=0.05)
    r.iniciar(eventos.append, lambda: cambios.append((r.estado, r.detalle)))
    yield r, eventos, cambios
    r.detener()


def test_sin_detector_dice_kinect_no_conectado():
    r = ReconocedorKinect(url="http://127.0.0.1:9", intervalo=0.05)    # puerto cerrado
    r.iniciar(lambda e: None, lambda: None)
    try:
        esperar(lambda: r.estado == "error")
        assert r.detalle == NO_CONECTADO and not r.conectado
        with pytest.raises(ErrorKinect, match=NO_CONECTADO):
            r.controlar("iniciar")
    finally:
        r.detener()


def test_detector_sin_camara_tambien_es_no_conectado(kinect, detector):
    r, _, _ = kinect
    esperar(lambda: r.conectado)
    assert (r.estado, r.detalle, r.camara) == ("error", NO_CONECTADO, False)
    detector.mantener_camara()
    esperar(lambda: r.camara and r.estado == "sin_persona")
    assert r.detalle == "Deletreo detenido."


def test_deletreo_completo(kinect, detector):
    r, eventos, _ = kinect
    detector.mantener_camara()
    esperar(lambda: r.camara)
    r.controlar("iniciar")
    assert r.activo and detector.ordenes == ["start"]
    for letra in "HOLA":
        detector.reconocer(letra)
    esperar(lambda: resumen(eventos) == ["h", "o", "l", "a"])
    assert r.estado == "listo" and r.detalle.startswith("Letra añadida")
    r.controlar("borrar")
    r.controlar("espacio")                           # tras borrar: "HOL" + " "
    esperar(lambda: resumen(eventos)[4:] == ["borrar", "espacio"])
    detector.reconocer("x")                          # una letra que llega justo antes de «Terminar»
    r.controlar("terminar")                          # la recoge, emite fin y deja el detector en blanco
    assert resumen(eventos)[6:] == ["x", "fin"]
    assert detector.texto == "" and detector.ordenes[-1] == "clear"
    r.controlar("detener")
    assert not r.activo
    assert all(not problemas_del_evento(e) for e in eventos)


def test_un_detector_reiniciado_queda_detenido(kinect, detector):
    r, _, _ = kinect
    detector.mantener_camara()
    esperar(lambda: r.camara)
    r.controlar("iniciar")
    detector.activo, detector.estado = False, "Deletreo detenido."     # p. ej. alguien lo detuvo en la app C#
    esperar(lambda: not r.activo)


def test_error_del_detector_llega_con_su_motivo(detector):
    detector.con_modelo = False
    r = ReconocedorKinect(url=detector.url, intervalo=0.05)
    r.iniciar(lambda e: None, lambda: None)
    try:
        with pytest.raises(ErrorKinect, match="modelo_estaticas.joblib"):
            r.controlar("iniciar")
        with pytest.raises(ErrorKinect):
            r.controlar("saludar")
    finally:
        r.detener()


def test_imagen_solo_si_llegan_cuadros(kinect, detector):
    r, _, _ = kinect
    esperar(lambda: r.conectado)
    assert r.imagen() is None
    detector.mantener_camara()
    esperar(lambda: (r.imagen() or b"").startswith(JPEG))       # cuadros nuevos: JPEG + contador


def test_estados_validos_y_detener_dos_veces(kinect):
    r, _, cambios = kinect
    esperar(lambda: len(cambios) >= 2)
    r.detener()
    r.detener()
    assert r.estado == "apagado"
    assert all(estado in ESTADOS for estado, _ in cambios)


def test_desde_config():
    from conftest import configuracion
    r = ReconocedorKinect.desde_config(configuracion(kinect_url="http://127.0.0.1:8799", kinect_intervalo=0.5))
    assert (r.url, r.intervalo) == ("http://127.0.0.1:8799", 0.5)


# ---------------------------------------------------------------- vista previa: ritmo, pareja estado+imagen, congelada
def test_mirando_lee_estado_e_imagen_juntos_y_rapido(kinect, detector):
    r, _, _ = kinect
    detector.mantener_camara(por_segundo=30)
    esperar(lambda: r.camara)
    r.controlar("iniciar")
    detector.reconocer("A")
    r.imagen_con_estado()                                   # el proyector empieza a mirar
    antes, t0 = detector.consultas, time.monotonic()
    vistos = set()
    while time.monotonic() - t0 < 1.0:
        foto = r.imagen_con_estado()
        vistos.add(foto["cuadro"])
        time.sleep(0.01)
    por_segundo = (detector.consultas - antes) / (time.monotonic() - t0)
    # ~20 vueltas/s (antes ~3). La prueba exige 10 para no fallar con el PC cargado; la cifra real se mide en Edge
    assert por_segundo >= 10, por_segundo
    assert len(vistos) >= 10, len(vistos)                   # imágenes distintas por segundo
    foto = r.imagen_con_estado()
    assert foto["texto"] == "A" and foto["detalle"].startswith("Letra añadida")   # el estado de ESA imagen
    assert foto["desfase_ms"] < 50 and foto["edad_ms"] < 200


def test_sin_mirar_no_carga_al_detector(kinect, detector):
    r, _, _ = kinect                                        # intervalo 0,05 en la prueba; nadie pide la imagen
    detector.mantener_camara()
    esperar(lambda: r.camara)
    r._t_pedida = -1e9
    antes, t0 = detector.consultas, time.monotonic()
    time.sleep(1)
    assert (detector.consultas - antes) / (time.monotonic() - t0) <= 25    # solo el estado, a su ritmo normal


def test_imagen_congelada_es_kinect_no_conectado(kinect, detector):
    r, _, _ = kinect
    detector.mantener_camara()
    r.imagen_con_estado()                                   # mirando
    esperar(lambda: r.camara and r.estado == "sin_persona")
    detector.congelar()                                     # el detector sigue repitiendo la última imagen
    t0 = time.monotonic()
    esperar(lambda: r.estado == "error" and r.detalle == NO_CONECTADO, timeout=4)
    assert time.monotonic() - t0 < 2.5                      # antes: 3 s después de que el detector diera 503

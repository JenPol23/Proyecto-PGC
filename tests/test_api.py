"""API HTTP y WebSocket (caracterización de servidor.crear_app con TestClient)."""
import io
import os
from unittest.mock import ANY

import pytest

from conftest import AUDIO_WEBM, IP_LOCAL, TunelFalso, admin, esperar

PC = "127.0.0.1"


# =============================================================================
#  Páginas y recursos
# =============================================================================
@pytest.mark.parametrize("ruta, texto", [("/", "Mano bidireccional LSC"), ("/pantalla", "Mano bidireccional LSC")])
def test_paginas(abrir_api, ruta, texto):
    with abrir_api() as (c, _):
        r = c.get(ruta)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert r.headers["cache-control"] == "no-store"
    assert texto in r.text


def test_logo(abrir_api):
    with abrir_api() as (c, _):
        r = c.get("/logo-udec.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_qr_apunta_a_la_url_publica(abrir_api):
    cv2 = pytest.importorskip("cv2")
    np = pytest.importorskip("numpy")
    with abrir_api() as (c, _):
        r = c.get("/qr.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.headers["cache-control"] == "no-store"
    img = cv2.imdecode(np.frombuffer(r.content, np.uint8), cv2.IMREAD_COLOR)
    texto, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    assert texto == TunelFalso.URL


def test_documentacion_automatica(abrir_api):
    with abrir_api() as (c, _):
        assert c.get("/docs").status_code == 404
        assert c.get("/redoc").status_code == 404
        assert c.get("/openapi.json").status_code == 404        # E7: solo con --dev o con el token


def test_sin_cors(abrir_api):
    with abrir_api() as (c, _):
        r = c.get("/api/estado", headers={"Origin": "https://otro-sitio.example"})
    assert "access-control-allow-origin" not in r.headers


# =============================================================================
#  Estado y ciclo de vida
# =============================================================================
def test_estado_con_tunel(abrir_api):
    with abrir_api() as (c, s):
        d = c.get("/api/estado").json()
        assert s.voz.cargado and s.tunel.iniciado
    assert s.tunel.detenido                                       # al cerrar se detiene el túnel
    assert d["tunel"] == {"estado": "activo", "url": TunelFalso.URL}
    assert d["url_publica"] == TunelFalso.URL
    assert d["url_local"] == f"http://{IP_LOCAL}:8000"
    assert d["sesion"] == s.sesion


def test_estado_sin_tunel_y_sin_voz(abrir_api):
    with abrir_api(sin_tunel=True, sin_voz=True) as (c, s):
        d = c.get("/api/estado").json()
        assert not s.tunel.iniciado and not s.voz.cargado
    assert d["url_publica"] == f"http://{IP_LOCAL}:8000"
    assert d["voz"]["estado"] == "desactivado"


def test_previa(abrir_api):
    with abrir_api() as (c, _):
        r = c.post("/api/previa", json={"texto": "Señor"})
    assert r.status_code == 200
    assert r.json() == {"pasos": [{"c": "S", "tipo": "nd"}, {"c": "E", "tipo": "ok"}, {"c": "Ñ", "tipo": "aprox"},
                                  {"c": "O", "tipo": "ok"}, {"c": "R", "tipo": "ok"}]}


# =============================================================================
#  Mensajes
# =============================================================================
def test_enviar_mensaje_y_deletrearlo(abrir_api):
    with abrir_api() as (c, s):
        r = c.post("/api/mensaje", json={"texto": "Hola", "cliente": "A"})
        assert r.status_code == 200
        assert r.json() == {"id": 1, "texto": "hola", "sesion": s.sesion}
        esperar(lambda: len(s.historial) == 1)
        assert s.mano.ordenes == ["o", "l", "a", "reset"]


@pytest.mark.parametrize("cuerpo, codigo, detalle", [
    ({"texto": "a" * 61, "cliente": "A"}, 400, "Máximo 60 caracteres."),
    ({"texto": "  " + "a" * 60 + "  ", "cliente": "A"}, 200, None),       # se cuenta sin espacios de los bordes
    ({"texto": "gh", "cliente": "A"}, 400, "La mano todavía no puede hacer esas letras"),
    ({"texto": "¡¿?!", "cliente": "A"}, 400, "Escribe al menos una letra."),
])
def test_validaciones_de_mensaje(abrir_api, cuerpo, codigo, detalle):
    with abrir_api() as (c, _):
        r = c.post("/api/mensaje", json=cuerpo)
    assert r.status_code == codigo
    if detalle:
        assert r.json() == {"detail": detalle}


@pytest.mark.parametrize("cuerpo", [{}, {"texto": 5}, {"cliente": "A"}])
def test_cuerpo_invalido(abrir_api, cuerpo):
    with abrir_api() as (c, _):
        assert c.post("/api/mensaje", json=cuerpo).status_code == 422


def test_cliente_por_defecto_y_recortado(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "a"
        c.post("/api/mensaje", json={"texto": "a"})
        s.mano.llego.wait(5)
        r = c.post("/api/mensaje", json={"texto": "b", "cliente": "x" * 100})
        assert s.actual["cliente"] == "anonimo"
        assert r.status_code == 422 and s.cola == []                   # E7: ya no se recorta, se rechaza


def test_limite_por_cliente_y_cancelar(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "a"
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "A"}).status_code == 200
        s.mano.llego.wait(5)
        assert c.post("/api/mensaje", json={"texto": "b", "cliente": "A"}).status_code == 200
        r = c.post("/api/mensaje", json={"texto": "c", "cliente": "A"})
        assert r.status_code == 400
        assert r.json() == {"detail": "Ya tienes 2 mensajes en espera. Espera a que la mano los haga."}
        assert c.post("/api/mensaje", json={"texto": "d", "cliente": "B"}).status_code == 200

        r = c.delete("/api/mensaje/2", params={"cliente": "B"})          # no es suyo
        assert r.status_code == 404 and r.json() == {"detail": "Ese mensaje ya no se puede cancelar."}
        assert c.delete("/api/mensaje/1", params={"cliente": "A"}).status_code == 404   # en curso
        r = c.delete("/api/mensaje/2", params={"cliente": "A"})
        assert r.status_code == 200 and r.json() == {"ok": True}
        assert c.delete("/api/mensaje/2").status_code == 422                 # falta ?cliente=
        assert [m["id"] for m in s.cola] == [3]


# =============================================================================
#  Voz
# =============================================================================
def subir(c, datos=AUDIO_WEBM, nombre="voz.m4a"):
    return c.post("/api/transcribir", files={"audio": (nombre, io.BytesIO(datos), "audio/mp4")})


def test_transcribir(abrir_api):
    with abrir_api() as (c, s):
        r = subir(c)
        assert r.status_code == 200 and r.json() == {"texto": "hola jurado"}
        ruta, existia, datos = s.voz.recibidos[0]
    assert existia and datos == AUDIO_WEBM
    assert ruta.endswith(".m4a") and os.path.basename(ruta).startswith("voz_")
    assert not os.path.exists(ruta)                                   # el archivo temporal se borra


def test_transcribir_sufijo_por_defecto(abrir_api):
    with abrir_api() as (c, s):
        subir(c, nombre="grabacion")
        assert s.voz.recibidos[0][0].endswith(".webm")


def test_transcripcion_se_recorta_a_60(abrir_api):
    with abrir_api() as (c, s):
        s.voz.texto = "x" * 80
        assert subir(c).json() == {"texto": "x" * 60}


def test_transcribir_errores(abrir_api):
    with abrir_api() as (c, s):
        r = subir(c, datos=b"")
        assert r.status_code == 400 and r.json() == {"detail": "No llegó audio."}
        relleno = 10 * 1024 * 1024 - len(AUDIO_WEBM)
        r = subir(c, datos=AUDIO_WEBM + b"0" * (relleno + 1))
        assert r.status_code == 413 and r.json() == {"detail": "El audio es muy largo. Graba máximo 10 segundos."}
        assert subir(c, datos=AUDIO_WEBM + b"0" * relleno).status_code == 200

        s.voz.error = RuntimeError("audio dañado")
        r = subir(c)
        assert r.status_code == 500
        assert r.json() == {"detail": "No se pudo entender el audio. Intenta de nuevo o escríbelo."}
        assert not os.path.exists(s.voz.recibidos[-1][0])             # también se borra si falla

        s.voz.estado = "cargando"
        r = subir(c)
        assert r.status_code == 503
        assert r.json() == {"detail": "El reconocimiento de voz se está cargando, intenta en unos segundos."}


# =============================================================================
#  Rutas solo desde el PC
# =============================================================================
@pytest.mark.parametrize("ruta", ["/api/mano/reconectar", "/api/mano/saltar"])
def test_admin_rechaza_celulares_y_tunel(abrir_api, ruta):
    with abrir_api() as (c, _):                                       # IP de un celular
        r = c.post(ruta)
        assert r.status_code == 403 and r.json() == {"detail": "Solo desde el PC del proyector."}
    with abrir_api(desde=PC) as (c, _):                               # por el túnel: llega de 127.0.0.1
        r = c.post(ruta, headers={"cf-connecting-ip": "203.0.113.7"})
        assert r.status_code == 403


def test_reconectar_desde_el_pc(abrir_api):
    with abrir_api(desde=PC) as (c, s):
        esperar(lambda: s.mano.conexiones >= 1)
        n = s.mano.conexiones
        r = c.post("/api/mano/reconectar", headers=admin(c))           # E7: con el token de /pantalla
        assert r.status_code == 200 and r.json() == {"ok": True}
        esperar(lambda: s.mano.conexiones == n + 1)


def test_saltar_desde_el_pc(abrir_api):
    with abrir_api(desde="::1") as (c, s):
        encabezados = admin(c)                                          # E7: con el token de /pantalla
        r = c.post("/api/mano/saltar", headers=encabezados)
        assert r.status_code == 404 and r.json() == {"detail": "No hay ningún mensaje en curso."}
        s.mano.bloquear_en = "b"
        c.post("/api/mensaje", json={"texto": "abcd", "cliente": "A"})
        s.mano.llego.wait(5)
        assert c.post("/api/mano/saltar", headers=encabezados).json() == {"ok": True}
        s.mano.soltar.set()
        esperar(lambda: len(s.historial) == 1)
        assert s.mano.ordenes == ["a", "b", "reset"]
        assert c.get("/api/estado").json()["historial"][0]["saltado"] is True


# =============================================================================
#  WebSocket
# =============================================================================
def recibir_hasta(ws, condicion, maximo=50):
    for _ in range(maximo):
        d = ws.receive_json()
        if d.get("tipo") == "estado" and condicion(d):
            return d
    raise AssertionError("no llegó el estado esperado")


def test_websocket_estado_inicial(abrir_api):
    with abrir_api() as (c, s):
        with c.websocket_connect("/ws") as ws:
            d = ws.receive_json()
    assert d["tipo"] == "estado"
    assert d["sesion"] == s.sesion
    assert d["actual"] is None and d["cola"] == []


def test_websocket_sigue_un_mensaje(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "b"
        with c.websocket_connect("/ws") as ws:
            ws.receive_json()
            c.post("/api/mensaje", json={"texto": "ab", "cliente": "A"})
            d = recibir_hasta(ws, lambda d: d["actual"] and d["actual"]["i"] == 1)
            assert d["actual"]["texto"] == "ab"
            assert [p["r"] for p in d["actual"]["pasos"]] == ["ok", None]
            c.post("/api/mensaje", json={"texto": "c", "cliente": "B"})
            d = recibir_hasta(ws, lambda d: d["cola"])
            assert d["cola"] == [{"id": 2, "texto": "c", "pid": ANY, "nombre": None}]    # E8: autor
            s.mano.soltar.set()
            d = recibir_hasta(ws, lambda d: len(d["historial"]) == 2 and d["actual"] is None)
    assert [m["texto"] for m in d["historial"]] == ["c", "ab"]


def test_varios_websockets_reciben_lo_mismo(abrir_api):
    with abrir_api() as (c, _):
        with c.websocket_connect("/ws") as w1, c.websocket_connect("/ws") as w2:
            w1.receive_json(); w2.receive_json()
            c.post("/api/mensaje", json={"texto": "a", "cliente": "A"})
            for ws in (w1, w2):
                recibir_hasta(ws, lambda d: d["historial"])

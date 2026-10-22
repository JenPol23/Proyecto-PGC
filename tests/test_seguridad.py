"""Medidas de seguridad de la etapa E7 (docs/ARQUITECTURA.md §B)."""
import io
import re
import tempfile
from pathlib import Path

import pytest
from starlette.websockets import WebSocketDisconnect

from conftest import AUDIO_WEBM, TunelFalso, admin, token_de_pantalla

PC = "127.0.0.1"
TUNEL = {"cf-connecting-ip": "203.0.113.7"}


# =============================================================================
#  M1 · Token de administrador
# =============================================================================
def test_token_solo_en_la_pantalla_del_pc(abrir_api):
    with abrir_api(desde=PC) as (c, s):
        token = token_de_pantalla(c)
        assert len(token) >= 40
        assert token_de_pantalla(c) == token                       # el mismo durante todo el arranque
        # Por el túnel (cloudflared conecta desde 127.0.0.1) la pantalla se sirve sin token
        r = c.get("/pantalla", headers=TUNEL)
        assert r.status_code == 200 and '<meta name="pgc-admin" content="">' in r.text
        # DNS rebinding: un dominio ajeno que apunta a 127.0.0.1
        r = c.get("/pantalla", headers={"Host": "atacante.example:8000"})
        assert '<meta name="pgc-admin" content="">' in r.text
    with abrir_api() as (c, _):                                    # celular
        assert token_de_pantalla(c) == ""


@pytest.mark.parametrize("encabezados, codigo", [
    ({}, 403),                                                     # sin token (CSRF desde otra página)
    ({"X-PGC-Admin": "falso"}, 403),
    (None, 404),                                                   # token correcto → llega a la ruta
])
def test_admin_exige_token(abrir_api, encabezados, codigo):
    with abrir_api(desde=PC) as (c, _):
        r = c.post("/api/mano/saltar", headers=admin(c) if encabezados is None else encabezados)
        assert r.status_code == codigo


def test_token_no_sirve_fuera_del_pc(abrir_api):
    with abrir_api(desde=PC) as (c, _):
        h = admin(c)
        assert c.post("/api/mano/saltar", headers={**h, **TUNEL}).status_code == 403
        assert c.post("/api/mano/saltar", headers={**h, "Host": "atacante.example"}).status_code == 403
        assert c.post("/api/mano/saltar", headers={**h, "X-Forwarded-For": "1.2.3.4"}).status_code == 403


def test_token_no_aparece_en_el_log(abrir_api, registro):
    with abrir_api(desde=PC) as (c, _):
        token = token_de_pantalla(c)
    assert token not in "\n".join(registro)


# =============================================================================
#  M8 · Documentación solo con --dev o con el token
# =============================================================================
def test_documentacion_en_modo_dev(abrir_api):
    with abrir_api(dev=True) as (c, _):
        assert c.get("/openapi.json").status_code == 200
        r = c.get("/docs")
        assert r.status_code == 200 and "swagger" in r.text.lower()


def test_documentacion_con_token(abrir_api):
    with abrir_api(desde=PC) as (c, _):
        token = token_de_pantalla(c)
        assert c.get("/openapi.json").status_code == 404
        assert c.get("/openapi.json", headers={"X-PGC-Admin": token}).status_code == 200
        r = c.get("/docs", params={"token": token})
        assert r.status_code == 200 and f"/openapi.json?token={token}" in r.text
        assert c.get("/docs", params={"token": token}, headers=TUNEL).status_code == 404


def test_404_amable(abrir_api):
    with abrir_api() as (c, _):
        assert c.get("/no-existe").json() == {"detail": "No encontramos esa página."}


# =============================================================================
#  M2 · Validación con mensajes amables
# =============================================================================
@pytest.mark.parametrize("cuerpo, detalle", [
    ({"texto": "a" * 201, "cliente": "A"}, "El mensaje es muy largo (máximo 60 caracteres)."),
    ({"texto": "hola\x00", "cliente": "A"}, "El mensaje tiene caracteres que no se pueden mostrar."),
    ({"texto": "hola", "cliente": "con espacios"}, "Recarga la página e intenta de nuevo."),
    ({"texto": "hola", "cliente": "<script>"}, "Recarga la página e intenta de nuevo."),
    ({"texto": 5, "cliente": "A"}, "Escribe tu mensaje de nuevo, por favor."),
    ({}, "Escribe tu mensaje de nuevo, por favor."),
])
def test_validacion_amable(abrir_api, cuerpo, detalle):
    with abrir_api() as (c, _):
        r = c.post("/api/mensaje", json=cuerpo)
    assert r.status_code == 422 and r.json() == {"detail": detalle}


def test_saltos_de_linea_si_se_permiten(abrir_api):
    with abrir_api() as (c, _):
        r = c.post("/api/mensaje", json={"texto": "hola\njurado", "cliente": "A"})
    assert r.status_code == 200 and r.json()["texto"] == "hola jurado"


def test_previa_tambien_limita_el_texto(abrir_api):
    with abrir_api() as (c, _):
        assert c.post("/api/previa", json={"texto": "a" * 201}).status_code == 422
        assert c.post("/api/previa", json={"texto": "a" * 200}).status_code == 200


def test_cancelar_valida_el_cliente(abrir_api):
    with abrir_api() as (c, _):
        assert c.delete("/api/mensaje/1", params={"cliente": "no valido!"}).status_code == 422


# =============================================================================
#  M4 · Tamaño del cuerpo
# =============================================================================
def test_cuerpo_json_demasiado_grande(abrir_api):
    with abrir_api() as (c, _):
        r = c.post("/api/mensaje", content=b'{"texto": "' + b"a" * 20000 + b'"}',
                   headers={"Content-Type": "application/json"})
    assert r.status_code == 413 and r.json() == {"detail": "El mensaje es muy largo."}


def test_cuerpo_sin_content_length_tambien_se_corta(abrir_api):
    def trozos():
        for _ in range(40):
            yield b"a" * 1024
    with abrir_api() as (c, _):
        r = c.post("/api/previa", content=trozos(), headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_audio_demasiado_grande_antes_de_leerlo(abrir_api):
    with abrir_api() as (c, s):
        r = c.post("/api/transcribir", content=b"x", headers={"Content-Length": str(50 * 1024 * 1024),
                                                              "Content-Type": "multipart/form-data; boundary=x"})
        assert r.status_code == 413
        assert s.voz.recibidos == []


# =============================================================================
#  M3 · Audio
# =============================================================================
def subir(c, datos=AUDIO_WEBM, tipo="audio/webm", nombre="voz.webm", cliente=None):
    datos_form = {"cliente": cliente} if cliente else None
    return c.post("/api/transcribir", files={"audio": (nombre, io.BytesIO(datos), tipo)}, data=datos_form)


@pytest.mark.parametrize("cabecera", [
    b"\x1a\x45\xdf\xa3....",                  # webm (Android)
    b"\x00\x00\x00\x1cftypM4A ",               # m4a (iPhone)
    b"\x00\x00\x00\x18ftyp3gp4",               # 3gp (grabadora de Android)
    b"OggS\x00\x02",
    b"RIFF\x24\x00\x00\x00WAVEfmt ",
    b"ID3\x03\x00",
    b"\xff\xfb\x90\x00",                       # mp3 sin etiquetas
    b"\xff\xf1\x50\x80",                       # aac
    b"#!AMR\n",
])
def test_formatos_de_audio_aceptados(abrir_api, cabecera):
    with abrir_api() as (c, _):
        assert subir(c, datos=cabecera + b"\x00" * 32).status_code == 200


@pytest.mark.parametrize("datos, tipo", [
    (b"<html><script>alert(1)</script>", "audio/webm"),       # la firma no es de audio
    (b"MZ\x90\x00 ejecutable", "application/octet-stream"),
    (AUDIO_WEBM, "text/html"),                                 # el tipo declarado no es de audio
    (AUDIO_WEBM, "image/png"),
])
def test_rechaza_lo_que_no_es_audio(abrir_api, datos, tipo):
    with abrir_api() as (c, s):
        r = subir(c, datos=datos, tipo=tipo)
        assert r.status_code == 415
        assert r.json() == {"detail": "Ese archivo no parece un audio. Graba de nuevo con el botón."}
        assert s.voz.recibidos == []


def test_audio_demasiado_largo_en_segundos(abrir_api):
    with abrir_api() as (c, s):
        s.voz.segundos = 16.0
        r = subir(c)
        assert r.status_code == 413 and r.json() == {"detail": "El audio es muy largo. Graba máximo 10 segundos."}
        assert s.voz.recibidos == []                               # no llegó a Whisper
        s.voz.segundos = None                                      # duración desconocida: decide Whisper
        assert subir(c).status_code == 200


def test_temporales_en_carpeta_propia_y_limpieza_al_arrancar(abrir_api):
    carpeta = Path(tempfile.gettempdir()) / "pgc_voz"
    carpeta.mkdir(exist_ok=True)
    viejo = carpeta / "voz_de_una_caida.webm"
    viejo.write_bytes(b"x")
    with abrir_api() as (c, s):
        assert not viejo.exists()                                   # se limpió al arrancar
        subir(c)
        assert Path(s.voz.recibidos[0][0]).parent == carpeta
        assert not Path(s.voz.recibidos[0][0]).exists()


def test_nombre_de_archivo_raro_no_cambia_la_extension(abrir_api):
    with abrir_api() as (c, s):
        subir(c, nombre="..\\..\\evil.exe;rm -rf")
        assert s.voz.recibidos[0][0].endswith(".webm")


def test_demasiadas_transcripciones_a_la_vez(abrir_api):
    with abrir_api(voz_max_en_espera=3) as (c, _):
        c.app.state.voz_en_curso = 4                                # 1 transcribiendo + 3 esperando
        r = subir(c)
        assert r.status_code == 429
        assert r.json() == {"detail": "Hay varias personas usando la voz, intenta en unos segundos."}
        c.app.state.voz_en_curso = 0
        assert subir(c).status_code == 200


def test_error_de_whisper_no_filtra_detalles(abrir_api, registro):
    with abrir_api() as (c, s):
        s.voz.error = RuntimeError(r"C:\Users\secreto\ruta interna")
        subir(c)
    assert not any("secreto" in linea for linea in registro)


# =============================================================================
#  M5 · Límite de peticiones
# =============================================================================
def test_limite_por_ip(abrir_api):
    with abrir_api(lim_mensaje_ip=2, max_pendientes_cliente=10) as (c, _):
        for k in range(2):
            assert c.post("/api/mensaje", json={"texto": "a", "cliente": f"c{k}"}).status_code == 200
        r = c.post("/api/mensaje", json={"texto": "a", "cliente": "otro"})
    assert r.status_code == 429
    assert r.json() == {"detail": "Vas muy rápido, espera unos segundos."}
    assert int(r.headers["Retry-After"]) >= 1


def test_limite_por_cliente(abrir_api):
    with abrir_api(lim_mensaje_cliente=1, max_pendientes_cliente=10) as (c, _):
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "A"}).status_code == 200
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "A"}).status_code == 429
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "B"}).status_code == 200


def test_por_el_tunel_cuenta_la_ip_real(abrir_api):
    with abrir_api(desde=PC, lim_mensaje_ip=1, max_pendientes_cliente=10) as (c, _):
        def enviar(ip, cliente):
            return c.post("/api/mensaje", json={"texto": "a", "cliente": cliente},
                          headers={"cf-connecting-ip": ip}).status_code
        assert enviar("198.51.100.1", "a1") == 200
        assert enviar("198.51.100.1", "a2") == 429
        assert enviar("198.51.100.2", "b1") == 200               # otro celular por el túnel


def test_un_celular_no_puede_falsificar_su_ip(abrir_api):
    with abrir_api(lim_mensaje_ip=1, max_pendientes_cliente=10) as (c, _):
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "a1"},
                      headers={"cf-connecting-ip": "1.1.1.1"}).status_code == 200
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "a2"},
                      headers={"cf-connecting-ip": "2.2.2.2"}).status_code == 429


def test_el_pc_no_tiene_limite(abrir_api):
    with abrir_api(desde=PC, lim_previa_ip=1, lim_general_ip=1) as (c, _):
        for _ in range(5):
            assert c.post("/api/previa", json={"texto": "a"}).status_code == 200


def test_limite_general(abrir_api):
    with abrir_api(lim_general_ip=3) as (c, _):
        codigos = [c.get("/api/estado").status_code for _ in range(4)]
    assert codigos == [200, 200, 200, 429]


def test_limite_de_transcripcion_por_cliente(abrir_api):
    with abrir_api(lim_transcribir_cliente=1) as (c, _):
        assert subir(c, cliente="A").status_code == 200
        assert subir(c, cliente="A").status_code == 429
        assert subir(c, cliente="B").status_code == 200


# =============================================================================
#  M6 · WebSocket
# =============================================================================
def conectar(c, origen=None, **encabezados):
    if origen:
        encabezados["origin"] = origen
    return c.websocket_connect("/ws", headers=encabezados)


@pytest.mark.parametrize("origen", ["http://testserver", TunelFalso.URL, "http://192.168.0.10:8000"])
def test_websocket_acepta_las_paginas_propias(abrir_api, origen):
    with abrir_api() as (c, _):
        with conectar(c, origen) as ws:
            assert ws.receive_json()["tipo"] == "estado"


def test_websocket_rechaza_otros_sitios(abrir_api):
    with abrir_api() as (c, _):
        with pytest.raises(WebSocketDisconnect) as ex:
            with conectar(c, "https://sitio-ajeno.example") as ws:
                ws.receive_json()
    assert ex.value.code == 1008


def test_websocket_limite_por_ip(abrir_api):
    with abrir_api(ws_max_por_ip=1) as (c, _):
        with conectar(c) as w1:
            w1.receive_json()
            with pytest.raises(WebSocketDisconnect) as ex:
                with conectar(c) as w2:
                    w2.receive_json()
            assert ex.value.code == 1013
        with conectar(c) as w3:                                  # al cerrar el primero, vuelve a haber cupo
            assert w3.receive_json()["tipo"] == "estado"
        assert c.app.state.ws_total == 0 and c.app.state.ws_por_ip == {}


# =============================================================================
#  M7 · Encabezados y CSP
# =============================================================================
@pytest.mark.parametrize("ruta", ["/", "/pantalla", "/api/estado", "/qr.png", "/logo-udec.png", "/no-existe"])
def test_encabezados_de_seguridad(abrir_api, ruta):
    with abrir_api() as (c, _):
        r = c.get(ruta)
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["referrer-policy"] == "no-referrer"
    assert r.headers["x-frame-options"] == "DENY"
    assert "microphone=(self)" in r.headers["permissions-policy"]
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]
    assert "access-control-allow-origin" not in r.headers


@pytest.mark.parametrize("ruta", ["/", "/pantalla"])
def test_csp_con_nonce_en_cada_script(abrir_api, ruta):
    with abrir_api() as (c, _):
        r = c.get(ruta)
        r2 = c.get(ruta)
    nonce = re.search(r"'nonce-([^']+)'", r.headers["content-security-policy"]).group(1)
    scripts = re.findall(r"<script[^>]*>", r.text)
    assert scripts and all(s == f'<script nonce="{nonce}">' for s in scripts)
    assert nonce not in r2.text                                     # cambia en cada respuesta
    assert "'unsafe-inline'" not in r.headers["content-security-policy"].split("script-src")[1].split(";")[0]
    assert "connect-src 'self' ws://testserver wss://testserver" in r.headers["content-security-policy"]


def test_csp_no_acepta_un_host_raro(abrir_api):
    with abrir_api() as (c, _):
        r = c.get("/", headers={"Host": "x; script-src *"})
    assert "script-src *" not in r.headers["content-security-policy"]


@pytest.mark.parametrize("pagina", ["movil.html", "pantalla.html"])
def test_innerhtml_solo_con_constantes(carpeta_web, pagina):
    permitidos = {"b.innerHTML = oscuro ? SOL : LUNA;", "pos.innerHTML = '<span class=\"vivo-punto\"></span>';"}
    for linea in (carpeta_web / pagina).read_text(encoding="utf-8").splitlines():
        if "innerHTML" in linea:
            assert linea.strip() in permitidos, linea.strip()


# =============================================================================
#  M9 · Filtro de palabras  ·  M10 · Registros
# =============================================================================
@pytest.mark.parametrize("texto", ["gonorrea", "h p", "hola malparido", "put4"])
def test_filtro_de_palabras(abrir_api, texto):
    with abrir_api() as (c, s):
        r = c.post("/api/mensaje", json={"texto": texto, "cliente": "A"})
        assert r.status_code == 400
        assert r.json() == {"detail": "Ese mensaje no se puede mostrar. Intenta con otras palabras."}
        assert s.cola == [] and s.actual is None


def test_el_log_no_guarda_textos_por_defecto(abrir_api, registro):
    with abrir_api() as (c, s):
        c.post("/api/mensaje", json={"texto": "secreto", "cliente": "cliente123"})
        c.post("/api/mensaje", json={"texto": "gonorrea", "cliente": "cliente123"})
    log = "\n".join(registro)
    assert "secreto" not in log and "SECRETO" not in log and "gonorrea" not in log
    assert "cliente123" not in log and "testclient" not in log
    assert "(7 letras" in log


def test_log_textos_para_depurar(abrir_api, registro):
    with abrir_api(log_textos=True) as (c, _):
        c.post("/api/mensaje", json={"texto": "hola", "cliente": "A"})
    assert "'hola'" in "\n".join(registro)

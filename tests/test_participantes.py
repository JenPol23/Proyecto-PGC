"""Participantes (E8): nombre opcional, «Mensaje de», bloqueo por sesión y nada en disco."""
import ast

import pytest

from conftest import AUDIO_WEBM, RAIZ, admin, esperar

from pgc.dominio.participante import MAX_NOMBRE, normalizar_nombre

PC = "127.0.0.1"
PAUSA = "El presentador pausó tu participación en esta sesión. ¡Gracias por participar!"


def registrar(c, cliente, nombre=None):
    return c.post("/api/participante", json={"cliente": cliente, "nombre": nombre})


def enviar(c, cliente, texto="hola"):
    return c.post("/api/mensaje", json={"texto": texto, "cliente": cliente})


# ---------------------------------------------------------------- nombre
@pytest.mark.parametrize("entrada, esperado", [
    ("Ana", "Ana"), ("  ana   maría ", "ana maría"), ("José-Luis", "José-Luis"), ("O'Neil", "O'Neil"),
    ("Jurado 2", "Jurado 2"), ("", None), ("   ", None), (None, None), ("x" * MAX_NOMBRE, "x" * MAX_NOMBRE),
])
def test_normalizar_nombre(entrada, esperado):
    assert normalizar_nombre(entrada) == esperado


@pytest.mark.parametrize("entrada", ["x" * 21, "<b>Ana</b>", "Ana😀", "ana@correo.com", "a/b"])
def test_nombre_invalido(entrada):
    with pytest.raises(ValueError, match="Usa solo letras"):
        normalizar_nombre(entrada)


def test_registrar_devuelve_un_alias_opaco(abrir_api):
    with abrir_api() as (c, _):
        r = registrar(c, "celular-de-ana", "  Ana ")
        assert r.status_code == 200
        d = r.json()
        assert d["nombre"] == "Ana" and d["bloqueado"] is False
        assert d["pid"].startswith("p") and "celular-de-ana" not in d["pid"]
        assert registrar(c, "celular-de-ana", "Ana María").json()["pid"] == d["pid"]   # mismo celular, mismo alias
        assert registrar(c, "otro", "Ana").json()["pid"] != d["pid"]


@pytest.mark.parametrize("nombre, codigo, detalle", [
    ("x" * 21, 400, "Usa solo letras en tu nombre (máximo 20)."),
    ("<script>", 400, "Usa solo letras en tu nombre (máximo 20)."),
    ("gonorrea", 400, "Ese nombre no se puede mostrar. Prueba con otro."),
    ("x" * 61, 422, "Usa solo letras en tu nombre (máximo 20)."),
    ("Ana\x00", 422, "Usa solo letras en tu nombre (máximo 20)."),
])
def test_nombre_rechazado_con_mensaje_amable(abrir_api, nombre, codigo, detalle):
    with abrir_api() as (c, _):
        r = registrar(c, "A", nombre)
    assert r.status_code == codigo and r.json() == {"detail": detalle}


def test_mensaje_de_en_el_proyector(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "o"                               # la H no la hace la mano: se bloquea en la O
        registrar(c, "A", "Ana")
        enviar(c, "A", "hola")
        s.mano.llego.wait(5)
        enviar(c, "B", "uña")                                  # B no dio nombre
        registrar(c, "A", "Ana María")                         # cambiar el nombre no cambia lo ya enviado
        d = c.get("/api/estado").json()
        assert d["actual"]["nombre"] == "Ana"
        assert [(m["texto"], m["nombre"]) for m in d["cola"]] == [("uña", None)]


# ---------------------------------------------------------------- bloqueo
def test_bloquear_exige_el_token(abrir_api):
    with abrir_api() as (c, _):
        pid = registrar(c, "A").json()["pid"]
        assert c.post(f"/api/participantes/{pid}/bloquear").status_code == 403
    with abrir_api(desde=PC) as (c, _):
        pid = registrar(c, "A").json()["pid"]
        r = c.post(f"/api/participantes/{pid}/bloquear", headers={**admin(c), "cf-connecting-ip": "1.2.3.4"})
        assert r.status_code == 403


def test_bloquear_cancela_pendientes_y_avisa(abrir_api):
    with abrir_api(desde=PC, max_pendientes_cliente=5) as (c, s):
        s.mano.bloquear_en = "a"
        pid = registrar(c, "A", "Pedro").json()["pid"]
        enviar(c, "A", "a")                                    # en curso
        s.mano.llego.wait(5)
        enviar(c, "A", "b"); enviar(c, "A", "c"); enviar(c, "B", "d")
        with c.websocket_connect("/ws") as ws:
            ws.receive_json()
            r = c.post(f"/api/participantes/{pid}/bloquear", headers=admin(c))
            assert r.status_code == 200 and r.json() == {"ok": True, "cancelados": 2, "saltado": True}
            d = ws.receive_json()
            while pid not in d.get("bloqueados", []):
                d = ws.receive_json()
        assert [m["texto"] for m in d["cola"]] == ["d"]        # solo quedan los de otros
        assert s.cola[0]["texto"] == "d"
        s.mano.soltar.set()
        esperar(lambda: s.historial and s.historial[-1]["texto"] == "a")
        assert s.historial[-1]["saltado"] is True              # su mensaje en curso también se saltó
        # Su celular recibe un aviso amable al intentar participar
        r = enviar(c, "A", "otro")
        assert r.status_code == 403 and r.json() == {"detail": PAUSA}
        r = c.post("/api/transcribir", files={"audio": ("v.webm", AUDIO_WEBM, "audio/webm")}, data={"cliente": "A"})
        assert r.status_code == 403 and r.json() == {"detail": PAUSA}
        assert registrar(c, "A", "Otro nombre").json() == {"pid": pid, "nombre": "Pedro", "bloqueado": True}
        assert enviar(c, "B", "e").status_code == 200          # los demás siguen igual
        s.mano.soltar.set()


def test_desbloquear(abrir_api):
    with abrir_api(desde=PC) as (c, _):
        pid = registrar(c, "A").json()["pid"]
        h = admin(c)
        c.post(f"/api/participantes/{pid}/bloquear", headers=h)
        assert enviar(c, "A").status_code == 403
        assert c.post(f"/api/participantes/{pid}/desbloquear", headers=h).json() == {"ok": True}
        assert enviar(c, "A").status_code == 200
        assert c.get("/api/estado").json()["bloqueados"] == []


def test_bloquear_a_otro_no_salta_el_mensaje_en_curso(abrir_api):
    with abrir_api(desde=PC) as (c, s):
        s.mano.bloquear_en = "a"
        enviar(c, "A", "a")
        s.mano.llego.wait(5)
        pid_b = registrar(c, "B").json()["pid"]
        assert c.post(f"/api/participantes/{pid_b}/bloquear", headers=admin(c)).json()["saltado"] is False
        s.mano.soltar.set()
        esperar(lambda: len(s.historial) == 1)
        assert not s.historial[0].get("saltado")


def test_deshacer_no_recupera_el_mensaje_saltado(abrir_api):
    with abrir_api(desde=PC) as (c, s):
        s.mano.bloquear_en = "b"
        pid = registrar(c, "A").json()["pid"]
        enviar(c, "A", "abc")
        s.mano.llego.wait(5)
        h = admin(c)
        c.post(f"/api/participantes/{pid}/bloquear", headers=h)
        c.post(f"/api/participantes/{pid}/desbloquear", headers=h)
        s.mano.soltar.set()
        esperar(lambda: len(s.historial) == 1)
        assert s.historial[0]["saltado"] is True and s.mano.ordenes == ["a", "b", "reset"]
        assert s.cola == []


def test_participante_desconocido(abrir_api):
    with abrir_api(desde=PC) as (c, _):
        r = c.post("/api/participantes/pdeadbeef/bloquear", headers=admin(c))
    assert r.status_code == 404 and r.json() == {"detail": "No encontramos a ese participante."}


def test_quien_envia_sin_registrarse_tambien_tiene_alias(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "a"
        enviar(c, "nuevo", "a")
        s.mano.llego.wait(5)
        assert c.get("/api/estado").json()["actual"]["pid"].startswith("p")


# ---------------------------------------------------------------- privacidad
def test_el_nombre_no_queda_en_el_log(abrir_api, registro):
    with abrir_api(desde=PC) as (c, s):
        pid = registrar(c, "A", "Zacarías").json()["pid"]
        enviar(c, "A", "hola")
        c.post(f"/api/participantes/{pid}/bloquear", headers=admin(c))
        esperar(lambda: len(s.historial) == 1)
    assert not any("Zacar" in linea for linea in registro)


@pytest.mark.parametrize("ruta", ["pgc/aplicacion/participantes.py", "pgc/dominio/participante.py"])
def test_participantes_no_escriben_en_disco(ruta):
    arbol = ast.parse((RAIZ / ruta).read_text(encoding="utf-8"))
    nombres = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)} | \
              {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    assert not nombres & {"open", "write_text", "write_bytes", "dump", "Path", "sqlite3", "shelve"}

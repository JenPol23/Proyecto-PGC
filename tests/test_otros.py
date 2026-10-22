"""Túnel, voz y páginas web (caracterización)."""
import re

import pytest


# ---------------------------------------------------------------- túnel
def test_patron_url_del_tunel(modulo_tunel):
    linea = "2026-10-14T10:00:00Z INF |  https://ips-jews-saints-textbooks.trycloudflare.com  |"
    assert modulo_tunel.PATRON_URL.search(linea).group(0) == "https://ips-jews-saints-textbooks.trycloudflare.com"
    assert modulo_tunel.PATRON_URL.search("https://example.com") is None


def test_tunel_sin_cloudflared(monkeypatch, modulo_tunel):
    monkeypatch.setattr(modulo_tunel, "buscar_cloudflared", lambda: None)
    cambios = []
    t = modulo_tunel.Tunel(8000, log=lambda m: None, al_cambiar=lambda: cambios.append(t.estado))
    assert (t.estado, t.url) == ("apagado", None)
    t._bucle()
    assert (t.estado, t.url) == ("no instalado", None)
    assert cambios == ["no instalado"]


def test_ip_local_devuelve_una_ipv4(modulo_tunel):
    assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", modulo_tunel.ip_local())


# ---------------------------------------------------------------- voz
def test_transcriptor_antes_de_cargar(modulo_voz):
    t = modulo_voz.Transcriptor(log=lambda m: None)
    assert (t.estado, t.dispositivo, t.listo) == ("sin cargar", None, False)
    with pytest.raises(RuntimeError):
        t.transcribir("no-existe.webm")


# ---------------------------------------------------------------- páginas
@pytest.mark.parametrize("pagina", ["movil.html", "pantalla.html"])
def test_paginas_sin_dependencias_de_internet(carpeta_web, pagina):
    html = (carpeta_web / pagina).read_text(encoding="utf-8")
    assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", html)
    assert "@import" not in html and "url(http" not in html


@pytest.mark.parametrize("pagina, ids", [
    ("movil.html", ["texto", "enviar", "previa", "grabar", "archivoAudio", "listaMios", "ahoraLetras", "chipConexion", "btnTema"]),
    ("pantalla.html", ["qr", "escenario", "palabra", "cola", "historial", "btnSaltar",
                       "btnReconectar", "btnCompleta", "btnTema", "desconectado", "alfabeto"]),
])
def test_paginas_tienen_sus_controles(carpeta_web, pagina, ids):
    html = (carpeta_web / pagina).read_text(encoding="utf-8")
    for i in ids:
        assert f'id="{i}"' in html, i


@pytest.mark.parametrize("pagina, rutas", [
    ("movil.html", ["/api/previa", "/api/mensaje", "/api/transcribir", "/api/estado", "/ws", "/logo-udec.png"]),
    ("pantalla.html", ["/qr.png", "/api/mano/reconectar", "/api/mano/saltar", "/api/previa", "/ws", "/logo-udec.png"]),
])
def test_paginas_usan_la_api(carpeta_web, pagina, rutas):
    html = (carpeta_web / pagina).read_text(encoding="utf-8")
    for r in rutas:
        assert r in html, r

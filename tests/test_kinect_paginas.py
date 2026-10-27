"""Pestaña Kinect del celular y vista Kinect del proyector (contenido de las páginas)."""
import importlib
import re
import sys

import pytest

from conftest import RAIZ


def test_el_celular_ya_no_dice_siguiente_fase(carpeta_web):
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    assert "siguiente fase" not in html.lower()
    for id_ in ("kinEstado", "kinTexto", "kinDetalle", "kinTomar", "kinSoltar", "kinOcupado", "avisoKinect",
                "kinModo", "kinGuardar", "kinLeer", "kinCallar", "kinVoz"):
        assert f'id="{id_}"' in html, id_
    for accion in ("iniciar", "detener", "espacio", "borrar", "limpiar", "terminar"):   # los controles que ella diseñó
        assert f'data-kin="{accion}"' in html, accion
    assert "Kinect no conectado" in html
    # Sus funciones y mensajes (pestaña de iniciar_pgc_integrado.py, incorporada a movil.html)
    for texto in ("Activar control", "Volver a espectador", "Guardar TXT", "Leer frase", "Detener voz",
                  "Modo espectador.", "Control del teléfono activo", "Leyendo...", "Lectura terminada.",
                  "Lectura detenida.", "Lectura detenida o audio no disponible.", "No hay una voz en español disponible",
                  'download = "texto_lsc.txt"', "speechSynthesis"):
        assert texto in html, texto


def test_guardar_y_leer_no_dependen_del_turno(carpeta_web):
    """Los espectadores también guardan y leen: esos botones no son controles del deletreo (data-kin),
    que son los únicos que el turno apaga."""
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    botones = html[html.index('<div id="kinMios"'):html.index('<p id="kinVoz"')]
    for id_ in ("kinGuardar", "kinLeer", "kinCallar"):
        boton = re.search(rf'<button id="{id_}"[^>]*>', botones).group(0)
        assert "data-kin" not in boton, id_
    assert 'data-kin="limpiar"' in botones
    assert 'querySelectorAll("[data-kin]")' in html and "!puede" in html


@pytest.mark.parametrize("pagina", ["movil.html", "pantalla.html"])
def test_hidden_siempre_oculta(carpeta_web, pagina):
    """El error de «Volver a espectador»: .btn { display: flex } le ganaba al atributo hidden."""
    assert "[hidden] { display: none !important; }" in (carpeta_web / pagina).read_text(encoding="utf-8") or \
        ".oculto, [hidden] { display: none !important; }" in (carpeta_web / pagina).read_text(encoding="utf-8")


def test_los_celulares_no_consultan_el_kinect(carpeta_web):
    """Todo llega por el WebSocket: la página del celular no consulta rutas del Kinect ni del detector."""
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    assert "/api/deletreo" not in html and "8765" not in html and "/api/kinect/imagen" not in html


def test_el_proyector_tiene_la_vista_kinect(carpeta_web):
    html = (carpeta_web / "pantalla.html").read_text(encoding="utf-8")
    for id_ in ("vKinect", "kinTexto", "kinCamara", "kinFrase", "kinTira", "ctrlKinect", "kinEco", "kinLiberar"):
        assert f'id="{id_}"' in html, id_
    assert "Próxima fase" not in html


def test_el_lanzador_antiguo_aun_arma_su_pagina():
    """iniciar_pgc_integrado.py (obsoleto, de Camila) busca marcas en movil.html: no se le rompe nada."""
    sys.path.insert(0, str(RAIZ))
    modulo = importlib.import_module("iniciar_pgc_integrado")
    html = modulo.construir_html()
    assert "De tus manos al texto" in html and 'id="codigoControlKinect"' in html     # su panel reemplazó al mío
    assert 'id="kinTomar"' not in html

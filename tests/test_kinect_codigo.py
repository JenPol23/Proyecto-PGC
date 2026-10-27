"""Código del proyector para tomar el turno del Kinect (el «Código del PC» del diseño de Camila).

Con PGC_KINECT_CODIGO=true (por defecto) el proyector muestra 6 dígitos que cambian en
cada arranque; el celular los escribe para «Activar control». Sigue habiendo un solo
turno a la vez, con liberación por inactividad, y bloquear a alguien le quita el turno.
"""
import re

import pytest

from conftest import admin, configuracion, esperar
from pgc import config
from pgc.aplicacion.turno import CodigoIncorrecto, TurnoKinect, TurnoOcupado


def tomar(c, cliente, codigo=None):
    return c.post("/api/kinect/turno", json={"cliente": cliente, "codigo": codigo})


def codigo_del_proyector(c):
    return c.get("/api/kinect/codigo", headers=admin(c)).json()["codigo"]


# ---------------------------------------------------------------- configuración
def test_el_codigo_esta_activo_por_defecto_y_se_desactiva_en_el_env(tmp_path):
    assert config.Config().kinect_codigo is True
    env = tmp_path / ".env"
    env.write_text("PGC_KINECT_CODIGO=false\n", encoding="utf-8")
    assert config.cargar([], entorno={}, archivo_env=env).kinect_codigo is False


# ---------------------------------------------------------------- dominio del turno
def test_codigo_de_6_digitos_distinto_en_cada_arranque():
    codigos = {TurnoKinect(con_codigo=True).codigo for _ in range(20)}
    assert all(re.fullmatch(r"\d{6}", c) for c in codigos)
    assert len(codigos) > 1


def test_sin_el_codigo_correcto_no_hay_turno():
    t = TurnoKinect(con_codigo=True)
    for malo in (None, "", "12345", "abcdef", str((int(t.codigo) + 1) % 10**6).zfill(6)):
        with pytest.raises(CodigoIncorrecto):
            t.tomar("A", "p1", "Ana", malo)
    assert t.instantanea() is None
    t.tomar("A", "p1", "Ana", " " + t.codigo[:3] + " " + t.codigo[3:])    # espacios del teclado: se aceptan
    assert t.es_dueno("A")


def test_con_el_codigo_sigue_habiendo_un_solo_turno_y_se_libera_solo():
    reloj = [0.0]
    t = TurnoKinect(segundos=120, reloj=lambda: reloj[0], con_codigo=True)
    t.tomar("A", "p1", "Ana", t.codigo)
    with pytest.raises(TurnoOcupado):
        t.tomar("B", "p2", "Beto", t.codigo)          # aunque sepa el código
    reloj[0] = 121
    t.tomar("B", "p2", "Beto", t.codigo)
    assert t.es_dueno("B")


def test_regenerar_cambia_el_codigo_y_quita_el_turno():
    t = TurnoKinect(con_codigo=True)
    viejo = t.codigo
    t.tomar("A", "p1", "Ana", viejo)
    nuevos = {t.regenerar_codigo() for _ in range(5)}
    assert t.version_codigo == 5 and t.instantanea() is None
    assert viejo != t.codigo or len(nuevos) > 1
    if viejo != t.codigo:
        with pytest.raises(CodigoIncorrecto):
            t.tomar("A", "p1", "Ana", viejo)


def test_sin_codigo_configurado_no_se_pide():
    t = TurnoKinect(con_codigo=False)
    assert t.codigo is None and t.regenerar_codigo() is None
    t.tomar("A", "p1", "Ana")
    assert t.es_dueno("A")


# ---------------------------------------------------------------- API
@pytest.fixture
def con_codigo(abrir_api, detector):
    def abrir(desde="testclient", **opciones):
        return abrir_api(desde, reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05,
                         kinect_codigo=True, **opciones)
    return abrir


@pytest.fixture
def detector():
    from detector_falso import DetectorFalso
    d = DetectorFalso()
    d.mantener_camara()
    yield d
    d.cerrar()


def test_el_celular_necesita_el_codigo_del_proyector(con_codigo):
    with con_codigo() as (c, s):
        codigo = s.senas.turno.codigo
        r = tomar(c, "A")
        assert r.status_code == 403 and "código" in r.json()["detail"].lower()
        assert tomar(c, "A", "000000" if codigo != "000000" else "111111").status_code == 403
        assert tomar(c, "A", "x" * 40).status_code == 422          # validación amable, en español
        assert "proyector" in tomar(c, "A", "x" * 40).json()["detail"]
        assert tomar(c, "A", codigo).status_code == 200
        assert s.senas.turno.es_dueno("A")
        assert tomar(c, "B", codigo).status_code == 409             # un solo turno a la vez


def test_el_codigo_nunca_va_a_los_celulares(con_codigo):
    with con_codigo() as (c, s):
        codigo = s.senas.turno.codigo
        estado = c.get("/api/estado")
        assert codigo not in estado.text
        assert estado.json()["kinect"]["codigo"] is True
        assert c.get("/api/kinect/codigo").status_code in (401, 403)            # sin token
        assert c.post("/api/kinect/codigo").status_code in (401, 403)
        assert codigo not in c.get("/").text


def test_el_proyector_ve_y_regenera_el_codigo(con_codigo):
    with con_codigo("127.0.0.1") as (pc, s):
        d = pc.get("/api/kinect/codigo", headers=admin(pc)).json()
        assert d == {"activo": True, "codigo": s.senas.turno.codigo, "version": 0}
        tomar(pc, "A", d["codigo"])
        assert s.senas.turno.es_dueno("A")
        nuevo = pc.post("/api/kinect/codigo", headers=admin(pc)).json()
        assert nuevo["version"] == 1 and re.fullmatch(r"\d{6}", nuevo["codigo"])
        assert s.senas.turno.instantanea() is None                              # quien lo tenía lo pierde
        esperar(lambda: pc.get("/api/estado").json()["kinect"]["codigo_version"] == 1)


def test_bloquear_quita_el_turno_tambien_con_codigo(con_codigo):
    with con_codigo("127.0.0.1") as (pc, s):
        pid = pc.post("/api/participante", json={"cliente": "A", "nombre": "Ana"}).json()["pid"]
        assert tomar(pc, "A", s.senas.turno.codigo).status_code == 200
        pc.post(f"/api/participantes/{pid}/bloquear", headers=admin(pc))
        assert s.senas.turno.instantanea() is None
        assert tomar(pc, "A", s.senas.turno.codigo).status_code == 403


def test_sin_codigo_en_el_env_basta_activar_control(abrir_api, detector):
    with abrir_api(reconocedor="kinect", kinect_url=detector.url, kinect_codigo=False) as (c, s):
        assert c.get("/api/estado").json()["kinect"]["codigo"] is False
        assert tomar(c, "A").status_code == 200


def test_adivinar_el_codigo_tiene_limite(con_codigo):
    with con_codigo(lim_kinect_cliente=1000) as (c, s):
        codigos = [str(n).zfill(6) for n in range(40) if str(n).zfill(6) != s.senas.turno.codigo]
        respuestas = [tomar(c, f"c{n}", cod).status_code for n, cod in enumerate(codigos)]
        assert 429 in respuestas and respuestas.count(403) <= 30


# ---------------------------------------------------------------- páginas
def test_la_pestana_tiene_el_diseno_de_camila(carpeta_web):
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    pestana = html[html.index('<section id="tab-kinect"'):html.index("<!-- ===================== MIS MENSAJES")]
    # En su orden: texto grande, estado, acceso con el código y botones en cuadrícula
    orden = ["Tus letras aparecerán aquí", 'id="kinDetalle"', 'id="kinModo"', "Código del PC", "Activar control",
             "Volver a espectador", 'data-kin="iniciar"', 'data-kin="detener"', 'data-kin="espacio"',
             'data-kin="borrar"', 'data-kin="limpiar"', ">Guardar TXT<", ">Leer frase<", ">Detener voz<",
             'data-kin="terminar"', 'id="kinEco"']
    posiciones = [pestana.index(t) for t in orden]
    assert posiciones == sorted(posiciones), orden
    assert 'class="kin-botones"' in pestana and "grid-template-columns" in html
    assert 'inputmode="numeric"' in pestana and 'maxlength="6"' in pestana
    assert "Terminar y decirlo" in pestana


def test_el_proyector_muestra_y_regenera_el_codigo(carpeta_web):
    html = (carpeta_web / "pantalla.html").read_text(encoding="utf-8")
    assert 'id="kinCodigo"' in html and 'id="kinNuevoCodigo"' in html
    assert "/api/kinect/codigo" in html


def test_la_pagina_del_celular_envia_el_codigo(carpeta_web):
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    assert '"/api/kinect/turno", { codigo' in html
    assert "/api/kinect/codigo" not in html          # el celular nunca pide el código


def test_configuracion_de_pruebas_sin_codigo_por_defecto():
    assert configuracion().kinect_codigo is False

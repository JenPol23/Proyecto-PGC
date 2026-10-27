"""Arranque del detector y del capturador junto con la plataforma (sin abrir procesos de verdad)."""
import subprocess
import threading
import time

import pytest

from conftest import configuracion, esperar

from pgc.adaptadores.kinect import procesos
from pgc.adaptadores.kinect.procesos import LanzadorKinect


class ProcesoFalso:
    def __init__(self, comando, **kw):
        self.comando, self.kw = comando, kw
        self.terminado = threading.Event()
        self._handle = 0
        self.pid = 4242

    def wait(self, timeout=None):
        if not self.terminado.wait(timeout if timeout is not None else 30):
            raise subprocess.TimeoutExpired(self.comando, timeout)
        return 0

    def poll(self):
        return 0 if self.terminado.is_set() else None

    def terminate(self):
        self.terminado.set()

    kill = terminate


@pytest.fixture
def lanzados(monkeypatch, tmp_path):
    lista = []
    monkeypatch.setattr(procesos, "REGISTROS", tmp_path)
    monkeypatch.setattr(procesos, "puerto_ocupado", lambda url: False)
    monkeypatch.setattr(procesos, "atar_al_proceso_actual", lambda proc: None)

    def popen(comando, **kw):
        p = ProcesoFalso(comando, **kw)
        lista.append(p)
        return p
    return lista, popen, tmp_path


def lanzador(lanzados, python=True, exe=True, listo=lambda url: True, ventanas=None, restos=(), cerrados=None,
             **ajustes):
    lista, popen, carpeta = lanzados
    (carpeta / "python.exe").write_bytes(b"")
    (carpeta / "LSCKinectFramework.exe").write_bytes(b"")
    cfg = configuracion(**{"reconocedor": "kinect", "kinect_lanzar": True, **ajustes})
    log = []
    l = LanzadorKinect(cfg, log.append, popen=popen,
                       pythons=[carpeta / ("python.exe" if python else "no-existe.exe")],
                       exes=[carpeta / ("LSCKinectFramework.exe" if exe else "no-existe.exe")],
                       listo=listo, minimizar=lambda pid: (ventanas if ventanas is not None else [("Kinect", True)]),
                       espera_detector=2.0,
                       # nunca buscar ni cerrar procesos reales desde las pruebas
                       buscar_restos=lambda: list(restos),
                       cerrar=(cerrados.append if cerrados is not None else (lambda pid: None)))
    return l, log


def test_lanza_detector_y_app_del_kinect_y_los_cierra(lanzados):
    lista, _, carpeta = lanzados
    l, log = lanzador(lanzados)
    l.iniciar()
    esperar(lambda: len(lista) == 2)
    detector = next(p for p in lista if "detector_paralelo.py" in " ".join(p.comando))
    assert detector.comando[-1] == str(procesos.DETECTOR)           # envuelve SU server_web_svm.py, sin cambiarlo
    app = next(p for p in lista if p.comando[0].endswith("LSCKinectFramework.exe"))
    assert detector.comando[0] == str(carpeta / "python.exe")
    assert detector.kw["cwd"] == str(procesos.DETECTOR)                 # su carpeta, sus archivos, tal cual
    assert detector.kw["env"]["PYTHONDONTWRITEBYTECODE"] == "1"           # sin __pycache__ en su carpeta
    assert app.kw["startupinfo"] is None or app.kw["startupinfo"].wShowWindow == procesos.MINIMIZADA
    l.detener()
    assert all(p.terminado.is_set() for p in lista)


def test_camara_del_pc_en_lugar_del_kinect(lanzados):
    lista, _, carpeta = lanzados
    l, log = lanzador(lanzados, kinect_capturador="camara_pc", kinect_camara=1)
    l.iniciar()
    esperar(lambda: len(lista) == 2)
    camara = next(p for p in lista if "camara_pc.py" in " ".join(p.comando))
    assert camara.comando[0] == str(carpeta / "python.exe")            # el Python del detector (trae OpenCV)
    assert camara.comando[-2:] == ["--camara", "1"]
    l.detener()


def test_sin_entorno_ni_exe_avisa_y_no_lanza_nada(lanzados):
    lista, _, _ = lanzados
    l, log = lanzador(lanzados, python=False, exe=False)
    l.iniciar()
    esperar(lambda: any("No está la app del Kinect" in x for x in log))
    assert lista == []
    texto = " ".join(log)
    assert "Falta el entorno del detector" in texto and "No está la app del Kinect compilada" in texto


def test_detector_ya_corriendo_no_se_duplica(lanzados, monkeypatch):
    lista, _, _ = lanzados
    monkeypatch.setattr(procesos, "puerto_ocupado", lambda url: True)
    l, log = lanzador(lanzados, kinect_capturador="no")
    l.iniciar()
    assert lista == [] and any("Ya hay un detector" in x for x in log)


@pytest.mark.parametrize("ajustes", [{"kinect_lanzar": False}, {"reconocedor": "simulado"}])
def test_no_lanza_si_no_corresponde(lanzados, ajustes):
    lista, _, _ = lanzados
    l, _ = lanzador(lanzados, **ajustes)
    l.iniciar()
    assert lista == []


def test_el_detector_se_reinicia_si_se_cae(lanzados):
    lista, _, _ = lanzados
    l, log = lanzador(lanzados, kinect_capturador="no")
    l._parar.wait = lambda s: False                        # sin esperar los 3 s entre intentos
    l.iniciar()
    esperar(lambda: len(lista) == 1)
    lista[0].terminate()                                  # se cae
    esperar(lambda: len(lista) == 2)
    assert any("se reinicia" in x for x in log)
    l.detener()


def test_config_del_capturador_se_valida():
    from pgc.config import Config, ErrorConfig, validar
    with pytest.raises(ErrorConfig, match="PGC_KINECT_CAPTURADOR"):
        validar(Config(kinect_capturador="webcam"))
    with pytest.raises(ErrorConfig, match="PGC_KINECT_URL"):          # el detector siempre en este PC
        validar(Config(kinect_url="http://192.168.0.5:8765"))


def test_la_app_espera_a_que_el_detector_responda(lanzados):
    """Antes se abrían a la vez y la app mandaba imágenes ~4,5 s a un detector que aún no existía."""
    lista, _, _ = lanzados
    listo = threading.Event()
    l, log = lanzador(lanzados, listo=lambda url: listo.is_set())
    l.iniciar()
    esperar(lambda: len(lista) == 1)                     # solo el detector
    time.sleep(0.6)
    assert len(lista) == 1 and "detector_paralelo.py" in " ".join(lista[0].comando)
    listo.set()                                          # el detector ya responde
    esperar(lambda: len(lista) == 2)
    assert lista[1].comando[0].endswith("LSCKinectFramework.exe")
    assert any("Detector listo en" in x for x in log)
    l.detener()


def test_si_el_detector_no_responde_la_app_se_abre_igual(lanzados):
    lista, _, _ = lanzados
    l, log = lanzador(lanzados, listo=lambda url: False)          # espera_detector = 2 s en la prueba
    l.iniciar()
    esperar(lambda: len(lista) == 2, timeout=6)
    assert any("no respondió en 2 s" in x for x in log)
    l.detener()


def test_si_la_ventana_se_abre_en_grande_se_minimiza(lanzados):
    lista, _, _ = lanzados
    l, log = lanzador(lanzados, kinect_capturador="kinect", ventanas=[("Kinect - Ejemplos de LSC", False)])
    l.iniciar()
    esperar(lambda: any("se minimizó" in x for x in log))
    l.detener()


def test_se_puede_volver_a_su_servidor_original(lanzados):
    lista, _, _ = lanzados
    l, _ = lanzador(lanzados, kinect_capturador="no", kinect_detector_paralelo=False)
    l.iniciar()
    esperar(lambda: len(lista) == 1)
    assert lista[0].comando[-1] == "server_web_svm.py"
    l.detener()


def test_cierra_los_restos_antes_de_lanzar(lanzados):
    lista, _, _ = lanzados
    cerrados = []
    restos = [(111, "python.exe", "python.exe -u detector_paralelo.py carpeta"),
              (112, "python.exe", "python.exe -u server_web_svm.py"),
              (113, "LSCKinectFramework.exe", "LSCKinectFramework.exe")]
    l, log = lanzador(lanzados, restos=restos, cerrados=cerrados)
    l.iniciar()
    assert cerrados == [111, 112, 113]                      # se cierran ANTES de lanzar los nuevos
    assert any("restos de una ejecución anterior: 1 app del Kinect, 2 detector" in x for x in log)
    esperar(lambda: len(lista) == 2)                         # y luego uno de cada uno
    l.detener()


def test_tipos_de_resto():
    assert procesos.tipo_de_resto("LSCKinectFramework.exe", "") == "app del Kinect"
    assert procesos.tipo_de_resto("python.exe", "python camara_pc.py --camara 0") == "cámara del PC"
    assert procesos.tipo_de_resto("python.exe", "python -u detector_paralelo.py carpeta") == "detector"


def test_no_arranca_una_segunda_plataforma(monkeypatch, capsys):
    from pgc import arranque
    monkeypatch.setattr(arranque, "puerto_en_uso", lambda puerto: True)
    lanzados = []
    monkeypatch.setattr(arranque, "crear_lanzador", lambda cfg, log: lanzados.append(1))
    assert arranque.main(["--simular", "--no-abrir", "--puerto-web", "8799"]) == 3
    assert lanzados == []                                    # no se tocó nada de la otra plataforma
    assert "Ya hay una plataforma corriendo" in capsys.readouterr().err


def test_buscar_restos_cuenta_el_lanzador_del_entorno_y_su_hijo_como_uno(monkeypatch):
    import json
    import types
    datos = [{"ProcessId": 10, "ParentProcessId": 1, "Name": "python.exe", "CommandLine": "python -u detector_paralelo.py c"},
             {"ProcessId": 11, "ParentProcessId": 10, "Name": "python.exe", "CommandLine": "python -u detector_paralelo.py c"},
             {"ProcessId": 12, "ParentProcessId": 1, "Name": "LSCKinectFramework.exe", "CommandLine": "x"},
             {"ProcessId": 13, "ParentProcessId": 1, "Name": "python.exe", "CommandLine": "python -m pgc"}]
    monkeypatch.setattr(procesos.os, "name", "nt")
    monkeypatch.setattr(procesos.subprocess, "run", lambda *a, **k: types.SimpleNamespace(stdout=json.dumps(datos)))
    assert [r[0] for r in procesos.buscar_restos()] == [10, 12]          # ni el hijo 11 ni la plataforma 13

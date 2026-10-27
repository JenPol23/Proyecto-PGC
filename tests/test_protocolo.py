"""Protocolo de prueba de letras: análisis, máquina de estados, guardado y API (sin Kinect)."""
import csv
import threading
import time

import pytest

from conftest import admin, esperar
from detector_falso import DetectorFalso

from pgc.adaptadores import experimentos
from pgc.aplicacion.protocolo import ProtocoloLetras, ServicioProtocolo
from pgc.dominio import experimento as ex

PC = "127.0.0.1"
TUNEL = {"CF-Connecting-IP": "181.50.1.2"}


def intento(letra, reconocida, **kw):
    base = {"letra": letra, "intento": 1, "reconocida": reconocida, "tiempo_s": 1.2 if reconocida else None,
            "mano_pct": 90.0, "prediccion_frecuente": reconocida or letra, "margen_medio": 0.9,
            "estable_max_s": 1.0, "cambios": 0, "sin_letra_pct": 0.0, "motivo_frecuente": "Confirmando…"}
    return {**base, **kw}


# ---------------------------------------------------------------- análisis
def test_resumen_y_matriz():
    datos = [intento("a", "a"), intento("a", "a"), intento("a", "e"), intento("a", None),
             intento("b", "b")]
    por = {f["letra"]: f for f in ex.resumen_por_letra(datos)}
    assert por["a"] == {"letra": "a", "intentos": 4, "aciertos": 2, "confusiones": {"e": 1}, "no_detectadas": 1,
                        "exactitud_pct": 50.0, "tiempo_medio_s": 1.2}
    filas, columnas, matriz = ex.matriz_confusion(datos, ["a", "b"])
    assert columnas == ["a", "b", "e", ex.NINGUNA]
    assert matriz == [[2, 0, 1, 1], [0, 1, 0, 0]]
    inf = ex.informe(datos)
    assert inf["exactitud_pct"] == 60.0 and inf["fallan"] == ["a"] and "b" not in inf["causas"]


@pytest.mark.parametrize("cambios, tipo", [
    ({"mano_pct": 20.0}, "mano"),
    ({"prediccion_frecuente": "sin_letra", "sin_letra_pct": 80.0}, "sin_letra"),
    ({"reconocida": "e"}, "parecida"),
    ({"cambios": 6}, "inestable"),
    ({"estable_max_s": 0.4}, "tiempo"),
    ({"margen_medio": 0.1}, "margen"),
])
def test_causa_probable(cambios, tipo):
    fallo = intento("a", None, **{k: v for k, v in cambios.items() if k != "reconocida"})
    if "reconocida" in cambios:
        fallo = intento("a", cambios["reconocida"])
    assert ex.causa_probable("a", [fallo, intento("a", "a")])[0] == tipo
    assert ex.causa_probable("a", [intento("a", "a")]) is None


# ---------------------------------------------------------------- máquina de estados
def diag(t, manos=0, pred=None, texto="", armado=True, estable=0.0):
    return {"t": t, "manos": manos, "prediccion": pred, "segunda": None, "margen": 0.5 if pred else None,
            "estable_s": estable, "confirmaciones": 0, "armado": armado, "texto": texto, "motivo": "x"}


def test_acierto_confusion_y_no_detectada():
    p = ProtocoloLetras(["a", "b", "c"], repeticiones=1, tiempo_max=3.0)
    assert p.iniciar(0.0) == ["iniciar", "limpiar"]
    p.muestra(diag(1, 0), 0.5)                                     # sin mano: el tiempo aún no corre
    p.muestra(diag(2, 1, "a"), 1.0)                                # aparece la mano
    p.muestra(diag(3, 1, "a", estable=0.8), 1.8)
    p.muestra(diag(4, 1, "a", texto="A", armado=False), 2.0)       # su lógica confirmó A
    assert p.fase == "retirar" and p.intentos[0]["reconocida"] == "a" and p.intentos[0]["tiempo_s"] == 1.0
    assert p.muestra(diag(5, 0, None, texto="A", armado=False), 2.2) == []      # aún no está lista
    assert p.muestra(diag(6, 0, None, texto="A", armado=True), 2.8) == ["limpiar"]
    assert p.estado()["letra"] == "b"
    p.muestra(diag(7, 1, "e", texto=""), 3.0)
    p.muestra(diag(8, 1, "e", texto="E", armado=False), 3.9)       # confundida con E
    p.muestra(diag(9, 0, texto="E"), 4.2)                          # retira la mano
    p.muestra(diag(10, 1, "sin_letra", texto=""), 4.5)
    p.muestra(diag(11, 1, "sin_letra", texto=""), 7.6)             # pasan 3 s: no detectada
    assert [(i["letra"], i["reconocida"]) for i in p.intentos] == [("a", "a"), ("b", "e"), ("c", None)]
    assert p.intentos[2]["sin_letra_pct"] == 100.0
    p.muestra(diag(12, 0), 7.8)
    assert p.fase == "terminado"


def test_tras_limpiar_no_cuenta_el_texto_viejo():
    """El diagnóstico se actualiza con cada imagen: justo tras limpiar puede traer aún la letra anterior."""
    p = ProtocoloLetras(["a"], repeticiones=2, tiempo_max=5.0)
    p.iniciar(0.0)
    p.muestra(diag(1, 1, "a", texto="A", armado=False), 1.0)       # intento 1: A
    p.muestra(diag(2, 0, texto="A", armado=True), 1.5)             # retirar → limpiar, intento 2
    assert p.estado()["intento"] == 2
    p.muestra(diag(2, 0, texto="A", armado=True), 1.6)             # MISMA imagen (t=2), aún con "A": no cuenta
    assert p.fase == "pedir"
    p.muestra(diag(3, 1, "a", texto=""), 1.7)                      # imagen nueva, ya limpio
    p.muestra(diag(4, 1, "a", texto="A", armado=False), 2.6)       # ahora sí: A otra vez
    assert [i["reconocida"] for i in p.intentos] == ["a", "a"]


def test_el_servicio_corre_y_guarda():
    ordenes, guardado = [], []
    muestras = iter([diag(1, 1, "a"), diag(2, 1, "a", texto="A", armado=False), diag(3, 0, texto="A")]
                    + [diag(4, 0)] * 50)

    class Senas:
        def diagnostico(self):
            return next(muestras)

        def controlar(self, accion):
            ordenes.append(accion)

    s = ServicioProtocolo(Senas(), guardar=lambda p, info: (guardado.append(p) or "experimentos/x", {"ok": 1}),
                          periodo=0.001)
    s.iniciar(["a"], repeticiones=1)
    esperar(lambda: s.estado()["fase"] == "terminado" and s.carpeta)
    assert ordenes[:2] == ["iniciar", "limpiar"] and guardado and s.estado()["carpeta"] == "experimentos/x"


# ---------------------------------------------------------------- guardado
def test_guardar_archivos(tmp_path):
    p = ProtocoloLetras(["a", "b"], repeticiones=2)
    p.intentos = [intento("a", "a"), intento("a", "e"), intento("b", None, mano_pct=10.0), intento("b", "b")]
    p.muestras = [{"t": 0.1, "fase": "pedir", "letra": "a", "intento": 1, "manos": 1, "prediccion": "a",
                   "segunda": "e", "margen": 0.5, "estable_s": 0.3, "confirmaciones": 2, "motivo": "x", "texto": ""}]
    carpeta, informe = experimentos.guardar(p, {}, carpeta_base=tmp_path)
    archivos = {f.name for f in next(tmp_path.iterdir()).iterdir()}
    assert {"intentos.csv", "muestras.csv", "resumen_por_letra.csv", "matriz_confusion.csv", "matriz_confusion.png",
            "aciertos_por_letra.png", "tiempos_por_letra.png", "informe.md"} <= archivos
    with open(next(tmp_path.iterdir()) / "intentos.csv", encoding="utf-8-sig") as f:
        filas = list(csv.reader(f, delimiter=";"))
    assert filas[0][:4] == ["letra", "intento", "resultado", "reconocida"] and filas[1][4] == "1,2"   # coma decimal
    assert informe["exactitud_pct"] == 50.0 and informe["causas"]["b"]["tipo"] == "mano"


# ---------------------------------------------------------------- API (detector falso)
@pytest.fixture
def detector():
    d = DetectorFalso()
    d.mantener_camara()
    yield d
    d.cerrar()


def test_diagnostico_solo_en_el_pc(abrir_api, detector):
    with abrir_api(PC, reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05) as (c, s):
        detector.mostrar("l")
        r = c.get("/api/kinect/diagnostico", headers=admin(c))
        assert r.status_code == 200 and r.json()["prediccion"] == "l"
        assert c.get("/api/kinect/diagnostico").status_code == 403
        assert c.get("/api/kinect/diagnostico", headers={**admin(c), **TUNEL}).status_code == 403
        assert "pgc-admin" in c.get("/diagnostico").text
        detector.con_diagnostico = False                            # su servidor original no lo tiene
        assert c.get("/api/kinect/diagnostico", headers=admin(c)).status_code == 503


def test_protocolo_completo_por_la_api(abrir_api, detector, monkeypatch, tmp_path):
    monkeypatch.setattr(experimentos, "CARPETA", tmp_path)
    with abrir_api(PC, reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05) as (c, s):
        s.protocolo.periodo = 0.02
        esperar(lambda: s.senas.reconocedor.camara)
        assert c.post("/api/kinect/protocolo/iniciar", json={"letras": "a x"}).status_code == 403   # sin token
        assert c.post("/api/kinect/protocolo/iniciar", json={"letras": "a ñ"}, headers=admin(c)).status_code == 400
        r = c.post("/api/kinect/protocolo/iniciar", json={"letras": "a b", "repeticiones": 2, "tiempo_max": 2},
                   headers=admin(c))
        assert r.status_code == 200 and r.json()["total"] == 4

        def persona():                                              # hace lo que le piden; la B la confunde con D
            hechas = 0
            while hechas < 4:
                e = c.get("/api/kinect/protocolo", headers=admin(c)).json()
                if e["fase"] == "pedir" and e["hecho"] == hechas:
                    letra = "d" if e["letra"] == "b" and e["intento"] == 2 else e["letra"]
                    detector.mostrar(letra)
                    time.sleep(0.15)
                    detector.reconocer(letra)
                    esperar(lambda: c.get("/api/kinect/protocolo", headers=admin(c)).json()["hecho"] > hechas)
                    detector.retirar()
                    hechas += 1
                time.sleep(0.03)
        hilo = threading.Thread(target=persona, daemon=True)
        hilo.start()
        esperar(lambda: c.get("/api/kinect/protocolo", headers=admin(c)).json().get("carpeta"), timeout=20)
        e = c.get("/api/kinect/protocolo", headers=admin(c)).json()
        assert e["informe"]["exactitud_pct"] == 75.0
        assert e["informe"]["por_letra"][1]["confusiones"] == {"d": 1}
        carpeta = next(tmp_path.iterdir())
        assert (carpeta / "matriz_confusion.png").exists() and (carpeta / "informe.md").exists()


def test_eco_desde_el_celular_con_turno(abrir_api, detector):
    with abrir_api(reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05) as (c, s):
        assert c.post("/api/kinect/eco", json={"activo": True, "cliente": "A"}).status_code == 403   # sin turno
        c.post("/api/kinect/turno", json={"cliente": "A"})
        assert c.post("/api/kinect/eco", json={"activo": True, "cliente": "A"}).json() == {"eco": True}
        assert c.post("/api/kinect/eco", json={"activo": False, "cliente": "B"}).status_code == 403  # espectador
        assert s.eco is True

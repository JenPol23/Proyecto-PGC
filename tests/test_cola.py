"""Cola de mensajes y deletreo (caracterización de servidor.Sistema con una mano falsa)."""
import re
from unittest.mock import ANY

import pytest

from conftest import esperar


# =============================================================================
#  Cola (sin hilo de la mano: los mensajes se quedan pendientes)
# =============================================================================
def test_encolar_limpia_y_numera(crear_sistema):
    s = crear_sistema()
    m1 = s.encolar("  HOLA  ", "c1")
    m2 = s.encolar("Uña", "c2")
    assert (m1["id"], m1["texto"]) == (1, "hola")
    assert (m2["id"], m2["texto"]) == (2, "uña")
    assert m1["i"] == -1 and m1["cliente"] == "c1"
    assert [m["id"] for m in s.cola] == [1, 2]


def test_maximo_dos_pendientes_por_cliente(crear_sistema):
    s = crear_sistema()
    s.encolar("hola", "c1")
    s.encolar("uña", "c1")
    with pytest.raises(ValueError, match=r"^Ya tienes 2 mensajes en espera\. Espera a que la mano los haga\.$"):
        s.encolar("otro", "c1")
    s.encolar("ve mi", "c2")                       # otro celular sí puede
    assert len(s.cola) == 3


@pytest.mark.parametrize("entrada, error", [
    ("¡¿?!", "Escribe al menos una letra."),
    ("", "Escribe al menos una letra."),
    ("gh", "La mano todavía no puede hacer esas letras"),
    ("Jhs", "La mano todavía no puede hacer esas letras"),
    ("zz gg", "La mano todavía no puede hacer esas letras"),
])
def test_rechazos(crear_sistema, entrada, error):
    s = crear_sistema()
    with pytest.raises(ValueError) as ex:
        s.encolar(entrada, "c1")
    assert str(ex.value) == error
    assert s.cola == []


@pytest.mark.parametrize("entrada", ["hola gh", "Ñ", "a"])
def test_se_acepta_si_hay_al_menos_una_letra_posible(crear_sistema, entrada):
    s = crear_sistema()
    s.encolar(entrada, "c1")
    assert len(s.cola) == 1


def test_cola_global_de_30(crear_sistema):
    s = crear_sistema()
    for k in range(30):
        s.encolar("a", f"c{k}")
    with pytest.raises(ValueError, match=r"^La cola está llena, intenta en un momento\.$"):
        s.encolar("a", "otro")


def test_cancelar_solo_lo_propio(crear_sistema):
    s = crear_sistema()
    m1 = s.encolar("hola", "A")
    m2 = s.encolar("uña", "A")
    m3 = s.encolar("ve mi", "B")
    assert s.cancelar(m2["id"], "B") is False      # B no puede cancelar el de A
    assert s.cancelar(m2["id"], "A") is True
    assert s.cancelar(m2["id"], "A") is False      # ya no existe
    assert s.cancelar(999, "A") is False
    assert [m["id"] for m in s.cola] == [m1["id"], m3["id"]]


def test_instantanea_no_expone_el_cliente(crear_sistema):
    s = crear_sistema()
    s.encolar("hola", "secreto-del-celular")
    d = s.instantanea()
    assert d["cola"] == [{"id": 1, "texto": "hola", "pid": ANY, "nombre": "Anónimo"}]     # E8: autor (sin nombre)
    assert re.fullmatch(r"p[0-9a-f]{8}", d["cola"][0]["pid"])
    assert "secreto-del-celular" not in repr(d)


def test_instantanea_estructura(crear_sistema):
    s = crear_sistema()
    d = s.instantanea()
    assert set(d) == {"tipo", "sesion", "mano", "voz", "tunel", "url_local", "url_publica", "kinect",
                      "max_caracteres", "actual", "cola", "historial", "bloqueados"}     # E8: bloqueados
    assert d["bloqueados"] == []
    assert d["tipo"] == "estado"
    assert d["mano"] == {"modo": "simulada", "medio": None, "puerto": None, "letras": None}   # E10: medio
    assert d["voz"] == {"estado": "listo", "dispositivo": "cuda float16"}
    assert d["tunel"] == {"estado": "apagado", "url": None}
    assert d["url_local"] == d["url_publica"] == "http://192.168.0.10:8000"
    assert d["kinect"] == {"estado": "pendiente"}
    assert d["max_caracteres"] == 60
    assert (d["actual"], d["cola"], d["historial"]) == (None, [], [])


def test_saltar_sin_mensaje_en_curso(crear_sistema):
    assert crear_sistema().saltar_actual() is False


# =============================================================================
#  Deletreo: órdenes que recibe la mano (con el hilo de la mano)
# =============================================================================
def deletrear(s, texto, cliente="c1"):
    """Encola, espera a que termine y devuelve las órdenes enviadas a la mano."""
    antes = len(s.mano.ordenes)
    m = s.encolar(texto, cliente)
    esperar(lambda: s.historial and s.historial[0]["id"] == m["id"])
    return s.mano.ordenes[antes:]


@pytest.mark.parametrize("entrada, ordenes", [
    ("calle", "c a l reset l e reset"),
    ("carro", "c a r reset r o reset"),
    ("ll ll", "l reset l reset l reset l reset"),
    ("ñn", "n reset n reset"),                     # la Ñ se hace con la forma de la N
    ("lgl", "l reset l reset"),                    # la g no se envía; la mano seguía en l
    ("hola", "o l a reset"),                       # la h no se envía
    ("ve mi", "v e reset m i reset"),              # espacio = mano abierta
    ("a", "a reset"),
])
def test_ordenes_a_la_mano(sistema_con_mano, entrada, ordenes):
    assert deletrear(sistema_con_mano, entrada) == ordenes.split()


def test_si_la_mano_no_confirma_no_se_abre_antes_de_repetir(sistema_con_mano):
    s = sistema_con_mano
    s.mano.fallar = {"l"}
    assert deletrear(s, "ll") == ["l", "l", "reset"]
    assert [p["r"] for p in s.historial[0]["pasos"]] == ["error", "error"]


def test_resultado_por_paso_y_fin(sistema_con_mano):
    s = sistema_con_mano
    deletrear(s, "ha b")
    m = s.historial[0]
    assert [(p["c"], p["r"]) for p in m["pasos"]] == [("H", "nd"), ("A", "ok"), (" ", "ok"), ("B", "ok")]
    assert m["i"] == len(m["pasos"])
    assert s.actual is None
    d = s.instantanea()
    assert d["historial"][0] == {"id": m["id"], "texto": "ha b", "nombre": "Anónimo", "saltado": False}


def test_secuencia_se_recalcula_con_las_letras_de_la_mano(sistema_con_mano):
    s = sistema_con_mano
    s.mano.letras = set("agh")
    assert deletrear(s, "gha") == ["g", "h", "a", "reset"]


def test_mensajes_en_orden_de_llegada(sistema_con_mano):
    s = sistema_con_mano
    s.mano.bloquear_en = "a"
    s.encolar("a", "c1")
    s.mano.llego.wait(5)
    s.encolar("b", "c2")
    s.encolar("c", "c3")
    s.mano.soltar.set()
    esperar(lambda: len(s.historial) == 3)
    assert s.mano.ordenes == ["a", "reset", "b", "reset", "c", "reset"]
    assert [m["texto"] for m in s.historial] == ["c", "b", "a"]      # el más reciente primero


def test_historial_guarda_los_ultimos_6(sistema_con_mano):
    s = sistema_con_mano
    for k in range(8):
        deletrear(s, "a", cliente=f"c{k}")
    assert len(s.historial) == 6
    assert len(s.instantanea()["historial"]) == 6


def test_el_mensaje_en_curso_cuenta_para_el_limite(sistema_con_mano):
    s = sistema_con_mano
    s.mano.bloquear_en = "a"
    s.encolar("a", "c1")
    s.mano.llego.wait(5)
    assert s.actual is not None and s.cola == []
    s.encolar("b", "c1")
    with pytest.raises(ValueError, match="Ya tienes 2"):
        s.encolar("c", "c1")
    assert s.cancelar(s.actual["id"], "c1") is False                 # el que está en curso no se cancela


def test_estado_durante_el_deletreo(sistema_con_mano):
    s = sistema_con_mano
    s.mano.bloquear_en = "c"
    s.encolar("abc", "c1")
    s.mano.llego.wait(5)
    a = s.instantanea()["actual"]
    assert a == {"id": 1, "texto": "abc", "i": 2, "saltado": False, "pid": ANY, "nombre": "Anónimo", "pasos": [
        {"c": "A", "tipo": "ok", "r": "ok"}, {"c": "B", "tipo": "ok", "r": "ok"}, {"c": "C", "tipo": "ok", "r": None}]}


def test_saltar_mensaje(sistema_con_mano):
    s = sistema_con_mano
    s.mano.bloquear_en = "c"
    s.encolar("abcdefiklmnop", "c1")
    s.mano.llego.wait(5)
    assert s.saltar_actual() is True
    s.mano.soltar.set()
    esperar(lambda: len(s.historial) == 1)
    assert s.mano.ordenes == ["a", "b", "c", "reset"]                 # la letra en curso termina
    assert s.historial[0]["saltado"] is True
    assert s.instantanea()["historial"][0]["saltado"] is True
    # El siguiente mensaje se deletrea normal
    assert deletrear(s, "ok", cliente="c2") == ["o", "k", "reset"]
    assert s.instantanea()["historial"][0] == {"id": 2, "texto": "ok", "nombre": "Anónimo", "saltado": False}


def test_reconexion_pedida(sistema_con_mano):
    s = sistema_con_mano
    n = s.mano.conexiones
    s.pedir_reconexion = True
    with s.cv:
        s.cv.notify_all()
    esperar(lambda: s.mano.conexiones == n + 1)
    assert s.pedir_reconexion is False

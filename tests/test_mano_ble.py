"""Mano por Bluetooth y respaldo por USB, contra el main.py REAL de la placa (en un hilo, radio BLE falsa)."""
import time
import types

import pytest

from conftest import esperar
from esp32_falso import TOKEN, Esp32Falso
from test_mano_serial import SerialFalso

from pgc.adaptadores.mano_ble import ManoBLE
from pgc.adaptadores.mano_respaldo import Mano

RESPUESTAS_USB = {"reset": ["reset_ok"], "a": ["gesto_a_ok"], "b": ["gesto_b_ok"]}


@pytest.fixture
def esp():
    e = Esp32Falso()
    yield e
    e.detener()


@pytest.fixture
def log():
    return []


def ble(esp, log, token=TOKEN, **kw):
    kw.setdefault("timeout_letra", 1.0)
    kw.setdefault("tiempo_busqueda", 0.5)
    return ManoBLE(esp.nombre, token, log=log.append, bleak=esp.bleak, **kw)


def serial_falso(respuestas=RESPUESTAS_USB, puertos=(("COM5", 0x303A),)):
    falso = SerialFalso(respuestas)
    lista = [types.SimpleNamespace(device=d, vid=v) for d, v in puertos]
    return falso, types.SimpleNamespace(
        Serial=lambda: falso,
        tools=types.SimpleNamespace(list_ports=types.SimpleNamespace(comports=lambda: lista)))


def mano(esp, log, modo="auto", usb=True, **kw_ble):
    falso, modulo = serial_falso(puertos=(("COM5", 0x303A),) if usb else ())
    m = Mano(log=log.append, modo=modo, ble=ble(esp, log, **kw_ble), modulo_serial=modulo,
             dormir=lambda s: None, timeout_letra=0.3)
    return m, falso


# ---------------------------------------------------------------- conexión
def test_conexion_por_bluetooth(esp, log):
    b = ble(esp, log)
    assert b.conectar() is True
    assert b.conectada and b.puerto == "Mano-LSC" and b.medio == "ble"
    assert b.letras is None                                     # el firmware no las informa
    assert b.hacer("a") is True and b.hacer("g") is False      # g: comando_no_reconocido
    assert b.hacer("reset") is True and b.latido() is True
    assert esp.ordenes == ["reset", "a", "g", "reset"]          # el latido no manda nada
    assert log[-1] == "[mano] Conectada por Bluetooth a Mano-LSC"
    assert TOKEN not in "\n".join(log)                          # el token nunca va al log
    b.cerrar()


def test_mueve_igual_que_el_original(esp, log):
    from arnes_firmware import ORIGINAL, correr
    b = ble(esp, log)
    b.conectar()
    for letra in "calle":
        b.hacer(letra)
    b.hacer("reset")
    reg_o, _ = correr(ORIGINAL, ["reset"] + list("calle") + ["reset"])
    assert list(esp.registro) == list(reg_o)
    b.cerrar()


def test_token_incorrecto(esp, log):
    b = ble(esp, log, token="otro-token-de-veinte-caracteres")
    assert b.conectar() is False and not b.conectada
    assert "rechazó el token" in log[-1]
    assert esp.ordenes == []                                    # no ejecutó nada
    assert any("token incorrecto" in l for l in esp.log)


def test_sin_placa(esp, log):
    esp.apagar()
    b = ble(esp, log)
    assert b.conectar() is False
    assert "no disponible" in log[-1] and "no se encontró" in log[-1]


def test_sin_bluetooth_en_el_pc(log):
    class Escaner:
        @staticmethod
        async def find_device_by_name(nombre, timeout=5.0):
            raise OSError("Bluetooth apagado")
    b = ManoBLE("Mano-LSC", TOKEN, log=log.append, bleak=types.SimpleNamespace(Escaner=Escaner, Cliente=None))
    assert b.conectar() is False
    assert "Bluetooth apagado" in log[-1]
    BleakBluetoothNotAvailableError = type("BleakBluetoothNotAvailableError", (Exception,), {})

    class EscanerApagado:
        @staticmethod
        async def find_device_by_name(nombre, timeout=5.0):
            raise BleakBluetoothNotAvailableError("Bluetooth radio is not powered on.", 3)
    b = ManoBLE("Mano-LSC", TOKEN, log=log.append, bleak=types.SimpleNamespace(Escaner=EscanerApagado, Cliente=None))
    b.conectar()
    assert "el Bluetooth del PC está apagado" in log[-1]


def test_no_llena_el_log_si_la_placa_esta_apagada(esp, log):
    esp.apagar()
    b = ble(esp, log, tiempo_busqueda=0.1, reintento=0)
    for _ in range(3):
        b.conectar()
    assert len(log) == 1


def test_espera_entre_intentos(esp, log):
    esp.apagar()
    reloj = [100.0]
    b = ble(esp, log, tiempo_busqueda=0.1, reintento=10, reloj=lambda: reloj[0])
    assert b.puede_intentar()
    b.conectar()
    assert not b.puede_intentar()
    reloj[0] += 10
    assert b.puede_intentar()


# ---------------------------------------------------------------- fallas
def test_timeout_de_una_letra(esp, log):
    b = ble(esp, log, timeout_letra=0.3)
    b.conectar()
    esp.callada = True                                          # la placa se colgó
    t0 = time.monotonic()
    assert b.hacer("a") is False
    assert 0.25 < time.monotonic() - t0 < 2
    assert "timeout" in log[-1]
    assert not b.conectada                                      # sin "ping", un timeout la da por perdida
    esp.callada = False


def test_perdida_del_bluetooth(esp, log):
    b = ble(esp, log)
    b.conectar()
    esp.apagar()
    assert b.latido() is False                                  # se nota sin enviar nada
    assert "Se perdió la conexión Bluetooth" in log[-1]
    assert b.hacer("a") is False and not b.conectada


def test_reconecta_cuando_vuelve(esp, log):
    b = ble(esp, log)
    b.conectar()
    esp.apagar()
    b.latido()
    esp.encender()
    assert b.conectar() is True and b.hacer("b") is True


# ---------------------------------------------------------------- respaldo Bluetooth → USB
def test_auto_prefiere_bluetooth(esp, log):
    m, falso = mano(esp, log)
    assert m.conectar() is True
    assert (m.modo, m.medio, m.puerto) == ("real", "ble", "Mano-LSC")
    assert falso.escrito == []                                  # el USB ni se abrió
    m.cerrar()


def test_cambio_a_usb_sin_perder_la_letra(esp, log):
    m, falso = mano(esp, log)
    m.conectar()
    assert m.hacer("a") is True
    esp.apagar()                                                # se pierde el Bluetooth
    assert m.hacer("b") is True                                 # la letra sale por USB
    assert (m.medio, m.puerto) == ("usb", "COM5")
    assert falso.escrito[-1] == b"b\n"
    assert "Respaldo: ahora por USB" in "\n".join(log)


def test_caida_entre_mensajes_se_detecta_con_el_latido(esp, log):
    m, _ = mano(esp, log)
    m.conectar()
    esp.apagar()
    assert m.revisar() is True                                  # el latido falla → USB
    assert m.medio == "usb"


def test_vuelve_al_bluetooth_cuando_reaparece(esp, log):
    m, falso = mano(esp, log, reintento=0)
    m.conectar()
    esp.apagar()
    m.hacer("a")
    assert m.medio == "usb"
    esp.encender()
    esperar(lambda: m.revisar() or m.medio == "ble", timeout=5)
    assert m.medio == "ble"
    assert falso.abierto is False                               # el USB se soltó
    assert "Cambio a Bluetooth" in "\n".join(log)
    m.cerrar()


def test_sin_bluetooth_ni_usb_queda_simulada(esp, log):
    m, _ = mano(esp, log, usb=False)
    m.conectar()
    esp.apagar()
    assert m.hacer("a") is True                                 # bleak avisó la caída: ya va simulada
    assert (m.modo, m.medio) == ("simulada", None)
    assert m.hacer("b") is True                                 # las siguientes, simuladas


def test_modo_usb_ignora_el_bluetooth(esp, log):
    m, _ = mano(esp, log, modo="usb")
    m.conectar()
    assert m.medio == "usb" and esp.ordenes == []


def test_modo_ble_nunca_usa_usb(esp, log):
    m, falso = mano(esp, log, modo="ble")
    m.conectar()
    esp.apagar()
    m.hacer("a")
    assert m.modo == "simulada" and falso.escrito == []


def test_reconectar_desde_la_pantalla(esp, log):
    m, _ = mano(esp, log)
    m.conectar()
    m.cerrar()
    time.sleep(0.05)
    assert m.conectar() is True and m.medio == "ble"
    m.cerrar()


# ---------------------------------------------------------------- de punta a punta
def test_de_punta_a_punta_por_bluetooth(esp, log):
    """Celular → API → cola → Deletreador → ManoBLE → main.py real de la placa."""
    from fastapi.testclient import TestClient
    from conftest import IP_LOCAL, TranscriptorFalso, TunelFalso, configuracion
    from pgc import arranque
    from pgc.api.app import crear_app

    def crear_mano(cfg, log_):
        return Mano(log=log_, modo="ble", ble=ble(esp, log), timeout_letra=1.0)

    sistema = arranque.construir_sistema(
        configuracion(simular=False, mano="ble", mano_ble_token=TOKEN), log=log.append, crear_mano=crear_mano,
        crear_transcriptor=lambda cfg, l, al: TranscriptorFalso(l, al),
        crear_tunel=lambda cfg, l, al: TunelFalso(cfg.puerto_web, l, al), ip_local=lambda: IP_LOCAL)
    with TestClient(crear_app(sistema, abrir_navegador=lambda url: None)) as cliente:
        esperar(lambda: cliente.get("/api/estado").json()["mano"]["modo"] == "real", timeout=5)
        mano_ = cliente.get("/api/estado").json()["mano"]
        assert (mano_["medio"], mano_["puerto"]) == ("ble", "Mano-LSC")
        antes = len(esp.ordenes)
        assert cliente.post("/api/mensaje", json={"texto": "calle", "cliente": "c1"}).status_code == 200
        esperado = "c a l reset l e reset".split()               # regla de repetidas: abrir entre las dos l
        esperar(lambda: esp.ordenes[antes:] == esperado, timeout=10)
    sistema.mano.cerrar()


# ---------------------------------------------------------------- configuración
def test_configuracion_de_la_mano():
    from conftest import configuracion
    from pgc import arranque, config
    cfg = configuracion(simular=False, mano_ble_token="t" * 20, mano_ble_nombre="Mano-2")
    m = arranque.crear_mano(cfg, lambda x: None)
    assert m.ble is not None and m.ble.nombre == "Mano-2" and m.modo_config == "auto"
    assert arranque.crear_mano(configuracion(simular=False), lambda x: None).ble is None   # sin token: solo USB
    with pytest.raises(config.ErrorConfig, match="necesita PGC_MANO_BLE_TOKEN"):
        config.cargar([], {"PGC_MANO": "ble"}, "no-existe.env")
    with pytest.raises(config.ErrorConfig, match="muy corto"):
        config.cargar([], {"PGC_MANO_BLE_TOKEN": "corto"}, "no-existe.env")
    with pytest.raises(config.ErrorConfig, match="PGC_MANO debe ser"):
        config.cargar([], {"PGC_MANO": "wifi"}, "no-existe.env")

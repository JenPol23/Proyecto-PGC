"""Protocolo serial con el ESP32 (caracterización de mano_serial con un puerto falso)."""
import time
import types
from collections import deque

import pytest


class SerialFalso:
    """Imita serial.Serial: responde según `respuestas[orden]` (lista de líneas)."""

    def __init__(self, respuestas, falla_al_escribir=False):
        self.respuestas = respuestas
        self.falla_al_escribir = falla_al_escribir
        self.escrito = []
        self.entrada = deque()
        self.abierto = False
        self.reinicios = 0
        self.port = self.baudrate = self.timeout = None
        self.dtr = self.rts = None
        self.dtr_al_abrir = self.rts_al_abrir = None

    def open(self):
        self.abierto = True
        self.dtr_al_abrir, self.rts_al_abrir = self.dtr, self.rts

    def close(self):
        self.abierto = False

    def reset_input_buffer(self):
        self.entrada.clear()

    def write(self, datos):
        if self.falla_al_escribir:
            raise OSError("el puerto desapareció")
        self.escrito.append(datos)
        if datos == b"\x03\x04":
            self.reinicios += 1
            return
        orden = datos.decode().strip()
        r = self.respuestas.get(orden, [])
        self.entrada.extend(r(self) if callable(r) else r)

    def readline(self):
        if self.entrada:
            return (self.entrada.popleft() + "\r\n").encode()
        return b""


@pytest.fixture
def puerto(monkeypatch, modulo_mano):
    """Reemplaza pyserial por un falso; devuelve una función para configurarlo."""
    monkeypatch.setattr(modulo_mano, "time", types.SimpleNamespace(sleep=lambda s: None, time=time.time))
    monkeypatch.setattr(modulo_mano, "TIMEOUT_LETRA", 0.05)
    estado = {}

    def configurar(respuestas, puertos=(), **kw):
        falso = SerialFalso(respuestas, **kw)
        lista = [types.SimpleNamespace(device=d, vid=v) for d, v in puertos]
        modulo = types.SimpleNamespace(
            Serial=lambda: falso,
            tools=types.SimpleNamespace(list_ports=types.SimpleNamespace(comports=lambda: lista)))
        monkeypatch.setattr(modulo_mano, "serial", modulo)
        estado["falso"] = falso
        return falso
    return configurar


def nueva_mano(modulo_mano, **kw):
    log = []
    return modulo_mano.Mano(log=log.append, **kw), log


# Respuestas del firmware = las del código original del autor (sin "ping" ni "letras")
RESPUESTAS_OK = {"reset": ["reset_ok"], "a": ["gesto_a_ok"], "b": ["gesto_b_ok"]}


def test_buscar_puerto_por_vid(puerto, modulo_mano):
    puerto({}, puertos=[("COM1", None), ("COM3", 0x1234), ("COM7", 0x303A)])
    assert modulo_mano.buscar_puerto() == "COM7"
    for vid in (0x1A86, 0x10C4):
        puerto({}, puertos=[("COM4", vid)])
        assert modulo_mano.buscar_puerto() == "COM4"
    puerto({}, puertos=[("COM1", 0x1234)])
    assert modulo_mano.buscar_puerto() is None


def test_conectar(puerto, modulo_mano):
    s = puerto(RESPUESTAS_OK)
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    assert mano.conectar() is True
    assert (mano.conectada, mano.modo, mano.puerto) == (True, "real", "COM9")
    assert mano.letras is None                                       # el firmware no las informa
    assert (s.port, s.baudrate) == ("COM9", 115200)
    assert (s.dtr_al_abrir, s.rts_al_abrir) == (False, False)          # no reinicia la placa
    assert s.escrito == [b"reset\n"]                                   # comprobación sin "ping"
    assert log[-1] == "[mano] Conectada por USB en COM9"


def test_conectar_tras_reinicio_suave(puerto, modulo_mano):
    s = puerto({"reset": lambda falso: ["reset_ok"] if falso.reinicios else []})
    mano, _ = nueva_mano(modulo_mano, puerto="COM9")
    assert mano.conectar() is True
    assert s.escrito == [b"reset\n", b"\x03\x04", b"reset\n"]


def test_nunca_manda_ping_ni_letras(puerto, modulo_mano):
    """El código original deletrearía "ping" o "letras" como palabras: el PC no los envía."""
    s = puerto(RESPUESTAS_OK)
    mano, _ = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    mano.hacer("a")
    mano.latido()
    mano.reset()
    assert all(len(o.strip()) == 1 or o in (b"reset\n", b"\x03\x04") for o in s.escrito)


def test_conectar_sin_respuesta(puerto, modulo_mano):
    s = puerto({})
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    assert mano.conectar() is False
    assert (mano.conectada, mano.modo) == (False, "simulada")
    assert s.abierto is False
    assert "el ESP32 no responde" in log[-1]


def test_conectar_sin_esp32(puerto, modulo_mano):
    puerto({}, puertos=[])
    mano, log = nueva_mano(modulo_mano)
    assert mano.conectar() is False
    assert log == ["[mano] No se encontró el ESP32 -> modo simulado"]


def test_modo_simulado(puerto, modulo_mano):
    puerto(RESPUESTAS_OK, puertos=[("COM7", 0x303A)])
    mano, _ = nueva_mano(modulo_mano, simular=True)
    assert mano.conectar() is False
    assert mano.modo == "simulada"
    assert mano.hacer("a") is True and mano.reset() is True


@pytest.mark.parametrize("respuesta, esperado", [
    (["gesto_a_ok"], True),
    (["comando_no_reconocido"], False),
    (["Mano lista.", "GESTO_A_OK"], True),   # ignora líneas ajenas; no distingue mayúsculas
    (["gesto_b_ok", "gesto_a_ok"], True),    # la respuesta de otra letra no cuenta
    ([], False),                             # sin respuesta: timeout
])
def test_hacer_letra(puerto, modulo_mano, respuesta, esperado):
    s = puerto({**RESPUESTAS_OK, "a": respuesta})
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    assert mano.hacer("a") is esperado
    assert s.escrito[-1] == b"a\n"
    if not respuesta:
        assert log[-1] == "[mano] Sin confirmación para 'a' (timeout)"
        assert mano.conectada                 # un timeout no desconecta


def test_errores_del_firmware_se_registran(puerto, modulo_mano):
    puerto({**RESPUESTAS_OK, "a": ["error:algo falló", "gesto_a_ok"]})
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    assert mano.hacer("a") is True
    assert "[mano] error:algo falló" in log


def test_reset(puerto, modulo_mano):
    s = puerto(RESPUESTAS_OK)
    mano, _ = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    assert mano.reset() is True
    assert s.escrito[-1] == b"reset\n"


def test_perder_la_conexion(puerto, modulo_mano):
    s = puerto(RESPUESTAS_OK)
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    s.falla_al_escribir = True
    assert mano.hacer("a") is False
    assert mano.conectada is False and mano.modo == "simulada"
    assert log[-1].startswith("[mano] Se perdió la conexión")

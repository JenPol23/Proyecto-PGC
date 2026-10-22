"""Arnés para ejecutar el firmware de la mano en el PC (CPython), sin la placa.

Ejecuta TAL CUAL el código original (original/main_original.py) y el main.py de la
placa, con piezas falsas de MicroPython:
- `machine`: registra cada pulso enviado a cada pin;
- `time`: registra cada time.sleep() (las pausas del código original);
- `sys.stdin`: las órdenes "por USB";
- `uselect`, `micropython` y `bluetooth`: el bucle sin bloqueo y una radio BLE falsa
  (RadioBLE) que conecta la placa con un "PC" falso (y con el adaptador real del PC
  a través de un bleak falso, ver BleakFalso).
"""
import asyncio
import io
import sys
import threading
import time as _time
import types
from contextlib import contextmanager
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FIRMWARE = RAIZ / "firmware" / "esp32"
ORIGINAL = FIRMWARE / "original" / "main_original.py"
MAIN = FIRMWARE / "main.py"
MARCA = "# ---------------- BUCLE PRINCIPAL ----------------"
ARRANQUE = 12                      # eventos del arranque: 6 dedos × (pulso + pausa de 0,5 s)
UART_RX = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"     # el PC escribe aquí
UART_TX = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"     # la placa notifica aquí


class Registro(list):
    """Eventos: ("pulso", pin, ns) y ("pausa", segundos)."""


class StdinFalso:
    """El USB: se le escriben órdenes; el firmware las lee con readline() o read(1)."""

    def __init__(self, texto=""):
        self._datos = texto
        self._lock = threading.Lock()

    def escribir(self, texto):
        with self._lock:
            self._datos += texto

    def hay_datos(self):
        return bool(self._datos)

    def read(self, n=1):
        with self._lock:
            c, self._datos = self._datos[:n], self._datos[n:]
            return c

    def readline(self):
        while True:                                 # el original espera (bloqueante) una línea
            with self._lock:
                if "\n" in self._datos:
                    linea, self._datos = self._datos.split("\n", 1)
                    return linea + "\n"
            _time.sleep(0.001)


class Salida(io.StringIO):
    """Lo que el firmware imprime."""

    def lineas(self):
        return self.getvalue().splitlines()


def machine_falso(registro):
    class Pin:
        def __init__(self, numero, *args, **kwargs):
            self.numero = numero

    class PWM:
        def __init__(self, pin, freq=50):
            self.pin = pin.numero

        def duty_ns(self, ns):
            registro.append(("pulso", self.pin, int(ns)))

    return types.SimpleNamespace(Pin=Pin, PWM=PWM)


def tiempo_falso(registro, escala=0.0, pausa_bucle=None):
    """time de MicroPython: sleep() se registra (y opcionalmente dura escala×segundos)."""
    def sleep(s):
        registro.append(("pausa", s))
        if escala:
            _time.sleep(s * escala)

    def sleep_ms(ms):
        if pausa_bucle:
            pausa_bucle()                            # para "colgar" la placa en las pruebas
        _time.sleep(ms / 1000)

    return types.SimpleNamespace(sleep=sleep, sleep_ms=sleep_ms,
                                 ticks_ms=lambda: int(_time.monotonic() * 1000),
                                 ticks_diff=lambda a, b: a - b)


def uselect_falso():
    class Poll:
        def __init__(self):
            self.objetos = []

        def register(self, obj, eventos=1):
            self.objetos.append(obj)

        def poll(self, timeout=0):
            return [(o, 1) for o in self.objetos if o.hay_datos()]

    return types.SimpleNamespace(poll=Poll, POLLIN=1)


# =============================================================================
#  Bluetooth falso
# =============================================================================
class UUIDFalso:
    def __init__(self, texto):
        self.texto = texto.upper()

    def __bytes__(self):                             # como en MicroPython: 16 bytes al revés
        return bytes.fromhex(self.texto.replace("-", ""))[::-1]


class RadioBLE:
    """El aire entre la placa (bluetooth.BLE de MicroPython) y un PC (central)."""
    H_TX, H_RX = 1, 2

    def __init__(self):
        self.irq = None
        self.nombre = None
        self.anunciando = False
        self.anuncio = None
        self.conexion = None                         # conn_handle de MicroPython
        self.al_notificar = None                     # callback del PC conectado
        self.al_desconectar = None
        self.rx = b""
        self.fuera_de_alcance = False
        self.conexiones = 0
        self._lock = threading.Lock()

    # --- lado de la placa (lo que llama el firmware)
    def active(self, valor=None):
        return True

    def config(self, *args, **kw):
        if "gap_name" in kw:
            self.nombre = kw["gap_name"]

    def irq_handler(self, handler):
        self.irq = handler

    def gatts_register_services(self, servicios):
        return ((self.H_TX, self.H_RX),)

    def gatts_set_buffer(self, handle, largo, agregar=False):
        pass

    def gatts_read(self, handle):
        with self._lock:
            datos, self.rx = self.rx, b""
        return datos

    def gatts_notify(self, conexion, handle, datos):
        if conexion == self.conexion and self.al_notificar:
            self.al_notificar(bytes(datos))

    def gap_advertise(self, intervalo, adv_data=None, resp_data=None):
        self.anunciando = intervalo is not None
        self.anuncio = adv_data

    def gap_disconnect(self, conexion):
        if conexion == self.conexion:
            self._cortar()

    # --- lado del PC (central)
    def visible(self, nombre):
        return self.anunciando and not self.fuera_de_alcance and self.nombre == nombre

    def conectar(self, al_notificar, al_desconectar):
        if not self.anunciando or self.fuera_de_alcance:
            raise OSError("la mano no está disponible")
        self.conexiones += 1
        self.conexion = 100 + self.conexiones
        self.anunciando = False                      # MicroPython deja de anunciarse al conectarse
        self.al_notificar, self.al_desconectar = al_notificar, al_desconectar
        self.irq(1, (self.conexion, 0, b""))

    def escribir(self, datos):
        if self.conexion is None or self.fuera_de_alcance:
            raise OSError("no hay conexión")
        with self._lock:
            self.rx += bytes(datos)
        self.irq(3, (self.conexion, self.H_RX))

    def desconectar_central(self):
        if self.conexion is not None:
            self._cortar()

    def _cortar(self):
        conexion, avisar = self.conexion, self.al_desconectar
        self.conexion, self.al_notificar, self.al_desconectar = None, None, None
        self.irq(2, (conexion, 0, b""))
        if avisar:
            avisar()

    def salir_de_alcance(self):
        """Como alejarse o apagar la placa: se corta la conexión y deja de verse."""
        self.fuera_de_alcance = True
        if self.conexion is not None:
            self._cortar()

    def volver(self):
        self.fuera_de_alcance = False


def bluetooth_falso(radio):
    ble = types.SimpleNamespace(active=radio.active, config=radio.config, irq=radio.irq_handler,
                                gatts_register_services=radio.gatts_register_services,
                                gatts_set_buffer=radio.gatts_set_buffer, gatts_read=radio.gatts_read,
                                gatts_notify=radio.gatts_notify, gap_advertise=radio.gap_advertise,
                                gap_disconnect=radio.gap_disconnect)
    return types.SimpleNamespace(BLE=lambda: ble, UUID=UUIDFalso)


class BleakFalso:
    """El mismo uso de bleak que hace pgc/adaptadores/mano_ble.py, contra la RadioBLE."""

    def __init__(self, radio):
        self.radio = radio
        radio_ = radio

        class Escaner:
            @staticmethod
            async def find_device_by_name(nombre, timeout=5.0):
                limite = _time.monotonic() + min(timeout, 1.0)
                while _time.monotonic() < limite:
                    if radio_.visible(nombre):
                        return types.SimpleNamespace(name=nombre, address="AA:BB:CC:DD:EE:FF")
                    await asyncio.sleep(0.02)
                return None

        class Cliente:
            def __init__(self, dispositivo, disconnected_callback=None):
                self.dispositivo = dispositivo
                self.al_desconectar = disconnected_callback
                self.al_notificar = None
                self.is_connected = False

            async def connect(self, timeout=10.0):
                radio_.conectar(self._notificar, self._desconectado)
                self.is_connected = True

            def _notificar(self, datos):
                if self.al_notificar:
                    self.al_notificar(None, bytearray(datos))

            def _desconectado(self):
                self.is_connected = False
                if self.al_desconectar:
                    self.al_desconectar(self)

            async def start_notify(self, caracteristica, callback):
                assert caracteristica.upper() == UART_TX
                self.al_notificar = callback

            async def write_gatt_char(self, caracteristica, datos, response=False):
                assert caracteristica.upper() == UART_RX
                assert len(datos) <= 20, "paquetes de más de 20 bytes"
                radio_.escribir(datos)

            async def disconnect(self):
                if self.is_connected:
                    radio_.desconectar_central()
                self.is_connected = False

        self.Escaner, self.Cliente = Escaner, Cliente


# =============================================================================
#  Ejecutar el firmware
# =============================================================================
@contextmanager
def modulos(**reemplazos):
    """Pone módulos falsos en sys.modules mientras corre el firmware (None = 'no existe')."""
    antes = {n: sys.modules.get(n, KeyError) for n in reemplazos}
    sys.modules.update(reemplazos)
    try:
        yield
    finally:
        for n, v in antes.items():
            if v is KeyError:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = v


def ejecutar(ruta, registro, stdin, salida, config_ble=None, radio=None, escala=0.0, pausa_bucle=None,
             espacio=None):
    """Ejecuta un main.py de MicroPython hasta que termine (con 'salir').

    espacio: diccionario de variables globales del programa (para mirarlo mientras corre).
    """
    fuente = ruta.read_text(encoding="utf-8")
    for linea in ("from machine import Pin, PWM\n", "import time\n", "import sys\n"):
        fuente = fuente.replace(linea, "", 1)
    m = machine_falso(registro)
    espacio = {} if espacio is None else espacio
    espacio.update({"__name__": "__main__", "Pin": m.Pin, "PWM": m.PWM,
                    "time": tiempo_falso(registro, escala, pausa_bucle),
                    "sys": types.SimpleNamespace(stdin=stdin)})
    original_print = print

    def imprimir(*args, **kw):                      # print() del firmware → Salida
        original_print(*args, file=salida, **{k: v for k, v in kw.items() if k != "file"})

    espacio["print"] = imprimir
    with modulos(uselect=uselect_falso(), micropython=types.SimpleNamespace(const=lambda x: x),
                 bluetooth=bluetooth_falso(radio or RadioBLE()), config_ble=config_ble):
        exec(compile(fuente, str(ruta), "exec"), espacio)
    return espacio


def correr(ruta, ordenes, **kw):
    """Corre el firmware con estas órdenes por USB (y 'salir'). Devuelve (registro, líneas impresas)."""
    registro, salida = Registro(), Salida()
    stdin = StdinFalso("".join(o + "\n" for o in ordenes) + "salir\n")
    ejecutar(ruta, registro, stdin, salida, **kw)
    return registro, salida.lineas()


def config_ble_falso(token, nombre="Mano-LSC"):
    return types.SimpleNamespace(NOMBRE=nombre, TOKEN=token)


class PlacaEnHilo:
    """El main.py REAL corriendo en un hilo, con Bluetooth (radio falsa)."""

    def __init__(self, token, nombre="Mano-LSC", escala=0.0):
        self.registro, self.salida = Registro(), Salida()
        self.stdin = StdinFalso()
        self.radio = RadioBLE()
        self.callada = threading.Event()             # set(): la placa se "cuelga"
        self.error = None
        self.espacio = {}                            # variables globales del main.py en marcha
        self.ordenes = []                            # órdenes que recibió (USB o Bluetooth)
        cfg = config_ble_falso(token, nombre)

        def bucle_colgado():
            while self.callada.is_set():
                _time.sleep(0.01)

        def correr_main():
            try:
                ejecutar(MAIN, self.registro, self.stdin, self.salida, config_ble=cfg, radio=self.radio,
                         escala=escala, pausa_bucle=bucle_colgado, espacio=self.espacio)
            except Exception as ex:                  # para verlo en la prueba
                self.error = ex

        self.hilo = threading.Thread(target=correr_main, daemon=True, name="placa")
        self.hilo.start()
        limite = _time.time() + 5
        while _time.time() < limite and "Listo. Esperando comandos..." not in self.salida.lineas():
            _time.sleep(0.01)
        # El bucle busca `atender_orden` en cada vuelta: se envuelve para anotar las órdenes
        atender = self.espacio.get("atender_orden")
        if atender:
            def anotar(cmd, responder):
                self.ordenes.append(cmd.strip())
                return atender(cmd, responder)
            self.espacio["atender_orden"] = anotar

    def detener(self):
        self.callada.clear()
        self.stdin.escribir("salir\n")
        self.hilo.join(5)


class CentralFalsa:
    """Un PC conectado por Bluetooth, escribiendo directo a la radio (para probar la placa)."""

    def __init__(self, placa):
        self.radio = placa.radio
        self.recibido = b""
        self.desconectado = threading.Event()
        self.radio.conectar(self._notificar, self.desconectado.set)

    def _notificar(self, datos):
        assert len(datos) <= 20
        self.recibido += datos

    def enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), 20):
            self.radio.escribir(datos[k:k + 20])

    def lineas(self, cuantas, timeout=5):
        limite = _time.time() + timeout
        while self.recibido.count(b"\n") < cuantas and _time.time() < limite:
            _time.sleep(0.005)
        partes = self.recibido.split(b"\n")
        listas, self.recibido = partes[:cuantas], b"\n".join(partes[cuantas:])
        return [p.decode() for p in listas]

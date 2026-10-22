"""Red de seguridad: pruebas de caracterización del comportamiento actual.

ÚNICO punto de acoplamiento con la estructura del código: los imports y la
forma de armar el sistema con dobles están solo aquí. Cuando se reorganicen los
módulos, se cambia este archivo y las pruebas deben seguir pasando sin tocarlas.
"""
import os
import sys
import threading
import time
import types
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from pgc import arranque, config  # noqa: E402
from pgc.adaptadores import acceso, mano_respaldo, mano_simulada, mano_usb, whisper  # noqa: E402
from pgc.api.app import crear_app  # noqa: E402
from pgc.dominio import ordenes as modulo_ordenes  # noqa: E402,F401
from pgc.dominio import texto as modulo_texto      # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

def pytest_addoption(parser):
    parser.addoption("--reconocedor", default="pgc.adaptadores.reconocedor_simulado:ReconocedorSimulado",
                     help="clase a revisar con tests/contratos (paquete.modulo:Clase)")


# Valores que tenía servidor.py antes de la migración (los compara test_config)
servidor = types.SimpleNamespace(PAUSA_ENTRE_LETRAS=0.5, PAUSA_NO_DISPONIBLE=0.9, MAX_PENDIENTES_CLIENTE=2,
                                 MAX_COLA=30, MAX_AUDIO_BYTES=10 * 1024 * 1024)


# =============================================================================
#  Dobles de prueba
# =============================================================================
class ManoFalsa:
    """Misma interfaz que mano_serial.Mano; registra cada orden que recibiría el ESP32."""

    def __init__(self, puerto=None, baudios=115200, simular=False, log=print):
        self.ordenes = []
        self.letras = None             # None = la mano no reportó letras (usa las por defecto)
        self.conectada = False
        self.puerto = None
        self.conexiones = 0
        self.fallar = set()            # órdenes a las que la mano "no confirma" (devuelve False)
        self.bloquear_en = None        # la primera vez que llegue esta orden, espera a `soltar`
        self.llego = threading.Event()
        self.soltar = threading.Event()

    @property
    def modo(self):
        return "real" if self.conectada else "simulada"

    @property
    def medio(self):
        return "usb" if self.conectada else None

    def conectar(self):
        self.conexiones += 1
        return self.conectada

    def revisar(self):
        self.revisiones = getattr(self, "revisiones", 0) + 1
        return False

    def latido(self):
        return self.conectada

    def cerrar(self):
        self.conectada = False

    _cerrar = cerrar

    def hacer(self, orden):
        self.ordenes.append(orden)
        if orden == self.bloquear_en and not self.llego.is_set():
            self.llego.set()
            self.soltar.wait(5)
        return orden not in self.fallar

    def reset(self):
        return self.hacer("reset")


class TranscriptorFalso:
    """Misma interfaz que voz_entrada.Transcriptor, sin cargar Whisper."""

    def __init__(self, log=print, al_cambiar=None):
        self.estado = "listo"
        self.dispositivo = "cuda float16"
        self.texto = "hola jurado"
        self.segundos = 3.0            # lo que respondería PyAV
        self.error = None
        self.cargado = False
        self.recibidos = []            # (ruta, existía durante la transcripción, bytes)

    @property
    def listo(self):
        return self.estado == "listo"

    def cargar_en_segundo_plano(self):
        self.cargado = True

    def transcribir(self, ruta):
        with open(ruta, "rb") as f:
            self.recibidos.append((ruta, os.path.exists(ruta), f.read()))
        if self.error:
            raise self.error
        return self.texto

    def duracion(self, ruta):
        return self.segundos


class TunelFalso:
    """Misma interfaz que tunel.Tunel, sin lanzar cloudflared."""
    URL = "https://prueba-pgc.trycloudflare.com"

    def __init__(self, puerto, log=print, al_cambiar=None):
        self.url = None
        self.estado = "apagado"
        self.iniciado = False
        self.detenido = False

    def iniciar(self):
        self.iniciado = True
        self.estado = "activo"
        self.url = self.URL

    def detener(self):
        self.detenido = True


class FabricaMano:
    """Arma la mano de verdad (USB + simulada) con la forma del antiguo módulo mano_serial.

    Las pruebas del protocolo reemplazan `serial`, `time` y `TIMEOUT_LETRA` con
    monkeypatch sobre este objeto; aquí se inyectan en el constructor.
    """
    VIDS_ESP32 = mano_usb.VIDS_ESP32
    TIEMPO_SIMULADO = mano_simulada.TIEMPO_SIMULADO

    def __init__(self):
        self.serial = mano_usb.serial
        self.time = time
        self.TIMEOUT_LETRA = mano_usb.TIMEOUT_LETRA

    def Mano(self, puerto=None, simular=False, log=print):
        return mano_respaldo.Mano(puerto=puerto, simular=simular, log=log, timeout_letra=self.TIMEOUT_LETRA,
                                  modulo_serial=self.serial, dormir=self.time.sleep, reloj=self.time.time)

    def buscar_puerto(self):
        return mano_usb.buscar_puerto(modulo_serial=self.serial)


mano_serial = FabricaMano()     # constantes del adaptador (las usa test_config)

IP_LOCAL = "192.168.0.10"


# =============================================================================
#  Utilidades
# =============================================================================
def esperar(condicion, timeout=5.0, paso=0.01):
    limite = time.time() + timeout
    while time.time() < limite:
        if condicion():
            return True
        time.sleep(paso)
    raise AssertionError("La condición no se cumplió a tiempo")


def tipos(pasos):
    """[('S','nd'), ('E','ok'), ...] para comparar secuencias de forma legible."""
    return [(p["c"], p["tipo"]) for p in pasos]


# =============================================================================
#  Fixtures
# =============================================================================
@pytest.fixture
def texto():
    """Módulo de texto → secuencia (limpiar, a_secuencia, constantes)."""
    return modulo_texto


@pytest.fixture
def modulo_mano():
    return FabricaMano()


@pytest.fixture
def modulo_tunel():
    return acceso


@pytest.fixture
def modulo_voz():
    return whisper


@pytest.fixture
def registro():
    """Líneas que el servidor escribe en el log."""
    return []


def configuracion(simular=True, puerto=None, puerto_web=8000, sin_tunel=False, sin_voz=False, no_abrir=True,
                  dev=False, **ajustes):
    """Config como la daría la línea de comandos de siempre, sin pausas (las pruebas corren en ms).

    ajustes: otros campos de Config (p. ej. lim_mensaje_ip=2) para una prueba concreta.
    """
    argv = ["--puerto-web", str(puerto_web)]
    argv += ["--simular"] * simular + ["--sin-tunel"] * sin_tunel + ["--sin-voz"] * sin_voz + ["--no-abrir"] * no_abrir
    argv += ["--dev"] * dev
    if puerto:
        argv += ["--puerto", puerto]
    cfg = config.cargar(argv, entorno={}, archivo_env=RAIZ / "tests" / "no-existe.env")
    return replace(cfg, pausa_letra=0, pausa_no_disponible=0, **ajustes)


@pytest.fixture
def crear_sistema(registro):
    """Arma el sistema con dobles de mano, Whisper, túnel y red; por defecto sin hilo de la mano."""
    def crear(**opciones):
        return arranque.construir_sistema(
            configuracion(**opciones), log=registro.append,
            crear_mano=lambda cfg, log: ManoFalsa(),
            crear_transcriptor=lambda cfg, log, al_cambiar: TranscriptorFalso(log, al_cambiar),
            crear_tunel=lambda cfg, log, al_cambiar: TunelFalso(cfg.puerto_web, log, al_cambiar),
            ip_local=lambda: IP_LOCAL)
    return crear


@pytest.fixture
def sistema_con_mano(crear_sistema):
    """Sistema con el hilo de la mano corriendo (deletrea de verdad contra la ManoFalsa)."""
    s = crear_sistema()
    s.iniciar_trabajador()
    esperar(lambda: s.mano.conexiones >= 1)
    yield s
    s.mano.soltar.set()


@pytest.fixture
def abrir_api(crear_sistema):
    """Abre la app con TestClient (ejecuta el ciclo de vida: hilo de la mano, voz, túnel).

    desde: IP de origen ("testclient" = un celular cualquiera; "127.0.0.1" o "::1" = el PC).
    Desde el PC se usa Host: 127.0.0.1:8000, como el navegador del proyector.
    """
    pendientes = []

    @contextmanager
    def abrir(desde="testclient", **opciones):
        sistema = crear_sistema(**opciones)
        app = crear_app(sistema, abrir_navegador=lambda url: None)
        base = "http://127.0.0.1:8000" if desde in ("127.0.0.1", "::1") else "http://testserver"
        with TestClient(app, client=(desde, 50000), base_url=base) as cliente:
            pendientes.append(sistema)
            yield cliente, sistema
    yield abrir
    for s in pendientes:
        s.mano.soltar.set()


def token_de_pantalla(cliente):
    """El token como lo obtiene el navegador: del <meta> de /pantalla ('' si no lo hay)."""
    import re
    m = re.search(r'<meta name="pgc-admin" content="([^"]*)">', cliente.get("/pantalla").text)
    return m.group(1) if m else ""


def admin(cliente):
    """Encabezados del presentador para las rutas /api/mano/*."""
    return {"X-PGC-Admin": token_de_pantalla(cliente)}


# Comienzo de un archivo webm (firma EBML): pasa la revisión de "parece audio"
AUDIO_WEBM = b"\x1a\x45\xdf\xa3" + b"\x00" * 12


@pytest.fixture
def carpeta_web():
    return RAIZ / "web"

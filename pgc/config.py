"""Configuración centralizada.

Prioridad (de menor a mayor): valores por defecto → archivo .env → variables de
entorno PGC_* → opciones de la línea de comandos. Ningún otro módulo lee
variables de entorno: todos reciben un `Config`.
"""
import argparse
import os
from dataclasses import dataclass, fields, replace
from pathlib import Path

from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent.parent
MODOS_MANO = ("auto", "ble", "usb", "simulada")
CAPTURADORES = ("auto", "kinect", "camara_pc", "no")


class ErrorConfig(ValueError):
    """Valor inválido en .env, en una variable de entorno o en una opción."""


@dataclass(frozen=True)
class Config:
    # --- web
    puerto_web: int = 8000
    abrir_navegador: bool = True
    ping_ws: float = 20.0                  # s sin cambios antes de enviar un ping por el WebSocket
    # --- mano
    mano: str = "auto"                     # auto (Bluetooth → USB → simulada) | ble | usb | simulada
    mano_puerto: str | None = None         # None = autodetección por VID
    mano_ble_nombre: str = "Mano-LSC"      # NOMBRE de config_ble.py (con el que la placa se anuncia)
    mano_ble_token: str = ""               # secreto compartido con config_ble.py; vacío = sin Bluetooth
    mano_ble_reintento: float = 10.0       # s entre intentos de conectar por Bluetooth
    mano_baudios: int = 115200
    mano_vids: tuple[int, ...] = (0x303A, 0x1A86, 0x10C4)
    mano_timeout_letra: float = 12.0       # s máximos esperando "ok:<letra>"
    mano_tiempo_simulado: float = 1.2      # duración de una letra en modo simulado
    autodeteccion_cada: float = 3.0        # s entre búsquedas de la mano en reposo
    # --- deletreo y cola
    pausa_letra: float = 0.5               # la letra queda formada un momento para que se lea
    pausa_no_disponible: float = 0.9       # letras que la mano no hace: solo se muestran
    max_caracteres: int = 60
    max_pendientes_cliente: int = 2
    max_cola: int = 30
    historial: int = 6
    # --- voz
    voz: bool = True
    voz_modelo: str = "medium"
    audio_max_mb: int = 10
    audio_max_segundos: float = 15.0       # la página corta a 10 s
    voz_max_en_espera: int = 3             # transcripciones esperando turno (además de la que corre)
    # --- túnel
    tunel: bool = True
    # --- voz de salida (Coqui VITS): dice en los parlantes del PC las frases del Kinect
    voz_salida: bool = True
    voz_salida_modelo: str = "tts_models/es/css10/vits"
    # --- Kinect: "kinect" (detector SVM de integracion_kinect/), "simulado" o "paquete.modulo:Clase"
    reconocedor: str = "kinect"
    kinect_url: str = "http://127.0.0.1:8765"   # detector (server_web_svm.py)
    kinect_intervalo: float = 0.3          # s entre consultas a /spell/status
    kinect_lanzar: bool = True             # arrancar el detector y el capturador junto con la plataforma
    kinect_detector_paralelo: bool = True  # su server_web_svm.py envuelto con lecturas en paralelo (detector_paralelo.py)
    kinect_python: str = ""                # Python del entorno del detector; vacío = buscarlo (ver procesos.py)
    kinect_capturador: str = "auto"        # auto (app C# si está compilada) | kinect | camara_pc | no
    kinect_exe: str = ""                   # LSCKinectFramework.exe; vacío = buscarlo en bin/Release o bin/Debug
    kinect_camara: int = 0                 # cámara del PC para kinect_capturador=camara_pc
    kinect_turno_segundos: float = 120.0   # el turno de un celular se libera tras este tiempo sin usarlo
    kinect_codigo: bool = True             # para tomar el turno hay que escribir el código de 6 dígitos del proyector
    kinect_eco: bool = False               # modo eco al arrancar: la mano repite lo que reconoce el Kinect
    lim_kinect_cliente: int = 60           # controles del Kinect por minuto y celular
    # --- seguridad
    dev: bool = False                      # publica /docs y /openapi.json (opción --dev)
    texto_max_cuerpo: int = 200            # caracteres que acepta la API antes de recortar a max_caracteres
    json_max_kb: int = 16                  # tamaño máximo del cuerpo de una petición (salvo el audio)
    lim_mensaje_ip: int = 20               # peticiones por minuto
    lim_mensaje_cliente: int = 6
    lim_transcribir_ip: int = 10
    lim_transcribir_cliente: int = 4
    lim_previa_ip: int = 240
    lim_general_ip: int = 300
    ws_max_conexiones: int = 100
    ws_max_por_ip: int = 40                # por el túnel, los celulares del mismo WiFi comparten una IP
    log_textos: bool = False               # escribir los textos de los mensajes en el log (solo para depurar)

    @property
    def audio_max_bytes(self):
        return self.audio_max_mb * 1024 * 1024


# ----------------------------------------------------------------- lectura
def _a_bool(texto):
    t = texto.strip().lower()
    if t in ("1", "true", "si", "sí", "yes", "on"):
        return True
    if t in ("0", "false", "no", "off", ""):
        return False
    raise ValueError("se esperaba true o false")


def _a_vids(texto):
    return tuple(int(v.strip(), 16) for v in texto.split(",") if v.strip())


def _convertir(campo, texto):
    if campo.name == "mano_vids":
        return _a_vids(texto)
    if campo.name == "mano_puerto":
        return texto.strip() or None
    tipo = campo.type
    if tipo is bool:
        return _a_bool(texto)
    if tipo is int:
        return int(texto)
    if tipo is float:
        return float(texto)
    return texto.strip()


def _desde_variables(variables):
    """Toma solo las PGC_<CAMPO> conocidas y las convierte a su tipo."""
    valores = {}
    for campo in fields(Config):
        nombre = "PGC_" + campo.name.upper()
        if nombre in variables and variables[nombre] is not None:
            try:
                valores[campo.name] = _convertir(campo, variables[nombre])
            except ValueError as ex:
                raise ErrorConfig(f"{nombre}={variables[nombre]!r} no es válido: {ex}") from None
    return valores


def crear_parser():
    """Las mismas opciones de siempre de servidor.py."""
    ap = argparse.ArgumentParser(description="Servidor de la mano robótica LSC")
    ap.add_argument("--simular", action="store_true", help="no buscar la mano; simularla")
    ap.add_argument("--puerto", help="puerto serial de la mano (ej. COM5)")
    ap.add_argument("--puerto-web", type=int, default=None)
    ap.add_argument("--sin-tunel", action="store_true", help="no lanzar cloudflared")
    ap.add_argument("--sin-voz", action="store_true", help="no cargar Whisper")
    ap.add_argument("--no-abrir", action="store_true", help="no abrir el navegador")
    ap.add_argument("--dev", action="store_true", help="modo desarrollo: publica /docs y /openapi.json")
    return ap


def _desde_opciones(args):
    valores = {}
    if args.simular:
        valores["mano"] = "simulada"
    if args.puerto:
        valores["mano_puerto"] = args.puerto
    if args.puerto_web is not None:
        valores["puerto_web"] = args.puerto_web
    if args.sin_tunel:
        valores["tunel"] = False
    if args.sin_voz:
        valores["voz"] = False
    if args.no_abrir:
        valores["abrir_navegador"] = False
    if args.dev:
        valores["dev"] = True
    return valores


def validar(cfg):
    if cfg.mano not in MODOS_MANO:
        raise ErrorConfig(f"PGC_MANO debe ser uno de {', '.join(MODOS_MANO)} (llegó {cfg.mano!r})")
    if cfg.kinect_capturador not in CAPTURADORES:
        raise ErrorConfig(f"PGC_KINECT_CAPTURADOR debe ser uno de {', '.join(CAPTURADORES)} "
                          f"(llegó {cfg.kinect_capturador!r})")
    if not cfg.kinect_url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise ErrorConfig("PGC_KINECT_URL debe apuntar a este PC (http://127.0.0.1:<puerto>)")
    if not 1 <= cfg.puerto_web <= 65535:
        raise ErrorConfig(f"puerto web fuera de rango: {cfg.puerto_web}")
    if not cfg.mano_ble_nombre:
        raise ErrorConfig("PGC_MANO_BLE_NOMBRE no puede estar vacío")
    if cfg.mano_ble_token and len(cfg.mano_ble_token) < 16:
        raise ErrorConfig("PGC_MANO_BLE_TOKEN es muy corto (mínimo 16 caracteres)")
    if cfg.mano == "ble" and not cfg.mano_ble_token:
        raise ErrorConfig("PGC_MANO=ble necesita PGC_MANO_BLE_TOKEN (el mismo TOKEN de config_ble.py)")
    for nombre in ("max_caracteres", "max_pendientes_cliente", "max_cola", "historial", "audio_max_mb",
                   "texto_max_cuerpo", "json_max_kb", "lim_mensaje_ip", "lim_mensaje_cliente", "lim_transcribir_ip",
                   "lim_transcribir_cliente", "lim_previa_ip", "lim_general_ip", "ws_max_conexiones", "ws_max_por_ip",
                   "lim_kinect_cliente"):
        if getattr(cfg, nombre) < 1:
            raise ErrorConfig(f"PGC_{nombre.upper()} debe ser mayor que 0")
    if cfg.texto_max_cuerpo < cfg.max_caracteres:
        raise ErrorConfig("PGC_TEXTO_MAX_CUERPO no puede ser menor que PGC_MAX_CARACTERES")
    for nombre in ("pausa_letra", "pausa_no_disponible", "mano_timeout_letra", "mano_tiempo_simulado",
                   "autodeteccion_cada", "ping_ws", "audio_max_segundos", "voz_max_en_espera", "mano_ble_reintento",
                   "kinect_intervalo", "kinect_turno_segundos", "kinect_camara"):
        if getattr(cfg, nombre) < 0:
            raise ErrorConfig(f"PGC_{nombre.upper()} no puede ser negativo")
    return cfg


def cargar(argv=None, entorno=None, archivo_env=None):
    """Arma la configuración final.

    argv: opciones de línea de comandos (None = sys.argv[1:]; [] = ninguna).
    entorno: variables de entorno (None = os.environ).
    archivo_env: ruta del .env (None = .env en la carpeta del proyecto; si no existe, se ignora).
    """
    archivo_env = Path(archivo_env) if archivo_env is not None else RAIZ / ".env"
    valores = {}
    if archivo_env.is_file():
        valores.update(_desde_variables(dotenv_values(archivo_env)))
    valores.update(_desde_variables(os.environ if entorno is None else entorno))
    args = crear_parser().parse_args(argv)
    valores.update(_desde_opciones(args))
    return validar(replace(Config(), **valores))

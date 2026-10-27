"""Raíz de composición: el único lugar que conoce los adaptadores concretos.

Lee la configuración, crea la mano, la voz y el túnel, arma el Sistema y la app web.
"""
import importlib
import sys

from pgc import config, registro
from pgc.adaptadores import acceso
from pgc.adaptadores.mano_respaldo import Mano
from pgc.adaptadores.mano_ble import ManoBLE
from pgc.aplicacion.estado import Publicador
from pgc.aplicacion.sistema import Sistema
from pgc.dominio.moderacion import cargar_moderador


def crear_mano(cfg, log):
    ble = None
    if cfg.mano_ble_token and cfg.mano in ("auto", "ble"):
        ble = ManoBLE(cfg.mano_ble_nombre, cfg.mano_ble_token, timeout_letra=cfg.mano_timeout_letra, log=log,
                      reintento=cfg.mano_ble_reintento)
    return Mano(puerto=cfg.mano_puerto, baudios=cfg.mano_baudios, simular=cfg.mano == "simulada", log=log,
                timeout_letra=cfg.mano_timeout_letra, vids=cfg.mano_vids, tiempo_simulado=cfg.mano_tiempo_simulado,
                modo=cfg.mano, ble=ble)


def crear_transcriptor(cfg, log, al_cambiar):
    from pgc.adaptadores.whisper import Transcriptor    # importa numpy: solo si se usa
    return Transcriptor(log=log, al_cambiar=al_cambiar, nombre_modelo=cfg.voz_modelo, log_textos=cfg.log_textos)


def crear_tunel(cfg, log, al_cambiar):
    return acceso.Tunel(cfg.puerto_web, log=log, al_cambiar=al_cambiar)


def ip_local():
    return acceso.ip_local()


RECONOCEDORES = {"kinect": "pgc.adaptadores.kinect.reconocedor:ReconocedorKinect"}


def cargar_reconocedor(cfg, log):
    """'kinect', 'simulado' o 'paquete.modulo:Clase'. Si falla, el simulado (la demo no se cae).

    Si la clase tiene desde_config(cfg), se arma con la configuración; si no, sin argumentos (contrato, regla 6).
    """
    from pgc.adaptadores.reconocedor_simulado import ReconocedorSimulado
    if cfg.reconocedor == "simulado":
        return ReconocedorSimulado()
    try:
        modulo, nombre = RECONOCEDORES.get(cfg.reconocedor, cfg.reconocedor).split(":")
        clase = getattr(importlib.import_module(modulo), nombre)
        return clase.desde_config(cfg) if hasattr(clase, "desde_config") else clase()
    except Exception as ex:
        log(f"[kinect] No se pudo cargar {cfg.reconocedor}: {type(ex).__name__}: {ex} -> simulado")
        return ReconocedorSimulado(detalle="Kinect: no disponible")


def crear_sintetizador(cfg, log, al_cambiar):
    from pgc.adaptadores.voz_salida import SintetizadorCoqui
    return SintetizadorCoqui(cfg.voz_salida_modelo, log=log, al_cambiar=al_cambiar)


def crear_lanzador(cfg, log):
    from pgc.adaptadores.kinect.procesos import LanzadorKinect
    return LanzadorKinect(cfg, log)


def construir_sistema(cfg, log=registro.log, *, crear_mano=crear_mano, crear_transcriptor=crear_transcriptor,
                      crear_tunel=crear_tunel, ip_local=ip_local, crear_reconocedor=cargar_reconocedor,
                      crear_sintetizador=crear_sintetizador):
    """Arma el Sistema. Las pruebas pasan sus dobles en lugar de los adaptadores reales."""
    mano = crear_mano(cfg, log)
    publicador = Publicador()
    voz = crear_transcriptor(cfg, log, publicador.notificar)
    tunel = crear_tunel(cfg, log, publicador.notificar)
    sintetizador = crear_sintetizador(cfg, log, publicador.notificar) if cfg.voz_salida else None
    url_local = f"http://{ip_local()}:{cfg.puerto_web}"
    return Sistema(cfg, mano, voz, tunel, url_local, publicador, log, moderador=cargar_moderador(),
                   reconocedor=crear_reconocedor(cfg, log), sintetizador=sintetizador)


def main(argv=None):
    # Evita que un carácter raro en consola tumbe el servidor
    try:
        sys.stdout.reconfigure(errors="replace")
        sys.stderr.reconfigure(errors="replace")
    except AttributeError:
        pass
    try:
        cfg = config.cargar(argv)
    except config.ErrorConfig as ex:
        print(f"Error de configuración: {ex}", file=sys.stderr)
        return 2

    import uvicorn
    from pgc.api.app import crear_app

    sistema = construir_sistema(cfg)
    app = crear_app(sistema)
    lanzador = crear_lanzador(cfg, registro.log)     # detector + app del Kinect (o cámara del PC)
    lanzador.iniciar()
    try:
        uvicorn.run(app, host="0.0.0.0", port=cfg.puerto_web, log_level="warning",
                    ws_max_size=64 * 1024,             # el servidor no espera mensajes de los clientes
                    limit_concurrency=cfg.ws_max_conexiones + 200)
    finally:
        lanzador.detener()                         # y si Python muere a la fuerza, el Job Object los cierra
    return 0

"""Mano con respaldo: Bluetooth → USB → simulada (implementa PuertoMano).

Modos (PGC_MANO):
  auto     Bluetooth si está configurado y responde; si no, USB; si no, simulada.
  ble      solo Bluetooth (y simulada si no responde).
  usb      solo USB (y simulada si no responde).
  simulada nunca busca la mano.
Si el medio activo se cae, se pasa al siguiente sin perder la letra en curso.
Entre mensajes, `revisar()` manda un latido, vuelve a buscar la mano y, en modo
auto, vuelve al Bluetooth cuando reaparece. El modo se muestra siempre en el proyector.
"""
import threading
import time

from pgc.adaptadores.mano_simulada import TIEMPO_SIMULADO, ManoSimulada
from pgc.adaptadores.mano_usb import TIMEOUT_LETRA, VIDS_ESP32, ManoUSB

NOMBRES = {"ble": "Bluetooth", "usb": "USB"}


class Mano:
    def __init__(self, puerto=None, baudios=115200, simular=False, log=print, *,
                 timeout_letra=TIMEOUT_LETRA, vids=VIDS_ESP32, tiempo_simulado=TIEMPO_SIMULADO,
                 modulo_serial=None, dormir=time.sleep, reloj=time.time, modo="auto", ble=None):
        self.puerto_pedido = puerto
        self.modo_config = "simulada" if simular else modo
        self.log = log
        self.usb = ManoUSB(baudios, timeout_letra, vids, log, modulo_serial, dormir, reloj)
        self.ble = ble                        # ManoBLE o None (sin token configurado)
        self.simulada = ManoSimulada(tiempo_simulado, dormir=dormir)
        self.activo = None                    # ManoUSB o ManoBLE en uso
        self._letras = None                   # se conservan aunque la mano se desconecte
        self._puerto_fallido = None           # puerto USB que falló (no se reintenta hasta desenchufarlo)
        self._lock = threading.Lock()         # una orden a la vez

    # ------------------------------------------------------------------ estado
    @property
    def forzar_simulado(self):
        return self.modo_config == "simulada"

    @property
    def conectada(self):
        return self.activo is not None and self.activo.conectada

    @property
    def modo(self):
        return "real" if self.conectada else "simulada"

    @property
    def medio(self):
        return self.activo.medio if self.conectada else None

    @property
    def puerto(self):
        return self.activo.puerto if self.activo is not None else None

    @property
    def letras(self):
        return self._letras

    @letras.setter
    def letras(self, valor):
        self._letras = valor

    def _medios(self):
        if self.forzar_simulado:
            return []
        medios = ["ble"] if self.ble is not None and self.modo_config in ("auto", "ble") else []
        return medios + (["usb"] if self.modo_config in ("auto", "usb") else [])

    # --------------------------------------------------------------- conexión
    def _usar(self, medio):
        nuevo = self.ble if medio == "ble" else self.usb
        if self.activo is not None and self.activo is not nuevo:
            self.activo.cerrar()
        self.activo = nuevo
        if nuevo.letras:
            self._letras = nuevo.letras

    def _conectar(self, medio):
        if medio == "ble":
            ok = self.ble.conectar()
        else:
            if not self.usb.disponible:
                self.log("[mano] pyserial no está instalado -> modo simulado")
                return False
            puerto = self.puerto_pedido or self.usb.buscar_puerto()
            if not puerto:
                self.log("[mano] No se encontró el ESP32 -> modo simulado")
                self._puerto_fallido = None
                return False
            ok = self.usb.conectar(puerto)
            self._puerto_fallido = None if ok else puerto
        if ok:
            self._usar(medio)
        return ok

    def _respaldo(self, excluir):
        """Tras perder un medio, intenta los demás en orden. True si quedó conectada."""
        for medio in self._medios():
            if medio != excluir and self._conectar(medio):
                self.log(f"[mano] Respaldo: ahora por {NOMBRES[medio]}")
                return True
        return False

    def conectar(self):
        """Primera conexión (y la que pide el presentador con «Reconectar mano»)."""
        if self.forzar_simulado:
            return False
        if not self.usb.disponible and "ble" not in self._medios():
            self.log("[mano] pyserial no está instalado -> modo simulado")
            return False
        return any(self._conectar(medio) for medio in self._medios())

    def cerrar(self):
        if self.activo is not None:
            self.activo.cerrar()

    _cerrar = cerrar          # nombre antiguo

    def revisar(self):
        """Entre mensajes (cada ~3 s): latido, respaldo, regreso al Bluetooth y autodetección USB.

        Devuelve True si cambió la conexión (para avisar a las pantallas).
        """
        if self.forzar_simulado:
            return False
        with self._lock:
            antes = (self.conectada, self.medio)
            if self.conectada:
                medio = self.activo.medio
                if not self.activo.latido():
                    self.activo = None
                    self._respaldo(excluir=medio)
                elif medio == "usb" and "ble" in self._medios() and self.ble.puede_intentar():
                    if self.ble.conectar():                  # el Bluetooth volvió: se prefiere
                        self._usar("ble")
                        self.log("[mano] Cambio a Bluetooth")
            else:
                for medio in self._medios():
                    if medio == "ble":
                        if self.ble.puede_intentar() and self._conectar("ble"):
                            break
                        continue
                    puerto = self.puerto_pedido or self.usb.buscar_puerto()
                    if puerto is None:
                        self._puerto_fallido = None          # al volver a enchufarla, se reintenta
                    elif puerto != self._puerto_fallido:
                        self.log(f"[mano] Detectado {puerto}, conectando...")
                        if self._conectar("usb"):
                            break
            return antes != (self.conectada, self.medio)

    # ---------------------------------------------------------------- órdenes
    def hacer(self, letra):
        """Forma una letra (o 'reset'). Devuelve True si la mano confirmó."""
        with self._lock:
            if self.activo is not None and not self.activo.conectada:      # se cayó entre órdenes
                perdido, self.activo = self.activo.medio, None
                self._respaldo(excluir=perdido)
            if not self.conectada:
                return self.simulada.hacer(letra)
            ok = self.activo.hacer(letra)
            if not ok and not self.activo.conectada:                     # se cayó en esta orden
                perdido, self.activo = self.activo.medio, None
                if self._respaldo(excluir=perdido):
                    return self.activo.hacer(letra)                      # se repite por el respaldo
            return ok

    def reset(self):
        return self.hacer("reset")

    def latido(self):
        return self.activo.latido() if self.conectada else False

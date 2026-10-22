"""Mano por USB serial: una línea por orden, con la respuesta del código original.

PC → ESP32: "<letra>\\n" | "reset\\n"
ESP32 → PC: "gesto_<letra>_ok" | "comando_no_reconocido" | "reset_ok"   (ver protocolo_mano.py)
Ojo: en la PCB de la mano no se pueden conectar USB y 12 V a la vez; por USB la
placa responde pero los servos no se mueven (sirve para pruebas sin fuerza).
"""
import time

from pgc.adaptadores.protocolo_mano import ORDEN_COMPROBAR, RESPUESTA_RESET, resultado

try:
    import serial
    import serial.tools.list_ports
except ImportError:  # pyserial no instalado
    serial = None

# VID USB típicos: 303A = Espressif (USB nativo del S3), 1A86 = CH340, 10C4 = CP210x
VIDS_ESP32 = frozenset({0x303A, 0x1A86, 0x10C4})
TIMEOUT_LETRA = 12.0      # segundos máximos esperando "ok:<letra>"


def buscar_puerto(vids=VIDS_ESP32, modulo_serial=None):
    s = serial if modulo_serial is None else modulo_serial
    if s is None:
        return None
    for p in list(s.tools.list_ports.comports()):
        if p.vid in vids:
            return p.device
    return None


class ManoUSB:
    medio = "usb"

    def __init__(self, baudios=115200, timeout_letra=TIMEOUT_LETRA, vids=VIDS_ESP32, log=print,
                 modulo_serial=None, dormir=time.sleep, reloj=time.time):
        self.baudios = baudios
        self.timeout_letra = timeout_letra
        self.vids = vids
        self.log = log
        self.serial = serial if modulo_serial is None else modulo_serial
        self._dormir = dormir
        self._reloj = reloj
        self.ser = None
        self.puerto = None
        self.letras = None          # el firmware original no informa sus letras

    @property
    def disponible(self):
        """pyserial está instalado."""
        return self.serial is not None

    @property
    def conectada(self):
        return self.ser is not None

    def buscar_puerto(self):
        return buscar_puerto(self.vids, self.serial)

    # --------------------------------------------------------------- conexión
    def conectar(self, puerto):
        """Abre `puerto` y comprueba que el firmware responde (con "reset" → "reset_ok")."""
        try:
            s = self.serial.Serial()
            s.port = puerto
            s.baudrate = self.baudios
            s.timeout = 0.2
            s.dtr = False          # evita reiniciar la placa al abrir el puerto
            s.rts = False
            s.open()
            self._dormir(0.3)
            s.reset_input_buffer()
            self.ser = s
            self.puerto = puerto
            if not self._comando_espera(ORDEN_COMPROBAR, lambda l: l == RESPUESTA_RESET, min(6.0, self.timeout_letra)):
                # Puede que el programa no esté corriendo: Ctrl-C Ctrl-D = soft reboot
                s.write(b"\x03\x04")
                self._dormir(4.0)                 # el firmware abre los 6 dedos al arrancar (~3 s)
                s.reset_input_buffer()
                if not self._comando_espera(ORDEN_COMPROBAR, lambda l: l == RESPUESTA_RESET, min(8.0, self.timeout_letra)):
                    raise RuntimeError("el ESP32 no responde (¿main.py cargado? ¿Thonny abierto?)")
            self.letras = None                    # el firmware no informa sus letras: se usan las por defecto
            self.log(f"[mano] Conectada por USB en {puerto}")
            return True
        except Exception as ex:
            self.log(f"[mano] Error conectando en {puerto}: {ex} -> modo simulado")
            self.cerrar()
            return False

    def cerrar(self):
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        self.ser = None

    def _leer_linea(self):
        raw = self.ser.readline()
        if not raw:
            return None
        return raw.decode("utf-8", "ignore").strip().lower()

    def _comando_espera(self, cmd, condicion, timeout):
        self.ser.write((cmd + "\n").encode())
        limite = self._reloj() + timeout
        while self._reloj() < limite:
            linea = self._leer_linea()
            if linea is None:
                continue
            if condicion(linea):
                return linea
            if linea.startswith("error:"):
                self.log(f"[mano] {linea}")
        return None

    # ---------------------------------------------------------------- órdenes
    def hacer(self, letra):
        """Envía una letra (o 'reset') y espera su confirmación. True si la mano la hizo."""
        try:
            resp = self._comando_espera(letra, lambda l: resultado(letra, l) is not None, self.timeout_letra)
            if resp is None:
                self.log(f"[mano] Sin confirmación para '{letra}' (timeout)")
                return False
            return resultado(letra, resp)
        except Exception as ex:
            self.log(f"[mano] Se perdió la conexión: {ex}")
            self.cerrar()
            return False

    def latido(self):
        """El firmware original no tiene "ping": entre mensajes no se le manda nada."""
        return self.conectada

"""Mano por Bluetooth (BLE): las mismas órdenes y respuestas que por USB (código original), con token.

El ESP32-S3 solo tiene Bluetooth de bajo consumo (BLE), así que no aparece como puerto COM:
se usa el servicio "UART" de Nordic (lo que el PC escribe en RX le llega a la placa como
líneas; lo que la placa responde llega por notificaciones de TX). No hace falta emparejar.

PC → ESP32: "auth <token>" (primera línea), luego "<letra>" | "reset"
ESP32 → PC: "ok:auth" | "error:auth", luego "gesto_<letra>_ok" | "comando_no_reconocido" | "reset_ok"
Con 12 V conectados la mano funciona SOLO por Bluetooth (la PCB no admite USB y 12 V a la vez).

bleak es asíncrono: corre en su propio hilo con su bucle de asyncio, y aquí se le
piden las cosas de forma bloqueante (el Deletreador es un hilo normal).
"""
import asyncio
import threading
import time

from pgc.adaptadores.protocolo_mano import ORDEN_COMPROBAR, RESPUESTA_RESET, resultado

UART_RX = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"     # el PC escribe aquí
UART_TX = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"     # la placa notifica aquí
TAMANO_PAQUETE = 20                                  # sirve con cualquier MTU
TIEMPO_BUSQUEDA = 5.0
TIEMPO_CONEXION = 10.0


def _bleak_real():
    """bleak en un proceso aparte: WinRT y Whisper (ctranslate2) chocan en el mismo proceso."""
    from pgc.adaptadores.ble_puente import BleakRemoto
    return BleakRemoto()


def _motivo(ex):
    """Texto corto del error para el log (bleak lo da en inglés y a veces como tupla)."""
    if type(ex).__name__ == "BleakBluetoothNotAvailableError":
        return "el Bluetooth del PC está apagado: actívalo en Configuración > Bluetooth y dispositivos"
    texto = ex.args[0] if ex.args and isinstance(ex.args[0], str) else str(ex)
    if texto == "Not connected":
        return ("la mano cortó la conexión. Si la emparejaste en Windows, quítala de "
                "Configuración > Bluetooth y dispositivos > Dispositivos y reinicia la mano")
    return texto or type(ex).__name__


class ManoBLE:
    medio = "ble"

    def __init__(self, nombre="Mano-LSC", token="", timeout_letra=12.0, log=print, reintento=10.0,
                 tiempo_busqueda=TIEMPO_BUSQUEDA, reloj=time.monotonic, bleak=None):
        self.nombre = nombre
        self.token = token
        self.timeout_letra = timeout_letra
        self.tiempo_busqueda = tiempo_busqueda
        self.reintento = reintento
        self.log = log
        self._reloj = reloj
        self._bleak = bleak                   # None = el bleak instalado (se importa al conectar)
        self.letras = None
        self._cliente = None
        self._enlazada = False                # False en cuanto bleak avisa de la desconexión
        self._bucle = None
        self._hilo = None
        self._buffer = b""
        self._llegada = threading.Condition()
        self._proximo_intento = 0.0
        self._ultimo_aviso = None

    @property
    def conectada(self):
        return self._cliente is not None and self._enlazada

    @property
    def puerto(self):
        """Lo que muestra la pantalla: el nombre de la mano."""
        return self.nombre

    def puede_intentar(self):
        return self._reloj() >= self._proximo_intento

    def _avisar(self, texto):
        """Escribe en el log solo si cambió (la placa apagada no llena el log)."""
        if texto != self._ultimo_aviso:
            self._ultimo_aviso = texto
            self.log(texto)

    # ------------------------------------------------------- hilo de asyncio
    def _correr(self, corrutina, timeout):
        """Ejecuta una corrutina de bleak en su hilo y espera el resultado."""
        if self._bucle is None:
            self._bucle = asyncio.new_event_loop()
            self._hilo = threading.Thread(target=self._bucle.run_forever, daemon=True, name="mano-ble")
            self._hilo.start()
        return asyncio.run_coroutine_threadsafe(corrutina, self._bucle).result(timeout)

    def _al_notificar(self, _caracteristica, datos):
        with self._llegada:
            self._buffer += bytes(datos)
            self._llegada.notify_all()

    def _al_desconectar(self, _cliente):
        with self._llegada:
            self._enlazada = False
            self._llegada.notify_all()

    # --------------------------------------------------------------- conexión
    def conectar(self):
        self._proximo_intento = self._reloj() + self.reintento
        try:
            bleak = self._bleak or _bleak_real()
            dispositivo = self._correr(bleak.Escaner.find_device_by_name(self.nombre, timeout=self.tiempo_busqueda),
                                       self.tiempo_busqueda + 5)
            if dispositivo is None:
                raise RuntimeError("no se encontró (¿placa con 12 V? ¿Bluetooth del PC encendido?)")
            cliente = bleak.Cliente(dispositivo, disconnected_callback=self._al_desconectar)
            self._correr(cliente.connect(timeout=TIEMPO_CONEXION), TIEMPO_CONEXION + 5)
            self._cliente, self._enlazada, self._buffer = cliente, True, b""
            self._correr(cliente.start_notify(UART_TX, self._al_notificar), 10)
            resp = self._comando("auth " + self.token, lambda l: l in ("ok:auth", "error:auth"), 3.0)
            if resp != "ok:auth":
                raise RuntimeError("la mano rechazó el token (revisa TOKEN en config_ble.py)" if resp
                                   else "la mano no respondió al token")
            # Comprobación con "reset" (el firmware original no tiene "ping"); deja la mano abierta
            if not self._comando(ORDEN_COMPROBAR, lambda l: l == RESPUESTA_RESET, self.timeout_letra):
                raise RuntimeError("la mano no respondió a 'reset'")
            self.letras = None                    # el firmware no informa sus letras: se usan las por defecto
            self._ultimo_aviso = None
            self.log(f"[mano] Conectada por Bluetooth a {self.nombre}")
            return True
        except Exception as ex:
            self._avisar(f"[mano] Bluetooth: {self.nombre} no disponible ({_motivo(ex)})")
            self.cerrar()
            return False

    def cerrar(self):
        cliente, self._cliente = self._cliente, None
        self._enlazada = False
        if cliente is not None:
            try:
                self._correr(cliente.disconnect(), 5)
            except Exception:
                pass

    def _linea(self, limite):
        with self._llegada:
            while b"\n" not in self._buffer:
                if not self._enlazada:
                    raise ConnectionError("la mano se desconectó")
                if self._reloj() > limite:
                    return None
                self._llegada.wait(0.1)
            linea, self._buffer = self._buffer.split(b"\n", 1)
        return linea.decode("utf-8", "ignore").strip().lower()

    def _enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), TAMANO_PAQUETE):
            self._correr(self._cliente.write_gatt_char(UART_RX, datos[k:k + TAMANO_PAQUETE], response=True), 5)

    def _comando(self, cmd, condicion, timeout):
        self._enviar(cmd)
        limite = self._reloj() + timeout
        while True:
            linea = self._linea(limite)
            if linea is None:
                return None
            if condicion(linea):
                return linea
            if linea.startswith("error:"):
                self.log(f"[mano] {linea}")

    # ---------------------------------------------------------------- órdenes
    def hacer(self, letra):
        """Envía una letra (o 'reset') y espera su confirmación. True si la mano la hizo.

        Sin respuesta a tiempo se da la conexión por perdida (el firmware no tiene "ping"
        para comprobarla de otra forma); el respaldo y la reconexión siguen solos.
        """
        if not self.conectada:
            return False
        try:
            resp = self._comando(letra, lambda l: resultado(letra, l) is not None, self.timeout_letra)
            if resp is None:
                self.log(f"[mano] Sin confirmación para '{letra}' por Bluetooth (timeout): se da por perdida")
                self.cerrar()
                return False
            return resultado(letra, resp)
        except Exception as ex:
            self.log(f"[mano] Se perdió la conexión Bluetooth: {ex or type(ex).__name__}")
            self.cerrar()
            return False

    def latido(self):
        """Entre mensajes: revisa, SIN enviar nada, si la conexión sigue viva."""
        if self.conectada and getattr(self._cliente, "is_connected", True):
            return True
        if self._cliente is not None:
            self.log("[mano] Se perdió la conexión Bluetooth")
        self.cerrar()
        return False

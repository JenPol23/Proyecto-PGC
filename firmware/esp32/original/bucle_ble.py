# =============================================================================
# >>> INICIO DE LO AGREGADO: este bloque reemplaza el BUCLE PRINCIPAL original.
# Recibe las MISMAS órdenes por USB y, si existe config_ble.py, también por
# Bluetooth (BLE, servicio "UART" de Nordic, con token), y responde con los
# MISMOS textos del código original.
# Todo lo que está arriba de este bloque es el código original sin cambios.
# =============================================================================
import bluetooth
from micropython import const

try:
    import uselect as select
except ImportError:
    import select

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_READ | _FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE)


def _ble_aviso(texto):
    print("# " + texto)            # avisos del Bluetooth: se ven en Thonny, el PC los ignora


def atender_orden(cmd, responder):
    """Lo mismo que hacía el bucle original con cada orden. Devuelve False con 'salir'."""
    cmd = cmd.strip().lower()
    if not cmd:
        return True
    if cmd == "salir":
        return False
    elif cmd == "reset" or cmd == "1":
        reset_all()
        responder("reset_ok")
    elif cmd in acciones:
        reset_all()
        acciones[cmd]()
        responder("gesto_" + cmd + "_ok")
    elif len(cmd) > 1:
        if responder is print:
            deletrear(cmd)          # por USB: la función original tal cual
        else:
            # por Bluetooth: los mismos pasos y textos de deletrear(), enviados al PC
            for letra in cmd:
                if letra in acciones:
                    reset_all()
                    acciones[letra]()
                    responder("gesto_" + letra + "_ok")
                    responder("letra_actual:" + letra)
                    time.sleep(PAUSA_LETRA)
                else:
                    responder("letra_" + letra + "_no_disponible")
            responder("deletreo_completo")
            reset_all()
    else:
        responder("comando_no_reconocido")
    return True


class LectorUSB:
    """Lee órdenes por USB sin quedarse esperando (para poder atender también el Bluetooth)."""

    def __init__(self):
        self.poll = select.poll()
        self.poll.register(sys.stdin, select.POLLIN)
        self.buffer = ""

    def leer(self):
        while self.poll.poll(0):
            c = sys.stdin.read(1)
            if c in ("\n", "\r", ""):
                if self.buffer:
                    linea, self.buffer = self.buffer, ""
                    return linea
                if c == "":
                    return None
                continue
            if len(self.buffer) < 64:
                self.buffer += c
        return None


class ServidorBLE:
    """La mano como periférico BLE con el servicio UART de Nordic. Nunca bloquea el bucle.

    Un solo PC a la vez (al conectarse uno, la placa deja de anunciarse). La primera
    línea debe ser "auth <TOKEN>" en 3 s; si no, la placa lo desconecta.
    """

    def __init__(self, cfg):
        self.nombre = getattr(cfg, "NOMBRE", "Mano-LSC")
        self.token = cfg.TOKEN
        if not self.token or len(self.token) < 16:
            raise ValueError("TOKEN de config_ble.py muy corto (minimo 16 caracteres)")
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        try:
            self.ble.config(gap_name=self.nombre)
        except Exception:
            pass
        self.ble.irq(self._irq)
        ((self.h_tx, self.h_rx),) = self.ble.gatts_register_services(((_UART_UUID, (_UART_TX, _UART_RX)),))
        self.ble.gatts_set_buffer(self.h_rx, 256, True)
        self.conexion = None
        self.autenticado = False
        self.desde = time.ticks_ms()
        self.trozos = []            # lo que llega por Bluetooth (lo llena _irq)
        self.buffer = b""
        self.eventos = []           # avisos de conexión/desconexión para imprimirlos fuera de _irq
        nombre = self.nombre.encode()
        self.anuncio = b"\x02\x01\x06" + bytes((len(nombre) + 1, 0x09)) + nombre
        self.respuesta = bytes((17, 0x07)) + bytes(_UART_UUID)
        self._anunciar()
        _ble_aviso("Bluetooth listo: se anuncia como {}".format(self.nombre))

    def _anunciar(self):
        self.ble.gap_advertise(100000, adv_data=self.anuncio, resp_data=self.respuesta)

    def _irq(self, evento, datos):
        if evento == _IRQ_CENTRAL_CONNECT:
            self.conexion = datos[0]
            self.autenticado = False
            self.desde = time.ticks_ms()
            self.trozos = []
            self.buffer = b""
            self.eventos.append("PC conectado por Bluetooth")
        elif evento == _IRQ_CENTRAL_DISCONNECT:
            self.conexion = None
            self.autenticado = False
            self.eventos.append("PC desconectado; anunciando de nuevo")
            self._anunciar()
        elif evento == _IRQ_GATTS_WRITE:
            if datos[1] == self.h_rx:
                self.trozos.append(self.ble.gatts_read(self.h_rx))

    def _enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), 20):             # paquetes de 20 bytes: sirve con cualquier MTU
            try:
                self.ble.gatts_notify(self.conexion, self.h_tx, datos[k:k + 20])
            except Exception:
                return

    def _desconectar(self):
        try:
            self.ble.gap_disconnect(self.conexion)
        except Exception:
            pass

    def atender(self, atender_orden):
        """Una pasada: avisos, token y órdenes recibidas. Devuelve False con 'salir'."""
        while self.eventos:
            _ble_aviso(self.eventos.pop(0))
        if self.conexion is None:
            return True
        while self.trozos:
            self.buffer += self.trozos.pop(0)
        if len(self.buffer) > 256:
            self.buffer = b""
        lineas = []
        while b"\n" in self.buffer:
            linea, self.buffer = self.buffer.split(b"\n", 1)
            lineas.append(linea.decode("utf-8", "ignore").strip("\r"))
        if not self.autenticado:
            if lineas and lineas[0].strip() == "auth " + self.token:
                self.autenticado = True
                lineas = lineas[1:]
                self._enviar("ok:auth")
            elif lineas:
                self._enviar("error:auth")
                _ble_aviso("Conexion rechazada (token incorrecto)")
                self._desconectar()
                return True
            elif time.ticks_diff(time.ticks_ms(), self.desde) > 3000:
                self._desconectar()                    # no se presentó a tiempo
                return True
        for linea in lineas:
            if not atender_orden(linea, self._enviar):
                return False
        return True


usb = LectorUSB()
ble = None
try:
    import config_ble
    ble = ServidorBLE(config_ble)
except ImportError:
    pass                            # sin config_ble.py: solo USB, igual que el original
except Exception as error:
    _ble_aviso("Bluetooth desactivado: {}".format(error))

print("Listo. Esperando comandos...")
seguir = True
while seguir:
    try:
        linea = usb.leer()
        if linea is not None:
            seguir = atender_orden(linea, print)
        if seguir and ble is not None:
            seguir = ble.atender(atender_orden)
        time.sleep_ms(5)
    except KeyboardInterrupt:
        break

reset_all()
print("Programa terminado.")
# =============================================================================
# <<< FIN DE LO AGREGADO
# =============================================================================

# ============================================================
#  main.py  -  Firmware de Doby para la ESP32-S3 (MicroPython)
# ------------------------------------------------------------
#  Protocolo de PLAN_MANANA.md (una orden por linea, termina en \n):
#     PING                -> PONG
#     MIC                 -> 4096 bytes (1024 muestras int32 del microfono)
#     HABLAR <n> + n bytes PCM int16 -> reproduce y responde OK
#     RELE <k> <1|0>      -> OK o ERR   (k = 1..4)
#     TODOS 0             -> apaga todos, OK
#  Seguridad: el cautin y la plancha (CALIENTES) se apagan solos si no hay PC
#  durante SEG_GRACIA s, si el PC no manda nada en SEG_SIN_ORDENES s o si se
#  pierde el WiFi. El ventilador y el bombillo conservan su estado.
#  Necesita secretos.py en la placa (RED y CLAVE).
# ============================================================

import errno
import network
import socket
import time
from machine import Pin, I2S
from secretos import RED, CLAVE

PUERTO = 5000
TX_WIFI_DBM = 10  # potencia WiFi reducida: menos ruido en el microfono (el AP esta cerca)

# ---------------- 1. Reles: APAGADOS antes que nada ----------------
PINES_RELE = {1: 10, 2: 11, 3: 12, 4: 13}   # ventilador, cautin, bombillo, plancha
APAGADO = 1       # activo en bajo
ENCENDIDO = 0
CALIENTES = (2, 4)       # cautin y plancha (= config.CALIENTES del PC): se apagan solos sin PC
SEG_GRACIA = 15          # s sin PC antes de apagarlos (Doby reconecta en ~2 s: no los apaga)
SEG_SIN_ORDENES = 60     # s con el PC conectado pero sin ninguna orden = PC caido o colgado

reles = {}
for numero, gpio in PINES_RELE.items():
    reles[numero] = Pin(gpio, Pin.OUT, value=APAGADO)


def apagar_calientes(motivo):
    encendidos = [k for k in CALIENTES if reles[k].value() == ENCENDIDO]
    for k in CALIENTES:
        reles[k].value(APAGADO)
    if encendidos:
        print("SEGURIDAD: apagados los reles {} (cautin/plancha): {}".format(encendidos, motivo))


# ---------------- 2. WiFi (copiada de pruebas/esp32_prueba_parlante.py) ----------------
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)

    # Reinicia el WiFi para limpiar cualquier intento anterior
    wlan.active(False)
    time.sleep(0.5)
    wlan.active(True)
    try:
        wlan.config(pm=wlan.PM_NONE)   # sin ahorro de energia
    except Exception:
        pass
    try:
        wlan.config(txpower=TX_WIFI_DBM)
        print("Potencia WiFi fijada:", wlan.config("txpower"), "dBm")
    except Exception as e:
        print("No se pudo fijar la potencia WiFi:", e)

    intento = 0
    while not wlan.isconnected():
        intento += 1
        print("Conectando al WiFi (intento {})...".format(intento))
        try:
            wlan.connect(RED, CLAVE)
        except OSError as e:
            print("  error:", e)

        for _ in range(15):
            if wlan.isconnected():
                break
            time.sleep(1)

        if not wlan.isconnected():
            print("  No se pudo. El punto de acceso esta encendido y en 2.4 GHz?")
            try:
                wlan.disconnect()
            except Exception:
                pass
            time.sleep(3)

    print("WiFi conectado. IP de la ESP32:", wlan.ifconfig()[0])
    print("Potencia WiFi tras conectar:", wlan.config("txpower"), "dBm")
    return wlan


wlan = conectar_wifi()

# ---------------- 3. Audio ----------------
mic = I2S(1, sck=Pin(4), ws=Pin(5), sd=Pin(6), mode=I2S.RX,
          bits=32, format=I2S.MONO, rate=16000, ibuf=16000)

parlante = I2S(0, sck=Pin(15), ws=Pin(16), sd=Pin(7), mode=I2S.TX,
               bits=16, format=I2S.MONO, rate=16000, ibuf=20000)

buf_mic = bytearray(4096)
mv_mic = memoryview(buf_mic)

# Buffer para recibir cada frase COMPLETA antes de reproducirla.
# Asi el WiFi no puede interrumpir la voz. Se intenta el mas grande posible.
buf_frase = None
for tam in (256000, 128000, 64000, 16000):
    try:
        buf_frase = bytearray(tam)
        break
    except MemoryError:
        pass
mv_frase = memoryview(buf_frase)
print("Buffer de voz: {:.1f} s".format(len(buf_frase) / 32000))


def llenar_mic():
    """Llena exactamente 4096 bytes del microfono."""
    total = 0
    while total < 4096:
        n = mic.readinto(mv_mic[total:])
        if n:
            total += n
    return mv_mic


def recibir(cliente, mv, cantidad):
    """Recibe 'cantidad' bytes del PC en mv. Devuelve cuantos llegaron."""
    total = 0
    while total < cantidad:
        n = cliente.readinto(mv[total:cantidad])
        if not n:
            break
        total += n
    return total


def atender_hablar(cliente, n):
    restante = n
    capacidad = len(buf_frase)
    while restante > 0:
        tam = min(capacidad, restante)
        leidos = recibir(cliente, mv_frase, tam)   # 1. recibe toda la frase
        par = leidos - (leidos % 2)                 # siempre muestras completas
        if par:
            parlante.write(mv_frase[:par])           # 2. la reproduce sin depender del WiFi
        restante -= leidos
        if leidos < tam:
            raise OSError("el PC corto la conexion durante HABLAR")
    time.sleep_ms(630)                               # lo que dura el buffer ibuf=20000
    cliente.write(b"OK\n")


def atender_orden(cliente, partes):
    orden = partes[0].upper()

    if orden == "PING":
        cliente.write(b"PONG\n")

    elif orden == "MIC":
        cliente.write(llenar_mic())

    elif orden == "HABLAR" and len(partes) == 2:
        atender_hablar(cliente, int(partes[1]))

    elif orden == "RELE" and len(partes) == 3:
        k = int(partes[1])
        v = int(partes[2])
        if k in reles and v in (0, 1):
            reles[k].value(ENCENDIDO if v == 1 else APAGADO)
            cliente.write(b"OK\n")
        else:
            cliente.write(b"ERR\n")

    elif orden == "TODOS" and len(partes) == 2 and partes[1] == "0":
        for rele in reles.values():
            rele.value(APAGADO)
        cliente.write(b"OK\n")

    else:
        cliente.write(b"ERR\n")


# ---------------- 4. Servidor ----------------
ESPERA = 1.0      # segundos sin ordenes antes de revisar conexiones nuevas y WiFi
servidor = None
cliente = None
ultimo_chequeo = time.ticks_ms()
ultima_orden = time.ticks_ms()   # ultima linea recibida del PC
sin_pc_desde = None              # desde cuando no hay PC (None: hay PC, o ya se apagaron los calientes)


def crear_servidor():
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", PUERTO))
    s.listen(1)
    s.setblocking(False)          # accept() no se queda esperando
    return s


def cerrar_cliente():
    global cliente, sin_pc_desde
    if cliente is None:
        return
    try:
        cliente.close()
    except Exception:
        pass
    cliente = None
    sin_pc_desde = time.ticks_ms()
    print("PC desconectado. Si no vuelve en {} s se apagan el cautin y la plancha.".format(SEG_GRACIA))


def aceptar_pendiente():
    """Si hay un PC esperando, lo acepta y reemplaza al anterior (aunque este muerto)."""
    global cliente, sin_pc_desde, ultima_orden
    if servidor is None:
        return
    try:
        nuevo, direccion = servidor.accept()
    except OSError:
        return                    # no hay nadie esperando
    cerrar_cliente()
    nuevo.settimeout(ESPERA)
    cliente = nuevo
    sin_pc_desde = None           # volvio un PC a tiempo: no se apaga nada
    ultima_orden = time.ticks_ms()
    print("PC conectado:", direccion)


def revisar_seguridad():
    """PC mudo SEG_SIN_ORDENES s -> se da por perdido; sin PC SEG_GRACIA s -> apaga cautin y plancha."""
    global sin_pc_desde
    ahora = time.ticks_ms()
    if cliente is not None and time.ticks_diff(ahora, ultima_orden) > SEG_SIN_ORDENES * 1000:
        print("{} s sin ordenes del PC: lo doy por perdido.".format(SEG_SIN_ORDENES))
        cerrar_cliente()
    if sin_pc_desde is not None and time.ticks_diff(ahora, sin_pc_desde) > SEG_GRACIA * 1000:
        apagar_calientes("{} s sin PC".format(SEG_GRACIA))
        sin_pc_desde = None


def revisar_wifi():
    """Cada 5 s: si se perdio el WiFi, reconecta y rehace el servidor."""
    global wlan, servidor, ultimo_chequeo
    if time.ticks_diff(time.ticks_ms(), ultimo_chequeo) < 5000:
        return
    ultimo_chequeo = time.ticks_ms()

    if not wlan.isconnected():
        print("Se perdio el WiFi. Reconectando...")
        apagar_calientes("se perdio el WiFi")    # conectar_wifi() puede tardar: no se espera la gracia
        cerrar_cliente()
        if servidor is not None:
            try:
                servidor.close()
            except Exception:
                pass
            servidor = None
        wlan = conectar_wifi()

    if servidor is None:
        servidor = crear_servidor()
        print("Doby listo en {}:{}".format(wlan.ifconfig()[0], PUERTO))


def es_espera(error):
    return error.args and error.args[0] in (errno.ETIMEDOUT, errno.EAGAIN)


servidor = crear_servidor()
print("Doby listo en {}:{}".format(wlan.ifconfig()[0], PUERTO))

while True:
    try:
        if cliente is None:
            aceptar_pendiente()
            time.sleep_ms(50)
        else:
            try:
                linea = cliente.readline()      # lectura directa: responde rapido
            except OSError as e:
                if not es_espera(e):
                    raise
                linea = None

            if linea is None:
                aceptar_pendiente()             # 1 s sin ordenes: hay un PC nuevo?
            elif not linea:
                cerrar_cliente()                # el PC cerro la conexion
            else:
                ultima_orden = time.ticks_ms()  # el PC sigue vivo
                partes = linea.decode().strip().split()
                if partes:
                    try:
                        atender_orden(cliente, partes)
                    except ValueError:
                        cliente.write(b"ERR\n")        # numeros mal escritos

        revisar_seguridad()
        revisar_wifi()

    except OSError as e:
        print("Error con el PC:", e)
        cerrar_cliente()
    except Exception as e:
        print("Error inesperado:", e)
        time.sleep_ms(500)

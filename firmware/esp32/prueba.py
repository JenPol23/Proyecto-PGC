# prueba.py  —  Baja y sube cada dedo, UNO POR UNO; al final cierra TODA la mano y la abre
# -----------------------------------------------------------------------------
# Programa aparte, sin PC ni Bluetooth: sirve para revisar cada servo.
#
# Cómo usarlo (en tu PCB no se pueden conectar USB y 12 V a la vez):
#   1. Sin 12 V y con USB, en Thonny: sube este archivo a la placa.
#   2. Para que corra solo al conectar los 12 V, la placa tiene que llamarlo
#      main.py: en la placa renombra main.py -> main_mano.py y prueba.py -> main.py.
#   3. Desconecta el USB y conecta los 12 V: la placa arranca sola y hace la prueba.
#   4. Para volver a la mano: quita los 12 V, conecta el USB, borra el main.py
#      (esta prueba) y renombra main_mano.py -> main.py.
#
# Qué hace:
#   1. Todos los dedos arriba (abiertos): primero el dedo gordo (pulgar2 y
#      pulgar) y después los demás, para que ningún dedo se trabe.
#   2. Uno por uno, en este orden: indice, medio, anular, menique: baja y sube.
#   3. Dedo gordo: "pulgar" gira, "pulgar2" se recoge; después se reinician los
#      dos al revés (pulgar2 se estira y pulgar vuelve), como en la letra l().
#   4. Cierra toda la mano empezando por el dedo gordo (pulgar gira, pulgar2 se
#      recoge) y luego los 4 dedos.
#   5. Espera PAUSA_PUNO y abre toda la mano al revés: primero los 4 dedos y el
#      dedo gordo DE ÚLTIMAS (pulgar2 se estira, pulgar vuelve). Termina ABIERTA.
#
# dedos_config es el mismo del código original (las pruebas del PC lo comparan).
# -----------------------------------------------------------------------------
from machine import Pin, PWM
import time

PAUSA = 1.0              # segundos que el dedo queda abajo y luego arriba
PAUSA_ENTRE_DEDOS = 0.5  # segundos antes de pasar al siguiente dedo
PAUSA_CIERRE = 0.4       # segundos entre dedo y dedo al cerrar/abrir toda la mano (= PAUSA_DEDO del original)
PAUSA_PUNO = 2.0         # segundos que la mano queda cerrada antes de abrirse

dedos_config = {
    "indice":   {"pin": 8,  "abierto": 500,  "cerrado": 2000, "mitad": 1000},
    "menique":  {"pin": 3,  "abierto": 500,  "cerrado": 2000, "mitad": 1200},
    "medio":    {"pin": 10, "abierto": 500,  "cerrado": 2000, "mitad": 1000},
    "anular":   {"pin": 4,  "abierto": 2200, "cerrado": 500,  "mitad": 1700},
    "pulgar":   {"pin": 6,  "abierto": 1500, "cerrado": 500,  "mitad": 1000},  # antes abierto era 10: calibrar
    "pulgar2":  {"pin": 7,  "abierto": 500,  "cerrado": 2500, "mitad": 1600},
}

ORDEN_DEDOS = ["indice", "medio", "anular", "menique"]   # los cuatro dedos, en este orden
ABRIR = ["pulgar2", "pulgar"] + ORDEN_DEDOS               # primero el dedo gordo: así ningún dedo se traba

print("Prueba: todos los dedos arriba (dedo gordo de primeras)...")
for nombre in ABRIR:
    cfg = dedos_config[nombre]
    s = PWM(Pin(cfg["pin"]), freq=50)
    s.duty_ns(int(cfg["abierto"] * 1000))
    cfg["servo"] = s
    time.sleep(0.5)


def poner(nombre, posicion, pausa):
    cfg = dedos_config[nombre]
    us = cfg[posicion]
    print("  {} (GPIO {}): {} = {} us".format(nombre, cfg["pin"], posicion, us))
    cfg["servo"].duty_ns(int(us * 1000))
    time.sleep(pausa)


# 1) Los cuatro dedos, uno por uno: bajar y subir
for nombre in ORDEN_DEDOS:
    print("Dedo:", nombre)
    poner(nombre, "cerrado", PAUSA)
    poner(nombre, "abierto", PAUSA)
    time.sleep(PAUSA_ENTRE_DEDOS)

# 2) Dedo gordo: gira, se recoge, y luego se reinician los dos (al revés)
print("Dedo gordo: gira y se recoge")
poner("pulgar", "cerrado", PAUSA)       # gira
poner("pulgar2", "cerrado", PAUSA)      # se recoge
print("Dedo gordo: se reinicia")
poner("pulgar2", "abierto", PAUSA)      # se estira
poner("pulgar", "abierto", PAUSA)       # vuelve el giro
time.sleep(PAUSA_ENTRE_DEDOS)

# 3) Toda la mano: primero el dedo gordo (gira y se recoge) y luego los cuatro dedos
print("Cerrando toda la mano (dedo gordo de primeras)...")
for nombre in ["pulgar", "pulgar2"] + ORDEN_DEDOS:
    poner(nombre, "cerrado", PAUSA_CIERRE)
time.sleep(PAUSA_PUNO)

# 4) Abrir toda la mano al revés: primero los cuatro dedos y el dedo gordo de últimas
print("Abriendo toda la mano (dedo gordo de ultimas)...")
for nombre in ORDEN_DEDOS + ["pulgar2", "pulgar"]:
    poner(nombre, "abierto", PAUSA_CIERRE)

print("Prueba terminada: mano abierta.")

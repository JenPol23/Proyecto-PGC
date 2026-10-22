# prueba_dedos.py  —  Prueba cada dedo POR SEPARADO, solo, sin PC
# -----------------------------------------------------------------------------
# Para revisar el cableado y la calibración de cada servo.
#
# Cómo usarlo (en tu PCB no se pueden conectar USB y 12 V a la vez):
#   1. Sin 12 V y con USB: en Thonny sube ESTE archivo a la placa con el nombre
#      main.py (reemplaza temporalmente al main.py de la mano).
#   2. Desconecta el USB y conecta los 12 V: la placa arranca sola y mueve los
#      dedos uno por uno, REPETICIONES veces, y termina con la mano abierta.
#   3. Al terminar: quita los 12 V, conecta el USB y vuelve a subir el main.py
#      de la mano (ProyectoPGC\firmware\esp32\main.py).
#
# Orden de cada dedo: abierto -> cerrado -> mitad -> abierto, con PAUSA s entre
# posiciones. Antes de cada dedo, el dedo anterior queda abierto.
# dedos_config es el mismo del código original (las pruebas del PC lo comparan).
# -----------------------------------------------------------------------------
from machine import Pin, PWM
import time

REPETICIONES = 3     # vueltas completas por los 6 dedos
PAUSA = 1.0          # segundos en cada posición
PAUSA_ENTRE_DEDOS = 1.5

dedos_config = {
    "indice":   {"pin": 8,  "abierto": 500,  "cerrado": 2000, "mitad": 1000},
    "menique":  {"pin": 3,  "abierto": 500,  "cerrado": 2000, "mitad": 1200},
    "medio":    {"pin": 10, "abierto": 500,  "cerrado": 2000, "mitad": 1000},
    "anular":   {"pin": 4,  "abierto": 2200, "cerrado": 500,  "mitad": 1700},
    "pulgar":   {"pin": 6,  "abierto": 1500, "cerrado": 500,  "mitad": 1000},  # antes abierto era 10: calibrar
    "pulgar2":  {"pin": 7,  "abierto": 500,  "cerrado": 2500, "mitad": 1600},
}

print("Prueba de dedos: iniciando motores (todos abiertos)...")
for nombre, cfg in dedos_config.items():
    s = PWM(Pin(cfg["pin"]), freq=50)
    s.duty_ns(int(cfg["abierto"] * 1000))
    cfg["servo"] = s
    time.sleep(0.5)


def poner(nombre, posicion):
    cfg = dedos_config[nombre]
    us = cfg[posicion]
    print("  {} (GPIO {}): {} = {} us".format(nombre, cfg["pin"], posicion, us))
    cfg["servo"].duty_ns(int(us * 1000))
    time.sleep(PAUSA)


for vuelta in range(REPETICIONES):
    print("Vuelta {} de {}".format(vuelta + 1, REPETICIONES))
    for nombre in dedos_config:
        print("Dedo:", nombre)
        for posicion in ("cerrado", "mitad", "abierto"):
            poner(nombre, posicion)
        time.sleep(PAUSA_ENTRE_DEDOS)

print("Prueba de dedos terminada: mano abierta.")

from machine import Pin, PWM
import time
import sys

# ---------------- CONFIGURACION ----------------
PAUSA_DEDO = 0.4     # segundos que espera cada dedo antes de mover el siguiente
PAUSA_LETRA = 1.0    # pausa entre letras al deletrear
US_MIN = 500         # pulso minimo permitido (microsegundos)
US_MAX = 2500        # pulso maximo permitido (microsegundos)

dedos_config = {
    "indice":   {"pin": 8,  "abierto": 500,  "cerrado": 2000, "mitad": 1000},
    "menique":  {"pin": 3,  "abierto": 500,  "cerrado": 2000, "mitad": 1200},
    "medio":    {"pin": 10, "abierto": 500,  "cerrado": 2000, "mitad": 1000},
    "anular":   {"pin": 4,  "abierto": 2200, "cerrado": 500,  "mitad": 1700},
    "pulgar":   {"pin": 6,  "abierto": 1500, "cerrado": 500,  "mitad": 1000},  # antes abierto era 10: calibrar
    "pulgar2":  {"pin": 7,  "abierto": 500,  "cerrado": 2500, "mitad": 1600},
}

# ---------------- INICIO DE SERVOS ----------------
print("Iniciando motores...")
for dedo, cfg in dedos_config.items():
    s = PWM(Pin(cfg["pin"]), freq=50)
    s.duty_ns(int(cfg["abierto"] * 1000))
    cfg["servo"] = s
    cfg["pos"] = cfg["abierto"]
    time.sleep(0.5)
print("Mano lista.")

# ---------------- MOVIMIENTO BASICO ----------------
def mover_a(nombre, us):
    cfg = dedos_config.get(nombre)
    if not cfg:
        return
    us = int(us)
    if us < US_MIN:
        us = US_MIN
    if us > US_MAX:
        us = US_MAX
    if cfg["pos"] == us:
        return                      # ya esta en esa posicion, no espera
    cfg["servo"].duty_ns(us * 1000)
    cfg["pos"] = us
    time.sleep(PAUSA_DEDO)          # espera a que este dedo termine

def mover_dedo(nombre, estado):
    cfg = dedos_config.get(nombre)
    if not cfg:
        return
    mover_a(nombre, cfg["cerrado"] if estado == 1 else cfg["abierto"])

def mover_mitad(nombre):
    cfg = dedos_config.get(nombre)
    if not cfg:
        return
    mover_a(nombre, cfg["mitad"])

def mover_cuarto(nombre):
    cfg = dedos_config.get(nombre)
    if not cfg:
        return
    mover_a(nombre, (cfg["abierto"] + cfg["mitad"]) / 2)

def mover_cuarto_mas(nombre):
    cfg = dedos_config.get(nombre)
    if not cfg:
        return
    cuarto = (cfg["abierto"] + cfg["mitad"]) / 2
    mover_a(nombre, (cuarto + cfg["mitad"]) / 2)

def reset_all():
    for nombre in dedos_config:
        mover_dedo(nombre, 0)

# ---------------- LETRAS ----------------
def a():
    for d in ["indice", "medio", "anular", "menique", "pulgar", "pulgar2"]:
        mover_dedo(d, 1)

def b():
    for d in ["indice", "medio", "anular", "menique"]:
        mover_dedo(d, 0)
    mover_dedo("pulgar", 1)
    mover_dedo("pulgar2", 1)

def c():
    mover_dedo("pulgar2", 0)
    for d in ["medio", "anular", "menique", "pulgar", "indice"]:
        mover_mitad(d)

def d():
    mover_dedo("indice", 0)
    for n_ in ["medio", "anular", "menique", "pulgar", "pulgar2"]:
        mover_mitad(n_)

def e():
    for d in ["indice", "medio", "anular", "menique"]:
        mover_dedo(d, 1)
    mover_dedo("pulgar", 0)
    mover_dedo("pulgar2", 0)

def f():
    mover_dedo("indice", 0)
    for d in ["medio", "anular", "menique", "pulgar", "pulgar2"]:
        mover_dedo(d, 1)

def i():
    for d in ["indice", "medio", "anular", "pulgar", "pulgar2"]:
        mover_dedo(d, 1)
    mover_dedo("menique", 0)

def k():
    mover_dedo("indice", 0)
    mover_cuarto_mas("medio")
    mover_mitad("pulgar")
    mover_mitad("pulgar2")
    mover_dedo("anular", 1)
    mover_dedo("menique", 1)

def l():
    mover_dedo("pulgar2", 0)
    mover_dedo("pulgar", 0)
    mover_dedo("indice", 0)
    for d in ["medio", "anular", "menique"]:
        mover_dedo(d, 1)

def m():
    mover_mitad("medio")
    mover_mitad("indice")
    mover_mitad("anular")
    mover_dedo("menique", 1)
    mover_dedo("pulgar", 1)
    mover_dedo("pulgar2", 1)

def n():
    mover_mitad("indice")
    mover_mitad("medio")
    mover_dedo("anular", 1)
    mover_dedo("menique", 1)
    mover_dedo("pulgar", 1)
    mover_dedo("pulgar2", 1)

def o():
    for d in ["indice", "medio", "anular", "menique", "pulgar2"]:
        mover_mitad(d)
    mover_dedo("pulgar", 0)

def p():
    mover_cuarto_mas("indice")
    mover_mitad("medio")
    mover_dedo("anular", 1)
    mover_dedo("menique", 1)
    mover_dedo("pulgar", 1)
    mover_dedo("pulgar2", 1)

def q():
    for d in ["indice", "medio", "anular", "menique"]:
        mover_dedo(d, 0)
    mover_mitad("pulgar")
    mover_dedo("pulgar2", 1)

def r():
    mover_cuarto("indice")
    mover_dedo("medio", 0)
    for d in ["anular", "menique", "pulgar", "pulgar2"]:
        mover_dedo(d, 1)

def t():
    for d in ["medio", "anular", "menique", "pulgar", "pulgar2"]:
        mover_dedo(d, 0)
    mover_mitad("indice")

def u():
    mover_dedo("indice", 0)
    mover_dedo("menique", 0)
    for d in ["medio", "anular", "pulgar", "pulgar2"]:
        mover_dedo(d, 1)

def v():
    mover_dedo("indice", 0)
    mover_dedo("medio", 0)
    for d in ["anular", "menique", "pulgar", "pulgar2"]:
        mover_dedo(d, 1)

def w():
    for d in ["indice", "medio", "anular"]:
        mover_dedo(d, 0)
    for d in ["menique", "pulgar", "pulgar2"]:
        mover_dedo(d, 1)

def x():
    mover_cuarto("indice")
    for d in ["medio", "anular", "menique", "pulgar", "pulgar2"]:
        mover_dedo(d, 1)

def y():
    mover_dedo("pulgar", 0)
    mover_dedo("pulgar2", 0)
    mover_dedo("menique", 0)
    for d in ["indice", "medio", "anular"]:
        mover_dedo(d, 1)

acciones = {
    "a": a, "b": b, "c": c, "d": d, "e": e,
    "f": f, "i": i, "k": k, "l": l, "m": m,
    "n": n, "o": o, "p": p, "q": q, "r": r,
    "t": t, "u": u, "v": v, "w": w, "x": x,
    "y": y,
}

# ---------------- DELETREO ----------------
def deletrear(palabra):
    for letra in palabra.lower():
        if letra in acciones:
            reset_all()
            acciones[letra]()
            print("gesto_" + letra + "_ok")
            print("letra_actual:" + letra)
            time.sleep(PAUSA_LETRA)
        else:
            print("letra_" + letra + "_no_disponible")
    print("deletreo_completo")
    reset_all()

# ---------------- BUCLE PRINCIPAL ----------------
print("Listo. Esperando comandos...")
while True:
    try:
        cmd = sys.stdin.readline().strip().lower()
        if not cmd:
            continue
        if cmd == "salir":
            break
        elif cmd == "reset" or cmd == "1":
            reset_all()
            print("reset_ok")
        elif cmd in acciones:
            reset_all()
            acciones[cmd]()
            print("gesto_" + cmd + "_ok")
        elif len(cmd) > 1:
            deletrear(cmd)
        else:
            print("comando_no_reconocido")
    except KeyboardInterrupt:
        break

reset_all()
print("Programa terminado.")

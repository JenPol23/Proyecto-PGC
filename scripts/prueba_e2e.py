"""Prueba de punta a punta en modo simulado (sin mano, sin Whisper, sin túnel).

Arranca el servidor como un proceso aparte, igual que iniciar.bat, y comprueba
páginas, envío de un mensaje, su seguimiento por WebSocket y las rutas de
administración. Sale con código 0 si todo pasa.

Uso:
    py -3.11 scripts/prueba_e2e.py                    # arranca con servidor.py
    py -3.11 scripts/prueba_e2e.py --entrada modulo   # arranca con  python -m pgc

La mano por Bluetooth (con el main.py real de la placa) se prueba de punta a punta en
tests/test_mano_ble.py::test_de_punta_a_punta_por_bluetooth.
"""
import argparse
import asyncio
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import websockets

RAIZ = Path(__file__).resolve().parent.parent
PUERTO = 8765
BASE = f"http://127.0.0.1:{PUERTO}"
fallos = []


def comprobar(condicion, descripcion):
    print(("  OK    " if condicion else "  FALLA ") + descripcion, flush=True)
    if not condicion:
        fallos.append(descripcion)


def http(metodo, ruta, datos=None, encabezados=None):
    req = urllib.request.Request(BASE + ruta, method=metodo,
                                 data=json.dumps(datos).encode() if datos is not None else None,
                                 headers={"Content-Type": "application/json", **(encabezados or {})})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as ex:
        return ex.code, ex.headers, ex.read()


def esperar_servidor(proceso, segundos=30):
    limite = time.time() + segundos
    while time.time() < limite:
        if proceso.poll() is not None:
            return False
        try:
            if http("GET", "/api/estado")[0] == 200:
                return True
        except OSError:
            pass
        time.sleep(0.3)
    return False


async def seguir_mensaje(texto):
    """Envía `texto` y devuelve las letras que la pantalla vio en orden y el estado final."""
    async with websockets.connect(f"ws://127.0.0.1:{PUERTO}/ws", max_size=2**20) as ws:
        inicial = json.loads(await ws.recv())
        comprobar(inicial.get("tipo") == "estado", "WebSocket: estado inicial")
        codigo, _, cuerpo = http("POST", "/api/mensaje", {"texto": texto, "cliente": "e2e"})
        comprobar(codigo == 200, f"POST /api/mensaje «{texto}» → {codigo}")
        id_msg = json.loads(cuerpo)["id"]
        vistas, ultimo = [], None
        limite = time.time() + 60
        while time.time() < limite:
            d = json.loads(await asyncio.wait_for(ws.recv(), timeout=25))
            if d.get("tipo") != "estado":
                continue
            a = d["actual"]
            if a and a["id"] == id_msg and 0 <= a["i"] < len(a["pasos"]) and (a["id"], a["i"]) != ultimo:
                ultimo = (a["id"], a["i"])
                vistas.append(a["pasos"][a["i"]]["c"])
            if any(h["id"] == id_msg for h in d["historial"]):
                return vistas, d
        return vistas, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", choices=["servidor", "modulo"], default="servidor")
    args = ap.parse_args()
    entorno = dict(os.environ)
    opciones = ["--simular", "--sin-voz", "--sin-tunel", "--no-abrir", "--puerto-web", str(PUERTO)]
    comando = [sys.executable, "servidor.py", *opciones] if args.entrada == "servidor" else [sys.executable, "-m", "pgc", *opciones]
    print("Arrancando:", " ".join(comando[1:]))
    with tempfile.TemporaryFile() as salida:
        proceso = subprocess.Popen(comando, cwd=RAIZ, stdout=salida, stderr=subprocess.STDOUT, env=entorno)
        try:
            listo = esperar_servidor(proceso)
            comprobar(listo, "el servidor arranca y responde /api/estado")
            if not listo:
                salida.seek(0)
                print(salida.read().decode(errors="replace"))
                return 1
            for ruta, texto in (("/", b"Mano bidireccional LSC"), ("/pantalla", b"Mano bidireccional LSC")):
                codigo, enc, cuerpo = http("GET", ruta)
                comprobar(codigo == 200 and texto in cuerpo and enc["Cache-Control"] == "no-store", f"GET {ruta}")
            for ruta in ("/qr.png", "/logo-udec.png"):
                codigo, _, cuerpo = http("GET", ruta)
                comprobar(codigo == 200 and cuerpo[:4] == b"\x89PNG", f"GET {ruta} es un PNG")
            estado = json.loads(http("GET", "/api/estado")[2])
            comprobar(estado["mano"]["modo"] == "simulada", "la mano está en modo simulado")

            codigo, _, cuerpo = http("POST", "/api/mensaje", {"texto": "gh", "cliente": "e2e"})
            comprobar(codigo == 400 and json.loads(cuerpo)["detail"] == "La mano todavía no puede hacer esas letras",
                      "«gh» se rechaza con su mensaje")

            vistas, final = asyncio.run(seguir_mensaje("calle"))
            comprobar("".join(vistas) == "CALLE", f"la pantalla vio las letras en orden: {''.join(vistas)}")
            comprobar(final is not None and final["actual"] is None and final["historial"][0]["texto"] == "calle",
                      "el mensaje terminó y pasó al historial")

            # El token de administrador solo viene en /pantalla abierta desde el PC
            html = http("GET", "/pantalla")[2].decode()
            m = re.search(r'<meta name="pgc-admin" content="([^"]+)">', html)
            comprobar(bool(m), "/pantalla en el PC trae el token de administrador")
            token = m.group(1) if m else ""
            por_tunel = http("GET", "/pantalla", encabezados={"cf-connecting-ip": "203.0.113.7"})[2].decode()
            comprobar('content="">' in por_tunel, "/pantalla por el túnel no trae el token")
            for ruta in ("/api/mano/saltar", "/api/mano/reconectar"):
                codigo = http("POST", ruta, encabezados={"cf-connecting-ip": "203.0.113.7", "X-PGC-Admin": token})[0]
                comprobar(codigo == 403, f"POST {ruta} por el túnel (aun con token) → 403")
            comprobar(http("POST", "/api/mano/saltar")[0] == 403, "saltar desde el PC sin token → 403")
            comprobar(http("POST", "/api/mano/saltar", encabezados={"X-PGC-Admin": token})[0] == 404,
                      "saltar desde el PC con token y sin mensaje → 404")
            codigo, _, cuerpo = http("POST", "/api/mensaje", {"texto": "gonorrea", "cliente": "e2e"})
            comprobar(codigo == 400 and "no se puede mostrar" in json.loads(cuerpo)["detail"],
                      "el filtro de palabras rechaza un insulto")
            codigo, enc, _ = http("GET", "/")
            comprobar("nonce-" in enc.get("Content-Security-Policy", "") and enc.get("X-Frame-Options") == "DENY",
                      "encabezados de seguridad y CSP con nonce")
            comprobar(http("GET", "/openapi.json")[0] == 404, "/openapi.json cerrado en modo normal")
        finally:
            proceso.terminate()
            try:
                proceso.wait(10)
            except subprocess.TimeoutExpired:
                proceso.kill()
            print("\nRESULTADO:", "TODO PASA" if not fallos else f"{len(fallos)} FALLA(N)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

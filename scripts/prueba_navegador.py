"""Prueba en un navegador real (Microsoft Edge sin ventana, controlado por CDP).

Arranca el servidor en modo simulado CON túnel y comprueba, en el PC y por el
túnel HTTPS: que la CSP no bloquea nada, que el WebSocket conecta, que el
celular envía mensajes y que el botón «Saltar mensaje» funciona con el token.

Uso:  py -3.11 scripts/prueba_navegador.py [--capturas carpeta] [--tema dark|light]
"""
import argparse
import asyncio
import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import websockets

RAIZ = Path(__file__).resolve().parent.parent
PUERTO = 8767
LOCAL = f"http://127.0.0.1:{PUERTO}"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
PUERTO_CDP = 9334
# Se instala antes que cualquier script de la página: registra violaciones de CSP
ESPIA_CSP = ("window.__csp = []; document.addEventListener('securitypolicyviolation', "
             "e => window.__csp.push(e.violatedDirective + ' ' + e.blockedURI));")
fallos = []


def comprobar(condicion, descripcion):
    print(("  OK    " if condicion else "  FALLA ") + descripcion, flush=True)
    if not condicion:
        fallos.append(descripcion)


def estado():
    with urllib.request.urlopen(LOCAL + "/api/estado", timeout=5) as r:
        return json.loads(r.read())


class Pestana:
    def __init__(self, ws):
        self.ws, self.n, self.pendientes = ws, 0, {}

    tema = "dark"

    @classmethod
    async def abrir(cls, movil=False):
        req = urllib.request.Request(f"http://127.0.0.1:{PUERTO_CDP}/json/new?about:blank", method="PUT")
        info = json.loads(urllib.request.urlopen(req).read())
        p = cls(await websockets.connect(info["webSocketDebuggerUrl"], max_size=None))
        asyncio.create_task(p._leer())
        await p.cmd("Page.enable")
        await p.cmd("Page.addScriptToEvaluateOnNewDocument", source=ESPIA_CSP)
        await p.cmd("Emulation.setDeviceMetricsOverride", width=390 if movil else 1920, height=844 if movil else 1080,
                    deviceScaleFactor=2 if movil else 1, mobile=movil)
        await p.cmd("Emulation.setEmulatedMedia", features=[{"name": "prefers-color-scheme", "value": cls.tema}])
        return p

    async def _leer(self):
        async for m in self.ws:
            d = json.loads(m)
            if d.get("id") in self.pendientes:
                self.pendientes.pop(d["id"]).set_result(d)

    async def cmd(self, metodo, **params):
        self.n += 1
        f = asyncio.get_running_loop().create_future()
        self.pendientes[self.n] = f
        await self.ws.send(json.dumps({"id": self.n, "method": metodo, "params": params}))
        r = await asyncio.wait_for(f, 30)
        if "error" in r:
            raise RuntimeError(f"{metodo}: {r['error']}")
        return r.get("result", {})

    async def js(self, expr):
        r = await self.cmd("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        return r.get("result", {}).get("value")

    async def ir(self, url, espera=3.0):
        await self.cmd("Page.bringToFront")
        await self.cmd("Page.navigate", url=url)
        await asyncio.sleep(espera)

    async def esperar(self, expr, segundos=15):
        limite = time.time() + segundos
        while time.time() < limite:
            if await self.js(expr):
                return True
            await asyncio.sleep(0.3)
        return False

    async def foto(self, ruta):
        await self.cmd("Page.bringToFront")
        await asyncio.sleep(0.6)
        r = await self.cmd("Page.captureScreenshot", format="png")
        Path(ruta).write_bytes(base64.b64decode(r["data"]))


async def probar(url_tunel, capturas):
    pc = await Pestana.abrir()
    celular = await Pestana.abrir(movil=True)

    print("\n[PC] /pantalla")
    await pc.ir(LOCAL + "/pantalla")
    comprobar(await pc.js("window.__csp.length") == 0, f"sin violaciones de CSP {await pc.js('window.__csp')}")
    comprobar(await pc.js("document.querySelector('#alfabeto').children.length") == 21, "el JavaScript corre (alfabeto)")
    comprobar(await pc.esperar("!document.querySelector('#desconectado').classList.contains('si')"),
              "WebSocket conectado (sin franja de desconexión)")
    comprobar(await pc.js("document.querySelector('.controles').style.display !== 'none'"), "controles visibles en el PC")
    comprobar(await pc.esperar("document.querySelector('#qr').naturalWidth > 0"), "el QR carga")

    print("\n[Celular por el túnel] /")
    await celular.ir(url_tunel + "/", espera=6)
    comprobar(await celular.js("location.protocol") == "https:", "la página llega por HTTPS")
    comprobar(await celular.js("window.__csp.length") == 0, f"sin violaciones de CSP {await celular.js('window.__csp')}")
    comprobar(await celular.esperar("document.querySelector('#chipConexion .txt').textContent === 'Mano simulada'", 20),
              "WebSocket seguro conectado por el túnel (pasa la revisión de Origin)")
    comprobar(await celular.js("window.isSecureContext") is True, "contexto seguro: el micrófono está disponible")
    comprobar(await celular.js("!document.querySelector('#veloNombre').classList.contains('oculto')"),
              "la primera vez pregunta «¿Cómo te llamas?»")
    if capturas:
        await celular.foto(Path(capturas) / f"navegador_movil_nombre_{Pestana.tema}.png")
    await celular.js("document.querySelector('#nombre').value = 'gonorrea';"
                     "document.querySelector('#hojaNombre').requestSubmit()")
    comprobar(await celular.esperar("document.querySelector('#avisoNombre').textContent.includes('no se puede mostrar')"),
              "un nombre ofensivo se rechaza con un mensaje amable")
    await celular.js("document.querySelector('#nombre').value = 'Ana';"
                     "document.querySelector('#hojaNombre').requestSubmit()")
    comprobar(await celular.esperar("document.querySelector('#veloNombre').classList.contains('oculto')"),
              "con un nombre válido la hoja se cierra")
    comprobar(await celular.js("document.querySelector('#quienTexto').textContent") == "Participas como Ana",
              "el encabezado muestra «Participas como Ana»")
    await celular.js("(() => { const t = document.querySelector('#texto'); t.value = 'abcdefiklmnop';"
                     " t.dispatchEvent(new Event('input')); })()")
    comprobar(await celular.esperar("document.querySelectorAll('#previa .l').length === 13"), "vista previa de letras")
    await celular.js("document.querySelector('#enviar').click()")
    comprobar(await celular.esperar("!document.querySelector('#misMensajes').classList.contains('oculto')"),
              "el mensaje aparece en «Tus mensajes»")
    if capturas:
        await asyncio.sleep(1.5)
        await celular.foto(Path(capturas) / f"navegador_movil_tunel_{Pestana.tema}.png")

    print("\n[PC] «Mensaje de» y botón «Saltar mensaje»")
    comprobar(await pc.esperar("document.querySelector('#rotulo').textContent === 'Mensaje de: Ana'", 10),
              "el proyector muestra «Mensaje de: Ana»")
    comprobar(await pc.esperar("!document.querySelector('#btnSaltar').disabled", 10), "el botón se activa con un mensaje en curso")
    if capturas:
        await pc.foto(Path(capturas) / f"navegador_pantalla_{Pestana.tema}.png")
    await pc.js("document.querySelector('#btnSaltar').click()")
    limite = time.time() + 15
    while time.time() < limite and not (estado()["historial"] and estado()["historial"][0]["saltado"]):
        await asyncio.sleep(0.3)
    comprobar(estado()["historial"][0]["saltado"] is True, "el mensaje quedó saltado (token aceptado)")

    print("\n[PC] bloquear a un participante")
    await celular.js("(() => { const t = document.querySelector('#texto'); t.value = 'abcdef';"
                     " t.dispatchEvent(new Event('input')); })()")
    await celular.esperar("!document.querySelector('#enviar').disabled")
    await celular.js("document.querySelector('#enviar').click()")
    comprobar(await pc.esperar("document.querySelector('#btnBloquear').textContent === 'Bloquear a Ana'"
                               " && !document.querySelector('#btnBloquear').disabled", 15),
              "el botón dice «Bloquear a Ana»")
    await pc.js("document.querySelector('#btnBloquear').click()")
    comprobar(await pc.esperar("document.querySelector('#avisoAdmin').textContent.startsWith('Bloqueaste a Ana')"),
              "el proyector confirma el bloqueo con «Deshacer»")
    comprobar(await celular.esperar("!document.querySelector('#avisoPausa').classList.contains('oculto')", 15),
              "el celular de Ana ve el aviso amable de pausa")
    comprobar(await celular.js("document.querySelector('#enviar').disabled") is True, "y ya no puede enviar")
    if capturas:
        await celular.foto(Path(capturas) / f"navegador_movil_pausa_{Pestana.tema}.png")
    await pc.js("document.querySelector('#avisoAdmin button').click()")
    comprobar(await celular.esperar("document.querySelector('#avisoPausa').classList.contains('oculto')", 15),
              "«Deshacer» le devuelve la participación")

    print("\n[Otro equipo por el túnel] /pantalla")
    await pc.ir(url_tunel + "/pantalla", espera=6)
    comprobar(await pc.js("document.querySelector('meta[name=pgc-admin]').content") == "", "sin token por el túnel")
    comprobar(await pc.js("[...document.querySelectorAll('.controles button')].every(b => !b.getClientRects().length)"),
              "sin botones de control (ni de la mano ni del Kinect)")
    comprobar(await pc.esperar("!document.querySelector('#desconectado').classList.contains('si')", 20),
              "la pantalla por el túnel también conecta el WebSocket")
    comprobar(await pc.js("window.__csp.length") == 0, "sin violaciones de CSP por el túnel")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--capturas", help="carpeta donde guardar capturas")
    ap.add_argument("--tema", choices=["dark", "light"], default="dark")
    args = ap.parse_args()
    Pestana.tema = args.tema
    perfil = Path(tempfile.mkdtemp(prefix="pgc_edge_"))
    # Plataforma simulada: sin el detector real del Kinect ni la voz de salida
    entorno = {**os.environ, "PGC_RECONOCEDOR": "simulado", "PGC_VOZ_SALIDA": "false", "PGC_KINECT_LANZAR": "false"}
    comando = [sys.executable, "-m", "pgc", "--simular", "--sin-voz", "--no-abrir", "--puerto-web", str(PUERTO)]
    with tempfile.TemporaryFile() as salida:
        servidor = subprocess.Popen(comando, cwd=RAIZ, stdout=salida, stderr=subprocess.STDOUT, env=entorno)
        edge = subprocess.Popen([EDGE, "--headless=new", f"--remote-debugging-port={PUERTO_CDP}",
                                 f"--user-data-dir={perfil}", "--no-first-run", "--hide-scrollbars", "about:blank"])
        try:
            url = None
            limite = time.time() + 90
            while time.time() < limite and not url:
                try:
                    d = estado()
                    url = d["tunel"]["url"] if d["tunel"]["estado"] == "activo" else None
                except OSError:
                    pass
                time.sleep(1)
            comprobar(bool(url), f"túnel activo: {url}")
            if url:
                time.sleep(4)                           # el DNS de trycloudflare tarda un poco
                asyncio.run(probar(url, args.capturas))
        finally:
            edge.terminate()
            servidor.terminate()
            try:
                servidor.wait(15)
            except subprocess.TimeoutExpired:
                servidor.kill()
            time.sleep(1)
            shutil.rmtree(perfil, ignore_errors=True)
    print("\nRESULTADO:", "TODO PASA" if not fallos else f"{len(fallos)} FALLA(N)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

"""Prueba con servicios reales: Whisper (GPU o CPU) y túnel HTTPS de Cloudflare.

Necesita internet. La mano va simulada. Genera un audio en español con la voz de
Windows (System.Speech) y lo transcribe en local y por el túnel.

Uso:  py -3.11 scripts/prueba_servicios_reales.py
"""
import asyncio
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import httpx
import websockets

RAIZ = Path(__file__).resolve().parent.parent
PUERTO = 8766
LOCAL = f"http://127.0.0.1:{PUERTO}"
FRASE = "Hola jurado, bienvenidos a la sustentación"
fallos = []


def comprobar(condicion, descripcion):
    print(("  OK    " if condicion else "  FALLA ") + descripcion, flush=True)
    if not condicion:
        fallos.append(descripcion)


def generar_wav(ruta):
    """Voz sintética en español con System.Speech (Windows)."""
    script = (
        "Add-Type -AssemblyName System.Speech;"
        "$s = New-Object System.Speech.Synthesis.SpeechSynthesizer;"
        "$v = $s.GetInstalledVoices() | Where-Object { $_.VoiceInfo.Culture.Name -like 'es-*' } | Select-Object -First 1;"
        "if ($v) { $s.SelectVoice($v.VoiceInfo.Name) };"
        f"$s.SetOutputToWaveFile('{ruta}'); $s.Speak('{FRASE}'); $s.Dispose();"
        "if ($v) { $v.VoiceInfo.Name } else { 'sin voz en español' }"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def esperar_estado(condicion, segundos, descripcion):
    limite = time.time() + segundos
    d = None
    while time.time() < limite:
        try:
            d = httpx.get(LOCAL + "/api/estado", timeout=5).json()
            if condicion(d):
                return d
        except httpx.HTTPError:
            pass
        time.sleep(1)
    comprobar(False, f"{descripcion} (último estado: {d and {k: d[k] for k in ('voz', 'tunel')}})")
    return None


def transcribir(base, wav):
    with open(wav, "rb") as f:
        r = httpx.post(base + "/api/transcribir", files={"audio": ("prueba.wav", f, "audio/wav")}, timeout=60)
    return r.status_code, r.json()


def reintentar(funcion, segundos=40):
    """El DNS de *.trycloudflare.com puede tardar unos segundos en responder."""
    limite, error = time.time() + segundos, None
    while time.time() < limite:
        try:
            return funcion()
        except (httpx.HTTPError, OSError) as ex:
            error = ex
            time.sleep(2)
    raise RuntimeError(f"no respondió: {error}")


async def ws_por_tunel(url):
    async with websockets.connect(url.replace("https://", "wss://") + "/ws", max_size=2**20) as ws:
        return json.loads(await asyncio.wait_for(ws.recv(), timeout=20))


def main():
    wav = Path(tempfile.gettempdir()) / "pgc_prueba_voz.wav"
    voz = generar_wav(wav)
    comprobar(wav.exists() and wav.stat().st_size > 1000, f"audio de prueba generado (voz: {voz})")

    comando = [sys.executable, "-m", "pgc", "--simular", "--no-abrir", "--puerto-web", str(PUERTO)]
    print("Arrancando:", " ".join(comando[1:]))
    with tempfile.TemporaryFile() as salida:
        proceso = subprocess.Popen(comando, cwd=RAIZ, stdout=salida, stderr=subprocess.STDOUT)
        try:
            d = esperar_estado(lambda d: d["voz"]["estado"] in ("listo", "error"), 180, "Whisper cargó")
            if d:
                comprobar(d["voz"]["estado"] == "listo", f"Whisper listo en {d['voz']['dispositivo']}")
            t0 = time.time()
            codigo, cuerpo = transcribir(LOCAL, wav)
            comprobar(codigo == 200 and "jurado" in cuerpo.get("texto", "").lower(),
                      f"transcripción local en {time.time() - t0:.1f} s: {cuerpo}")

            d = esperar_estado(lambda d: d["tunel"]["estado"] in ("activo", "no instalado"), 90, "el túnel arrancó")
            url = d and d["tunel"]["url"]
            comprobar(bool(url) and d["url_publica"] == url, f"túnel activo: {url}")
            if url:
                r = reintentar(lambda: httpx.get(url + "/", timeout=20))
                comprobar(r.status_code == 200 and "Mano bidireccional LSC" in r.text, "GET / por el túnel (HTTPS)")
                t0 = time.time()
                codigo, cuerpo = reintentar(lambda: transcribir(url, wav))
                comprobar(codigo == 200 and "jurado" in cuerpo.get("texto", "").lower(),
                          f"transcripción por el túnel en {time.time() - t0:.1f} s: {cuerpo}")
                inicial = asyncio.run(ws_por_tunel(url))
                comprobar(inicial.get("tipo") == "estado", "WebSocket seguro (wss) por el túnel")
                r = reintentar(lambda: httpx.post(url + "/api/mano/saltar", timeout=20))
                comprobar(r.status_code == 403, "saltar por el túnel → 403")
        finally:
            proceso.terminate()
            try:
                proceso.wait(15)
            except subprocess.TimeoutExpired:
                proceso.kill()
            salida.seek(0)
            registro = salida.read().decode("utf-8", errors="replace")
            print("\n--- log del servidor (voz y túnel) ---")
            print("\n".join(l for l in registro.splitlines() if "[voz]" in l or "[tunel]" in l))
    print("\nRESULTADO:", "TODO PASA" if not fallos else f"{len(fallos)} FALLA(N)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())

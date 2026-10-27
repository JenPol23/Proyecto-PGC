"""Diagnóstico del Kinect, paso a paso, antes de la demo (lo lanza diagnostico_kinect.bat).

Revisa, de lo más simple a lo más completo, y dice qué hacer si algo falla:
  1. Windows: .NET 4.8, Kinect SDK 1.8 y el Kinect conectado (Administrador de dispositivos)
  2. Archivos: entorno del detector, versiones, modelo SVM y app del Kinect compilada
  3. Puertos: 8000 (plataforma) y 8765 (detector)
  4. En vivo: arranca el detector y la app del Kinect (como iniciar.bat), mide cuántas imágenes
     por segundo llegan y los cierra al final. Si la plataforma ya está corriendo, solo mide.
No cambia nada: no inicia el deletreo, no graba y no escribe dentro de integracion_kinect/.
El informe queda en registros\\diagnostico_kinect.txt.

Uso:  py -3.11 scripts/diagnostico_kinect.py [--sin-capturador] [--segundos 10]
"""
import argparse
import hashlib
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import replace
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from pgc import config  # noqa: E402
from pgc.adaptadores.kinect import procesos  # noqa: E402
from pgc.adaptadores.kinect.procesos import DETECTOR, LanzadorKinect  # noqa: E402

try:
    sys.stdout.reconfigure(errors="replace")
except AttributeError:
    pass

lineas, resumen = [], {"OK": 0, "AVISO": 0, "FALLA": 0}


def informar(nivel, texto, solucion=""):
    resumen[nivel] += 1
    linea = f"  [{nivel:5}] {texto}" + (f"\n          -> {solucion}" if solucion and nivel != "OK" else "")
    print(linea, flush=True)
    lineas.append(linea)


def titulo(texto):
    print(f"\n{texto}", flush=True)
    lineas.append(f"\n{texto}")


def puerto_abierto(puerto):
    with socket.socket() as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", puerto)) == 0


def obtener(url, timeout=2.0):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as ex:
        return ex.code, "", ex.read()
    except (urllib.error.URLError, OSError):
        return None, "", b""


def powershell(comando):
    r = subprocess.run(["powershell", "-NoProfile", "-Command", comando], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    return r.stdout.strip()


# ---------------------------------------------------------------- 1. Windows
def revisar_windows():
    titulo("1. Windows: .NET, Kinect SDK y el Kinect conectado")
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full") as k:
            release = winreg.QueryValueEx(k, "Release")[0]
        if release >= 528040:
            informar("OK", f".NET Framework 4.8 o superior (Release {release})")
        else:
            informar("FALLA", f".NET Framework anterior a 4.8 (Release {release})",
                     "Instala .NET Framework 4.8 Runtime (la app del Kinect lo necesita)")
    except OSError:
        informar("FALLA", "No se encontró .NET Framework 4.x", "Instala .NET Framework 4.8 Runtime")

    sdk = os.environ.get("KINECTSDK10_DIR") or str(Path(os.environ.get("ProgramFiles", "")) / "Microsoft SDKs/Kinect/v1.8")
    if (Path(sdk) / "Assemblies" / "Microsoft.Kinect.dll").is_file():
        informar("OK", f"Kinect for Windows SDK 1.8 instalado ({sdk})")
    else:
        informar("FALLA", "No está el Kinect for Windows SDK 1.8 (trae los controladores)",
                 "Instala KinectSDK-v1.8-Setup.exe y reinicia")

    salida = powershell("Get-PnpDevice -PresentOnly -ErrorAction SilentlyContinue | "
                        "Where-Object { $_.FriendlyName -match 'Kinect|Xbox NUI' } | "
                        "Select-Object Status, FriendlyName | ConvertTo-Json -Compress")
    dispositivos = json.loads(salida) if salida else []
    dispositivos = [dispositivos] if isinstance(dispositivos, dict) else dispositivos
    if not dispositivos:
        informar("FALLA", "Windows no ve ningún Kinect conectado",
                 "Revisa el adaptador de corriente del Kinect (luz verde), usa un puerto USB 2.0/3.0 directo "
                 "del portátil (sin hub) y espera ~30 s; en el Administrador de dispositivos debe aparecer "
                 "'Kinect for Windows'")
    else:
        for d in dispositivos:
            nombre, estado = d.get("FriendlyName"), d.get("Status")
            if "Xbox NUI" in (nombre or ""):
                informar("FALLA", f"{nombre}: Windows lo ve sin el controlador del SDK",
                         "Reinstala el Kinect SDK 1.8 con el Kinect desconectado y vuelve a conectarlo")
            elif estado == "OK":
                informar("OK", f"{nombre}")
            else:
                informar("FALLA", f"{nombre}: estado {estado}",
                         "Desconecta y conecta el Kinect; si sigue, reinstala el controlador desde el Administrador de dispositivos")


# ---------------------------------------------------------------- 2. Archivos
def revisar_archivos(lanzador):
    titulo("2. Archivos: entorno del detector, modelo y app del Kinect")
    python = lanzador.buscar_python()
    if python is None:
        informar("FALLA", "No está el entorno del detector (.venv-detector)", "Doble clic en instalar_detector.bat")
    else:
        prueba = (
            "import warnings, joblib, mediapipe, sklearn, cv2, numpy\n"
            "with warnings.catch_warnings(record=True) as w:\n"
            "    warnings.simplefilter('always')\n"
            "    m = joblib.load('modelo_estaticas.joblib')\n"
            "print(mediapipe.__version__, sklearn.__version__, cv2.__version__, numpy.__version__, "
            "len(m['categorias']), len(w))\n")
        r = subprocess.run([str(python), "-B", "-c", prueba], cwd=DETECTOR, capture_output=True, text=True,
                           timeout=180, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if r.returncode != 0:
            informar("FALLA", "El entorno del detector no carga el modelo: " + (r.stderr.strip().splitlines() or ["?"])[-1],
                     "Vuelve a ejecutar instalar_detector.bat")
        else:
            mp, skl, cv, npv, categorias, avisos = r.stdout.split()
            informar("OK", f"Entorno del detector: mediapipe {mp}, scikit-learn {skl}, OpenCV {cv}, numpy {npv}")
            if skl != "1.5.2" or avisos != "0":
                informar("AVISO", f"El modelo se cargó con scikit-learn {skl} y {avisos} aviso(s) de versión",
                         "El modelo se guardó con scikit-learn 1.5.2: usa esa versión (instalar_detector.bat)")
            else:
                informar("OK", f"modelo_estaticas.joblib carga sin avisos ({categorias} categorías)")

    exe = lanzador.buscar_exe()
    if exe is None:
        informar("FALLA", "No está la app del Kinect compilada (LSCKinectFramework.exe)",
                 "Copia la carpeta bin\\Debug de Camila a integracion_kinect\\capturador\\LSCKinectFramework\\bin\\Debug "
                 "o pon su ruta en PGC_KINECT_EXE")
    else:
        fecha = time.strftime("%d/%m/%Y %H:%M", time.localtime(exe.stat().st_mtime))
        informar("OK", f"App del Kinect: {exe.relative_to(RAIZ) if RAIZ in exe.parents else exe} (compilada el {fecha})")
        if not (exe.parent / "Microsoft.Kinect.dll").is_file():
            informar("AVISO", "No está Microsoft.Kinect.dll junto al .exe",
                     "Copia la carpeta bin\\Debug completa (la DLL también viene con el SDK 1.8)")


# ---------------------------------------------------------------- 3. Puertos
def revisar_puertos(cfg):
    titulo("3. Puertos")
    plataforma = puerto_abierto(cfg.puerto_web)
    detector = puerto_abierto(8765)
    informar("OK" if not plataforma else "AVISO",
             f"Puerto {cfg.puerto_web} (plataforma): {'libre' if not plataforma else 'en uso: la plataforma ya está corriendo'}",
             "Si no es la plataforma, cierra el programa que lo usa")
    informar("OK" if not detector else "AVISO",
             f"Puerto 8765 (detector): {'libre' if not detector else 'en uso: ya hay un detector corriendo'}",
             "Se medirá ese detector; si no responde, ciérralo desde el Administrador de tareas (python.exe)")
    return plataforma, detector


# ---------------------------------------------------------------- 4. En vivo
def medir_en_vivo(cfg, lanzador, segundos, sin_capturador):
    titulo("4. En vivo: detector y app del Kinect")
    propio = not puerto_abierto(8765)
    if propio:
        print("  Arrancando el detector" + ("" if sin_capturador else " y la app del Kinect (minimizada)") + "...", flush=True)
        lanzador.cfg = replace(cfg, **{"kinect_lanzar": True, "reconocedor": "kinect",
                                        "kinect_capturador": "no" if sin_capturador else cfg.kinect_capturador})
        lanzador.iniciar()
    try:
        limite = time.time() + 60
        while time.time() < limite and obtener("http://127.0.0.1:8765/spell/status")[0] != 200:
            time.sleep(0.5)
        codigo, _, cuerpo = obtener("http://127.0.0.1:8765/spell/status")
        if codigo != 200:
            informar("FALLA", "El detector no responde en 127.0.0.1:8765", "Revisa registros\\detector.log")
            return
        texto = cuerpo.decode("utf-8", "replace").replace("\r", "").replace("\n", " | ")
        informar("OK", f"Detector responde: {texto[:90]}")

        # Imágenes por segundo: cuántas imágenes distintas entrega /preview.jpg
        espera = 20 if propio and not sin_capturador else 3
        print(f"  Esperando imágenes de la cámara (hasta {espera} s)...", flush=True)
        limite = time.time() + espera
        while time.time() < limite and obtener("http://127.0.0.1:8765/preview.jpg")[0] != 200:
            time.sleep(0.5)
        print(f"  Midiendo durante {segundos} s; párate frente al Kinect y muestra una mano...", flush=True)
        vistas, ultima, t0 = set(), None, time.time()
        while time.time() - t0 < segundos:
            codigo, tipo, cuerpo = obtener("http://127.0.0.1:8765/preview.jpg", timeout=1.0)
            if codigo == 200 and tipo.startswith("image/jpeg"):
                huella = hashlib.md5(cuerpo).hexdigest()
                if huella != ultima:
                    vistas.add(huella)
                    ultima = huella
            time.sleep(0.04)
        fps = len(vistas) / segundos
        if fps == 0 and sin_capturador:
            informar("AVISO", "No llegan imágenes (normal con --sin-capturador: no se abrió la app del Kinect)",
                     "Repite sin --sin-capturador, con el Kinect conectado")
        elif fps == 0:
            informar("FALLA", "No llegan imágenes al detector",
                     "Abre la app del Kinect (está minimizada en la barra de tareas): debe decir 'Kinect conectado'. "
                     "Si dice 'No se detectó ningún Kinect', revisa el paso 1")
        elif fps < 3:
            informar("AVISO", f"Llegan pocas imágenes: {fps:.1f} por segundo (lo normal es 5-10)",
                     "Cierra programas pesados; revisa que el portátil esté conectado a la corriente")
        else:
            informar("OK", f"Llegan {fps:.1f} imágenes por segundo al detector (lo normal es 5-10)")
    finally:
        if propio:
            lanzador.detener()
            time.sleep(1)
            informar("OK" if not puerto_abierto(8765) else "AVISO", "Detector y app del Kinect cerrados al terminar",
                     "Ciérralos desde el Administrador de tareas")


def main():
    ap = argparse.ArgumentParser(description="Diagnóstico del Kinect")
    ap.add_argument("--sin-capturador", action="store_true", help="no abrir la app del Kinect (solo el detector)")
    ap.add_argument("--segundos", type=int, default=10, help="cuánto medir las imágenes por segundo")
    args = ap.parse_args()
    print("Diagnóstico del Kinect - " + time.strftime("%d/%m/%Y %H:%M"))
    try:
        cfg = config.cargar([])
    except config.ErrorConfig as ex:
        print(f"Error en el .env: {ex}")
        return 2
    procesos.REGISTROS.mkdir(exist_ok=True)
    lanzador = LanzadorKinect(cfg, lambda m: print("  " + m, flush=True))
    revisar_windows()
    revisar_archivos(lanzador)
    revisar_puertos(cfg)
    medir_en_vivo(cfg, lanzador, args.segundos, args.sin_capturador)
    final = f"\nRESULTADO: {resumen['OK']} OK, {resumen['AVISO']} avisos, {resumen['FALLA']} fallas"
    print(final)
    informe = procesos.REGISTROS / "diagnostico_kinect.txt"
    informe.write_text("Diagnóstico del Kinect - " + time.strftime("%d/%m/%Y %H:%M") + "\n" + "\n".join(lineas) + final + "\n",
                       encoding="utf-8")
    print(f"Informe guardado en {informe.relative_to(RAIZ)}")
    return 1 if resumen["FALLA"] else 0


if __name__ == "__main__":
    sys.exit(main())

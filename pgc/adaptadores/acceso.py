"""Cómo llegan los celulares al servidor: túnel HTTPS de Cloudflare o la IP local.

El túnel (quick tunnel) hace falta para el micrófono del celular, que solo
funciona con HTTPS. Lanza `cloudflared tunnel --url http://127.0.0.1:<puerto>`,
lee la URL *.trycloudflare.com de su salida y la publica. Si cloudflared se cae,
lo vuelve a lanzar (la URL nueva se refleja en el QR automáticamente).
Sin internet, el QR usa http://<ip_local()>:<puerto> (plan B: subir una nota de voz).
"""
import glob
import os
import re
import shutil
import socket
import subprocess
import threading
import time

PATRON_URL = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def buscar_cloudflared():
    ruta = shutil.which("cloudflared")
    if ruta:
        return ruta
    # Instalado con winget pero sin PATH actualizado en esta consola
    local = os.environ.get("LOCALAPPDATA", "")
    for patron in (
        os.path.join(local, "Microsoft", "WinGet", "Links", "cloudflared.exe"),
        os.path.join(local, "Microsoft", "WinGet", "Packages", "Cloudflare.cloudflared*", "cloudflared.exe"),
        os.path.join(os.environ.get("ProgramFiles(x86)", ""), "cloudflared", "cloudflared.exe"),
        os.path.join(os.environ.get("ProgramFiles", ""), "cloudflared", "cloudflared.exe"),
    ):
        encontrados = glob.glob(patron)
        if encontrados:
            return encontrados[0]
    return None


def atar_al_proceso_actual(proc):
    """Windows: cloudflared muere con este proceso aunque Python se cierre a la fuerza.

    Mete el proceso hijo en un Job Object con KILL_ON_JOB_CLOSE; el handle del Job
    se cierra solo cuando termina Python (incluso con la X de la ventana o
    taskkill), y Windows mata entonces a cloudflared. Devuelve el handle o None.
    """
    if os.name != "nt":
        return None
    try:
        import ctypes
        from ctypes import wintypes

        class Basico(ctypes.Structure):
            _fields_ = [("PerProcessUserTimeLimit", ctypes.c_int64), ("PerJobUserTimeLimit", ctypes.c_int64),
                        ("LimitFlags", wintypes.DWORD), ("MinimumWorkingSetSize", ctypes.c_size_t),
                        ("MaximumWorkingSetSize", ctypes.c_size_t), ("ActiveProcessLimit", wintypes.DWORD),
                        ("Affinity", ctypes.c_size_t), ("PriorityClass", wintypes.DWORD),
                        ("SchedulingClass", wintypes.DWORD)]

        class Extendido(ctypes.Structure):
            _fields_ = [("BasicLimitInformation", Basico), ("IoInfo", ctypes.c_ulonglong * 6),
                        ("ProcessMemoryLimit", ctypes.c_size_t), ("JobMemoryLimit", ctypes.c_size_t),
                        ("PeakProcessMemoryUsed", ctypes.c_size_t), ("PeakJobMemoryUsed", ctypes.c_size_t)]

        k32 = ctypes.WinDLL("kernel32", use_last_error=True)
        k32.CreateJobObjectW.restype = wintypes.HANDLE
        k32.CreateJobObjectW.argtypes = (ctypes.c_void_p, wintypes.LPCWSTR)
        k32.SetInformationJobObject.argtypes = (wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD)
        k32.AssignProcessToJobObject.argtypes = (wintypes.HANDLE, wintypes.HANDLE)
        job = k32.CreateJobObjectW(None, None)
        info = Extendido()
        info.BasicLimitInformation.LimitFlags = 0x2000          # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        if (job and k32.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info))
                and k32.AssignProcessToJobObject(job, int(proc._handle))):
            return job
    except Exception:
        pass
    return None


def ip_local():
    """IP del PC en la red WiFi (sin enviar nada: UDP no conecta de verdad)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Tunel:
    """Implementa el puerto AccesoPublico con cloudflared."""

    def __init__(self, puerto, log=print, al_cambiar=None):
        self.puerto = puerto
        self.log = log
        self.al_cambiar = al_cambiar or (lambda: None)
        self.url = None
        self.estado = "apagado"   # apagado | iniciando | activo | error | no instalado
        self._proc = None
        self._job = None
        self._parar = False

    def _cambiar(self, estado, url=None):
        self.estado = estado
        self.url = url
        self.al_cambiar()

    def iniciar(self):
        threading.Thread(target=self._bucle, daemon=True, name="tunel").start()

    def _bucle(self):
        exe = buscar_cloudflared()
        if not exe:
            self.log("[tunel] cloudflared no está instalado -> solo red local (HTTP)")
            self._cambiar("no instalado")
            return
        espera = 2
        while not self._parar:
            self._cambiar("iniciando")
            try:
                self._proc = subprocess.Popen(
                    # 127.0.0.1 y no "localhost": en Windows este último prueba IPv6
                    # primero y suma ~2 s a cada conexión
                    [exe, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{self.puerto}"],
                    stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                    text=True, encoding="utf-8", errors="ignore",
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                self._job = atar_al_proceso_actual(self._proc)     # sin cloudflared huérfanos
                for linea in self._proc.stderr:
                    m = PATRON_URL.search(linea)
                    if m and self.url != m.group(0):
                        self.log(f"[tunel] URL pública: {m.group(0)}")
                        self._cambiar("activo", m.group(0))
                        espera = 2
                self._proc.wait()
            except Exception as ex:
                self.log(f"[tunel] Error: {ex}")
            if self._parar:
                break
            self.log(f"[tunel] cloudflared terminó; reintentando en {espera} s")
            self._cambiar("error")
            time.sleep(espera)
            espera = min(espera * 2, 30)

    def detener(self):
        self._parar = True
        if self._proc and self._proc.poll() is None:
            self._proc.terminate()

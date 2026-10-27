"""Arranca la parte del Kinect junto con la plataforma y la cierra al salir.

    detector    integracion_kinect/detector/server_web_svm.py, con el Python de SU entorno
                (mediapipe 0.10.21, numpy 1.26, scikit-learn 1.5.2: no caben en el Python de la plataforma)
    capturador  la app C# del Kinect ya compilada (LSCKinectFramework.exe), o
                camara_pc.py, que manda la cámara del PC al detector (para probar sin Kinect)

Los dos quedan atados a este proceso con un Job Object (como cloudflared): si la
plataforma se cierra, incluso a la fuerza, Windows los cierra también.
Si algo falta, se avisa en el registro y la plataforma sigue: el celular y el
proyector dicen "Kinect no conectado".
Los archivos de integracion_kinect/ se usan tal cual; nada aquí los modifica.
"""
import os
import socket
import subprocess
import threading
import time
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

from pgc.adaptadores.acceso import atar_al_proceso_actual

RAIZ = Path(__file__).resolve().parents[3]
DETECTOR = RAIZ / "integracion_kinect" / "detector"
CAPTURADOR = RAIZ / "integracion_kinect" / "capturador" / "LSCKinectFramework"
CAMARA_PC = Path(__file__).resolve().parent / "camara_pc.py"
DETECTOR_PARALELO = Path(__file__).resolve().parent / "detector_paralelo.py"
REGISTROS = RAIZ / "registros"
# Dónde puede estar el entorno del detector: el de su README y el de la raíz del repositorio
PYTHONS = (DETECTOR / ".venv" / "Scripts" / "python.exe", RAIZ / ".venv-detector" / "Scripts" / "python.exe")
EXES = tuple(CAPTURADOR / "bin" / v / "LSCKinectFramework.exe" for v in ("Release", "Debug"))
MINIMIZADA = 7                    # SW_SHOWMINNOACTIVE: la ventana C# no tapa el proyector
ESPERA_DETECTOR = 60.0            # s máximos esperando al detector antes de abrir la app del Kinect


def detector_listo(url):
    """El detector ya responde (/spell/status). Abrir la app antes es mandarle imágenes a nadie."""
    try:
        with urllib.request.urlopen(url.rstrip("/") + "/spell/status", timeout=0.5) as r:
            return r.status == 200
    except OSError:
        return False


def minimizar_ventanas(pid):
    """Minimiza (sin activarlas) las ventanas visibles del proceso. Devuelve [(título, ya_estaba_minimizada)].

    La app se lanza ya minimizada (STARTUPINFO); esto lo confirma y lo corrige si WPF la abrió en grande.
    """
    if os.name != "nt":
        return []
    import ctypes
    from ctypes import wintypes
    u32 = ctypes.WinDLL("user32", use_last_error=True)
    encontradas = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def revisar(hwnd, _):
        dueno = wintypes.DWORD()
        u32.GetWindowThreadProcessId(hwnd, ctypes.byref(dueno))
        if dueno.value == pid and u32.IsWindowVisible(hwnd) and u32.GetWindowTextLengthW(hwnd):
            titulo = ctypes.create_unicode_buffer(256)
            u32.GetWindowTextW(hwnd, titulo, 256)
            minimizada = bool(u32.IsIconic(hwnd))
            if not minimizada:
                u32.ShowWindow(hwnd, MINIMIZADA)
            encontradas.append((titulo.value, minimizada))
        return True
    u32.EnumWindows(revisar, 0)
    return encontradas


def puerto_ocupado(url):
    partes = urlsplit(url)
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex((partes.hostname, partes.port or 80)) == 0


class LanzadorKinect:
    def __init__(self, cfg, log=print, popen=subprocess.Popen, pythons=PYTHONS, exes=EXES,
                 listo=detector_listo, minimizar=minimizar_ventanas, espera_detector=ESPERA_DETECTOR):
        self.cfg = cfg
        self.log = log
        self._popen = popen
        self._pythons = pythons
        self._exes = exes
        self._listo = listo
        self._minimizar = minimizar
        self._espera_detector = espera_detector
        self._procesos = {}          # nombre → (Popen, job)
        self._parar = threading.Event()
        self._lock = threading.Lock()
        self.python = self.exe = None

    # ------------------------------------------------------------ búsqueda
    def buscar_python(self):
        if self.cfg.kinect_python:
            ruta = Path(self.cfg.kinect_python)
            return ruta if ruta.is_file() else None
        return next((p for p in self._pythons if Path(p).is_file()), None)

    def buscar_exe(self):
        if self.cfg.kinect_exe:
            ruta = Path(self.cfg.kinect_exe)
            return ruta if ruta.is_file() else None
        return next((e for e in self._exes if Path(e).is_file()), None)

    # ------------------------------------------------------------ arranque
    def iniciar(self):
        if not self.cfg.kinect_lanzar or self.cfg.reconocedor != "kinect":
            return
        REGISTROS.mkdir(exist_ok=True)
        self.python = self.buscar_python()
        if puerto_ocupado(self.cfg.kinect_url):
            self.log(f"[kinect] Ya hay un detector en {self.cfg.kinect_url}: se usa ese")
        elif self.python is None:
            self.log("[kinect] Falta el entorno del detector: py -3.11 -m venv .venv-detector y luego "
                     ".venv-detector\\Scripts\\python -m pip install -r "
                     "integracion_kinect\\detector\\requirements-detector.txt")
        else:
            threading.Thread(target=self._vigilar_detector, daemon=True, name="detector").start()
        # La app del Kinect se abre cuando el detector ya responde (en su propio hilo: el servidor no espera)
        threading.Thread(target=self._capturador_cuando_este_el_detector, daemon=True, name="capturador").start()

    def _capturador_cuando_este_el_detector(self):
        if self.cfg.kinect_capturador == "no":
            return
        inicio = time.monotonic()
        while not self._listo(self.cfg.kinect_url):
            if self._parar.is_set():
                return
            if time.monotonic() - inicio > self._espera_detector:
                self.log(f"[kinect] El detector no respondió en {self._espera_detector:.0f} s; "
                         "se abre la app del Kinect de todas formas (revisa registros\\detector.log)")
                break
            self._parar.wait(0.25)
        else:
            self.log(f"[kinect] Detector listo en {time.monotonic() - inicio:.1f} s")
        if not self._parar.is_set():
            self._lanzar_capturador()

    def _lanzar(self, nombre, comando, cwd, ventana=None):
        info = None
        banderas = 0
        if ventana is None:
            banderas = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        elif hasattr(subprocess, "STARTUPINFO"):
            info = subprocess.STARTUPINFO()
            info.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            info.wShowWindow = ventana
        salida = open(REGISTROS / f"{nombre}.log", "ab")
        # Sin __pycache__: nada se escribe dentro de integracion_kinect/ (sus archivos se usan tal cual)
        entorno = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        with self._lock:                     # detener() no debe colarse entre crear y registrar el proceso
            proc = self._popen([str(c) for c in comando], cwd=str(cwd), stdout=salida, stderr=subprocess.STDOUT,
                               stdin=subprocess.DEVNULL, creationflags=banderas, startupinfo=info, env=entorno)
            salida.close()                   # el hijo ya tiene su copia
            self._procesos[nombre] = (proc, atar_al_proceso_actual(proc))
            if self._parar.is_set():         # nació después de detener(): se cierra ya
                proc.terminate()
        return proc

    def _vigilar_detector(self):
        """Lanza el detector y lo vuelve a lanzar si se cae (máximo 5 veces seguidas)."""
        fallos = 0
        while not self._parar.is_set() and fallos < 5:
            inicio = time.monotonic()
            self.log(f"[kinect] Iniciando el detector (registro en registros\\detector.log)")
            if self.cfg.kinect_detector_paralelo:     # su servidor, envuelto: lecturas en paralelo
                comando = [self.python, "-u", DETECTOR_PARALELO, DETECTOR]
            else:                                     # su servidor original, de a una petición
                comando = [self.python, "-u", "server_web_svm.py"]
            proc = self._lanzar("detector", comando, DETECTOR)
            codigo = proc.wait()
            if self._parar.is_set():
                return
            fallos = 0 if time.monotonic() - inicio > 60 else fallos + 1
            self.log(f"[kinect] El detector terminó (código {codigo}); se reinicia en 3 s")
            self._parar.wait(3)
        if fallos >= 5:
            self.log("[kinect] El detector falla al arrancar; revisa registros\\detector.log")

    def _lanzar_capturador(self):
        modo = self.cfg.kinect_capturador
        if modo == "no":
            return
        if modo == "camara_pc":
            if self.python is None:
                self.log("[kinect] Sin el entorno del detector no se puede usar la cámara del PC")
                return
            self.log(f"[kinect] Usando la cámara {self.cfg.kinect_camara} del PC en lugar del Kinect")
            self._lanzar("camara_pc", [self.python, "-u", CAMARA_PC, "--url", self.cfg.kinect_url,
                                       "--camara", self.cfg.kinect_camara], RAIZ)
            return
        self.exe = self.buscar_exe()
        if self.exe is None:
            donde = f"en {self.cfg.kinect_exe}" if self.cfg.kinect_exe else "en bin\\Release ni bin\\Debug"
            self.log(f"[kinect] No está la app del Kinect compilada ({donde}). Compílala en Visual Studio o "
                     "pon su ruta en PGC_KINECT_EXE; para probar sin Kinect: PGC_KINECT_CAPTURADOR=camara_pc")
            return
        self.log(f"[kinect] Abriendo la app del Kinect ({self.exe.name}), minimizada")
        proc = self._lanzar("capturador", [self.exe], self.exe.parent, ventana=MINIMIZADA)
        self._confirmar_minimizada(proc)

    def _confirmar_minimizada(self, proc, segundos=15.0):
        """Espera a que aparezca la ventana de la app y se asegura de que quede minimizada."""
        limite = time.monotonic() + segundos
        while time.monotonic() < limite and not self._parar.is_set() and proc.poll() is None:
            ventanas = self._minimizar(proc.pid)
            if ventanas:
                if not all(minimizada for _, minimizada in ventanas):
                    self.log("[kinect] La app del Kinect se abrió en grande: se minimizó")
                return
            self._parar.wait(0.2)

    # ------------------------------------------------------------ cierre
    def detener(self):
        with self._lock:
            self._parar.set()
            procesos = list(self._procesos.values())
        for proc, _ in procesos:
            if proc.poll() is None:
                proc.terminate()
        for proc, _ in procesos:
            try:
                proc.wait(5)
            except subprocess.TimeoutExpired:
                proc.kill()
        self._procesos.clear()

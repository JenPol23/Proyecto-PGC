# Código completo del proyecto

Generado el 27/10/2026 13:01 con `scripts/generar_codigo_completo.py`, a partir de los archivos actuales (no se edita a mano). No incluye el firmware de Doby (otro proyecto) ni secretos (`.env`, `config_ble.py`).

## Índice

- `servidor.py`
- `iniciar.bat`
- `.env.example`
- `requirements.txt`
- `requirements-dev.txt`
- `requirements-gpu.txt`
- `pytest.ini`
- `.gitignore`
- `datos/letras.json`
- `datos/palabras_bloqueadas.txt`
- `pgc/__init__.py`
- `pgc/__main__.py`
- `pgc/adaptadores/__init__.py`
- `pgc/adaptadores/acceso.py`
- `pgc/adaptadores/ble_puente.py`
- `pgc/adaptadores/experimentos.py`
- `pgc/adaptadores/kinect/__init__.py`
- `pgc/adaptadores/kinect/camara_pc.py`
- `pgc/adaptadores/kinect/detector_paralelo.py`
- `pgc/adaptadores/kinect/procesos.py`
- `pgc/adaptadores/kinect/reconocedor.py`
- `pgc/adaptadores/mano_ble.py`
- `pgc/adaptadores/mano_respaldo.py`
- `pgc/adaptadores/mano_simulada.py`
- `pgc/adaptadores/mano_usb.py`
- `pgc/adaptadores/protocolo_mano.py`
- `pgc/adaptadores/reconocedor_simulado.py`
- `pgc/adaptadores/voz_salida.py`
- `pgc/adaptadores/whisper.py`
- `pgc/api/__init__.py`
- `pgc/api/app.py`
- `pgc/api/dependencias.py`
- `pgc/api/esquemas.py`
- `pgc/api/rutas/__init__.py`
- `pgc/api/rutas/admin.py`
- `pgc/api/rutas/kinect.py`
- `pgc/api/rutas/mensajes.py`
- `pgc/api/rutas/paginas.py`
- `pgc/api/rutas/participantes.py`
- `pgc/api/rutas/voz.py`
- `pgc/api/rutas/ws.py`
- `pgc/api/seguridad.py`
- `pgc/aplicacion/__init__.py`
- `pgc/aplicacion/cola.py`
- `pgc/aplicacion/deletreo.py`
- `pgc/aplicacion/estado.py`
- `pgc/aplicacion/participantes.py`
- `pgc/aplicacion/protocolo.py`
- `pgc/aplicacion/senas.py`
- `pgc/aplicacion/sistema.py`
- `pgc/aplicacion/turno.py`
- `pgc/arranque.py`
- `pgc/config.py`
- `pgc/dominio/__init__.py`
- `pgc/dominio/abecedario.py`
- `pgc/dominio/experimento.py`
- `pgc/dominio/moderacion.py`
- `pgc/dominio/ordenes.py`
- `pgc/dominio/participante.py`
- `pgc/dominio/texto.py`
- `pgc/puertos/__init__.py`
- `pgc/puertos/acceso.py`
- `pgc/puertos/mano.py`
- `pgc/puertos/reconocedor.py`
- `pgc/puertos/sintetizador.py`
- `pgc/puertos/transcriptor.py`
- `pgc/registro.py`
- `web/diagnostico.html`
- `web/movil.html`
- `web/pantalla.html`
- `firmware/esp32/config_ble.example.py`
- `firmware/esp32/main - copia.py`
- `firmware/esp32/main.py`
- `firmware/esp32/main_mano.py`
- `firmware/esp32/original/bucle_ble.py`
- `firmware/esp32/original/main_original.py`
- `firmware/esp32/protocolo.md`
- `firmware/esp32/prueba.py`
- `firmware/esp32/prueba_dedos.py`
- `tests/arnes_firmware.py`
- `tests/ble_falso_hijo.py`
- `tests/conftest.py`
- `tests/contratos/test_reconocedor.py`
- `tests/detector_falso.py`
- `tests/esp32_falso.py`
- `tests/test_acceso_huerfanos.py`
- `tests/test_api.py`
- `tests/test_atajos.py`
- `tests/test_ble_puente.py`
- `tests/test_capas.py`
- `tests/test_cola.py`
- `tests/test_config.py`
- `tests/test_dominio.py`
- `tests/test_firmware.py`
- `tests/test_kinect_adaptador.py`
- `tests/test_kinect_codigo.py`
- `tests/test_kinect_lanzador.py`
- `tests/test_kinect_paginas.py`
- `tests/test_kinect_plataforma.py`
- `tests/test_mano_ble.py`
- `tests/test_mano_serial.py`
- `tests/test_moderacion.py`
- `tests/test_otros.py`
- `tests/test_participantes.py`
- `tests/test_protocolo.py`
- `tests/test_puertos.py`
- `tests/test_seguridad.py`
- `tests/test_senas.py`
- `tests/test_texto.py`
- `scripts/armar_main_placa.py`
- `scripts/diagnostico_kinect.py`
- `scripts/generar_codigo_completo.py`
- `scripts/prueba_e2e.py`
- `scripts/prueba_navegador.py`
- `scripts/prueba_servicios_reales.py`

## `servidor.py`

```python
"""Atajo de compatibilidad: el servidor está en el paquete pgc (py -3.11 -m pgc).

Uso (igual que siempre):
    py -3.11 servidor.py                 # busca la mano por USB; si no, simulada
    py -3.11 servidor.py --simular       # fuerza modo simulado
    py -3.11 servidor.py --puerto COM5   # puerto fijo de la mano
    py -3.11 servidor.py --sin-tunel     # solo red local (sin HTTPS)
    py -3.11 servidor.py --sin-voz       # no carga Whisper (arranque rápido)

Páginas:  /  (celular de los jurados)   /pantalla  (proyector)
"""
import sys

from pgc.arranque import main

if __name__ == "__main__":
    sys.exit(main())
```

## `iniciar.bat`

```bat
@echo off
rem Inicia TODO el sistema (abre la pantalla del proyector sola):
rem   - la plataforma (pagina del celular, proyector, mano, voz, tunel HTTPS)
rem   - el detector de senas de integracion_kinect (con el Python de .venv-detector)
rem   - la app del Kinect ya compilada (LSCKinectFramework.exe), minimizada
rem Al cerrar esta ventana (o con Ctrl+C) se cierran el detector y la app del Kinect.
rem Si falta el detector o el Kinect, la plataforma arranca igual ("Kinect no conectado").
rem Opciones: --simular  --puerto COM5  --sin-tunel  --sin-voz  --no-abrir  --dev
rem Lo demas (mano por Bluetooth, token, Kinect, camara del PC...) se configura en el archivo .env
rem (copia .env.example como .env la primera vez). Primera vez del detector: instalar_detector.bat
cd /d "%~dp0"
py -3.11 -m pgc %*
pause
```

## `.env.example`

```ini
# Copia este archivo como .env y cambia solo lo que necesites.
# Prioridad: valores por defecto < .env < variables de entorno < opciones de línea de comandos.
# El .env puede tener secretos: no lo entregues ni lo compartas.

# ---------- web
# PGC_PUERTO_WEB=8000
# PGC_ABRIR_NAVEGADOR=true          # abrir /pantalla al arrancar (opción --no-abrir)
# PGC_PING_WS=20                    # segundos sin cambios antes de enviar un ping por el WebSocket

# ---------- mano
# PGC_MANO=auto                     # auto (Bluetooth → USB → simulada) | ble | usb | simulada  (opción --simular)
# PGC_MANO_PUERTO=                  # vacío = autodetección; ej. COM5  (opción --puerto)
# PGC_MANO_BLE_NOMBRE=Mano-LSC     # el NOMBRE de config_ble.py (con el que la placa aparece por Bluetooth)
# PGC_MANO_BLE_TOKEN=               # SECRETO: el mismo TOKEN de config_ble.py; vacío = la mano solo por USB
# PGC_MANO_BLE_REINTENTO=10         # segundos entre intentos de conectar por Bluetooth
# PGC_MANO_BAUDIOS=115200
# PGC_MANO_VIDS=303A,1A86,10C4      # VID USB del ESP32-S3, CH340 y CP210x
# PGC_MANO_TIMEOUT_LETRA=12         # segundos máximos esperando la confirmación de una letra
# PGC_MANO_TIEMPO_SIMULADO=1.2      # duración de una letra en modo simulado
# PGC_AUTODETECCION_CADA=3          # segundos entre búsquedas de la mano en reposo

# ---------- deletreo y cola
# PGC_PAUSA_LETRA=0.5               # la letra queda formada un momento para que se lea
# PGC_PAUSA_NO_DISPONIBLE=0.9       # tiempo en pantalla de las letras que la mano no hace
# PGC_MAX_CARACTERES=60
# PGC_MAX_PENDIENTES_CLIENTE=2
# PGC_MAX_COLA=30
# PGC_HISTORIAL=6

# ---------- voz (Whisper)
# PGC_VOZ=true                      # false = no cargar Whisper (opción --sin-voz)
# PGC_VOZ_MODELO=medium
# PGC_AUDIO_MAX_MB=10
# PGC_AUDIO_MAX_SEGUNDOS=15         # la página corta a 10 s; esto frena audios subidos a mano
# PGC_VOZ_MAX_EN_ESPERA=3           # transcripciones esperando turno; la siguiente recibe "intenta en unos segundos"

# ---------- túnel HTTPS (cloudflared)
# PGC_TUNEL=true                    # false = solo red local (opción --sin-tunel)

# ---------- voz de salida (Coqui VITS): dice las frases del Kinect por los parlantes del PC
# PGC_VOZ_SALIDA=true
# PGC_VOZ_SALIDA_MODELO=tts_models/es/css10/vits

# ---------- Kinect (detector SVM de integracion_kinect/, ver docs/CONTRATO_KINECT.md)
# PGC_RECONOCEDOR=kinect            # kinect | simulado | paquete.modulo:Clase
# PGC_KINECT_URL=http://127.0.0.1:8765   # el detector (server_web_svm.py); siempre en este PC
# PGC_KINECT_INTERVALO=0.3          # segundos entre consultas al detector
# PGC_KINECT_LANZAR=true            # arrancar el detector y el capturador junto con la plataforma
# PGC_KINECT_DETECTOR_PARALELO=true # false = su server_web_svm.py original (atiende de a una petición; más lento)
# PGC_KINECT_PYTHON=                # Python del entorno del detector; vacío = .venv del detector o .venv-detector
# PGC_KINECT_CAPTURADOR=auto        # auto (app C# si está compilada) | kinect | camara_pc | no
# PGC_KINECT_EXE=                   # ruta de LSCKinectFramework.exe; vacío = bin\Release o bin\Debug
# PGC_KINECT_CAMARA=0               # cámara del PC (con PGC_KINECT_CAPTURADOR=camara_pc)
# PGC_KINECT_TURNO_SEGUNDOS=120     # el turno de un celular se libera tras este tiempo sin usar los controles
# PGC_KINECT_CODIGO=true            # para tomar el turno hay que escribir el código de 6 dígitos del proyector
# PGC_KINECT_ECO=false              # modo eco al arrancar (el presentador lo cambia en el proyector)
# PGC_LIM_KINECT_CLIENTE=60         # controles del Kinect por minuto y celular

# ---------- seguridad
# PGC_DEV=false                     # true = publica /docs y /openapi.json (opción --dev)
# PGC_TEXTO_MAX_CUERPO=200          # caracteres que acepta la API (luego se recorta a PGC_MAX_CARACTERES)
# PGC_JSON_MAX_KB=16                # tamaño máximo de una petición (salvo el audio)
# Límites de peticiones por minuto. Ojo: varios celulares con datos móviles pueden compartir IP.
# PGC_LIM_MENSAJE_IP=20
# PGC_LIM_MENSAJE_CLIENTE=6
# PGC_LIM_TRANSCRIBIR_IP=10
# PGC_LIM_TRANSCRIBIR_CLIENTE=4
# PGC_LIM_PREVIA_IP=240
# PGC_LIM_GENERAL_IP=300
# PGC_WS_MAX_CONEXIONES=100         # pantallas y celulares conectados en vivo
# PGC_WS_MAX_POR_IP=40               # por el túnel, los celulares del mismo WiFi comparten una IP
# PGC_LOG_TEXTOS=false              # true = escribir los textos de los mensajes en el log (solo para depurar)
```

## `requirements.txt`

```text
# Plataforma (fase 1): servidor, mano por USB, voz → texto y túnel.
# Versiones fijas = las instaladas y probadas el 20/10/2026 con Python 3.11.
# Instalar:  py -3.11 -m pip install -r requirements.txt
fastapi==0.143.1
starlette==1.8.0
pydantic==2.14.1
pydantic_core==2.50.1
uvicorn[standard]==0.54.0
websockets==17.2
python-multipart==0.0.32
python-dotenv==1.2.4
pyserial==3.5
bleak==3.0.2              # mano por Bluetooth (BLE); en Windows instala sus paquetes winrt-*
qrcode[pil]==8.2
pillow==12.3.0
faster-whisper==1.2.1
ctranslate2==4.8.2
av==18.1.0
numpy==2.4.6
```

## `requirements-dev.txt`

```text
# Pruebas y auditoría (no hacen falta para la demo).
# Instalar:  py -3.11 -m pip install -r requirements-dev.txt
-r requirements.txt
pytest==9.1.1
httpx==0.28.1
pip-audit==2.10.1   # revisión de dependencias:  py -3.11 -m pip_audit -r requirements.txt --no-deps --disable-pip
```

## `requirements-gpu.txt`

```text
# GPU y fases 2–5 (Kinect, MediaPipe, modelos propios, TTS). Ya instalados en el PC de la demo.
# torch con CUDA 12.8 (RTX 5050, sm_120) viene de un índice propio:
#   py -3.11 -m pip install -r requirements-gpu.txt --extra-index-url https://download.pytorch.org/whl/cu128
torch==2.11.0+cu128
torchaudio==2.11.0+cu128
torchvision==0.26.0+cu128
mediapipe==0.10.9
opencv-contrib-python==5.0.0.93
coqui-tts==0.27.5
sounddevice==0.5.6
pygame==2.6.1
```

## `pytest.ini`

```ini
[pytest]
testpaths = tests
addopts = -q
filterwarnings =
    # starlette avisa que su TestClient pasará de httpx a httpx2; no afecta a las pruebas
    ignore:Using .httpx. with .starlette.testclient. is deprecated
```

## `.gitignore`

```
# Secretos: nunca al repositorio
.env
.env.*
!.env.example
config_ble.py
config_wifi.py
firmware/esp32/config_ble.py
secrets.py
secretos.py
*.pem
*.key

# Python generado
__pycache__/
*.py[cod]
.pytest_cache/
*.egg-info/
build/
dist/

# Entornos virtuales
.venv/
venv/
env/

# Editores y herramientas locales
.vscode/
.idea/
.claude/

# Pesados: instaladores, videos, datasets y modelos
*.exe
*.msi
*.zip
*.mp4
*.avi
*.mov
*.mkv
dataset/
datasets/
*.pt
*.pth
*.onnx
*.npz

# Copias locales y basura del sistema
respaldos/
capturas/
Thumbs.db
desktop.ini

# Entornos y archivos temporales de Python
.venv/
__pycache__/
*.pyc

# Configuración privada
.env

# Archivos temporales de Visual Studio
.vs/
[Bb]in/
[Oo]bj/
*.user
*.suo

# Grabaciones de entrenamiento
dataset/
dataset_alfabeto/
# Entorno del detector (sus versiones no caben en el Python de la plataforma) y registros de los procesos del Kinect
.venv-detector/
registros/

# Binarios compilados (la app C# del Kinect se copia a bin\Debug; nunca al repositorio)
*.exe
*.dll
*.pdb
*.exe.config
integracion_kinect/capturador/LSCKinectFramework/bin/
integracion_kinect/capturador/LSCKinectFramework/obj/
```

## `datos/letras.json`

```json
{
  "_descripcion": "Letras de la mano. 'por_defecto' se usa mientras la mano no informe las suyas con la orden 'letras'. Para agregar G, H o S: añádelas aquí y en el firmware.",
  "por_defecto": "abcdefiklmnopqrtuvwxy",
  "aproximaciones": {"ñ": "n"},
  "con_movimiento": ["j", "z", "ñ"]
}
```

## `datos/palabras_bloqueadas.txt`

```text
# Palabras que no se muestran en el proyector ni se envían a la mano.
# Una por línea, en minúscula. Se comparan sin tildes, sin signos y con las
# letras repetidas reducidas ("gonorreaaa" = "gonorrea"). Las de 7 letras o más
# también bloquean las palabras que empiezan por ellas ("hijueputas").
# Las cortas solo bloquean la palabra completa (y su plural), para no afectar
# palabras legítimas ("marica" no bloquea "Maricarmen").
# Editar sin miedo: se lee al arrancar el servidor.

# --- groserías e insultos
hijueputa
hijuepta
hijuputa
hpta
hp
gonorrea
malparido
malparida
marica
maricon
mk
puta
puto
mierda
culo
culicagado
verga
chimba
carechimba
caremonda
monda
pirobo
piroba
cachon
cacorro
guevon
huevon
guevona
huevona
mamaguevo
mamahuevo
pendejo
pendeja
estupido
estupida
imbecil
idiota
perra
zorra
coño
joder
follar
culear
culiar
# --- odio y discriminación
nazi
sudaca
veneco
veneca
```

## `pgc/__init__.py`

```python
"""Plataforma de la mano robótica bidireccional en Lengua de Señas Colombiana (PGC)."""
```

## `pgc/__main__.py`

```python
"""py -3.11 -m pgc  [--simular] [--puerto COM5] [--puerto-web 8000] [--sin-tunel] [--sin-voz] [--no-abrir]"""
import sys

from pgc.arranque import main

sys.exit(main())
```

## `pgc/adaptadores/__init__.py`

```python
"""Implementaciones concretas de los puertos (hardware, modelos, túnel)."""
```

## `pgc/adaptadores/acceso.py`

```python
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
```

## `pgc/adaptadores/ble_puente.py`

```python
"""Puente Bluetooth: bleak en un PROCESO APARTE, manejado desde ManoBLE.

Por qué: el Bluetooth de Windows (WinRT, que usa bleak) y faster-whisper (ctranslate2
en la GPU) no pueden convivir en el mismo proceso: con solo importar WinRT antes de cargar
Whisper, Python se cae con "access violation" (probado el 22/10/2026). Aquí cada uno vive
en su proceso y una librería nunca puede tumbar a la otra.

Lado del servidor: `BleakRemoto` se usa igual que bleak (Escaner + Cliente), así ManoBLE
no cambia. Lado del hijo: `python -m pgc.adaptadores.ble_puente` atiende pedidos en JSON,
una línea por pedido, por stdin; responde y avisa (datos, desconexión) por stdout.
Si el servidor se cierra, el hijo ve stdin cerrado y termina (y el Job Object lo cierra igual).
"""
import asyncio
import importlib
import itertools
import json
import subprocess
import sys
import threading
import types
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
TIEMPO_ARRANQUE = 20.0             # s para que el hijo importe bleak y conteste


# =============================================================================
#  Lado del servidor
# =============================================================================
class BleakRemoto:
    """Escaner y Cliente con la misma forma que bleak; el trabajo lo hace el proceso hijo."""

    def __init__(self, comando=None, entorno=None):
        self.comando = comando or [sys.executable, "-m", "pgc.adaptadores.ble_puente"]
        self.entorno = entorno
        self._proc = None
        self._job = None
        self._ids = itertools.count(1)
        self._pendientes = {}              # id → (bucle, futuro)
        self._lock = threading.Lock()
        self._cliente = None               # el Cliente activo recibe datos y desconexión
        remoto = self

        class Escaner:
            @staticmethod
            async def find_device_by_name(nombre, timeout=5.0):
                res = await remoto._pedir({"op": "buscar", "nombre": nombre, "timeout": timeout}, timeout + 10)
                return types.SimpleNamespace(**res) if res else None

        class Cliente:
            def __init__(self, dispositivo, disconnected_callback=None):
                self.dispositivo = dispositivo
                self.al_desconectar = disconnected_callback
                self.al_notificar = None
                self.is_connected = False

            async def connect(self, timeout=10.0):
                remoto._cliente = self
                await remoto._pedir({"op": "conectar", "address": self.dispositivo.address, "timeout": timeout},
                                    timeout + 10)
                self.is_connected = True

            async def start_notify(self, caracteristica, callback):
                self.al_notificar = callback
                await remoto._pedir({"op": "notificar", "uuid": caracteristica}, 10)

            async def write_gatt_char(self, caracteristica, datos, response=False):
                await remoto._pedir({"op": "escribir", "uuid": caracteristica, "hex": bytes(datos).hex(),
                                     "response": response}, 10)

            async def disconnect(self):
                self.is_connected = False
                await remoto._pedir({"op": "desconectar"}, 10)

        self.Escaner, self.Cliente = Escaner, Cliente

    # ------------------------------------------------------------ proceso hijo
    def _arrancar(self):
        if self._proc is not None and self._proc.poll() is None:
            return
        self._proc = subprocess.Popen(
            self.comando, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            cwd=RAIZ, env=self.entorno,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))     # Ctrl+C solo al servidor
        try:
            from pgc.adaptadores.acceso import atar_al_proceso_actual
            self._job = atar_al_proceso_actual(self._proc)                        # sin hijos huérfanos
        except Exception:
            pass
        threading.Thread(target=self._leer, args=(self._proc,), daemon=True, name="ble-puente").start()

    def _leer(self, proc):
        for linea in proc.stdout:
            try:
                msg = json.loads(linea)
            except ValueError:
                continue
            if "id" in msg:
                with self._lock:
                    bucle, futuro = self._pendientes.pop(msg["id"], (None, None))
                if futuro is not None:
                    bucle.call_soon_threadsafe(_resolver, futuro, msg)
            elif msg.get("ev") == "datos" and self._cliente and self._cliente.al_notificar:
                self._cliente.al_notificar(None, bytearray.fromhex(msg["hex"]))
            elif msg.get("ev") == "desconectado":
                self._avisar_desconexion()
        # el hijo terminó: falla lo pendiente y se avisa la desconexión
        with self._lock:
            pendientes, self._pendientes = self._pendientes, {}
        for bucle, futuro in pendientes.values():
            bucle.call_soon_threadsafe(_resolver, futuro, {"ok": False, "tipo": "ConnectionError",
                                                           "motivo": "el puente Bluetooth se cerró"})
        self._avisar_desconexion()

    def _avisar_desconexion(self):
        cliente = self._cliente
        if cliente is not None and cliente.is_connected:
            cliente.is_connected = False
            if cliente.al_desconectar:
                cliente.al_desconectar(cliente)

    async def _pedir(self, pedido, timeout):
        bucle = asyncio.get_running_loop()
        futuro = bucle.create_future()
        with self._lock:
            self._arrancar()
            pedido["id"] = next(self._ids)
            self._pendientes[pedido["id"]] = (bucle, futuro)
            try:
                self._proc.stdin.write((json.dumps(pedido) + "\n").encode())
                self._proc.stdin.flush()
            except OSError:
                self._pendientes.pop(pedido["id"], None)
                raise ConnectionError("el puente Bluetooth no responde") from None
        try:
            return await asyncio.wait_for(futuro, TIEMPO_ARRANQUE + timeout)
        finally:
            with self._lock:
                self._pendientes.pop(pedido["id"], None)

    def cerrar(self):
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.stdin.close()
                self._proc.wait(3)
            except Exception:
                self._proc.kill()


def _resolver(futuro, msg):
    if futuro.done():
        return
    if msg.get("ok"):
        futuro.set_result(msg.get("res"))
    else:
        # misma clase (por nombre) que en el hijo, para que ManoBLE dé el mensaje adecuado
        futuro.set_exception(type(msg.get("tipo") or "Error", (RuntimeError,), {})(msg.get("motivo", "")))


# =============================================================================
#  Lado del proceso hijo
# =============================================================================
def _bleak_de(ruta):
    """'paquete.modulo:funcion' → objeto con Escaner y Cliente (solo para pruebas)."""
    if not ruta:
        import bleak
        return types.SimpleNamespace(Escaner=bleak.BleakScanner, Cliente=bleak.BleakClient)
    modulo, funcion = ruta.split(":")
    return getattr(importlib.import_module(modulo), funcion)()


async def _atender(bleak):
    bucle = asyncio.get_running_loop()
    salida = sys.stdout.buffer
    cola = asyncio.Queue()
    estado = {"cliente": None, "dispositivos": {}}
    candado = threading.Lock()                 # los avisos de bleak pueden llegar desde otro hilo

    def enviar(msg):
        with candado:
            salida.write((json.dumps(msg) + "\n").encode())
            salida.flush()

    def leer_stdin():
        for linea in sys.stdin.buffer:
            bucle.call_soon_threadsafe(cola.put_nowait, linea)
        bucle.call_soon_threadsafe(cola.put_nowait, None)          # el servidor se cerró

    threading.Thread(target=leer_stdin, daemon=True).start()

    def al_desconectar(_cliente):
        enviar({"ev": "desconectado"})

    def al_notificar(_caracteristica, datos):
        enviar({"ev": "datos", "hex": bytes(datos).hex()})

    async def hacer(p):
        op = p["op"]
        if op == "buscar":
            d = await bleak.Escaner.find_device_by_name(p["nombre"], timeout=p["timeout"])
            if d is None:
                return None
            estado["dispositivos"][d.address] = d
            return {"name": d.name, "address": d.address}
        if op == "conectar":
            if estado["cliente"] is not None:
                try:
                    await estado["cliente"].disconnect()
                except Exception:
                    pass
            dispositivo = estado["dispositivos"].get(p["address"], p["address"])
            cliente = bleak.Cliente(dispositivo, disconnected_callback=al_desconectar)
            await cliente.connect(timeout=p["timeout"])
            estado["cliente"] = cliente
            return None
        cliente = estado["cliente"]
        if op == "desconectar":
            estado["cliente"] = None
            if cliente is not None:
                await cliente.disconnect()
            return None
        if cliente is None:
            raise ConnectionError("Not connected")
        if op == "notificar":
            await cliente.start_notify(p["uuid"], al_notificar)
        elif op == "escribir":
            await cliente.write_gatt_char(p["uuid"], bytes.fromhex(p["hex"]), response=p["response"])
        return None

    async def responder(p):
        try:
            enviar({"id": p["id"], "ok": True, "res": await hacer(p)})
        except Exception as ex:
            motivo = ex.args[0] if ex.args and isinstance(ex.args[0], str) else str(ex)
            enviar({"id": p["id"], "ok": False, "tipo": type(ex).__name__, "motivo": motivo})

    while True:
        linea = await cola.get()
        if linea is None:
            break
        try:
            pedido = json.loads(linea)
        except ValueError:
            continue
        await responder(pedido)            # uno a la vez, en orden (como espera ManoBLE)
    if estado["cliente"] is not None:
        try:
            await estado["cliente"].disconnect()
        except Exception:
            pass


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ruta = argv[argv.index("--bleak") + 1] if "--bleak" in argv else None
    asyncio.run(_atender(_bleak_de(ruta)))


if __name__ == "__main__":
    main()
```

## `pgc/adaptadores/experimentos.py`

```python
"""Guarda un protocolo de letras en experimentos/<fecha_hora>/: CSV, gráficas e informe (para el informe final).

    intentos.csv            un renglón por intento (letra pedida, reconocida, tiempo, % con mano, ...)
    muestras.csv            todas las muestras del diagnóstico (~10/s)
    resumen_por_letra.csv   aciertos, confusiones, no detectadas y tiempo medio por letra
    matriz_confusion.csv / .png
    aciertos_por_letra.png  aciertos, confusiones y no detectadas por letra
    tiempos_por_letra.png   tiempo hasta confirmar (solo aciertos)
    informe.md              exactitud, letras que fallan y causa probable de cada una

Los CSV usan ";" y coma decimal (Excel en español los abre bien) y UTF-8 con BOM.
"""
import csv
import time
from pathlib import Path

from pgc.dominio import experimento as ex

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = RAIZ / "experimentos"


def _num(v):
    return str(v).replace(".", ",") if isinstance(v, float) else ("" if v is None else v)


def _csv(ruta, filas, columnas):
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(columnas)
        for fila in filas:
            w.writerow([_num(fila.get(c)) for c in columnas])


def guardar(protocolo, info=None, carpeta_base=None):
    """Devuelve (carpeta relativa al proyecto, informe)."""
    carpeta = Path(carpeta_base or CARPETA) / time.strftime("%Y-%m-%d_%H%M%S")
    carpeta.mkdir(parents=True, exist_ok=True)
    intentos = protocolo.intentos
    letras = list(dict.fromkeys(letra for letra, _ in protocolo.plan))
    resumen = ex.informe(intentos, letras)

    _csv(carpeta / "intentos.csv", [{**it, "resultado": ex.resultado_de(it)} for it in intentos],
         ["letra", "intento", "resultado", "reconocida", "tiempo_s", "mano_pct", "prediccion_frecuente",
          "margen_medio", "estable_max_s", "cambios", "sin_letra_pct", "motivo_frecuente"])
    _csv(carpeta / "muestras.csv", protocolo.muestras,
         ["t", "fase", "letra", "intento", "manos", "prediccion", "segunda", "margen", "estable_s",
          "confirmaciones", "motivo", "texto"])
    _csv(carpeta / "resumen_por_letra.csv",
         [{**f, "confusiones": ", ".join(f"{k.upper()}×{v}" for k, v in f["confusiones"].items()),
           "causa_probable": resumen["causas"].get(f["letra"], {}).get("texto", "")} for f in resumen["por_letra"]],
         ["letra", "intentos", "aciertos", "exactitud_pct", "confusiones", "no_detectadas", "tiempo_medio_s",
          "causa_probable"])
    filas, columnas, matriz = ex.matriz_confusion(intentos, [l for l in letras if any(i["letra"] == l for i in intentos)])
    with open(carpeta / "matriz_confusion.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["pedida \\ reconocida"] + [c.upper() for c in columnas])
        for letra, fila in zip(filas, matriz):
            w.writerow([letra.upper()] + fila)
    _graficas(carpeta, resumen, filas, columnas, matriz, intentos)
    _informe(carpeta, resumen, protocolo, info or {})
    return str(carpeta.relative_to(RAIZ)) if RAIZ in carpeta.parents else str(carpeta), resumen


def _graficas(carpeta, resumen, filas, columnas, matriz, intentos):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Matriz de confusión
    fig, eje = plt.subplots(figsize=(max(6, len(columnas) * 0.45), max(5, len(filas) * 0.4)))
    imagen = eje.imshow(matriz, cmap="Greens")
    eje.set_xticks(range(len(columnas)), [c.upper() if c != ex.NINGUNA else "ninguna" for c in columnas], rotation=90)
    eje.set_yticks(range(len(filas)), [f.upper() for f in filas])
    eje.set_xlabel("Reconocida")
    eje.set_ylabel("Pedida")
    eje.set_title("Matriz de confusión del protocolo de letras")
    for i, fila in enumerate(matriz):
        for j, v in enumerate(fila):
            if v:
                eje.text(j, i, v, ha="center", va="center", fontsize=8,
                         color="white" if v > max(map(max, matriz)) / 2 else "black")
    fig.colorbar(imagen, ax=eje, fraction=0.03)
    fig.tight_layout()
    fig.savefig(carpeta / "matriz_confusion.png", dpi=150)
    plt.close(fig)

    # Aciertos, confusiones y no detectadas por letra
    por = resumen["por_letra"]
    nombres = [f["letra"].upper() for f in por]
    aciertos = [f["aciertos"] for f in por]
    confus = [sum(f["confusiones"].values()) for f in por]
    nodet = [f["no_detectadas"] for f in por]
    fig, eje = plt.subplots(figsize=(max(6, len(por) * 0.4), 4))
    eje.bar(nombres, aciertos, color="#1A7A55", label="Acierto")
    eje.bar(nombres, confus, bottom=aciertos, color="#A86A00", label="Confundida")
    eje.bar(nombres, nodet, bottom=[a + c for a, c in zip(aciertos, confus)], color="#9AA3A0", label="No detectada")
    eje.set_ylabel("Intentos")
    eje.set_title(f"Resultado por letra (exactitud total {resumen['exactitud_pct']} %)")
    eje.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(carpeta / "aciertos_por_letra.png", dpi=150)
    plt.close(fig)

    # Tiempo hasta confirmar (aciertos)
    datos = {f["letra"]: [it["tiempo_s"] for it in intentos if it["letra"] == f["letra"]
                          and ex.resultado_de(it) == "acierto" and it["tiempo_s"] is not None] for f in por}
    con_datos = [(l.upper(), v) for l, v in datos.items() if v]
    if con_datos:
        fig, eje = plt.subplots(figsize=(max(6, len(con_datos) * 0.4), 4))
        eje.boxplot([v for _, v in con_datos], tick_labels=[l for l, _ in con_datos])
        eje.axhline(ex.TIEMPO_CONFIRMACION, color="#C2362B", linestyle="--", linewidth=1,
                    label=f"Mínimo de su lógica ({ex.TIEMPO_CONFIRMACION} s)")
        eje.set_ylabel("Segundos desde que aparece la mano")
        eje.set_title("Tiempo hasta confirmar la letra")
        eje.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(carpeta / "tiempos_por_letra.png", dpi=150)
        plt.close(fig)


def _informe(carpeta, resumen, protocolo, info):
    lineas = [
        "# Protocolo de letras: resultados",
        "",
        f"- Fecha: {time.strftime('%d/%m/%Y %H:%M')}",
        f"- Letras: {len({l for l, _ in protocolo.plan})} · repeticiones: {protocolo.repeticiones} · "
        f"tiempo máximo por intento: {protocolo.tiempo_max} s" + (" · **detenido antes de terminar**" if info.get("detenido") else ""),
        f"- Intentos: {resumen['intentos']} · aciertos: {resumen['aciertos']} · **exactitud {resumen['exactitud_pct']} %**"
        + (f" · tiempo medio hasta confirmar: {resumen['tiempo_medio_s']} s" if resumen["tiempo_medio_s"] else ""),
        "",
        "## Por letra",
        "",
        "| Letra | Aciertos | Confusiones | No detectadas | Tiempo medio (s) | Causa probable de los fallos |",
        "|---|---|---|---|---|---|",
    ]
    for f in resumen["por_letra"]:
        conf = ", ".join(f"{k.upper()}×{v}" for k, v in f["confusiones"].items()) or "—"
        causa = resumen["causas"].get(f["letra"], {}).get("texto", "—")
        tiempo = f["tiempo_medio_s"] if f["tiempo_medio_s"] is not None else "—"
        lineas.append(f"| {f['letra'].upper()} | {f['aciertos']}/{f['intentos']} | {conf} | {f['no_detectadas']} | "
                      f"{tiempo} | {causa} |")
    lineas += ["", "Archivos: intentos.csv, muestras.csv, resumen_por_letra.csv, matriz_confusion.csv/.png, "
               "aciertos_por_letra.png, tiempos_por_letra.png.", ""]
    (carpeta / "informe.md").write_text("\n".join(lineas), encoding="utf-8")
```

## `pgc/adaptadores/kinect/__init__.py`

```python
"""Carpeta del reconocimiento de señas (Lina, Paula y Jean Harry).

Aquí va la clase que cumple el puerto pgc.puertos.reconocedor.ReconocedorSenas.
Contrato completo, con un esqueleto para empezar: docs/CONTRATO_KINECT.md
"""
```

## `pgc/adaptadores/kinect/camara_pc.py`

```python
"""Envía la cámara del PC al detector, igual que la app C# hace con el Kinect (para probar sin Kinect).

Toma la cámara con OpenCV, la lleva a 640×480 (la resolución del Kinect v1) y
envía unas 10 imágenes por segundo en JPEG a POST /detect del detector.
Corre con el Python del entorno del detector (ya trae OpenCV); no importa nada de pgc.

    .venv-detector\\Scripts\\python pgc\\adaptadores\\kinect\\camara_pc.py [--camara 0] [--probar]
"""
import argparse
import sys
import time
import urllib.error
import urllib.request

import cv2


def abrir(indice):
    # En Windows, DirectShow abre más rápido y más cámaras que el backend por defecto
    for backend in ((cv2.CAP_DSHOW,) if sys.platform == "win32" else ()) + (cv2.CAP_ANY,):
        cam = cv2.VideoCapture(indice, backend)
        if cam.isOpened():
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return cam
        cam.release()
    return None


def main():
    try:                                     # su salida va a registros\camara_pc.log (cp1252 en Windows)
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default="http://127.0.0.1:8765")
    ap.add_argument("--camara", type=int, default=0)
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--probar", action="store_true", help="envía una sola imagen y termina")
    args = ap.parse_args()

    cam = abrir(args.camara)
    if cam is None:
        print(f"No se pudo abrir la cámara {args.camara}", flush=True)
        return 1
    print(f"Cámara {args.camara} abierta; enviando a {args.url}/detect", flush=True)
    pausa = 1.0 / max(args.fps, 1)
    try:
        while True:
            t0 = time.monotonic()
            ok, cuadro = cam.read()
            if not ok:
                print("La cámara no entregó imagen; reintentando", flush=True)
                time.sleep(1)
                continue
            cuadro = cv2.resize(cuadro, (640, 480))
            ok, jpeg = cv2.imencode(".jpg", cuadro, [cv2.IMWRITE_JPEG_QUALITY, 85])
            req = urllib.request.Request(args.url + "/detect", data=jpeg.tobytes(), method="POST",
                                         headers={"Content-Type": "image/jpeg"})
            try:
                with urllib.request.urlopen(req, timeout=3) as r:
                    manos = r.headers.get("X-Hands-Count", "?")
                if args.probar:
                    print(f"Imagen enviada; manos detectadas: {manos}", flush=True)
                    return 0
            except (urllib.error.URLError, OSError):
                time.sleep(1)                       # el detector aún no está listo
                continue
            time.sleep(max(0.0, pausa - (time.monotonic() - t0)))
    except KeyboardInterrupt:
        return 0
    finally:
        cam.release()


if __name__ == "__main__":
    sys.exit(main())
```

## `pgc/adaptadores/kinect/detector_paralelo.py`

```python
"""El detector de Camila (server_web_svm.py) TAL CUAL, atendiendo las lecturas en paralelo y con diagnóstico.

Su servidor (HTTPServer) atiende de a una petición: mientras procesa una imagen de /detect
(MediaPipe + SVM, ~25–45 ms), la vista previa y el estado esperan. Este envoltorio NO modifica
sus archivos: importa su módulo y lo sirve con ThreadingHTTPServer, con una regla para no
cambiar su lógica:

  - POST (/detect, /spell/*, /record/*, /alphabet/*, /recognize/*): de a uno, en orden, con un
    candado, igual que en su servidor (el deletreo y MediaPipe nunca corren en paralelo);
  - GET (/preview.jpg, /spell/status, ...): en paralelo; solo leen.

Además agrega GET /diagnostico (solo lectura): por qué una letra se confirma o no. Después de que
SU lógica procesa cada imagen, se leen los campos de su deletreador (candidata, desde cuándo,
confirmaciones, armado) y, con una copia propia de su modelo, la segunda letra más probable y el
margen entre ambas (su SVM no da probabilidades: probability=False). Nada de esto cambia su estado.

Lo lanza pgc/adaptadores/kinect/procesos.py con el Python de .venv-detector:
    python detector_paralelo.py <carpeta del detector>
"""
import json
import sys
import threading
import time
from collections import deque
from http.server import ThreadingHTTPServer
from pathlib import Path


class Diagnostico:
    """Último cuadro procesado: qué vio MediaPipe, qué dijo el SVM y por qué no (o sí) se confirma."""

    def __init__(self, svm_mod, entrenar_mod, modelo):
        self.svm = svm_mod                      # server_deletreo_svm (su módulo)
        self.caracteristicas = entrenar_mod.caracteristicas
        self.modelo = modelo                    # copia propia de su modelo_estaticas.joblib (o None)
        clases = list(modelo.classes_) if modelo is not None else list(entrenar_mod.CATEGORIAS)
        self.categorias = [str(c) for c in clases]
        self._lock = threading.Lock()
        self._ultimo = {"t": 0.0, "manos": None, "motivo": "Todavía no llegan imágenes"}
        self._recientes = deque(maxlen=60)      # (t, predicción) para ver si la letra está cambiando
        self._texto_antes = ""

    def registrar(self, resultado):
        ahora = time.monotonic()
        d = self.svm.deletreador
        manos = [[{"x": float(p.x), "y": float(p.y), "z": float(p.z)} for p in m.landmark]
                 for m in (resultado.multi_hand_landmarks or [])]
        pred = segunda = None
        margen = None
        if len(manos) == 1 and self.modelo is not None:
            vector = self.caracteristicas(manos)
            if vector is not None:
                fila = vector.reshape(1, -1)
                pred = str(self.modelo.predict(fila)[0])                  # la misma predicción que su lógica
                puntajes = self.modelo.decision_function(fila)[0]
                clases = [str(c) for c in self.modelo.classes_]
                orden = sorted(range(len(clases)), key=lambda i: puntajes[i], reverse=True)
                otras = [i for i in orden if clases[i] != pred]
                if otras:
                    segunda = clases[otras[0]]
                    margen = round(float(puntajes[clases.index(pred)] - puntajes[otras[0]]), 3)
        if pred is not None:
            self._recientes.append((ahora, pred))
        ventana = {p for t, p in self._recientes if ahora - t <= self.svm.TIEMPO_CONFIRMACION}
        estable = (ahora - d.candidata_desde) if (d.candidata and d.candidata_desde) else 0.0
        confirmada = d.texto[len(self._texto_antes):] if d.texto.startswith(self._texto_antes) else ""
        self._texto_antes = d.texto
        motivo = self._motivo(d, len(manos), pred, ventana, estable, confirmada)
        with self._lock:
            self._ultimo = {
                "t": ahora, "activo": bool(d.activo), "manos": len(manos),
                "prediccion": pred, "segunda": segunda, "margen": margen,
                "candidata": d.candidata, "estable_s": round(estable, 2), "confirmaciones": d.confirmaciones,
                "armado": bool(d.armado), "texto": d.texto, "estado": d.estado,
                "confirmada": confirmada.strip().lower() or None,
                "letras_recientes": sorted(ventana), "motivo": motivo,
                "tiempo_confirmacion": self.svm.TIEMPO_CONFIRMACION, "tiempo_liberacion": self.svm.TIEMPO_LIBERACION,
                "confirmaciones_necesarias": 4,
            }

    def _motivo(self, d, manos, pred, ventana, estable, confirmada):
        if confirmada.strip():
            return f"Letra confirmada: {confirmada.strip().upper()}"
        if not d.activo:
            return "Deletreo detenido"
        if manos == 0:
            return "Mano no detectada"
        if manos > 1:
            return "Más de una mano"
        if not d.armado:
            return f"Retira la mano {self.svm.TIEMPO_LIBERACION} s para la siguiente letra"
        if pred is None:
            return "Puntos de la mano no válidos"
        if pred == "sin_letra":
            return "El modelo dice «sin letra»"
        if len(ventana) > 1:
            return "Letra cambiando: " + " / ".join(sorted(x.upper() for x in ventana))
        if estable < self.svm.TIEMPO_CONFIRMACION:
            return f"Tiempo insuficiente: {estable:.1f} de {self.svm.TIEMPO_CONFIRMACION} s"
        if d.confirmaciones < 4:
            return f"Pocas imágenes: {d.confirmaciones} de 4"
        return "Confirmando…"

    def json(self):
        with self._lock:
            datos = dict(self._ultimo)
        datos["edad_ms"] = round((time.monotonic() - datos["t"]) * 1000) if datos["t"] else None
        datos["categorias"] = self.categorias
        return json.dumps(datos, ensure_ascii=False).encode("utf-8")


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    sys.path.insert(0, str(carpeta))
    import joblib
    import mediapipe as mp
    import entrenar_estaticas                           # sus módulos, sin cambios
    import server_deletreo_svm
    import server_web_svm

    try:                                                 # copia propia: su deletreador carga la suya al iniciar
        modelo = joblib.load(server_deletreo_svm.MODELO)["modelo"]
    except Exception as ex:                              # sin modelo, el diagnóstico sigue (sin predicción)
        print(f"Diagnóstico sin modelo: {ex}", flush=True)
        modelo = None
    diagnostico = Diagnostico(server_deletreo_svm, entrenar_estaticas, modelo)
    una_a_la_vez = threading.Lock()

    class DetectorConDiagnostico(server_web_svm.DetectorSVM):
        def process(self, imagen_rgb):
            resultado = super().process(imagen_rgb)      # SU procesamiento (MediaPipe + su deletreo)
            try:
                diagnostico.registrar(resultado)
            except Exception as ex:                      # el diagnóstico nunca afecta a su detector
                print(f"Diagnóstico: {type(ex).__name__}: {ex}", flush=True)
            return resultado

    class HandlerParalelo(server_web_svm.HandlerWeb):
        def do_GET(self):
            if self.path == "/diagnostico":
                self.send_data(200, diagnostico.json(), "application/json; charset=utf-8",
                               {"Cache-Control": "no-store"})
                return
            super().do_GET()

        def do_POST(self):
            with una_a_la_vez:
                super().do_POST()

    # Los mismos parámetros de MediaPipe que su main() en server_web_svm.py
    with mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5) as manos:
        HandlerParalelo.detector = DetectorConDiagnostico(manos)
        servidor = ThreadingHTTPServer(("127.0.0.1", 8765), HandlerParalelo)
        servidor.daemon_threads = True
        print("Detector para la página listo en 127.0.0.1:8765 (lecturas en paralelo, con diagnóstico)", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            servidor.server_close()


if __name__ == "__main__":
    main()
```

## `pgc/adaptadores/kinect/procesos.py`

```python
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


PATRONES_RESTOS = ("detector_paralelo.py", "server_web_svm.py", "camara_pc.py")


def buscar_restos():
    """Detectores, apps del Kinect y cámaras del PC que quedaron corriendo: [(pid, nombre, comando)].

    Solo se llama cuando NO hay otra plataforma corriendo (si la hay, esos procesos son suyos).
    """
    if os.name != "nt":
        return []
    consulta = ("Get-CimInstance Win32_Process -Filter \"Name='python.exe' or Name='LSCKinectFramework.exe'\" | "
                "Select-Object ProcessId, ParentProcessId, Name, CommandLine | ConvertTo-Json -Compress")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command", consulta], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=30,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        import json
        datos = json.loads(r.stdout) if r.stdout.strip() else []
    except (OSError, ValueError, subprocess.SubprocessError):
        return []
    datos = [datos] if isinstance(datos, dict) else datos
    restos = []
    for d in datos:
        comando = d.get("CommandLine") or ""
        if d.get("ProcessId") == os.getpid():
            continue
        if d.get("Name") == "LSCKinectFramework.exe" or any(p in comando for p in PATRONES_RESTOS):
            restos.append((d["ProcessId"], d["Name"], comando, d.get("ParentProcessId")))
    # El python.exe de un entorno virtual lanza un hijo con el mismo comando: es UN detector, no dos.
    # Se deja solo el de arriba (cerrarlo con /T cierra también al hijo).
    pids = {r[0] for r in restos}
    return [r[:3] for r in restos if r[3] not in pids]


def cerrar_proceso(pid):
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True,
                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def tipo_de_resto(nombre, comando):
    if nombre == "LSCKinectFramework.exe":
        return "app del Kinect"
    return "cámara del PC" if "camara_pc.py" in comando else "detector"


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
                 listo=detector_listo, minimizar=minimizar_ventanas, espera_detector=ESPERA_DETECTOR,
                 buscar_restos=buscar_restos, cerrar=cerrar_proceso):
        self.cfg = cfg
        self.log = log
        self._popen = popen
        self._pythons = pythons
        self._exes = exes
        self._listo = listo
        self._minimizar = minimizar
        self._espera_detector = espera_detector
        self._buscar_restos = buscar_restos
        self._cerrar = cerrar
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
        self.cerrar_restos()
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

    def cerrar_restos(self):
        """Cierra detectores, apps del Kinect y cámaras que quedaron de una ejecución anterior."""
        restos = self._buscar_restos()
        if not restos:
            return {}
        cuenta = {}
        for pid, nombre, comando in restos:
            tipo = tipo_de_resto(nombre, comando)
            cuenta[tipo] = cuenta.get(tipo, 0) + 1
            self._cerrar(pid)
        self.log("[kinect] Se cerraron restos de una ejecución anterior: "
                 + ", ".join(f"{n} {t}" for t, n in sorted(cuenta.items())))
        limite = time.monotonic() + 5                 # que el puerto del detector quede libre
        while puerto_ocupado(self.cfg.kinect_url) and time.monotonic() < limite:
            time.sleep(0.2)
        return cuenta

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
```

## `pgc/adaptadores/kinect/reconocedor.py`

```python
"""ReconocedorKinect: conecta el detector SVM del equipo con la plataforma.

El detector (integracion_kinect/detector/server_web_svm.py, de Camila) se usa
tal cual: MediaPipe Hands + el SVM entrenado por el equipo deciden las letras y
las van escribiendo en su propio texto. Este adaptador solo lo consulta:

    GET  /spell/status   "Texto: HOLA\\nEstado: Posible letra: A | Estable: 0.4 s"
    POST /spell/start | stop | space | backspace | clear
    GET  /preview.jpg    última imagen con los puntos de la mano (503 si no llegan)

y convierte cada cambio del texto en los eventos del contrato
(docs/CONTRATO_KINECT.md): letra nueva → "letra", espacio → "espacio",
texto más corto → "borrar". "fin" lo emite este adaptador cuando alguien toca
«Terminar»: primero recoge las letras pendientes, luego emite "fin" y deja en
blanco el texto del detector.

Si el detector cambia /spell/status a JSON ({"texto", "estado", "activo",
"confianza", "latencia_ms"}), se usa sin cambiar nada aquí.

Es el ÚNICO que habla con el detector: los celulares reciben todo por el
WebSocket de la plataforma (nada de consultas repetidas desde cada celular).
"""
import json
import os
import threading
import time
import urllib.error
import urllib.request

from pgc.puertos.reconocedor import LETRAS_VALIDAS, EventoSena

NO_CONECTADO = "Kinect no conectado"
DETENIDO = "Deletreo detenido."
ACCIONES = {"iniciar": "start", "detener": "stop", "espacio": "space", "borrar": "backspace", "limpiar": "clear"}
SIN_MANO = ("No se detecta la mano.", "Lista para la siguiente letra.")
MODELO = "SVM"                    # el modelo del detector (puntos de MediaPipe → letra)
PERIODO_VISTA = 0.015             # mientras el proyector muestra la cámara: imagen cada 15 ms (no se pierden cuadros)
ESTADO_MAX_S = 0.3                # el estado se lee con cada imagen nueva, y al menos cada 0,3 s
VISTA_ACTIVA_S = 3.0              # el proyector "está mirando" si pidió la imagen en los últimos 3 s
CONGELADA_S = 1.5                 # mirando: si la imagen no cambia en 1,5 s, ya no llegan cuadros
SIN_CUADROS_S = 3.0               # sin mirar (se revisa 1 vez/s): el mismo margen que usa el detector


class ErrorKinect(RuntimeError):
    """Mensaje corto y amable para la pantalla (p. ej. "Kinect no conectado")."""


def eventos_por_cambio(antes, despues):
    """Eventos que llevan el texto `antes` a `despues` (los dos en el formato del detector).

    Se borra hasta el prefijo común y se escribe el resto, como haría una persona.
    """
    comun = len(os.path.commonprefix([antes, despues]))
    eventos = [EventoSena("borrar") for _ in antes[comun:]]
    for c in despues[comun:]:
        if c == " ":
            eventos.append(EventoSena("espacio"))
        elif c.lower() in LETRAS_VALIDAS:
            eventos.append(EventoSena("letra", letra=c.lower(), modelo=MODELO, instante=time.monotonic()))
    return eventos


def leer_estado(cuerpo):
    """(texto, detalle, activo|None, confianza|None, latencia|None) de /spell/status (texto o JSON)."""
    cuerpo = cuerpo.strip()
    if cuerpo.startswith("{"):
        d = json.loads(cuerpo)
        return (str(d.get("texto", "")), str(d.get("estado", "")), d.get("activo"),
                d.get("confianza"), d.get("latencia_ms"))
    texto, separador, detalle = cuerpo.replace("\r\n", "\n").partition("\nEstado:")
    if not texto.startswith("Texto: ") or not separador:
        raise ValueError("estado del detector no válido")
    texto = texto[len("Texto: "):]
    return ("" if texto == "—" else texto), detalle.strip(), None, None, None


class ReconocedorKinect:
    """Implementa pgc.puertos.reconocedor.ReconocedorSenas (+ los controles opcionales del contrato §3.1)."""

    def __init__(self, url="http://127.0.0.1:8765", intervalo=0.3, timeout=1.5, reloj=time.monotonic):
        self.url = url.rstrip("/")
        self.intervalo = intervalo
        self.timeout = timeout
        self._reloj = reloj
        self.estado = "apagado"
        self.detalle = ""
        self.conectado = False        # el detector responde
        self.camara = False           # llegan imágenes del Kinect (o de la cámara del PC)
        self.activo = False           # el deletreo está iniciado
        self._texto = ""              # último texto visto en el detector
        self._imagen = None
        self._t_imagen = 0.0
        self._t_cambio = -1e9         # última vez que llegó una imagen DISTINTA (la cámara sigue viva)
        self._cuadro = 0              # número de imágenes distintas recibidas
        self._foto = None             # {jpeg, t, texto, detalle, desfase_ms, cuadro}: imagen + estado del mismo momento
        self._detalle_detector = ""   # la línea "Estado:" del detector, tal cual
        self._t_estado = 0.0
        self._t_pedida = -1e9         # alguien (el proyector) quiere ver la imagen
        self._nueva = threading.Condition()   # avisa a quien espera la siguiente imagen (proyector)
        self._al_evento = self._avisar = None
        self._lock = threading.RLock()
        self._parar = threading.Event()
        self._hilo = None

    @classmethod
    def desde_config(cls, cfg):
        """La plataforma lo arma con su configuración (PGC_KINECT_URL y PGC_KINECT_INTERVALO)."""
        return cls(url=cfg.kinect_url, intervalo=cfg.kinect_intervalo)

    # ------------------------------------------------------------ ciclo de vida
    def iniciar(self, al_evento, al_cambiar_estado):
        self._al_evento, self._avisar = al_evento, al_cambiar_estado
        self._parar.clear()
        self._cambiar("cargando", "Buscando el detector…")
        self._hilo = threading.Thread(target=self._bucle, daemon=True, name="kinect")
        self._hilo.start()

    def detener(self):
        self._parar.set()
        if self._hilo and self._hilo is not threading.current_thread():
            self._hilo.join(timeout=3)
        self._hilo = None
        self.conectado = self.camara = self.activo = False
        if self.estado != "apagado":
            self._cambiar("apagado", "")

    def _mirando(self):
        return self._reloj() - self._t_pedida < VISTA_ACTIVA_S

    def _bucle(self):
        """Sin nadie mirando: estado cada `intervalo` e imagen 1 vez/s (solo para saber si hay cámara).
        Con el proyector mirando: imagen cada 30 ms y, apenas llega una NUEVA, su estado (así coinciden
        y no se le piden al detector más estados de los necesarios: atiende de a una petición)."""
        siguiente_imagen = siguiente_estado = 0.0
        while not self._parar.is_set():
            inicio = self._reloj()
            mirando = self._mirando()
            try:
                with self._lock:
                    if mirando:
                        nueva = self._actualizar_imagen(emparejar=False)
                        if nueva or inicio >= siguiente_estado:
                            self._sincronizar()
                            siguiente_estado = inicio + ESTADO_MAX_S
                            if nueva:
                                self._emparejar()
                    else:
                        self._sincronizar()
                        if inicio >= siguiente_imagen:
                            self._actualizar_imagen()
                            siguiente_imagen = inicio + 1.0
            except Exception as ex:                       # regla 4: nada se escapa del hilo
                self._cambiar("error", f"Kinect: {type(ex).__name__}")
            periodo = PERIODO_VISTA if mirando else self.intervalo
            self._parar.wait(max(0.0, periodo - (self._reloj() - inicio)))   # descuenta lo que tardó la vuelta

    # ------------------------------------------------------------ detector
    def _pedir(self, ruta, metodo="GET"):
        req = urllib.request.Request(self.url + ruta, method=metodo, data=b"" if metodo == "POST" else None)
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()

    def _sincronizar(self):
        """Lee /spell/status, emite los eventos del cambio y actualiza estado y detalle."""
        try:
            _, _, cuerpo = self._pedir("/spell/status")
            texto, detalle, activo, _, _ = leer_estado(cuerpo.decode("utf-8", "replace"))
        except (urllib.error.URLError, OSError, ValueError):
            self.conectado = self.camara = self.activo = False
            self._cambiar("error", NO_CONECTADO)
            return
        self.conectado = True
        self._detalle_detector, self._t_estado = detalle, self._reloj()
        for evento in eventos_por_cambio(self._texto, texto):
            self._emitir(evento)
        self._texto = texto
        if activo is not None:
            self.activo = bool(activo)
        elif detalle == DETENIDO:                     # el detector se reinició o alguien lo detuvo
            self.activo = False
        self._camara_al_dia()
        if not self.camara:
            self._cambiar("error", NO_CONECTADO)
        elif self.activo and detalle not in SIN_MANO:
            self._cambiar("listo", detalle)
        else:
            self._cambiar("sin_persona", detalle)

    def _actualizar_imagen(self, emparejar=True):
        """Trae /preview.jpg. Devuelve True si es una imagen NUEVA (el detector repite la última si no llegan)."""
        nueva = False
        try:
            estado, tipo, cuerpo = self._pedir("/preview.jpg")
            if estado == 200 and tipo.startswith("image/jpeg"):
                ahora = self._reloj()
                if cuerpo != self._imagen:
                    nueva = True
                    self._cuadro += 1
                    self._t_cambio = ahora
                self._imagen, self._t_imagen = cuerpo, ahora
                if nueva and emparejar:
                    self._emparejar()
        except (urllib.error.URLError, OSError):
            pass                                       # 503 = no llegan imágenes; el detector puede no estar
        self._camara_al_dia()
        return nueva

    def _emparejar(self):
        """Guarda la imagen nueva con el texto y el estado leídos para ella, y avisa a quien la espera."""
        self._foto = {"jpeg": self._imagen, "t": self._t_imagen, "texto": self._texto,
                      "detalle": self._detalle_detector, "cuadro": self._cuadro,
                      "desfase_ms": round(abs(self._t_estado - self._t_imagen) * 1000, 1)}
        with self._nueva:
            self._nueva.notify_all()

    def _camara_al_dia(self):
        """Hay cámara si llegan imágenes NUEVAS (una imagen repetida = congelada = no llegan cuadros)."""
        limite = CONGELADA_S if self._mirando() else SIN_CUADROS_S
        self.camara = self.conectado and self._reloj() - self._t_cambio < limite

    def _emitir(self, evento):
        if self._al_evento:
            self._al_evento(evento)

    def _cambiar(self, estado, detalle):
        if (estado, detalle) == (self.estado, self.detalle):
            return
        self.estado, self.detalle = estado, detalle
        if self._avisar:
            self._avisar()

    # ------------------------------------------------------------ controles (contrato §3.1, opcionales)
    def controlar(self, accion):
        """iniciar | detener | espacio | borrar | limpiar | terminar. Lanza ErrorKinect si no se pudo."""
        with self._lock:
            if accion == "terminar":
                self._sincronizar()                  # primero las letras que aún no se habían visto
                self._emitir(EventoSena("fin"))
                self._texto = ""                     # la frase ya salió: el detector empieza de cero
                try:
                    self._pedir("/spell/clear", "POST")
                except (urllib.error.URLError, OSError):
                    pass                             # la frase ya se entregó; no es un error para el jurado
                return
            if accion not in ACCIONES:
                raise ErrorKinect("Acción no válida.")
            try:
                self._pedir("/spell/" + ACCIONES[accion], "POST")
            except urllib.error.HTTPError as ex:      # p. ej. 400 "No existe modelo_estaticas.joblib."
                mensaje = ex.read().decode("utf-8", "replace").strip()[:120] or "El detector rechazó la orden."
                raise ErrorKinect(mensaje) from None
            except (urllib.error.URLError, OSError):
                raise ErrorKinect(NO_CONECTADO) from None
            if accion == "iniciar":
                self.activo = True
            elif accion == "detener":
                self.activo = False
            self._sincronizar()

    def diagnostico(self):
        """Por qué una letra se confirma o no (GET /diagnostico de detector_paralelo.py), o None.

        Su servidor original no lo tiene (404): entonces None y la vista de diagnóstico lo dice.
        """
        try:
            estado, _, cuerpo = self._pedir("/diagnostico")
            return json.loads(cuerpo.decode("utf-8")) if estado == 200 else None
        except (urllib.error.URLError, OSError, ValueError):
            return None

    def imagen(self):
        """Última imagen JPEG con los puntos de la mano, o None. Pedirla sube el ritmo de actualización."""
        foto = self.imagen_con_estado()
        return foto["jpeg"] if foto else None

    def imagen_con_estado(self, despues=None, espera=0.0):
        """La imagen con el texto y el estado del detector leídos para ELLA (contrato §3.1).

        {"jpeg", "texto", "detalle", "cuadro", "edad_ms", "desfase_ms"}, o None si no llegan imágenes.
        despues/espera: si ya se mostró el cuadro `despues`, espera hasta `espera` s a que llegue uno más
        nuevo (así el proyector recibe cada imagen apenas existe, sin pedirla una y otra vez).
        """
        self._t_pedida = self._reloj()
        if despues is not None and espera > 0:
            limite = self._reloj() + espera
            with self._nueva:
                while (self._foto is None or self._foto["cuadro"] <= despues) and not self._parar.is_set():
                    restante = limite - self._reloj()
                    if restante <= 0:
                        break
                    self._t_pedida = self._reloj()
                    self._nueva.wait(min(restante, 0.5))
        foto = self._foto
        if foto is None or self._reloj() - self._t_cambio > SIN_CUADROS_S:
            return None
        return {**foto, "edad_ms": round((self._reloj() - foto["t"]) * 1000, 1)}
```

## `pgc/adaptadores/mano_ble.py`

```python
"""Mano por Bluetooth (BLE): las mismas órdenes y respuestas que por USB (código original), con token.

El ESP32-S3 solo tiene Bluetooth de bajo consumo (BLE), así que no aparece como puerto COM:
se usa el servicio "UART" de Nordic (lo que el PC escribe en RX le llega a la placa como
líneas; lo que la placa responde llega por notificaciones de TX). No hace falta emparejar.

PC → ESP32: "auth <token>" (primera línea), luego "<letra>" | "reset"
ESP32 → PC: "ok:auth" | "error:auth", luego "gesto_<letra>_ok" | "comando_no_reconocido" | "reset_ok"
Con 12 V conectados la mano funciona SOLO por Bluetooth (la PCB no admite USB y 12 V a la vez).

bleak es asíncrono: corre en su propio hilo con su bucle de asyncio, y aquí se le
piden las cosas de forma bloqueante (el Deletreador es un hilo normal).
"""
import asyncio
import threading
import time

from pgc.adaptadores.protocolo_mano import ORDEN_COMPROBAR, RESPUESTA_RESET, resultado

UART_RX = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"     # el PC escribe aquí
UART_TX = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"     # la placa notifica aquí
TAMANO_PAQUETE = 20                                  # sirve con cualquier MTU
TIEMPO_BUSQUEDA = 5.0
TIEMPO_CONEXION = 10.0


def _bleak_real():
    """bleak en un proceso aparte: WinRT y Whisper (ctranslate2) chocan en el mismo proceso."""
    from pgc.adaptadores.ble_puente import BleakRemoto
    return BleakRemoto()


def _motivo(ex):
    """Texto corto del error para el log (bleak lo da en inglés y a veces como tupla)."""
    if type(ex).__name__ == "BleakBluetoothNotAvailableError":
        return "el Bluetooth del PC está apagado: actívalo en Configuración > Bluetooth y dispositivos"
    texto = ex.args[0] if ex.args and isinstance(ex.args[0], str) else str(ex)
    if texto == "Not connected":
        return ("la mano cortó la conexión. Si la emparejaste en Windows, quítala de "
                "Configuración > Bluetooth y dispositivos > Dispositivos y reinicia la mano")
    return texto or type(ex).__name__


class ManoBLE:
    medio = "ble"

    def __init__(self, nombre="Mano-LSC", token="", timeout_letra=12.0, log=print, reintento=10.0,
                 tiempo_busqueda=TIEMPO_BUSQUEDA, reloj=time.monotonic, bleak=None):
        self.nombre = nombre
        self.token = token
        self.timeout_letra = timeout_letra
        self.tiempo_busqueda = tiempo_busqueda
        self.reintento = reintento
        self.log = log
        self._reloj = reloj
        self._bleak = bleak                   # None = el bleak instalado (se importa al conectar)
        self.letras = None
        self._cliente = None
        self._enlazada = False                # False en cuanto bleak avisa de la desconexión
        self._bucle = None
        self._hilo = None
        self._buffer = b""
        self._llegada = threading.Condition()
        self._proximo_intento = 0.0
        self._ultimo_aviso = None

    @property
    def conectada(self):
        return self._cliente is not None and self._enlazada

    @property
    def puerto(self):
        """Lo que muestra la pantalla: el nombre de la mano."""
        return self.nombre

    def puede_intentar(self):
        return self._reloj() >= self._proximo_intento

    def _avisar(self, texto):
        """Escribe en el log solo si cambió (la placa apagada no llena el log)."""
        if texto != self._ultimo_aviso:
            self._ultimo_aviso = texto
            self.log(texto)

    # ------------------------------------------------------- hilo de asyncio
    def _correr(self, corrutina, timeout):
        """Ejecuta una corrutina de bleak en su hilo y espera el resultado."""
        if self._bucle is None:
            self._bucle = asyncio.new_event_loop()
            self._hilo = threading.Thread(target=self._bucle.run_forever, daemon=True, name="mano-ble")
            self._hilo.start()
        return asyncio.run_coroutine_threadsafe(corrutina, self._bucle).result(timeout)

    def _al_notificar(self, _caracteristica, datos):
        with self._llegada:
            self._buffer += bytes(datos)
            self._llegada.notify_all()

    def _al_desconectar(self, _cliente):
        with self._llegada:
            self._enlazada = False
            self._llegada.notify_all()

    # --------------------------------------------------------------- conexión
    def conectar(self):
        self._proximo_intento = self._reloj() + self.reintento
        try:
            bleak = self._bleak or _bleak_real()
            dispositivo = self._correr(bleak.Escaner.find_device_by_name(self.nombre, timeout=self.tiempo_busqueda),
                                       self.tiempo_busqueda + 5)
            if dispositivo is None:
                raise RuntimeError("no se encontró (¿placa con 12 V? ¿Bluetooth del PC encendido?)")
            cliente = bleak.Cliente(dispositivo, disconnected_callback=self._al_desconectar)
            self._correr(cliente.connect(timeout=TIEMPO_CONEXION), TIEMPO_CONEXION + 5)
            self._cliente, self._enlazada, self._buffer = cliente, True, b""
            self._correr(cliente.start_notify(UART_TX, self._al_notificar), 10)
            resp = self._comando("auth " + self.token, lambda l: l in ("ok:auth", "error:auth"), 3.0)
            if resp != "ok:auth":
                raise RuntimeError("la mano rechazó el token (revisa TOKEN en config_ble.py)" if resp
                                   else "la mano no respondió al token")
            # Comprobación con "reset" (el firmware original no tiene "ping"); deja la mano abierta
            if not self._comando(ORDEN_COMPROBAR, lambda l: l == RESPUESTA_RESET, self.timeout_letra):
                raise RuntimeError("la mano no respondió a 'reset'")
            self.letras = None                    # el firmware no informa sus letras: se usan las por defecto
            self._ultimo_aviso = None
            self.log(f"[mano] Conectada por Bluetooth a {self.nombre}")
            return True
        except Exception as ex:
            self._avisar(f"[mano] Bluetooth: {self.nombre} no disponible ({_motivo(ex)})")
            self.cerrar()
            return False

    def cerrar(self):
        cliente, self._cliente = self._cliente, None
        self._enlazada = False
        if cliente is not None:
            try:
                self._correr(cliente.disconnect(), 5)
            except Exception:
                pass

    def _linea(self, limite):
        with self._llegada:
            while b"\n" not in self._buffer:
                if not self._enlazada:
                    raise ConnectionError("la mano se desconectó")
                if self._reloj() > limite:
                    return None
                self._llegada.wait(0.1)
            linea, self._buffer = self._buffer.split(b"\n", 1)
        return linea.decode("utf-8", "ignore").strip().lower()

    def _enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), TAMANO_PAQUETE):
            self._correr(self._cliente.write_gatt_char(UART_RX, datos[k:k + TAMANO_PAQUETE], response=True), 5)

    def _comando(self, cmd, condicion, timeout):
        self._enviar(cmd)
        limite = self._reloj() + timeout
        while True:
            linea = self._linea(limite)
            if linea is None:
                return None
            if condicion(linea):
                return linea
            if linea.startswith("error:"):
                self.log(f"[mano] {linea}")

    # ---------------------------------------------------------------- órdenes
    def hacer(self, letra):
        """Envía una letra (o 'reset') y espera su confirmación. True si la mano la hizo.

        Sin respuesta a tiempo se da la conexión por perdida (el firmware no tiene "ping"
        para comprobarla de otra forma); el respaldo y la reconexión siguen solos.
        """
        if not self.conectada:
            return False
        try:
            resp = self._comando(letra, lambda l: resultado(letra, l) is not None, self.timeout_letra)
            if resp is None:
                self.log(f"[mano] Sin confirmación para '{letra}' por Bluetooth (timeout): se da por perdida")
                self.cerrar()
                return False
            return resultado(letra, resp)
        except Exception as ex:
            self.log(f"[mano] Se perdió la conexión Bluetooth: {ex or type(ex).__name__}")
            self.cerrar()
            return False

    def latido(self):
        """Entre mensajes: revisa, SIN enviar nada, si la conexión sigue viva."""
        if self.conectada and getattr(self._cliente, "is_connected", True):
            return True
        if self._cliente is not None:
            self.log("[mano] Se perdió la conexión Bluetooth")
        self.cerrar()
        return False
```

## `pgc/adaptadores/mano_respaldo.py`

```python
"""Mano con respaldo: Bluetooth → USB → simulada (implementa PuertoMano).

Modos (PGC_MANO):
  auto     Bluetooth si está configurado y responde; si no, USB; si no, simulada.
  ble      solo Bluetooth (y simulada si no responde).
  usb      solo USB (y simulada si no responde).
  simulada nunca busca la mano.
Si el medio activo se cae, se pasa al siguiente sin perder la letra en curso.
Entre mensajes, `revisar()` manda un latido, vuelve a buscar la mano y, en modo
auto, vuelve al Bluetooth cuando reaparece. El modo se muestra siempre en el proyector.
"""
import threading
import time

from pgc.adaptadores.mano_simulada import TIEMPO_SIMULADO, ManoSimulada
from pgc.adaptadores.mano_usb import TIMEOUT_LETRA, VIDS_ESP32, ManoUSB

NOMBRES = {"ble": "Bluetooth", "usb": "USB"}


class Mano:
    def __init__(self, puerto=None, baudios=115200, simular=False, log=print, *,
                 timeout_letra=TIMEOUT_LETRA, vids=VIDS_ESP32, tiempo_simulado=TIEMPO_SIMULADO,
                 modulo_serial=None, dormir=time.sleep, reloj=time.time, modo="auto", ble=None):
        self.puerto_pedido = puerto
        self.modo_config = "simulada" if simular else modo
        self.log = log
        self.usb = ManoUSB(baudios, timeout_letra, vids, log, modulo_serial, dormir, reloj)
        self.ble = ble                        # ManoBLE o None (sin token configurado)
        self.simulada = ManoSimulada(tiempo_simulado, dormir=dormir)
        self.activo = None                    # ManoUSB o ManoBLE en uso
        self._letras = None                   # se conservan aunque la mano se desconecte
        self._puerto_fallido = None           # puerto USB que falló (no se reintenta hasta desenchufarlo)
        self._lock = threading.Lock()         # una orden a la vez

    # ------------------------------------------------------------------ estado
    @property
    def forzar_simulado(self):
        return self.modo_config == "simulada"

    @property
    def conectada(self):
        return self.activo is not None and self.activo.conectada

    @property
    def modo(self):
        return "real" if self.conectada else "simulada"

    @property
    def medio(self):
        return self.activo.medio if self.conectada else None

    @property
    def puerto(self):
        return self.activo.puerto if self.activo is not None else None

    @property
    def letras(self):
        return self._letras

    @letras.setter
    def letras(self, valor):
        self._letras = valor

    def _medios(self):
        if self.forzar_simulado:
            return []
        medios = ["ble"] if self.ble is not None and self.modo_config in ("auto", "ble") else []
        return medios + (["usb"] if self.modo_config in ("auto", "usb") else [])

    # --------------------------------------------------------------- conexión
    def _usar(self, medio):
        nuevo = self.ble if medio == "ble" else self.usb
        if self.activo is not None and self.activo is not nuevo:
            self.activo.cerrar()
        self.activo = nuevo
        if nuevo.letras:
            self._letras = nuevo.letras

    def _conectar(self, medio):
        if medio == "ble":
            ok = self.ble.conectar()
        else:
            if not self.usb.disponible:
                self.log("[mano] pyserial no está instalado -> modo simulado")
                return False
            puerto = self.puerto_pedido or self.usb.buscar_puerto()
            if not puerto:
                self.log("[mano] No se encontró el ESP32 -> modo simulado")
                self._puerto_fallido = None
                return False
            ok = self.usb.conectar(puerto)
            self._puerto_fallido = None if ok else puerto
        if ok:
            self._usar(medio)
        return ok

    def _respaldo(self, excluir):
        """Tras perder un medio, intenta los demás en orden. True si quedó conectada."""
        for medio in self._medios():
            if medio != excluir and self._conectar(medio):
                self.log(f"[mano] Respaldo: ahora por {NOMBRES[medio]}")
                return True
        return False

    def conectar(self):
        """Primera conexión (y la que pide el presentador con «Reconectar mano»)."""
        if self.forzar_simulado:
            return False
        if not self.usb.disponible and "ble" not in self._medios():
            self.log("[mano] pyserial no está instalado -> modo simulado")
            return False
        return any(self._conectar(medio) for medio in self._medios())

    def cerrar(self):
        if self.activo is not None:
            self.activo.cerrar()

    _cerrar = cerrar          # nombre antiguo

    def revisar(self):
        """Entre mensajes (cada ~3 s): latido, respaldo, regreso al Bluetooth y autodetección USB.

        Devuelve True si cambió la conexión (para avisar a las pantallas).
        """
        if self.forzar_simulado:
            return False
        with self._lock:
            antes = (self.conectada, self.medio)
            if self.conectada:
                medio = self.activo.medio
                if not self.activo.latido():
                    self.activo = None
                    self._respaldo(excluir=medio)
                elif medio == "usb" and "ble" in self._medios() and self.ble.puede_intentar():
                    if self.ble.conectar():                  # el Bluetooth volvió: se prefiere
                        self._usar("ble")
                        self.log("[mano] Cambio a Bluetooth")
            else:
                for medio in self._medios():
                    if medio == "ble":
                        if self.ble.puede_intentar() and self._conectar("ble"):
                            break
                        continue
                    puerto = self.puerto_pedido or self.usb.buscar_puerto()
                    if puerto is None:
                        self._puerto_fallido = None          # al volver a enchufarla, se reintenta
                    elif puerto != self._puerto_fallido:
                        self.log(f"[mano] Detectado {puerto}, conectando...")
                        if self._conectar("usb"):
                            break
            return antes != (self.conectada, self.medio)

    # ---------------------------------------------------------------- órdenes
    def hacer(self, letra):
        """Forma una letra (o 'reset'). Devuelve True si la mano confirmó."""
        with self._lock:
            if self.activo is not None and not self.activo.conectada:      # se cayó entre órdenes
                perdido, self.activo = self.activo.medio, None
                self._respaldo(excluir=perdido)
            if not self.conectada:
                return self.simulada.hacer(letra)
            ok = self.activo.hacer(letra)
            if not ok and not self.activo.conectada:                     # se cayó en esta orden
                perdido, self.activo = self.activo.medio, None
                if self._respaldo(excluir=perdido):
                    return self.activo.hacer(letra)                      # se repite por el respaldo
            return ok

    def reset(self):
        return self.hacer("reset")

    def latido(self):
        return self.activo.latido() if self.conectada else False
```

## `pgc/adaptadores/mano_simulada.py`

```python
"""Mano simulada: tarda lo mismo que una real y siempre confirma (para probar sin hardware)."""
import time

TIEMPO_SIMULADO = 1.2     # duración simulada de una letra
TIEMPO_RESET = 0.5


class ManoSimulada:
    def __init__(self, tiempo_letra=TIEMPO_SIMULADO, tiempo_reset=TIEMPO_RESET, dormir=time.sleep):
        self.tiempo_letra = tiempo_letra
        self.tiempo_reset = tiempo_reset
        self._dormir = dormir

    def hacer(self, orden):
        self._dormir(self.tiempo_letra if orden != "reset" else self.tiempo_reset)
        return True
```

## `pgc/adaptadores/mano_usb.py`

```python
"""Mano por USB serial: una línea por orden, con la respuesta del código original.

PC → ESP32: "<letra>\\n" | "reset\\n"
ESP32 → PC: "gesto_<letra>_ok" | "comando_no_reconocido" | "reset_ok"   (ver protocolo_mano.py)
Ojo: en la PCB de la mano no se pueden conectar USB y 12 V a la vez; por USB la
placa responde pero los servos no se mueven (sirve para pruebas sin fuerza).
"""
import time

from pgc.adaptadores.protocolo_mano import ORDEN_COMPROBAR, RESPUESTA_RESET, resultado

try:
    import serial
    import serial.tools.list_ports
except ImportError:  # pyserial no instalado
    serial = None

# VID USB típicos: 303A = Espressif (USB nativo del S3), 1A86 = CH340, 10C4 = CP210x
VIDS_ESP32 = frozenset({0x303A, 0x1A86, 0x10C4})
TIMEOUT_LETRA = 12.0      # segundos máximos esperando "ok:<letra>"


def buscar_puerto(vids=VIDS_ESP32, modulo_serial=None):
    s = serial if modulo_serial is None else modulo_serial
    if s is None:
        return None
    for p in list(s.tools.list_ports.comports()):
        if p.vid in vids:
            return p.device
    return None


class ManoUSB:
    medio = "usb"

    def __init__(self, baudios=115200, timeout_letra=TIMEOUT_LETRA, vids=VIDS_ESP32, log=print,
                 modulo_serial=None, dormir=time.sleep, reloj=time.time):
        self.baudios = baudios
        self.timeout_letra = timeout_letra
        self.vids = vids
        self.log = log
        self.serial = serial if modulo_serial is None else modulo_serial
        self._dormir = dormir
        self._reloj = reloj
        self.ser = None
        self.puerto = None
        self.letras = None          # el firmware original no informa sus letras

    @property
    def disponible(self):
        """pyserial está instalado."""
        return self.serial is not None

    @property
    def conectada(self):
        return self.ser is not None

    def buscar_puerto(self):
        return buscar_puerto(self.vids, self.serial)

    # --------------------------------------------------------------- conexión
    def conectar(self, puerto):
        """Abre `puerto` y comprueba que el firmware responde (con "reset" → "reset_ok")."""
        try:
            s = self.serial.Serial()
            s.port = puerto
            s.baudrate = self.baudios
            s.timeout = 0.2
            s.dtr = False          # evita reiniciar la placa al abrir el puerto
            s.rts = False
            s.open()
            self._dormir(0.3)
            s.reset_input_buffer()
            self.ser = s
            self.puerto = puerto
            if not self._comando_espera(ORDEN_COMPROBAR, lambda l: l == RESPUESTA_RESET, min(6.0, self.timeout_letra)):
                # Puede que el programa no esté corriendo: Ctrl-C Ctrl-D = soft reboot
                s.write(b"\x03\x04")
                self._dormir(4.0)                 # el firmware abre los 6 dedos al arrancar (~3 s)
                s.reset_input_buffer()
                if not self._comando_espera(ORDEN_COMPROBAR, lambda l: l == RESPUESTA_RESET, min(8.0, self.timeout_letra)):
                    raise RuntimeError("el ESP32 no responde (¿main.py cargado? ¿Thonny abierto?)")
            self.letras = None                    # el firmware no informa sus letras: se usan las por defecto
            self.log(f"[mano] Conectada por USB en {puerto}")
            return True
        except Exception as ex:
            self.log(f"[mano] Error conectando en {puerto}: {ex} -> modo simulado")
            self.cerrar()
            return False

    def cerrar(self):
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        self.ser = None

    def _leer_linea(self):
        raw = self.ser.readline()
        if not raw:
            return None
        return raw.decode("utf-8", "ignore").strip().lower()

    def _comando_espera(self, cmd, condicion, timeout):
        self.ser.write((cmd + "\n").encode())
        limite = self._reloj() + timeout
        while self._reloj() < limite:
            linea = self._leer_linea()
            if linea is None:
                continue
            if condicion(linea):
                return linea
            if linea.startswith("error:"):
                self.log(f"[mano] {linea}")
        return None

    # ---------------------------------------------------------------- órdenes
    def hacer(self, letra):
        """Envía una letra (o 'reset') y espera su confirmación. True si la mano la hizo."""
        try:
            resp = self._comando_espera(letra, lambda l: resultado(letra, l) is not None, self.timeout_letra)
            if resp is None:
                self.log(f"[mano] Sin confirmación para '{letra}' (timeout)")
                return False
            return resultado(letra, resp)
        except Exception as ex:
            self.log(f"[mano] Se perdió la conexión: {ex}")
            self.cerrar()
            return False

    def latido(self):
        """El firmware original no tiene "ping": entre mensajes no se le manda nada."""
        return self.conectada
```

## `pgc/adaptadores/protocolo_mano.py`

```python
"""Respuestas del firmware de la mano (el código ORIGINAL del autor), iguales por USB y Bluetooth.

Órdenes que manda el PC        Respuesta del firmware
  "<letra>"  (a..y disponibles) "gesto_<letra>_ok"   (antes hace reset_all(): abre la mano)
  "<letra>"  (no disponible)    "comando_no_reconocido"
  "reset"                       "reset_ok"
El firmware NO tiene "ping" ni "letras": una palabra de más de una letra la
deletrearía (p. ej. "ping" movería la mano). Por eso el PC comprueba la conexión
con "reset" y nunca manda palabras: siempre letra por letra.
"""
ORDEN_COMPROBAR = "reset"
RESPUESTA_RESET = "reset_ok"
NO_RECONOCIDO = "comando_no_reconocido"


def resultado(orden, linea):
    """True si `linea` confirma la orden, False si la rechaza, None si es otra cosa."""
    if orden == "reset":
        return True if linea == RESPUESTA_RESET else None
    if linea == f"gesto_{orden}_ok":
        return True
    if linea == NO_RECONOCIDO:
        return False
    return None
```

## `pgc/adaptadores/reconocedor_simulado.py`

```python
"""Reconocedor de señas simulado: emite los eventos de un texto, como lo haría el Kinect.

Sirve para construir y probar el modo Kinect, el modo eco y la pantalla antes de
que llegue el reconocedor real. No emite nada por sí solo: hay que llamar a
`simular("hola")`.
"""
import threading
import time

from pgc.puertos.reconocedor import EventoSena


class ReconocedorSimulado:
    def __init__(self, pausa=0.8, detalle="Kinect simulado"):
        self.estado = "apagado"
        self.detalle = detalle
        self.pausa = pausa
        self._al_evento = self._avisar = None
        self._parar = threading.Event()

    def iniciar(self, al_evento, al_cambiar_estado):
        self._al_evento, self._avisar = al_evento, al_cambiar_estado
        self._parar.clear()
        self._cambiar("sin_persona")

    def detener(self):
        self._parar.set()
        if self.estado != "apagado":
            self._cambiar("apagado")

    def _cambiar(self, estado):
        self.estado = estado
        if self._avisar:
            self._avisar()

    def simular(self, texto, esperar=False):
        """Emite letra por letra el texto (espacios incluidos) y al final 'fin'."""
        hilo = threading.Thread(target=self._emitir, args=(texto,), daemon=True, name="kinect-simulado")
        hilo.start()
        if esperar:
            hilo.join()

    def _emitir(self, texto):
        self._cambiar("listo")
        for c in texto.lower():
            if self._parar.is_set():
                return
            t0 = time.monotonic()
            if c == " ":
                evento = EventoSena("espacio")
            elif c.isalpha():
                evento = EventoSena("letra", letra=c, confianza=0.99, modelo="simulado", instante=t0)
            else:
                continue
            self._al_evento(evento)
            self._parar.wait(self.pausa)
        self._al_evento(EventoSena("fin"))
        self._cambiar("sin_persona")
```

## `pgc/adaptadores/voz_salida.py`

```python
"""Texto → voz con Coqui VITS en español (tts_models/es/css10/vits), por los parlantes del PC.

El modelo ya está en la caché (%LOCALAPPDATA%\\tts) y se carga en segundo plano
al arrancar, en CPU: una frase corta tarda menos de un segundo y así no compite
con Whisper por la GPU. Implementa el puerto pgc.puertos.sintetizador.Sintetizador.
"""
import threading
import time


class SintetizadorCoqui:
    def __init__(self, modelo="tts_models/es/css10/vits", log=print, al_cambiar=None):
        self.modelo = modelo
        self.log = log
        self.al_cambiar = al_cambiar or (lambda: None)
        self.estado = "sin cargar"     # sin cargar | cargando | listo | error | desactivado
        self._tts = None
        self._lock = threading.Lock()  # una frase a la vez

    def _cambiar(self, estado):
        self.estado = estado
        self.al_cambiar()

    def cargar_en_segundo_plano(self):
        threading.Thread(target=self.cargar, daemon=True, name="voz-salida-carga").start()

    def cargar(self):
        self._cambiar("cargando")
        t0 = time.time()
        try:
            from TTS.api import TTS
            tts = TTS(model_name=self.modelo, progress_bar=False).to("cpu")
            tts.tts(text="hola")                       # calentamiento
            self._tts = tts
            self.log(f"[voz] Voz de salida lista ({time.time() - t0:.1f} s)")
            self._cambiar("listo")
        except Exception as ex:
            self.log(f"[voz] No se pudo cargar la voz de salida: {type(ex).__name__}: {ex}")
            self._cambiar("error")

    def sintetizar(self, texto):
        """(muestras float32, frecuencia). Separado de decir() para probarlo sin parlantes."""
        import numpy as np
        if self._tts is None:
            raise RuntimeError("la voz de salida no está lista")
        with self._lock:
            muestras = np.asarray(self._tts.tts(text=texto), dtype=np.float32)
        return muestras, self._tts.synthesizer.output_sample_rate

    def decir(self, texto):
        if self._tts is None:
            self.log("[voz] La voz de salida no está lista; no se dice la frase")
            return
        import sounddevice as sd
        muestras, frecuencia = self.sintetizar(texto)
        sd.play(muestras, frecuencia)
        sd.wait()
```

## `pgc/adaptadores/whisper.py`

```python
"""Voz → texto con faster-whisper (español). Implementa el puerto Transcriptor.

El modelo se carga en segundo plano al iniciar el servidor. Primero intenta
CUDA float16 (con un calentamiento para detectar fallos de la RTX 5050 /
Blackwell sm_120 con ctranslate2); si algo falla, cae a CPU int8.
"""
import importlib.util
import os
import threading
import time

import numpy as np

MODELO = "medium"   # en la caché HF como Systran/faster-whisper-medium


def _agregar_dlls_cuda_de_torch():
    """ctranslate2 necesita cuBLAS/cuDNN; torch ya los trae en torch/lib."""
    spec = importlib.util.find_spec("torch")
    if not spec or not spec.submodule_search_locations:
        return
    lib = os.path.join(list(spec.submodule_search_locations)[0], "lib")
    if os.path.isdir(lib):
        try:
            os.add_dll_directory(lib)
        except (AttributeError, OSError):
            pass
        os.environ["PATH"] = lib + os.pathsep + os.environ.get("PATH", "")


class Transcriptor:
    def __init__(self, log=print, al_cambiar=None, nombre_modelo=MODELO, log_textos=False):
        self.log = log
        self.al_cambiar = al_cambiar or (lambda: None)
        self.nombre_modelo = nombre_modelo
        self.log_textos = log_textos   # False: la transcripción no queda en el log
        self.modelo = None
        self.estado = "sin cargar"     # sin cargar | cargando | listo | error | desactivado
        self.dispositivo = None        # "cuda float16" | "cpu int8"
        self._lock = threading.Lock()  # una transcripción a la vez

    @property
    def listo(self):
        return self.modelo is not None

    def _cambiar(self, estado):
        self.estado = estado
        self.al_cambiar()

    def cargar_en_segundo_plano(self):
        threading.Thread(target=self.cargar, daemon=True, name="whisper").start()

    def cargar(self):
        self._cambiar("cargando")
        try:
            from faster_whisper import WhisperModel
        except Exception as ex:
            self.log(f"[voz] faster-whisper no disponible: {ex}")
            self._cambiar("error")
            return
        _agregar_dlls_cuda_de_torch()
        for device, compute in (("cuda", "float16"), ("cpu", "int8")):
            t0 = time.time()
            try:
                modelo = self._crear(WhisperModel, device, compute)
                # Calentamiento: sin VAD para que el codificador corra de verdad
                ruido = (np.random.randn(16000) * 0.01).astype(np.float32)
                segs, _ = modelo.transcribe(ruido, language="es", vad_filter=False, beam_size=1)
                list(segs)
                self.modelo = modelo
                self.dispositivo = f"{device} {compute}"
                self.log(f"[voz] Whisper {self.nombre_modelo} listo en {self.dispositivo} ({time.time() - t0:.1f} s)")
                self._cambiar("listo")
                return
            except Exception as ex:
                self.log(f"[voz] Falló Whisper en {device} {compute}: {ex}")
        self._cambiar("error")

    def _crear(self, WhisperModel, device, compute):
        # Primero sin internet (el modelo ya está en la caché); si no, descarga
        try:
            return WhisperModel(self.nombre_modelo, device=device, compute_type=compute, local_files_only=True)
        except Exception:
            return WhisperModel(self.nombre_modelo, device=device, compute_type=compute)

    def transcribir(self, ruta_audio):
        """Devuelve el texto reconocido (puede ser cadena vacía)."""
        if not self.listo:
            raise RuntimeError("el modelo de voz aún no está listo")
        with self._lock:
            t0 = time.time()
            segs, _ = self.modelo.transcribe(
                ruta_audio, language="es", vad_filter=True, beam_size=5,
            )
            texto = " ".join(s.text.strip() for s in segs).strip()
            detalle = f"'{texto}'" if self.log_textos else f"{len(texto)} caracteres"
            self.log(f"[voz] Transcripción: {detalle} ({time.time() - t0:.1f} s)")
            return texto

    @staticmethod
    def duracion(ruta_audio):
        """Segundos de audio, o None si no se pudo leer (Whisper decidirá)."""
        try:
            import av
            with av.open(ruta_audio) as contenedor:
                if contenedor.duration:
                    return contenedor.duration / av.time_base
                pistas = [s for s in contenedor.streams if s.type == "audio" and s.duration and s.time_base]
                return float(pistas[0].duration * pistas[0].time_base) if pistas else None
        except Exception:
            return None
```

## `pgc/api/__init__.py`

```python
"""Capa web: FastAPI, rutas, esquemas y WebSocket. Solo habla con pgc.aplicacion."""
```

## `pgc/api/app.py`

```python
"""Aplicación FastAPI: ciclo de vida, seguridad, errores amables y rutas."""
import asyncio
import webbrowser
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from pgc.api.rutas import admin, kinect, mensajes, paginas, participantes, voz, ws
from pgc.api.seguridad import Limitador, MiddlewareSeguridad, es_admin, nuevo_token

TRADUCCIONES = {
    "Not Found": "No encontramos esa página.",
    "Method Not Allowed": "Esa acción no está permitida.",
}
CSP_DOCS = ("default-src 'none'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com; "
            "connect-src 'self'; frame-ancestors 'none'")


def mensaje_validacion(errores, cfg):
    """422 amable y en español según el campo que falló."""
    for e in errores:
        campo = e.get("loc", ("",))[-1]
        if campo == "texto":
            if "caracteres de control" in str(e.get("msg", "")):
                return "El mensaje tiene caracteres que no se pueden mostrar."
            return "Escribe tu mensaje de nuevo, por favor."
        if campo == "cliente":
            return "Recarga la página e intenta de nuevo."
        if campo == "codigo":
            return "Escribe el código de 6 dígitos que muestra el proyector."
        if campo == "nombre":
            return "Usa solo letras en tu nombre (máximo 20)."
        if campo == "audio":
            return "No llegó audio."
    return "No pudimos leer lo que enviaste. Recarga la página e intenta de nuevo."


def crear_app(sistema, abrir_navegador=webbrowser.open):
    cfg, log = sistema.cfg, sistema.log

    @asynccontextmanager
    async def ciclo_de_vida(app):
        sistema.loop = asyncio.get_running_loop()
        voz.limpiar_audios_viejos()
        sistema.iniciar_trabajador()
        if cfg.voz:
            sistema.voz.cargar_en_segundo_plano()
        else:
            sistema.voz.estado = "desactivado"
        if cfg.tunel:
            sistema.tunel.iniciar()
        sistema.voz_salida.cargar_en_segundo_plano()     # Coqui VITS: dice las frases del Kinect
        sistema.senas.iniciar()
        log(f"[web] Pantalla del proyector: http://127.0.0.1:{cfg.puerto_web}/pantalla")
        log(f"[web] Celulares en la misma red: {sistema.url_local}")
        if cfg.dev:
            log(f"[web] Modo desarrollo: documentación en http://127.0.0.1:{cfg.puerto_web}/docs")
        if cfg.abrir_navegador:
            abrir_navegador(f"http://127.0.0.1:{cfg.puerto_web}/pantalla")
        yield
        sistema.senas.detener()
        sistema.tunel.detener()

    # La documentación automática se sirve con rutas propias (solo --dev o con el token)
    app = FastAPI(lifespan=ciclo_de_vida, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.sistema = sistema
    app.state.token_admin = nuevo_token()       # solo en memoria; lo recibe /pantalla en el PC
    app.state.limitador = Limitador()
    app.state.voz_en_curso = 0
    app.state.ws_total = 0
    app.state.ws_por_ip = {}
    app.add_middleware(MiddlewareSeguridad, cfg=cfg, limitador=app.state.limitador)

    @app.exception_handler(RequestValidationError)
    async def validacion(request, exc):
        return JSONResponse({"detail": mensaje_validacion(exc.errors(), cfg)}, status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def http(request, exc):
        detalle = TRADUCCIONES.get(exc.detail, exc.detail)
        return JSONResponse({"detail": detalle}, status_code=exc.status_code, headers=exc.headers)

    def documentacion_permitida(request):
        return cfg.dev or es_admin(request, app.state.token_admin, permitir_parametro=True)

    @app.get("/openapi.json", include_in_schema=False)
    def openapi(request: Request):
        if not documentacion_permitida(request):
            raise StarletteHTTPException(404)
        return JSONResponse(app.openapi())

    @app.get("/docs", include_in_schema=False)
    def docs(request: Request):
        if not documentacion_permitida(request):
            raise StarletteHTTPException(404)
        token = request.query_params.get("token")
        url = "/openapi.json" + (f"?token={token}" if token and not cfg.dev else "")
        respuesta = get_swagger_ui_html(openapi_url=url, title="Mano bidireccional LSC · API")
        respuesta.headers["Content-Security-Policy"] = CSP_DOCS
        return respuesta

    for modulo in (paginas, mensajes, voz, participantes, admin, kinect, ws):
        app.include_router(modulo.router)
    return app
```

## `pgc/api/dependencias.py`

```python
"""Dependencias comunes de las rutas."""
from fastapi import Request

SIN_CACHE = {"Cache-Control": "no-store"}


def obtener_sistema(request: Request):
    return request.app.state.sistema
```

## `pgc/api/esquemas.py`

```python
"""Modelos de entrada de la API (pydantic)."""
import unicodedata
from typing import Literal

from pydantic import BaseModel, Field, field_validator

PATRON_CLIENTE = r"^[A-Za-z0-9_-]{1,64}$"     # id aleatorio que genera la página del celular
PERMITIDOS = {"\n", "\r", "\t"}               # el cuadro de texto admite saltos de línea


def sin_caracteres_de_control(texto: str) -> str:
    if any(unicodedata.category(c) == "Cc" and c not in PERMITIDOS for c in texto):
        raise ValueError("caracteres de control")
    return texto


class Texto(BaseModel):
    texto: str
    cliente: str = Field(default="anonimo", pattern=PATRON_CLIENTE)

    _validar_texto = field_validator("texto")(sin_caracteres_de_control)


class Cliente(BaseModel):
    cliente: str = Field(pattern=PATRON_CLIENTE)


class TomarTurno(BaseModel):
    cliente: str = Field(pattern=PATRON_CLIENTE)
    codigo: str | None = Field(default=None, max_length=12)    # el del proyector (con PGC_KINECT_CODIGO=true)


class ControlKinect(BaseModel):
    accion: Literal["iniciar", "detener", "espacio", "borrar", "limpiar", "terminar"]
    cliente: str | None = Field(default=None, pattern=PATRON_CLIENTE)    # None = el presentador (con token)


class Eco(BaseModel):
    activo: bool
    cliente: str | None = Field(default=None, pattern=PATRON_CLIENTE)    # None = el presentador (con token)


class Protocolo(BaseModel):
    letras: str | None = Field(default=None, pattern=r"^[a-zñ ,]{1,120}$")   # None = todas las del modelo
    repeticiones: int = Field(default=5, ge=1, le=20)
    tiempo_max: float = Field(default=8.0, ge=2.0, le=30.0)


class Participante(BaseModel):
    cliente: str = Field(pattern=PATRON_CLIENTE)
    nombre: str | None = Field(default=None, max_length=60)    # se normaliza a 20 caracteres

    @field_validator("nombre")
    @classmethod
    def _validar_nombre(cls, valor):
        return None if valor is None else sin_caracteres_de_control(valor)
```

## `pgc/api/rutas/__init__.py`

```python
"""Rutas HTTP y WebSocket, agrupadas por tema."""
```

## `pgc/api/rutas/admin.py`

```python
"""Controles del presentador: solo desde el PC del proyector y con el token de administrador."""
from fastapi import APIRouter, Depends, HTTPException

from pgc.api.dependencias import obtener_sistema
from pgc.api.seguridad import verificar_admin

router = APIRouter(dependencies=[Depends(verificar_admin)])


@router.post("/api/mano/reconectar")
def reconectar(sistema=Depends(obtener_sistema)):
    sistema.reconectar_mano()
    return {"ok": True}


@router.post("/api/mano/saltar")
def saltar(sistema=Depends(obtener_sistema)):
    if not sistema.saltar_actual():
        raise HTTPException(404, "No hay ningún mensaje en curso.")
    return {"ok": True}
```

## `pgc/api/rutas/kinect.py`

```python
"""Kinect: turno (un jurado a la vez), controles del deletreo, modo eco e imagen de la cámara.

El estado del Kinect (texto en vivo, detector, turno) NO tiene rutas para
consultar: llega a todos por el WebSocket. Aquí solo hay órdenes.
"""
import json
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from pgc.api.dependencias import SIN_CACHE, obtener_sistema
from pgc.api.esquemas import Cliente, ControlKinect, Eco, Protocolo, TomarTurno
from pgc.api.seguridad import es_admin, ip_real, limitar, verificar_admin
from pgc.aplicacion.senas import SinControles
from pgc.aplicacion.sistema import ParticipanteBloqueado, SinPermisoKinect
from pgc.aplicacion.turno import CodigoIncorrecto, TurnoOcupado

router = APIRouter()


@router.post("/api/kinect/turno")
def tomar_turno(datos: TomarTurno, request: Request, sistema=Depends(obtener_sistema)):
    limitar(request, "kinect", datos.cliente, sistema.cfg.lim_kinect_cliente)
    # Adivinar el código: 1 entre un millón y, por IP, unos 30 intentos por minuto
    limitar(request, "kinect-turno-ip", ip_real(request), 30)
    try:
        sistema.tomar_turno_kinect(datos.cliente, datos.codigo)
    except (ParticipanteBloqueado, CodigoIncorrecto) as ex:
        raise HTTPException(403, str(ex))
    except TurnoOcupado as ex:
        raise HTTPException(409, str(ex))
    return {"ok": True}


@router.post("/api/kinect/turno/soltar")
def soltar_turno(datos: Cliente, sistema=Depends(obtener_sistema)):
    sistema.soltar_turno_kinect(datos.cliente)
    return {"ok": True}


@router.post("/api/kinect/control")
def controlar(datos: ControlKinect, request: Request, sistema=Depends(obtener_sistema)):
    presentador = es_admin(request, request.app.state.token_admin)
    if not presentador:
        limitar(request, "kinect-ip", ip_real(request), sistema.cfg.lim_kinect_cliente * 2)
        if datos.cliente:
            limitar(request, "kinect", datos.cliente, sistema.cfg.lim_kinect_cliente)
    try:
        sistema.controlar_kinect(datos.accion, datos.cliente, presentador=presentador)
    except (SinPermisoKinect, ParticipanteBloqueado) as ex:
        raise HTTPException(403, str(ex))
    except SinControles as ex:
        raise HTTPException(409, str(ex))
    except RuntimeError as ex:                 # el detector no responde o rechazó la orden
        raise HTTPException(503, str(ex))
    return {"ok": True}


# ----------------------------------------------------------------- solo el presentador
@router.post("/api/kinect/liberar", dependencies=[Depends(verificar_admin)])
def liberar_turno(sistema=Depends(obtener_sistema)):
    sistema.liberar_turno_kinect()
    return {"ok": True}


@router.get("/api/kinect/codigo", dependencies=[Depends(verificar_admin)])
def ver_codigo(sistema=Depends(obtener_sistema)):
    """El código para tomar el turno: solo el proyector lo recibe (con el token), nunca por el WebSocket."""
    turno = sistema.senas.turno
    return Response(json.dumps({"activo": turno.con_codigo, "codigo": turno.codigo,
                                "version": turno.version_codigo}), media_type="application/json", headers=SIN_CACHE)


@router.post("/api/kinect/codigo", dependencies=[Depends(verificar_admin)])
def regenerar_codigo(sistema=Depends(obtener_sistema)):
    if not sistema.senas.turno.con_codigo:
        raise HTTPException(409, "El código está desactivado (PGC_KINECT_CODIGO=false).")
    codigo = sistema.regenerar_codigo_kinect()
    return Response(json.dumps({"activo": True, "codigo": codigo, "version": sistema.senas.turno.version_codigo}),
                    media_type="application/json", headers=SIN_CACHE)


@router.post("/api/kinect/eco")
def eco(datos: Eco, request: Request, sistema=Depends(obtener_sistema)):
    """El presentador (PC con token) o el celular que tiene el turno del Kinect."""
    presentador = es_admin(request, request.app.state.token_admin)
    if not presentador and datos.cliente:
        limitar(request, "kinect", datos.cliente, sistema.cfg.lim_kinect_cliente)
    try:
        sistema.fijar_eco(datos.activo, datos.cliente, presentador=presentador)
    except (SinPermisoKinect, ParticipanteBloqueado) as ex:
        raise HTTPException(403, str(ex))
    return {"eco": sistema.eco}


@router.get("/api/kinect/diagnostico", dependencies=[Depends(verificar_admin)])
def diagnostico(sistema=Depends(obtener_sistema)):
    """Por qué una letra se confirma o no, en vivo. Solo en el PC (como la cámara)."""
    datos = sistema.senas.diagnostico()
    if datos is None:
        raise HTTPException(503, "El detector no da diagnóstico (¿Kinect no conectado, o el detector original "
                                 "con PGC_KINECT_DETECTOR_PARALELO=false?).")
    return Response(json.dumps(datos, ensure_ascii=False), media_type="application/json", headers=SIN_CACHE)


@router.post("/api/kinect/protocolo/iniciar", dependencies=[Depends(verificar_admin)])
def iniciar_protocolo(datos: Protocolo, sistema=Depends(obtener_sistema)):
    diag = sistema.senas.diagnostico() or {}
    del_modelo = [c for c in diag.get("categorias", []) if c != "sin_letra"]
    letras = [l for l in (datos.letras or "").replace(",", " ").split() if l] or del_modelo
    fuera = [l for l in letras if del_modelo and l not in del_modelo]
    if not letras or fuera:
        raise HTTPException(400, f"Letras que el modelo no tiene: {', '.join(fuera)}" if fuera else
                                 "No hay letras para probar (¿Kinect no conectado?).")
    try:
        sistema.protocolo.iniciar(letras, datos.repeticiones, datos.tiempo_max)
    except RuntimeError as ex:
        raise HTTPException(409, str(ex))
    return sistema.protocolo.estado()


@router.post("/api/kinect/protocolo/detener", dependencies=[Depends(verificar_admin)])
def detener_protocolo(sistema=Depends(obtener_sistema)):
    sistema.protocolo.detener()
    return {"ok": True}


@router.get("/api/kinect/protocolo", dependencies=[Depends(verificar_admin)])
def estado_protocolo(sistema=Depends(obtener_sistema)):
    return Response(json.dumps(sistema.protocolo.estado(), ensure_ascii=False), media_type="application/json",
                    headers=SIN_CACHE)


@router.get("/api/kinect/imagen", dependencies=[Depends(verificar_admin)])
def imagen(despues: int | None = Query(default=None, ge=0), sistema=Depends(obtener_sistema)):
    """La cámara con los puntos de la mano: solo en el PC del proyector, nunca por el túnel ni la red.

    ?despues=N: responde apenas haya un cuadro más nuevo que N (o tras 1 s con el último).
    """
    foto = sistema.senas.imagen_con_estado(despues, 1.0 if despues is not None else 0.0)
    if not foto:
        raise HTTPException(503, "No llegan imágenes del Kinect.")
    # El estado del MISMO momento que la imagen, para que el proyector los muestre juntos
    cabeceras = {**SIN_CACHE, "X-Kinect-Texto": quote(foto.get("texto") or ""),
                 "X-Kinect-Detalle": quote(foto.get("detalle") or "")}
    for clave, nombre in (("cuadro", "X-Kinect-Cuadro"), ("edad_ms", "X-Kinect-Edad-Ms"),
                          ("desfase_ms", "X-Kinect-Desfase-Ms")):
        if foto.get(clave) is not None:
            cabeceras[nombre] = str(foto[clave])
    return Response(foto["jpeg"], media_type="image/jpeg", headers=cabeceras)
```

## `pgc/api/rutas/mensajes.py`

```python
"""Mensajes de los jurados: vista previa, enviar y cancelar."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from pgc.api.dependencias import obtener_sistema
from pgc.api.esquemas import PATRON_CLIENTE, Texto
from pgc.api.seguridad import ip_real, limitar
from pgc.aplicacion.sistema import ParticipanteBloqueado
from pgc.dominio.texto import a_secuencia

router = APIRouter()


def revisar_largo(datos, cfg):
    """Más de texto_max_cuerpo: 422 (no es algo que la página envíe)."""
    if len(datos.texto) > cfg.texto_max_cuerpo:
        raise HTTPException(422, f"El mensaje es muy largo (máximo {cfg.max_caracteres} caracteres).")


@router.post("/api/previa")
def previa(datos: Texto, request: Request, sistema=Depends(obtener_sistema)):
    limitar(request, "previa", ip_real(request), sistema.cfg.lim_previa_ip)
    revisar_largo(datos, sistema.cfg)
    pasos = a_secuencia(datos.texto, sistema.mano.letras, sistema.cfg.max_caracteres)
    return {"pasos": [{"c": p["c"], "tipo": p["tipo"]} for p in pasos]}


@router.post("/api/mensaje")
def nuevo_mensaje(datos: Texto, request: Request, sistema=Depends(obtener_sistema)):
    cfg = sistema.cfg
    limitar(request, "mensaje", ip_real(request), cfg.lim_mensaje_ip)
    limitar(request, "mensaje-cliente", datos.cliente, cfg.lim_mensaje_cliente)
    revisar_largo(datos, cfg)
    if len(datos.texto.strip()) > cfg.max_caracteres:
        raise HTTPException(400, f"Máximo {cfg.max_caracteres} caracteres.")
    try:
        msg = sistema.encolar(datos.texto, datos.cliente)
    except ParticipanteBloqueado as ex:
        raise HTTPException(403, str(ex))
    except ValueError as ex:
        raise HTTPException(400, str(ex))
    return {"id": msg["id"], "texto": msg["texto"], "nombre": msg["nombre"], "sesion": sistema.sesion}


@router.delete("/api/mensaje/{id_msg}")
def cancelar(id_msg: int, cliente: str = Query(pattern=PATRON_CLIENTE), sistema=Depends(obtener_sistema)):
    if not sistema.cancelar(id_msg, cliente):
        raise HTTPException(404, "Ese mensaje ya no se puede cancelar.")
    return {"ok": True}
```

## `pgc/api/rutas/paginas.py`

```python
"""Páginas (celular y proyector), logo, QR y estado."""
import io
from pathlib import Path

import qrcode
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

from pgc.api.dependencias import SIN_CACHE, obtener_sistema
from pgc.api.seguridad import es_local, preparar_pagina

CARPETA_WEB = Path(__file__).resolve().parent.parent.parent.parent / "web"

router = APIRouter()


def pagina(nombre, request, con_token=False):
    token = request.app.state.token_admin if con_token and es_local(request) else None
    html, csp = preparar_pagina(CARPETA_WEB / nombre, request, token)
    return HTMLResponse(html, headers={**SIN_CACHE, "Content-Security-Policy": csp})


@router.get("/")
def pagina_movil(request: Request):
    return pagina("movil.html", request)


@router.get("/pantalla")
def pagina_pantalla(request: Request):
    # Solo el navegador del PC recibe el token: por el túnel o la red local se ve sin controles
    return pagina("pantalla.html", request, con_token=True)


@router.get("/diagnostico")
def pagina_diagnostico(request: Request):
    # Vista de diagnóstico del Kinect: solo el navegador del PC recibe el token (por el túnel no funciona)
    return pagina("diagnostico.html", request, con_token=True)


@router.get("/logo-udec.png")
def logo():
    return FileResponse(CARPETA_WEB / "logo-udec.png")


@router.get("/qr.png")
def qr(sistema=Depends(obtener_sistema)):
    img = qrcode.make(sistema.url_publica, border=2, box_size=12)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png", headers=SIN_CACHE)


@router.get("/api/estado")
def estado(sistema=Depends(obtener_sistema)):
    return sistema.instantanea()
```

## `pgc/api/rutas/participantes.py`

```python
"""Participantes: nombre opcional (celular) y bloqueo por sesión (presentador)."""
from fastapi import APIRouter, Depends, HTTPException, Request

from pgc.api.dependencias import obtener_sistema
from pgc.api.esquemas import Participante
from pgc.api.seguridad import ip_real, limitar, verificar_admin

router = APIRouter()
NO_EXISTE = "No encontramos a ese participante."


@router.post("/api/participante")
def registrar(datos: Participante, request: Request, sistema=Depends(obtener_sistema)):
    """Lo llama el celular al abrir la página y al cambiar el nombre. Devuelve su alias (pid)."""
    limitar(request, "participante", ip_real(request), sistema.cfg.lim_mensaje_ip)
    try:
        return sistema.registrar_participante(datos.cliente, datos.nombre)
    except ValueError as ex:
        raise HTTPException(400, str(ex))


@router.post("/api/participantes/{pid}/bloquear", dependencies=[Depends(verificar_admin)])
def bloquear(pid: str, sistema=Depends(obtener_sistema)):
    resultado = sistema.bloquear(pid)
    if resultado is None:
        raise HTTPException(404, NO_EXISTE)
    return {"ok": True, **resultado}


@router.post("/api/participantes/{pid}/desbloquear", dependencies=[Depends(verificar_admin)])
def desbloquear(pid: str, sistema=Depends(obtener_sistema)):
    if not sistema.desbloquear(pid):
        raise HTTPException(404, NO_EXISTE)
    return {"ok": True}
```

## `pgc/api/rutas/voz.py`

```python
"""Voz → texto: el celular sube un audio y recibe la transcripción para revisarla."""
import os
import re
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool

from pgc.api.dependencias import obtener_sistema
from pgc.api.esquemas import PATRON_CLIENTE
from pgc.api.seguridad import MSG_AUDIO_LARGO, ip_real, limitar, parece_audio, tipo_permitido
from pgc.dominio.participante import MSG_BLOQUEADO

CARPETA_AUDIOS = Path(tempfile.gettempdir()) / "pgc_voz"     # temporales: se borran siempre

router = APIRouter()


def limpiar_audios_viejos():
    """Borra temporales que hayan quedado de una caída del servidor."""
    for ruta in CARPETA_AUDIOS.glob("voz_*"):
        try:
            ruta.unlink()
        except OSError:
            pass


@router.post("/api/transcribir")
async def transcribir(request: Request, audio: UploadFile = File(...), cliente: str | None = Form(None),
                      sistema=Depends(obtener_sistema)):
    cfg, estado = sistema.cfg, request.app.state
    limitar(request, "transcribir", ip_real(request), cfg.lim_transcribir_ip)
    if cliente and re.fullmatch(PATRON_CLIENTE, cliente):
        limitar(request, "transcribir-cliente", cliente, cfg.lim_transcribir_cliente)
        if sistema.esta_bloqueado(cliente):
            raise HTTPException(403, MSG_BLOQUEADO)
    if not sistema.voz.listo:
        raise HTTPException(503, "El reconocimiento de voz se está cargando, intenta en unos segundos.")
    if estado.voz_en_curso > cfg.voz_max_en_espera:                  # 1 transcribiendo + N esperando
        raise HTTPException(429, "Hay varias personas usando la voz, intenta en unos segundos.",
                            headers={"Retry-After": "5"})
    estado.voz_en_curso += 1
    try:
        return await _transcribir(audio, sistema)
    finally:
        estado.voz_en_curso -= 1


async def _transcribir(audio, sistema):
    cfg = sistema.cfg
    datos = await audio.read()                    # acotado: el middleware ya limitó el cuerpo
    if not datos:
        raise HTTPException(400, "No llegó audio.")
    if len(datos) > cfg.audio_max_bytes:
        raise HTTPException(413, MSG_AUDIO_LARGO)
    if not tipo_permitido(audio.content_type) or not parece_audio(datos[:16]):
        raise HTTPException(415, "Ese archivo no parece un audio. Graba de nuevo con el botón.")
    sufijo = Path(audio.filename or "").suffix.lower()
    sufijo = sufijo if re.fullmatch(r"\.[a-z0-9]{1,5}", sufijo) else ".webm"
    CARPETA_AUDIOS.mkdir(parents=True, exist_ok=True)
    fd, ruta = tempfile.mkstemp(suffix=sufijo, prefix="voz_", dir=CARPETA_AUDIOS)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(datos)
        segundos = await run_in_threadpool(sistema.voz.duracion, ruta)
        if segundos and segundos > cfg.audio_max_segundos:
            raise HTTPException(413, MSG_AUDIO_LARGO)
        texto = await run_in_threadpool(sistema.voz.transcribir, ruta)
    except HTTPException:
        raise
    except Exception as ex:
        sistema.log(f"[voz] Error transcribiendo: {type(ex).__name__}")
        raise HTTPException(500, "No se pudo entender el audio. Intenta de nuevo o escríbelo.")
    finally:
        try:
            os.remove(ruta)                       # el audio nunca se guarda
        except OSError:
            pass
    return {"texto": texto[:cfg.max_caracteres]}
```

## `pgc/api/rutas/ws.py`

```python
"""Estado en vivo por WebSocket (pantalla del proyector y celulares)."""
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pgc.api.seguridad import es_local, ip_real

router = APIRouter()


def origen_permitido(ws: WebSocket, sistema):
    """Solo páginas servidas por este mismo servidor (evita que otro sitio se conecte)."""
    origen = ws.headers.get("origin")
    if origen is None:                     # clientes que no son navegadores (scripts de prueba)
        return True
    host = ws.headers.get("host", "")
    puerto = sistema.cfg.puerto_web
    permitidos = {sistema.tunel.url, sistema.url_local, f"http://127.0.0.1:{puerto}", f"http://localhost:{puerto}",
                  f"http://{host}", f"https://{host}"}
    return origen.rstrip("/") in permitidos


@router.websocket("/ws")
async def ws_estado(ws: WebSocket):
    sistema, estado = ws.app.state.sistema, ws.app.state
    cfg = sistema.cfg
    if not origen_permitido(ws, sistema):
        await ws.close(code=1008)          # política: origen no permitido
        return
    ip = ip_real(ws)
    if not es_local(ws) and (estado.ws_total >= cfg.ws_max_conexiones
                             or estado.ws_por_ip.get(ip, 0) >= cfg.ws_max_por_ip):
        await ws.close(code=1013)          # vuelva a intentar más tarde
        return
    estado.ws_total += 1
    estado.ws_por_ip[ip] = estado.ws_por_ip.get(ip, 0) + 1
    try:
        await ws.accept()
        q = sistema.publicador.suscribir()
        try:
            await ws.send_json(sistema.instantanea())
            while True:
                try:
                    datos = await asyncio.wait_for(q.get(), timeout=cfg.ping_ws)
                except asyncio.TimeoutError:
                    datos = {"tipo": "ping"}     # mantiene vivo el túnel y detecta cierres
                await ws.send_json(datos)
        except (WebSocketDisconnect, RuntimeError, ConnectionError):
            pass
        finally:
            sistema.publicador.desuscribir(q)
    finally:
        estado.ws_total -= 1
        estado.ws_por_ip[ip] -= 1
        if not estado.ws_por_ip[ip]:
            del estado.ws_por_ip[ip]
```

## `pgc/api/seguridad.py`

```python
"""Seguridad de la capa web (ver docs/ARQUITECTURA.md §B).

- es_local / ip_real: distinguir el PC del proyector de los celulares y del túnel.
- Token de administrador por arranque (M1).
- Límite de peticiones por IP real y por cliente (M5).
- Páginas con nonce para la CSP y encabezados de seguridad (M7).
- Tamaño máximo del cuerpo antes de leerlo (M3, M4).
"""
import math
import re
import secrets
import threading
import time
from pathlib import Path

from fastapi import HTTPException
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse

ENCABEZADOS_PROXY = ("cf-connecting-ip", "cf-ray", "cf-visitor", "cdn-loop", "x-forwarded-for", "forwarded", "x-real-ip")
IPS_LOCALES = {"127.0.0.1", "::1"}
NOMBRES_LOCALES = {"127.0.0.1", "localhost", "[::1]"}
MSG_ADMIN = "Solo desde el PC del proyector."
MSG_RAPIDO = "Vas muy rápido, espera unos segundos."
MSG_AUDIO_LARGO = "El audio es muy largo. Graba máximo 10 segundos."
MSG_CUERPO_LARGO = "El mensaje es muy largo."
ENCABEZADOS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "x-frame-options": "DENY",
    "permissions-policy": "microphone=(self), camera=(), geolocation=()",
    "cross-origin-opener-policy": "same-origin",
}
CSP_POR_DEFECTO = "default-src 'none'; frame-ancestors 'none'"


# ----------------------------------------------------------------- origen
def _nombre_host(host):
    host = (host or "").strip().lower()
    if host.startswith("["):
        return host.split("]")[0] + "]"
    return host.split(":")[0]


def es_local(conn: HTTPConnection):
    """Petición del propio PC: IP local, sin pasar por un proxy (cloudflared) y con Host local.

    cloudflared se conecta desde 127.0.0.1, por eso no basta con la IP. Exigir un
    Host local frena además el 'DNS rebinding' (un dominio ajeno que resuelve a 127.0.0.1).
    """
    if not conn.client or conn.client.host not in IPS_LOCALES:
        return False
    if any(h in conn.headers for h in ENCABEZADOS_PROXY):
        return False
    return _nombre_host(conn.headers.get("host")) in NOMBRES_LOCALES


def ip_real(conn: HTTPConnection):
    """IP del celular. CF-Connecting-IP solo se cree si la conexión viene de cloudflared (127.0.0.1)."""
    host = conn.client.host if conn.client else "desconocida"
    if host in IPS_LOCALES and "cf-connecting-ip" in conn.headers:
        return conn.headers["cf-connecting-ip"][:64]
    return host


# ----------------------------------------------------------------- administrador
def nuevo_token():
    return secrets.token_urlsafe(32)


def es_admin(conn: HTTPConnection, token, permitir_parametro=False):
    """PC del proyector + token correcto (encabezado X-PGC-Admin; ?token= solo si se permite)."""
    if not es_local(conn):
        return False
    recibido = conn.headers.get("x-pgc-admin", "")
    if not recibido and permitir_parametro:
        recibido = conn.query_params.get("token", "")
    return bool(recibido) and secrets.compare_digest(recibido, token)


def verificar_admin(conn: HTTPConnection):
    if not es_admin(conn, conn.app.state.token_admin):
        raise HTTPException(403, MSG_ADMIN)


# ----------------------------------------------------------------- límite de peticiones
class Limitador:
    """Cubeta de fichas en memoria: `por_minuto` peticiones, que se recargan de forma continua."""

    def __init__(self, reloj=time.monotonic):
        self._reloj = reloj
        self._cubetas = {}
        self._lock = threading.Lock()

    def esperar(self, clave, por_minuto):
        """0 si se permite (y consume una ficha); si no, segundos que faltan."""
        ahora = self._reloj()
        ritmo = por_minuto / 60.0
        with self._lock:
            fichas, antes = self._cubetas.get(clave, (float(por_minuto), ahora))
            fichas = min(float(por_minuto), fichas + (ahora - antes) * ritmo)
            if fichas >= 1:
                self._cubetas[clave] = (fichas - 1, ahora)
                return 0.0
            self._cubetas[clave] = (fichas, ahora)
            if len(self._cubetas) > 5000:          # no crecer sin límite con IPs de paso
                viejas = [k for k, (_, t) in self._cubetas.items() if ahora - t > 120]
                for k in viejas:
                    del self._cubetas[k]
            return (1 - fichas) / ritmo


def limitar(conn: HTTPConnection, nombre, clave, por_minuto):
    """Lanza 429 si `clave` superó `por_minuto`. El PC del proyector no tiene límite."""
    if es_local(conn):
        return
    espera = conn.app.state.limitador.esperar(f"{nombre}:{clave}", por_minuto)
    if espera:
        raise HTTPException(429, MSG_RAPIDO, headers={"Retry-After": str(max(1, math.ceil(espera)))})


# ----------------------------------------------------------------- páginas y CSP
_HOST_SEGURO = re.compile(r"^[A-Za-z0-9.\-:\[\]]{1,255}$")


def csp_pagina(nonce, host):
    host = host if _HOST_SEGURO.match(host or "") else ""
    conectar = f"'self' ws://{host} wss://{host}" if host else "'self'"
    return ("default-src 'none'; "
            f"script-src 'nonce-{nonce}'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            f"connect-src {conectar}; "
            "media-src 'self' blob:; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")


def preparar_pagina(ruta: Path, conn: HTTPConnection, token=None):
    """HTML con nonce en cada <script> y, si corresponde, el token de administrador."""
    nonce = secrets.token_urlsafe(16)
    html = ruta.read_text(encoding="utf-8").replace("<script>", f'<script nonce="{nonce}">')
    if token:
        html = html.replace('<meta name="pgc-admin" content="">', f'<meta name="pgc-admin" content="{token}">')
    return html, csp_pagina(nonce, conn.headers.get("host", ""))


# ----------------------------------------------------------------- audio
TIPOS_AUDIO = ("audio/", "video/webm", "video/mp4", "video/3gpp", "application/octet-stream", "")


def tipo_permitido(content_type):
    tipo = (content_type or "").split(";")[0].strip().lower()
    return any(tipo.startswith(t) for t in TIPOS_AUDIO if t) or tipo == ""


def parece_audio(cabecera: bytes):
    """Firma de los formatos que graban los celulares (webm, mp4/m4a/3gp, ogg, wav, mp3, aac, amr, flac)."""
    c = cabecera
    return (c.startswith(b"\x1a\x45\xdf\xa3")                       # EBML: webm / mkv
            or c[4:8] == b"ftyp"                                    # mp4, m4a, 3gp
            or c.startswith(b"OggS")
            or (c.startswith(b"RIFF") and c[8:12] == b"WAVE")
            or c.startswith(b"ID3")                                 # mp3 con etiquetas
            or (len(c) > 1 and c[0] == 0xFF and (c[1] & 0xE0) == 0xE0)   # trama MPEG / AAC ADTS
            or c.startswith(b"#!AMR")
            or c.startswith(b"fLaC"))


# ----------------------------------------------------------------- middleware
class MiddlewareSeguridad:
    """ASGI: límite general por IP, tamaño máximo del cuerpo y encabezados de seguridad."""

    def __init__(self, app, cfg, limitador):
        self.app = app
        self.cfg = cfg
        self.limitador = limitador
        self.max_json = cfg.json_max_kb * 1024
        self.max_audio = cfg.audio_max_bytes + 64 * 1024      # margen del formulario multipart

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        async def enviar(evento):
            if evento["type"] == "http.response.start":
                encabezados = list(evento.get("headers", []))
                presentes = {k.decode().lower() for k, _ in encabezados}
                for k, v in ENCABEZADOS.items():
                    if k not in presentes:
                        encabezados.append((k.encode(), v.encode()))
                if "content-security-policy" not in presentes:
                    encabezados.append((b"content-security-policy", CSP_POR_DEFECTO.encode()))
                evento = {**evento, "headers": encabezados}
            await send(evento)

        conn = HTTPConnection(scope)
        if not es_local(conn):
            espera = self.limitador.esperar(f"general:{ip_real(conn)}", self.cfg.lim_general_ip)
            if espera:
                return await self._responder(scope, receive, enviar, 429, MSG_RAPIDO,
                                             {"Retry-After": str(max(1, math.ceil(espera)))})
        es_audio = scope["path"] == "/api/transcribir"
        limite = self.max_audio if es_audio else self.max_json
        mensaje = MSG_AUDIO_LARGO if es_audio else MSG_CUERPO_LARGO
        largo = conn.headers.get("content-length")
        if largo and largo.isdigit() and int(largo) > limite:
            return await self._responder(scope, receive, enviar, 413, mensaje)

        recibido = 0

        async def recibir():
            nonlocal recibido
            evento = await receive()
            if evento["type"] == "http.request":
                recibido += len(evento.get("body", b""))
                if recibido > limite:                              # sin Content-Length o mintiendo
                    # HTTPException: FastAPI la deja pasar aunque ocurra al leer el cuerpo
                    raise HTTPException(413, mensaje)
            return evento

        await self.app(scope, recibir, enviar)

    @staticmethod
    async def _responder(scope, receive, send, codigo, detalle, encabezados=None):
        respuesta = JSONResponse({"detail": detalle}, status_code=codigo, headers=encabezados)
        await respuesta(scope, receive, send)
```

## `pgc/aplicacion/__init__.py`

```python
"""Casos de uso: cola de deletreo, hilo de la mano y estado en vivo. Solo usan puertos."""
```

## `pgc/aplicacion/cola.py`

```python
"""Cola de mensajes: varios jurados envían a la vez y la mano los hace uno por uno."""
import itertools
import threading
import time
from collections import deque

from pgc.dominio.participante import ANONIMO
from pgc.dominio.texto import a_secuencia, limpiar


class ColaDeMensajes:
    def __init__(self, max_pendientes_cliente=2, max_cola=30, historial=6, max_caracteres=60,
                 al_cambiar=None, log=print, moderador=None, log_textos=True):
        self.max_pendientes_cliente = max_pendientes_cliente
        self.max_cola = max_cola
        self.max_caracteres = max_caracteres
        self.al_cambiar = al_cambiar or (lambda: None)
        self.log = log
        self.moderador = moderador           # filtro de palabras ofensivas (None = sin filtro)
        self.log_textos = log_textos         # False: el log no guarda lo que escribió el jurado
        self.cv = threading.Condition()      # protege pendientes/actual/historial
        self.pendientes = []                 # mensajes en espera (en orden)
        self.actual = None                   # mensaje que la mano está deletreando
        self.historial = deque(maxlen=historial)
        self._ids = itertools.count(1)
        self._saltar_id = None               # id del mensaje en curso que se pidió saltar

    # ------------------------------------------------------------ jurados
    def describir(self, msg):
        """Cómo aparece un mensaje en el log: sin su texto, salvo que se pida."""
        if self.log_textos:
            return f"#{msg['id']} '{msg['texto']}'"
        return f"#{msg['id']} ({sum(p['tipo'] != 'espacio' for p in msg['pasos'])} letras)"

    def encolar(self, texto, cliente, letras_mano=None, autor=None):
        """autor: {"pid", "nombre"} del participante (se muestra en el proyector).

        El nombre se copia al mensaje al encolarlo, tal como lo escribió la persona;
        sin nombre queda "Anónimo".
        """
        original = texto
        texto = limpiar(texto, self.max_caracteres)
        pasos = a_secuencia(texto, letras_mano, self.max_caracteres)
        if not any(p["tipo"] != "espacio" for p in pasos):
            raise ValueError("Escribe al menos una letra.")
        if self.moderador and (self.moderador.es_ofensivo(original) or self.moderador.es_ofensivo(texto)):
            self.log("[cola] Mensaje rechazado por el filtro de palabras")
            raise ValueError("Ese mensaje no se puede mostrar. Intenta con otras palabras.")
        if not any(p["tipo"] in ("ok", "aprox") for p in pasos):
            raise ValueError("La mano todavía no puede hacer esas letras")
        with self.cv:
            propios = [m for m in self.pendientes if m["cliente"] == cliente]
            if self.actual and self.actual["cliente"] == cliente:
                propios.append(self.actual)
            if len(propios) >= self.max_pendientes_cliente:
                raise ValueError(f"Ya tienes {self.max_pendientes_cliente} mensajes en espera. "
                                 "Espera a que la mano los haga.")
            if len(self.pendientes) >= self.max_cola:
                raise ValueError("La cola está llena, intenta en un momento.")
            autor = autor or {}
            msg = {"id": next(self._ids), "texto": texto, "cliente": cliente,
                   "pid": autor.get("pid"), "nombre": autor.get("nombre") or ANONIMO,
                   "pasos": pasos, "i": -1, "creado": time.time()}
            self.pendientes.append(msg)
            self.cv.notify_all()
        self.log(f"[cola] +{self.describir(msg)} (en cola: {len(self.pendientes)})")
        self.al_cambiar()
        return msg

    def cancelar(self, id_msg, cliente):
        """Solo el celular que lo envió puede cancelarlo, y solo mientras espera."""
        with self.cv:
            for m in self.pendientes:
                if m["id"] == id_msg and m["cliente"] == cliente:
                    self.pendientes.remove(m)
                    break
            else:
                return False
        self.log(f"[cola] -#{id_msg} cancelado")
        self.al_cambiar()
        return True

    def cancelar_de_cliente(self, cliente):
        """Quita todos los pendientes de un celular (el que está en curso sigue). Devuelve cuántos."""
        with self.cv:
            antes = len(self.pendientes)
            self.pendientes[:] = [m for m in self.pendientes if m["cliente"] != cliente]
            quitados = antes - len(self.pendientes)
        if quitados:
            self.al_cambiar()
        return quitados

    # ------------------------------------------------------------ presentador
    def saltar_actual(self):
        """Corta el mensaje en curso (la letra que se está formando termina primero)."""
        with self.cv:
            if not self.actual:
                return False
            self._saltar_id = self.actual["id"]
        self.log(f"[mano] Saltar #{self._saltar_id} pedido desde el PC")
        return True

    def debe_saltar(self, msg):
        return self._saltar_id == msg["id"]

    # ------------------------------------------------------------ hilo de la mano
    def tomar_siguiente(self, espera):
        """Pasa el primer pendiente a 'actual'; si no hay, espera hasta `espera` s y devuelve None."""
        with self.cv:
            if self.pendientes:
                self.actual = self.pendientes.pop(0)
                return self.actual
            self.cv.wait(timeout=espera)
            return None

    def terminar(self, msg):
        with self.cv:
            self.actual = None
            self.historial.appendleft(msg)

    def despertar(self):
        with self.cv:
            self.cv.notify_all()

    # ------------------------------------------------------------ estado
    def instantanea(self):
        """(actual, cola, historial) listos para enviar; nunca incluye el id del cliente."""
        with self.cv:
            actual = None
            if self.actual:
                m = self.actual
                actual = {"id": m["id"], "texto": m["texto"], "i": m["i"], "saltado": m.get("saltado", False),
                          "pid": m.get("pid"), "nombre": m.get("nombre"),
                          "pasos": [{"c": p["c"], "tipo": p["tipo"], "r": p.get("r")} for p in m["pasos"]]}
            cola = [{"id": m["id"], "texto": m["texto"], "pid": m.get("pid"), "nombre": m.get("nombre")}
                    for m in self.pendientes]
            historial = [{"id": m["id"], "texto": m["texto"], "nombre": m.get("nombre") or ANONIMO,
                          "saltado": m.get("saltado", False)}
                         for m in self.historial]
        return actual, cola, historial
```

## `pgc/aplicacion/deletreo.py`

```python
"""Hilo de la mano: saca mensajes de la cola y los deletrea esperando cada confirmación."""
import threading
import time

from pgc.dominio.ordenes import forma_despues, ordenes_para
from pgc.dominio.texto import a_secuencia


class Deletreador:
    def __init__(self, cola, mano, al_cambiar, log=print, pausa_letra=0.5, pausa_no_disponible=0.9,
                 simular=False, autodeteccion_cada=3.0):
        self.cola = cola
        self.mano = mano                      # PuertoMano
        self.al_cambiar = al_cambiar
        self.log = log
        self.pausa_letra = pausa_letra
        self.pausa_no_disponible = pausa_no_disponible
        self.simular = simular
        self.autodeteccion_cada = autodeteccion_cada
        self.pedir_reconexion = False

    def iniciar(self):
        threading.Thread(target=self._trabajar, daemon=True, name="mano").start()

    def reconectar(self):
        """Pide al hilo que vuelva a buscar la mano (lo hace entre mensajes)."""
        self.pedir_reconexion = True
        self.cola.despertar()

    # ------------------------------------------------------------ conexión
    def _conectar_mano(self):
        if self.simular:
            self.log("[mano] Modo simulado (--simular)")
        self.mano.conectar()
        self.al_cambiar()

    def _autodetectar(self):
        """Entre mensajes: latido, respaldo y búsqueda de la mano (si se conecta con el servidor
        ya corriendo, la toma sola)."""
        if self.simular:
            return
        if self.mano.revisar():
            self.al_cambiar()

    # ------------------------------------------------------------ bucle
    def _trabajar(self):
        self._conectar_mano()
        while True:
            if self.pedir_reconexion:
                self.pedir_reconexion = False
                if self.mano.conectada:
                    self.mano.cerrar()
                self._conectar_mano()
            msg = self.cola.tomar_siguiente(espera=self.autodeteccion_cada)
            if msg is None:
                self._autodetectar()
                continue
            try:
                self._deletrear(msg)
            except Exception as ex:          # nunca dejar morir el hilo
                self.log(f"[mano] Error deletreando #{msg['id']}: {ex}")
            self.cola.terminar(msg)
            self.al_cambiar()

    def _deletrear(self, msg):
        # Se recalcula por si la mano se conectó después y reportó otras letras
        msg["pasos"] = a_secuencia(msg["texto"], self.mano.letras, self.cola.max_caracteres)
        self.log(f"[mano] Deletreando {self.cola.describir(msg)} ({self.mano.modo})")
        forma = None                                  # letra que la mano tiene formada (None = abierta)
        for i, paso in enumerate(msg["pasos"]):
            if self.cola.debe_saltar(msg):
                break
            msg["i"] = i
            self.al_cambiar()
            ordenes = ordenes_para(paso, forma)       # regla de espacios y letras repetidas
            if ordenes:
                for orden in ordenes[:-1]:
                    self.mano.hacer(orden)
                ok = self.mano.hacer(ordenes[-1])
                if ok and paso["l"]:
                    time.sleep(self.pausa_letra)
            else:
                time.sleep(self.pausa_no_disponible)
                ok = None
            forma = forma_despues(paso, forma, ok)
            paso["r"] = "nd" if ok is None else ("ok" if ok else "error")
        if self.cola.debe_saltar(msg):
            msg["saltado"] = True
            self.log(f"[mano] #{msg['id']} saltado")
        else:
            msg["i"] = len(msg["pasos"])
        self.al_cambiar()
        self.mano.reset()
```

## `pgc/aplicacion/estado.py`

```python
"""Estado en vivo: instantánea del sistema y aviso a los WebSocket conectados."""
import asyncio


class Publicador:
    """Puente entre los hilos (mano, voz, túnel) y el bucle asyncio de la web.

    Cada suscriptor es una asyncio.Queue de tamaño 1: solo importa el estado más reciente.
    """

    def __init__(self, instantanea=None):
        self._instantanea = instantanea
        self.loop = None
        self.suscriptores = set()

    def fijar_instantanea(self, instantanea):
        """Se fija después porque los adaptadores necesitan `notificar` antes de que exista el Sistema."""
        self._instantanea = instantanea

    def notificar(self):
        """Se puede llamar desde cualquier hilo."""
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self._difundir)

    def _difundir(self):
        estado = self._instantanea()
        for q in list(self.suscriptores):
            if q.full():                      # solo importa el estado más reciente
                q.get_nowait()
            q.put_nowait(estado)

    def suscribir(self):
        q = asyncio.Queue(maxsize=1)
        self.suscriptores.add(q)
        return q

    def desuscribir(self, q):
        self.suscriptores.discard(q)


def instantanea_sistema(sesion, mano, voz, tunel, url_local, url_publica, max_caracteres, cola, bloqueados=(),
                        kinect=None, voz_salida="desactivado"):
    actual, pendientes, historial = cola.instantanea()
    return {
        "tipo": "estado",
        "sesion": sesion,
        "mano": {"modo": mano.modo, "medio": mano.medio, "puerto": mano.puerto,
                 "letras": "".join(sorted(mano.letras or [])) or None},
        "voz": {"estado": voz.estado, "dispositivo": voz.dispositivo},
        "tunel": {"estado": tunel.estado, "url": tunel.url},
        "url_local": url_local,
        "url_publica": url_publica,
        "voz_salida": {"estado": voz_salida},
        # estado, detalle, texto en curso, conectado/camara/activo, frases, turno (pid y nombre) y eco
        "kinect": kinect or {"estado": "apagado"},
        "max_caracteres": max_caracteres,
        "actual": actual,
        "cola": pendientes,
        "historial": historial,
        "bloqueados": list(bloqueados),      # alias (pid) bloqueados: cada celular sabe si es el suyo
    }
```

## `pgc/aplicacion/participantes.py`

```python
"""Participantes de la sesión: nombre opcional y bloqueo por el presentador (ADR-7).

Todo vive en memoria y desaparece al cerrar el servidor. Cada celular (`cliente`,
su id privado) recibe un alias opaco (`pid`) que sí se puede mostrar en el
WebSocket: con el pid no se pueden cancelar mensajes ajenos.
"""
import secrets
import threading

from pgc.dominio.participante import MSG_NOMBRE_OFENSIVO, normalizar_nombre


class Participantes:
    def __init__(self, moderador=None, al_cambiar=None, log=print):
        self.moderador = moderador
        self.al_cambiar = al_cambiar or (lambda: None)
        self.log = log
        self._lock = threading.Lock()
        self._por_cliente = {}          # cliente → {"pid", "nombre", "bloqueado"}
        self._por_pid = {}              # pid → cliente

    def _nuevo(self, cliente):
        pid = "p" + secrets.token_hex(4)
        while pid in self._por_pid:
            pid = "p" + secrets.token_hex(4)
        datos = {"pid": pid, "nombre": None, "bloqueado": False}
        self._por_cliente[cliente] = datos
        self._por_pid[pid] = cliente
        return datos

    def obtener(self, cliente):
        """Datos del participante (lo crea si es la primera vez que se le ve)."""
        with self._lock:
            return dict(self._por_cliente.get(cliente) or self._nuevo(cliente))

    def registrar(self, cliente, nombre):
        """Fija o cambia el nombre. Un participante bloqueado no puede cambiarlo."""
        nombre = normalizar_nombre(nombre)
        if nombre and self.moderador and self.moderador.es_ofensivo(nombre):
            raise ValueError(MSG_NOMBRE_OFENSIVO)
        with self._lock:
            datos = self._por_cliente.get(cliente) or self._nuevo(cliente)
            cambio = not datos["bloqueado"] and datos["nombre"] != nombre
            if cambio:
                datos["nombre"] = nombre
            resultado = dict(datos)
        if cambio:
            self.al_cambiar()
        return resultado

    def esta_bloqueado(self, cliente):
        with self._lock:
            datos = self._por_cliente.get(cliente)
            return bool(datos and datos["bloqueado"])

    def cliente_de(self, pid):
        with self._lock:
            return self._por_pid.get(pid)

    def fijar_bloqueo(self, pid, bloqueado, avisar=True):
        """Devuelve el cliente afectado, o None si el pid no existe.

        avisar=False: quien llama avisa después (p. ej. tras cancelar los pendientes),
        para que las pantallas nunca vean un estado a medias.
        """
        with self._lock:
            cliente = self._por_pid.get(pid)
            if cliente is None:
                return None
            self._por_cliente[cliente]["bloqueado"] = bloqueado
        self.log(f"[participantes] {pid} {'bloqueado' if bloqueado else 'desbloqueado'}")
        if avisar:
            self.al_cambiar()
        return cliente

    def bloqueados(self):
        with self._lock:
            return sorted(d["pid"] for d in self._por_cliente.values() if d["bloqueado"])
```

## `pgc/aplicacion/protocolo.py`

```python
"""Protocolo de prueba de letras: pide cada letra N veces y registra qué reconoce el detector y en cuánto tiempo.

Flujo de cada intento:
  pedir    "Haz la letra A (intento 2 de 5)". Termina cuando el texto del detector crece (letra confirmada:
           acierto o confusión) o cuando pasan `tiempo_max` s (no detectada). El tiempo se cuenta desde
           la primera imagen con mano, para no medir lo que tarda la persona en reaccionar.
  retirar  "Retira la mano". Hasta que no haya mano y su lógica esté lista para otra letra (o 3 s);
           entonces se limpia el texto del detector y empieza el siguiente intento.
Cada muestra del diagnóstico (~10/s) se guarda para el análisis (pgc/dominio/experimento.py).

ProtocoloLetras es pura (recibe muestras y la hora): se prueba con una línea de tiempo inventada.
ServicioProtocolo la alimenta desde un hilo y guarda los resultados al terminar.
"""
import threading
import time
from collections import Counter


class ProtocoloLetras:
    def __init__(self, letras, repeticiones=5, tiempo_max=8.0, espera_retirar=3.0):
        self.plan = [(letra, k) for letra in letras for k in range(1, repeticiones + 1)]
        self.repeticiones = repeticiones
        self.tiempo_max = tiempo_max
        self.espera_retirar = espera_retirar
        self.i = 0
        self.fase = "listo"                 # listo | pedir | retirar | terminado | detenido
        self.intentos = []                  # resultados (ver pgc/dominio/experimento.py)
        self.muestras = []                  # todas las muestras del diagnóstico, con el intento al que pertenecen
        self._actual = []                   # muestras del intento en curso
        self._t_diag = None                 # hora (del detector) de la última imagen vista
        self._t_corte = None                # imágenes procesadas hasta aquí son de antes de limpiar

    @property
    def total(self):
        return len(self.plan)

    @property
    def pedida(self):
        return self.plan[self.i] if self.i < len(self.plan) else (None, None)

    def iniciar(self, ahora):
        self._abrir(ahora, texto="")
        return ["iniciar", "limpiar"]

    def detener(self):
        if self.fase not in ("terminado",):
            self.fase = "detenido"

    def _abrir(self, ahora, texto):
        # El diagnóstico se actualiza con cada IMAGEN: hasta que llegue una nueva, puede seguir mostrando
        # el texto de antes de limpiar. Esas muestras no cuentan para decidir si se confirmó una letra.
        self._t_corte = self._t_diag
        self.fase = "pedir"
        self._t0 = ahora
        self._t_mano = None
        self._texto0 = texto
        self._actual = []

    def muestra(self, d, ahora):
        """Procesa una muestra del diagnóstico. Devuelve las órdenes para el detector (p. ej. ["limpiar"])."""
        if self.fase not in ("pedir", "retirar") or d is None:
            return []
        letra, k = self.pedida
        fila = {"t": round(ahora, 3), "fase": self.fase, "letra": letra, "intento": k,
                "manos": d.get("manos"), "prediccion": d.get("prediccion"), "segunda": d.get("segunda"),
                "margen": d.get("margen"), "estable_s": d.get("estable_s"), "confirmaciones": d.get("confirmaciones"),
                "motivo": d.get("motivo"), "texto": d.get("texto")}
        self.muestras.append(fila)
        texto = (d.get("texto") or "")
        vieja = self._t_corte is not None and (d.get("t") or 0) <= self._t_corte
        self._t_diag = d.get("t", self._t_diag)
        if self.fase == "pedir":
            self._actual.append(fila)
            if (d.get("manos") or 0) >= 1 and self._t_mano is None:
                self._t_mano = ahora
            nuevo = "" if vieja else (texto[len(self._texto0):].strip() if texto.startswith(self._texto0)
                                      else texto.strip())
            if nuevo:                                            # su lógica confirmó una letra
                self._cerrar(nuevo[-1].lower(), ahora)
            elif ahora - self._t0 >= self.tiempo_max:
                self._cerrar(None, ahora)
            return []
        # retirar: sin mano y su lógica lista para otra letra (armado), o tiempo agotado
        if ((d.get("manos") == 0 and d.get("armado")) or ahora - self._t_retirar >= self.espera_retirar):
            self.i += 1
            if self.i >= len(self.plan):
                self.fase = "terminado"
                return ["limpiar"]
            self._abrir(ahora, texto="")
            return ["limpiar"]
        return []

    def _cerrar(self, reconocida, ahora):
        letra, k = self.pedida
        con_mano = [m for m in self._actual if (m["manos"] or 0) == 1]
        preds = [m["prediccion"] for m in con_mano if m["prediccion"]]
        cambios = sum(1 for a, b in zip(preds, preds[1:]) if a != b)
        margenes = [m["margen"] for m in con_mano if m["margen"] is not None]
        motivos = Counter(m["motivo"] for m in self._actual if m["motivo"])
        n = len(self._actual) or 1
        self.intentos.append({
            "letra": letra, "intento": k, "reconocida": reconocida,
            "tiempo_s": round(ahora - (self._t_mano if self._t_mano is not None else self._t0), 2)
            if reconocida else None,
            "mano_pct": round(100 * len(con_mano) / n, 1),
            "prediccion_frecuente": Counter(preds).most_common(1)[0][0] if preds else None,
            "margen_medio": round(sum(margenes) / len(margenes), 3) if margenes else None,
            "estable_max_s": max((m["estable_s"] or 0 for m in self._actual), default=0.0),
            "cambios": cambios,
            "sin_letra_pct": round(100 * preds.count("sin_letra") / len(preds), 1) if preds else 0.0,
            "motivo_frecuente": motivos.most_common(1)[0][0] if motivos else None,
        })
        self.fase = "retirar"
        self._t_retirar = ahora

    def estado(self):
        letra, k = self.pedida
        return {"fase": self.fase, "letra": letra, "intento": k, "repeticiones": self.repeticiones,
                "hecho": len(self.intentos), "total": self.total, "ultimos": self.intentos[-8:][::-1]}


class ServicioProtocolo:
    """Corre el protocolo en un hilo (~10 muestras/s) y guarda los resultados al terminar."""

    def __init__(self, senas, guardar=None, log=print, al_cambiar=None, reloj=time.monotonic, periodo=0.1):
        self.senas = senas
        self.guardar = guardar               # (protocolo, info) -> carpeta; lo pone arranque.py
        self.log = log
        self.al_cambiar = al_cambiar or (lambda: None)
        self._reloj = reloj
        self.periodo = periodo
        self.protocolo = None
        self.carpeta = None
        self.error = None
        self.informe = None
        self._hilo = None

    @property
    def corriendo(self):
        return bool(self.protocolo and self.protocolo.fase in ("pedir", "retirar"))

    def iniciar(self, letras, repeticiones=5, tiempo_max=8.0):
        if self.corriendo:
            raise RuntimeError("Ya hay un protocolo en curso.")
        if self.senas.diagnostico() is None:
            raise RuntimeError("El detector no da diagnóstico (¿Kinect no conectado o detector original?).")
        self.protocolo = ProtocoloLetras(letras, repeticiones, tiempo_max)
        self.carpeta = self.error = self.informe = None
        for orden in self.protocolo.iniciar(self._reloj()):
            self.senas.controlar(orden)
        self.log(f"[kinect] Protocolo de letras: {len(letras)} letras × {repeticiones}")
        self._hilo = threading.Thread(target=self._bucle, daemon=True, name="protocolo")
        self._hilo.start()
        self.al_cambiar()

    def detener(self):
        if self.protocolo:
            self.protocolo.detener()

    def _bucle(self):
        p = self.protocolo
        while p.fase in ("pedir", "retirar"):
            try:
                for orden in p.muestra(self.senas.diagnostico(), self._reloj()):
                    self.senas.controlar(orden)
            except Exception as ex:                         # nunca dejar morir el hilo sin avisar
                self.error = f"{type(ex).__name__}: {ex}"
                p.detener()
                break
            time.sleep(self.periodo)
        if p.intentos and self.guardar:
            try:
                self.carpeta, self.informe = self.guardar(p, {"detenido": p.fase == "detenido"})
                self.log(f"[kinect] Protocolo guardado en {self.carpeta}")
            except Exception as ex:
                self.error = f"No se pudieron guardar los resultados: {type(ex).__name__}: {ex}"
        self.al_cambiar()

    def estado(self):
        if not self.protocolo:
            return {"fase": "sin_iniciar"}
        return {**self.protocolo.estado(), "carpeta": self.carpeta, "error": self.error, "informe": self.informe}
```

## `pgc/aplicacion/senas.py`

```python
"""Señas → texto: recibe los eventos del reconocedor y arma la frase.

Los callbacks del reconocedor pueden llegar desde cualquier hilo: solo se copian
a una cola y un hilo propio los procesa, así el reconocedor nunca se bloquea
(regla 3 del contrato). Al llegar 'fin' se entrega la frase a `al_frase`
(fase 4–5: decirla en voz alta, mostrarla y, en modo eco, enviarla a la mano).
"""
import queue
import threading
import time

from pgc.aplicacion.turno import TurnoKinect
from pgc.puertos.reconocedor import problemas_del_evento

MAX_TEXTO = 60
ACCIONES = ("iniciar", "detener", "espacio", "borrar", "limpiar", "terminar")


class SinControles(RuntimeError):
    """El reconocedor configurado no tiene controles (p. ej. el simulado)."""


class ReconocedorNulo:
    """Sin Kinect configurado: cumple el puerto y no emite nada."""
    estado = "apagado"
    detalle = "Kinect: próxima fase"

    def iniciar(self, al_evento, al_cambiar_estado):
        pass

    def detener(self):
        pass


class ServicioSenas:
    def __init__(self, reconocedor, al_frase=None, al_cambiar=None, log=print, moderador=None,
                 turno_segundos=120.0, reloj=time.monotonic, turno_codigo=False):
        self.reconocedor = reconocedor
        self.moderador = moderador      # la frase pasa por el mismo filtro que los mensajes
        self.al_frase = al_frase or (lambda texto: None)
        self.al_cambiar = al_cambiar or (lambda: None)
        self.log = log
        self.texto = ""                 # frase en construcción
        self.frases = []                # frases terminadas en esta sesión (las últimas 10)
        self.turno = TurnoKinect(turno_segundos, reloj, con_codigo=turno_codigo)
        self._eventos = queue.Queue(maxsize=500)
        self._iniciado = False

    # ---------------------------------------------------------------- ciclo de vida
    def iniciar(self):
        if self._iniciado:
            return
        self._iniciado = True
        threading.Thread(target=self._procesar, daemon=True, name="senas").start()
        try:
            self.reconocedor.iniciar(self._recibir, self.al_cambiar)
        except Exception as ex:          # un reconocedor roto no tumba el servidor
            self.log(f"[kinect] No se pudo iniciar el reconocedor: {type(ex).__name__}")
            self.reconocedor.estado, self.reconocedor.detalle = "error", "Kinect: no disponible"
            self.al_cambiar()

    def detener(self):
        try:
            self.reconocedor.detener()
        except Exception:
            pass

    # ---------------------------------------------------------------- eventos
    def _recibir(self, evento):
        """Lo llama el reconocedor desde su hilo: no bloquea nunca."""
        try:
            self._eventos.put_nowait(evento)
        except queue.Full:
            pass

    def _procesar(self):
        while True:
            try:
                evento = self._eventos.get(timeout=1.0)
            except queue.Empty:
                evento = None
            try:
                if evento is not None:
                    self._aplicar(evento)
                if self.turno.revisar():     # un turno vencido se libera solo
                    self.log("[kinect] Turno liberado por inactividad")
                    self.al_cambiar()
            except Exception as ex:      # nunca dejar morir el hilo
                self.log(f"[kinect] Error procesando un evento: {type(ex).__name__}")

    def _aplicar(self, evento):
        problemas = problemas_del_evento(evento)
        if problemas:
            self.log(f"[kinect] Evento ignorado: {problemas[0]}")
            return
        if evento.tipo == "letra" and len(self.texto) < MAX_TEXTO:
            self.texto += evento.letra
        elif evento.tipo == "espacio" and self.texto and not self.texto.endswith(" "):
            self.texto += " "
        elif evento.tipo == "borrar":
            self.texto = self.texto[:-1]
        elif evento.tipo == "fin":
            frase, self.texto = self.texto.strip(), ""
            if frase and self.moderador and self.moderador.es_ofensivo(frase):
                self.log("[kinect] Frase descartada por el filtro de palabras")
            elif frase:
                self.frases = (self.frases + [frase])[-10:]
                self.al_frase(frase)
        self.al_cambiar()

    # ---------------------------------------------------------------- controles
    @property
    def tiene_controles(self):
        return callable(getattr(self.reconocedor, "controlar", None))

    def controlar(self, accion):
        """Pasa la orden al reconocedor (contrato §3.1). Sus errores llegan como RuntimeError con el motivo."""
        if accion not in ACCIONES:
            raise ValueError("Acción no válida.")
        if not self.tiene_controles:
            raise SinControles("Este Kinect no tiene controles.")
        self.reconocedor.controlar(accion)
        self.al_cambiar()

    def diagnostico(self):
        """Diagnóstico en vivo del detector (solo para el PC), o None si el reconocedor no lo tiene."""
        obtener = getattr(self.reconocedor, "diagnostico", None)
        return obtener() if callable(obtener) else None

    def imagen(self):
        """JPEG con los puntos de la mano (solo para el proyector del PC), o None."""
        obtener = getattr(self.reconocedor, "imagen", None)
        return obtener() if callable(obtener) else None

    def imagen_con_estado(self, despues=None, espera=0.0):
        """La imagen y el estado del mismo momento ({"jpeg", "texto", "detalle", "cuadro", "edad_ms",
        "desfase_ms"}), o None. Si el reconocedor solo tiene imagen(), se arma con el estado actual."""
        obtener = getattr(self.reconocedor, "imagen_con_estado", None)
        if callable(obtener):
            return obtener(despues, espera)
        jpeg = self.imagen()
        return jpeg and {"jpeg": jpeg, "texto": self.texto, "detalle": self.reconocedor.detalle}

    def instantanea(self):
        r = self.reconocedor
        return {"estado": r.estado, "detalle": r.detalle, "texto": self.texto,
                "conectado": bool(getattr(r, "conectado", r.estado not in ("apagado", "error"))),
                "camara": bool(getattr(r, "camara", False)),
                "activo": bool(getattr(r, "activo", False)),
                "controles": self.tiene_controles,
                "frases": self.frases[-3:],
                "turno": self.turno.instantanea(),
                # Si hace falta el código del proyector y su versión, NUNCA el código (esto va a los celulares)
                "codigo": self.turno.con_codigo, "codigo_version": self.turno.version_codigo}
```

## `pgc/aplicacion/sistema.py`

```python
"""Sistema: reúne la cola, el hilo de la mano y el estado en vivo.

Recibe los componentes ya armados (mano, voz, túnel); quien los crea es pgc/arranque.py.
"""
import queue
import threading
import time

from pgc.aplicacion.cola import ColaDeMensajes
from pgc.aplicacion.deletreo import Deletreador
from pgc.aplicacion.estado import instantanea_sistema
from pgc.aplicacion.participantes import Participantes
from pgc.aplicacion.protocolo import ServicioProtocolo
from pgc.aplicacion.senas import ReconocedorNulo, ServicioSenas
from pgc.dominio.participante import MSG_BLOQUEADO

CLIENTE_KINECT = "kinect"        # el "celular" del modo eco: sus mensajes van a la cola como los demás
AUTOR_KINECT = {"pid": None, "nombre": "Kinect"}


class SintetizadorNulo:
    """Sin voz de salida: cumple el puerto y no dice nada."""
    estado = "desactivado"

    def cargar_en_segundo_plano(self):
        pass

    def decir(self, texto):
        pass


class SinPermisoKinect(Exception):
    """Solo quien tiene el turno (o el presentador) controla el Kinect."""

    def __init__(self):
        super().__init__("Toma el control del Kinect para usar estos botones.")


class ParticipanteBloqueado(Exception):
    """El presentador pausó a este participante durante la sesión."""

    def __init__(self):
        super().__init__(MSG_BLOQUEADO)


class Sistema:
    def __init__(self, cfg, mano, voz, tunel, url_local, publicador, log=print, moderador=None, reconocedor=None,
                 sintetizador=None, reloj=time.monotonic, guardar_experimento=None):
        self.cfg = cfg
        self.log = log
        self.sesion = str(int(time.time()))   # cambia en cada arranque del servidor
        self.mano = mano                      # PuertoMano
        self.voz = voz                        # Transcriptor
        self.tunel = tunel                    # acceso público (cloudflared)
        self.url_local = url_local
        self.publicador = publicador
        publicador.fijar_instantanea(self.instantanea)
        self.moderador = moderador
        self.participantes = Participantes(moderador, al_cambiar=self.notificar, log=log)
        self._cola = ColaDeMensajes(cfg.max_pendientes_cliente, cfg.max_cola, cfg.historial, cfg.max_caracteres,
                                    al_cambiar=self.notificar, log=log, moderador=moderador,
                                    log_textos=cfg.log_textos)
        # Kinect → texto → voz (y, en modo eco, → mano)
        self.senas = ServicioSenas(reconocedor or ReconocedorNulo(), al_frase=self._frase_reconocida,
                                   al_cambiar=self.notificar, log=log, moderador=moderador,
                                   turno_segundos=cfg.kinect_turno_segundos, reloj=reloj,
                                   turno_codigo=cfg.kinect_codigo)
        self.voz_salida = sintetizador or SintetizadorNulo()
        self.eco = cfg.kinect_eco
        self._por_decir = queue.Queue(maxsize=10)
        # Protocolo de prueba de letras (vista de diagnóstico del PC); guarda en experimentos/
        self.protocolo = ServicioProtocolo(self.senas, guardar=guardar_experimento, log=log)
        self._locutor = None
        self.deletreador = Deletreador(self._cola, mano, self.notificar, log,
                                       cfg.pausa_letra, cfg.pausa_no_disponible,
                                       simular=cfg.mano == "simulada", autodeteccion_cada=cfg.autodeteccion_cada)

    # ----------------------------------------------------------- estado
    cola = property(lambda self: self._cola.pendientes)
    actual = property(lambda self: self._cola.actual)
    historial = property(lambda self: self._cola.historial)
    cv = property(lambda self: self._cola.cv)

    @property
    def loop(self):
        return self.publicador.loop

    @loop.setter
    def loop(self, valor):
        self.publicador.loop = valor

    @property
    def pedir_reconexion(self):
        return self.deletreador.pedir_reconexion

    @pedir_reconexion.setter
    def pedir_reconexion(self, valor):
        self.deletreador.pedir_reconexion = valor

    @property
    def url_publica(self):
        return self.tunel.url or self.url_local

    def instantanea(self):
        kinect = {**self.senas.instantanea(), "eco": self.eco}
        return instantanea_sistema(self.sesion, self.mano, self.voz, self.tunel, self.url_local,
                                   self.url_publica, self.cfg.max_caracteres, self._cola,
                                   self.participantes.bloqueados(), kinect=kinect,
                                   voz_salida=self.voz_salida.estado)

    # ----------------------------------------------------------- operaciones
    def notificar(self):
        """Se puede llamar desde cualquier hilo."""
        self.publicador.notificar()

    def encolar(self, texto, cliente):
        autor = self.participantes.obtener(cliente)
        if autor["bloqueado"]:
            raise ParticipanteBloqueado()
        return self._cola.encolar(texto, cliente, self.mano.letras, autor)

    # ----------------------------------------------------------- participantes
    def registrar_participante(self, cliente, nombre):
        return self.participantes.registrar(cliente, nombre)

    def bloquear(self, pid):
        """Bloquea durante la sesión, cancela sus pendientes y salta el suyo si está en curso.

        Devuelve {"cancelados": n, "saltado": bool}, o None si el pid no existe.
        Desbloquear no recupera nada de esto.
        """
        # Primero se bloquea (ya no puede encolar), luego se limpia la cola y al final se avisa
        cliente = self.participantes.fijar_bloqueo(pid, True, avisar=False)
        if cliente is None:
            return None
        cancelados = self._cola.cancelar_de_cliente(cliente)
        actual = self._cola.actual
        saltado = bool(actual and actual["cliente"] == cliente and self._cola.saltar_actual())
        sin_turno = self.senas.turno.soltar(cliente)     # tampoco sigue controlando el Kinect
        self.log(f"[participantes] {pid}: {cancelados} pendiente(s) cancelado(s)"
                 + ("; se saltó el mensaje en curso" if saltado else "")
                 + ("; perdió el turno del Kinect" if sin_turno else ""))
        self.notificar()
        return {"cancelados": cancelados, "saltado": saltado}

    def desbloquear(self, pid):
        return self.participantes.fijar_bloqueo(pid, False) is not None

    def esta_bloqueado(self, cliente):
        return self.participantes.esta_bloqueado(cliente)

    def cancelar(self, id_msg, cliente):
        return self._cola.cancelar(id_msg, cliente)

    def saltar_actual(self):
        return self._cola.saltar_actual()

    def reconectar_mano(self):
        self.deletreador.reconectar()

    def iniciar_trabajador(self):
        self.deletreador.iniciar()

    # ----------------------------------------------------------- Kinect
    def tomar_turno_kinect(self, cliente, codigo=None):
        autor = self.participantes.obtener(cliente)
        if autor["bloqueado"]:
            raise ParticipanteBloqueado()
        # TurnoOcupado si lo tiene otro; CodigoIncorrecto si no es el del proyector
        self.senas.turno.tomar(cliente, autor["pid"], autor["nombre"], codigo)
        self.notificar()

    def soltar_turno_kinect(self, cliente):
        if self.senas.turno.soltar(cliente):
            self.notificar()

    def liberar_turno_kinect(self):
        if self.senas.turno.liberar():
            self.log("[kinect] El presentador liberó el turno")
            self.notificar()

    def regenerar_codigo_kinect(self):
        """Código nuevo en el proyector; quien tenía el turno lo pierde."""
        codigo = self.senas.turno.regenerar_codigo()
        if codigo:
            self.log("[kinect] El presentador cambió el código del turno")
            self.notificar()
        return codigo

    def controlar_kinect(self, accion, cliente=None, presentador=False):
        """El presentador siempre; un celular, solo si tiene el turno y no está bloqueado."""
        if not presentador:
            if cliente is None or not self.senas.turno.es_dueno(cliente):
                raise SinPermisoKinect()
            if self.participantes.esta_bloqueado(cliente):
                raise ParticipanteBloqueado()
            self.senas.turno.usar(cliente)
        self.senas.controlar(accion)

    def fijar_eco(self, activo, cliente=None, presentador=False):
        """El presentador siempre; un celular, solo si tiene el turno del Kinect (como los demás controles)."""
        if not presentador:
            if cliente is None or not self.senas.turno.es_dueno(cliente):
                raise SinPermisoKinect()
            if self.participantes.esta_bloqueado(cliente):
                raise ParticipanteBloqueado()
            self.senas.turno.usar(cliente)
        self.eco = bool(activo)
        self.log(f"[kinect] Modo eco {'activado' if self.eco else 'desactivado'}")
        self.notificar()

    def _frase_reconocida(self, frase):
        """'fin' del Kinect: la frase se dice en los parlantes y, en modo eco, la mano la deletrea."""
        self.log(f"[kinect] Frase reconocida ({len(frase)} caracteres)")
        self._decir(frase)
        if self.eco:
            try:
                self._cola.encolar(frase, CLIENTE_KINECT, self.mano.letras, AUTOR_KINECT)
            except ValueError as ex:          # p. ej. ninguna letra que la mano pueda hacer
                self.log(f"[kinect] Eco: la frase no va a la mano ({ex})")

    def _decir(self, frase):
        """La voz va en su propio hilo: decir() bloquea mientras habla y no debe frenar al Kinect."""
        if self._locutor is None:
            self._locutor = threading.Thread(target=self._hablar, daemon=True, name="voz-salida")
            self._locutor.start()
        try:
            self._por_decir.put_nowait(frase)
        except queue.Full:
            self.log("[voz] Demasiadas frases por decir; se omite una")

    def _hablar(self):
        while True:
            frase = self._por_decir.get()
            try:
                self.voz_salida.decir(frase)
            except Exception as ex:           # la voz nunca tumba el servidor
                self.log(f"[voz] No se pudo decir la frase: {type(ex).__name__}")
```

## `pgc/aplicacion/turno.py`

```python
"""Turno del Kinect: un solo jurado lo controla a la vez desde su celular.

Quien toma el turno puede iniciar, detener, poner espacio, borrar y terminar.
El turno se libera al soltarlo, al bloquear a esa persona, cuando el presentador
lo libera o, solo, tras `segundos` sin usar los controles. El presentador (PC con
token) controla siempre, tenga o no alguien el turno.

Con `con_codigo`, para tomar el turno hay que escribir el código de 6 dígitos que
muestra el proyector (como el «Código del PC» del diseño de Camila): así solo
controla quien está en la sala. Cambia en cada arranque y el presentador puede
regenerarlo (eso también quita el turno a quien lo tenga).
"""
import secrets
import threading
import time


class TurnoOcupado(Exception):
    """Otro celular tiene el turno."""

    def __init__(self, nombre):
        quien = nombre or "otra persona"
        super().__init__(f"El Kinect lo está usando {quien}. Espera tu turno.")


class CodigoIncorrecto(Exception):
    """El código escrito no es el que muestra el proyector."""

    def __init__(self):
        super().__init__("Código incorrecto. Escribe el código de 6 dígitos que muestra el proyector.")


def nuevo_codigo():
    return f"{secrets.randbelow(10**6):06d}"


class TurnoKinect:
    def __init__(self, segundos=120.0, reloj=time.monotonic, con_codigo=False):
        self.segundos = segundos
        self.con_codigo = con_codigo
        self._reloj = reloj
        self._lock = threading.Lock()
        self._dueno = None          # {"cliente", "pid", "nombre", "ultimo"}
        self._codigo = nuevo_codigo() if con_codigo else None
        self.version_codigo = 0     # sube al regenerarlo: el proyector sabe que debe pedirlo otra vez

    @property
    def codigo(self):
        """Solo para el proyector (ruta con token): nunca va en el estado que reciben los celulares."""
        return self._codigo

    def regenerar_codigo(self):
        """Código nuevo; quien tenía el turno lo pierde (tendrá que escribir el nuevo)."""
        with self._lock:
            if not self.con_codigo:
                return None
            self._codigo = nuevo_codigo()
            self.version_codigo += 1
            self._dueno = None
            return self._codigo

    def _vencido(self):
        return self._dueno and self._reloj() - self._dueno["ultimo"] >= self.segundos

    def tomar(self, cliente, pid, nombre, codigo=None):
        """Da el turno si está libre (o vencido) y el código es el del proyector.

        Lanza TurnoOcupado si lo tiene otro y CodigoIncorrecto si el código no coincide.
        """
        with self._lock:
            if self._vencido():
                self._dueno = None
            if self._dueno and self._dueno["cliente"] != cliente:
                raise TurnoOcupado(self._dueno["nombre"])
            escrito = "".join(c for c in str(codigo or "") if c.isdigit())
            if self.con_codigo and not secrets.compare_digest(escrito, self._codigo):
                raise CodigoIncorrecto()
            self._dueno = {"cliente": cliente, "pid": pid, "nombre": nombre, "ultimo": self._reloj()}

    def es_dueno(self, cliente):
        with self._lock:
            return bool(self._dueno and not self._vencido() and self._dueno["cliente"] == cliente)

    def usar(self, cliente):
        """Cuenta como actividad (reinicia la espera para liberarlo)."""
        with self._lock:
            if self._dueno and self._dueno["cliente"] == cliente:
                self._dueno["ultimo"] = self._reloj()

    def soltar(self, cliente):
        with self._lock:
            if self._dueno and self._dueno["cliente"] == cliente:
                self._dueno = None
                return True
            return False

    def liberar(self):
        """El presentador libera el turno, sea de quien sea."""
        with self._lock:
            libre = self._dueno is None
            self._dueno = None
            return not libre

    def revisar(self):
        """Libera el turno vencido. Devuelve True si cambió (para avisar a las pantallas)."""
        with self._lock:
            if self._vencido():
                self._dueno = None
                return True
            return False

    def instantanea(self):
        """Lo que ven las pantallas: alias y nombre, nunca el id privado del celular."""
        with self._lock:
            if not self._dueno or self._vencido():
                return None
            restante = self.segundos - (self._reloj() - self._dueno["ultimo"])
            return {"pid": self._dueno["pid"], "nombre": self._dueno["nombre"], "libera_en": round(max(0, restante))}
```

## `pgc/arranque.py`

```python
"""Raíz de composición: el único lugar que conoce los adaptadores concretos.

Lee la configuración, crea la mano, la voz y el túnel, arma el Sistema y la app web.
"""
import importlib
import sys

from pgc import config, registro
from pgc.adaptadores import acceso
from pgc.adaptadores.mano_respaldo import Mano
from pgc.adaptadores.mano_ble import ManoBLE
from pgc.aplicacion.estado import Publicador
from pgc.aplicacion.sistema import Sistema
from pgc.dominio.moderacion import cargar_moderador


def crear_mano(cfg, log):
    ble = None
    if cfg.mano_ble_token and cfg.mano in ("auto", "ble"):
        ble = ManoBLE(cfg.mano_ble_nombre, cfg.mano_ble_token, timeout_letra=cfg.mano_timeout_letra, log=log,
                      reintento=cfg.mano_ble_reintento)
    return Mano(puerto=cfg.mano_puerto, baudios=cfg.mano_baudios, simular=cfg.mano == "simulada", log=log,
                timeout_letra=cfg.mano_timeout_letra, vids=cfg.mano_vids, tiempo_simulado=cfg.mano_tiempo_simulado,
                modo=cfg.mano, ble=ble)


def crear_transcriptor(cfg, log, al_cambiar):
    from pgc.adaptadores.whisper import Transcriptor    # importa numpy: solo si se usa
    return Transcriptor(log=log, al_cambiar=al_cambiar, nombre_modelo=cfg.voz_modelo, log_textos=cfg.log_textos)


def crear_tunel(cfg, log, al_cambiar):
    return acceso.Tunel(cfg.puerto_web, log=log, al_cambiar=al_cambiar)


def ip_local():
    return acceso.ip_local()


def puerto_en_uso(puerto):
    import socket
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", puerto)) == 0


RECONOCEDORES = {"kinect": "pgc.adaptadores.kinect.reconocedor:ReconocedorKinect"}


def cargar_reconocedor(cfg, log):
    """'kinect', 'simulado' o 'paquete.modulo:Clase'. Si falla, el simulado (la demo no se cae).

    Si la clase tiene desde_config(cfg), se arma con la configuración; si no, sin argumentos (contrato, regla 6).
    """
    from pgc.adaptadores.reconocedor_simulado import ReconocedorSimulado
    if cfg.reconocedor == "simulado":
        return ReconocedorSimulado()
    try:
        modulo, nombre = RECONOCEDORES.get(cfg.reconocedor, cfg.reconocedor).split(":")
        clase = getattr(importlib.import_module(modulo), nombre)
        return clase.desde_config(cfg) if hasattr(clase, "desde_config") else clase()
    except Exception as ex:
        log(f"[kinect] No se pudo cargar {cfg.reconocedor}: {type(ex).__name__}: {ex} -> simulado")
        return ReconocedorSimulado(detalle="Kinect: no disponible")


def crear_sintetizador(cfg, log, al_cambiar):
    from pgc.adaptadores.voz_salida import SintetizadorCoqui
    return SintetizadorCoqui(cfg.voz_salida_modelo, log=log, al_cambiar=al_cambiar)


def guardar_experimento(protocolo, info):
    from pgc.adaptadores.experimentos import guardar        # importa matplotlib: solo si se usa
    return guardar(protocolo, info)


def crear_lanzador(cfg, log):
    from pgc.adaptadores.kinect.procesos import LanzadorKinect
    return LanzadorKinect(cfg, log)


def construir_sistema(cfg, log=registro.log, *, crear_mano=crear_mano, crear_transcriptor=crear_transcriptor,
                      crear_tunel=crear_tunel, ip_local=ip_local, crear_reconocedor=cargar_reconocedor,
                      crear_sintetizador=crear_sintetizador):
    """Arma el Sistema. Las pruebas pasan sus dobles en lugar de los adaptadores reales."""
    mano = crear_mano(cfg, log)
    publicador = Publicador()
    voz = crear_transcriptor(cfg, log, publicador.notificar)
    tunel = crear_tunel(cfg, log, publicador.notificar)
    sintetizador = crear_sintetizador(cfg, log, publicador.notificar) if cfg.voz_salida else None
    url_local = f"http://{ip_local()}:{cfg.puerto_web}"
    return Sistema(cfg, mano, voz, tunel, url_local, publicador, log, moderador=cargar_moderador(),
                   reconocedor=crear_reconocedor(cfg, log), sintetizador=sintetizador,
                   guardar_experimento=guardar_experimento)


def main(argv=None):
    # Evita que un carácter raro en consola tumbe el servidor
    try:
        sys.stdout.reconfigure(errors="replace")
        sys.stderr.reconfigure(errors="replace")
    except AttributeError:
        pass
    try:
        cfg = config.cargar(argv)
    except config.ErrorConfig as ex:
        print(f"Error de configuración: {ex}", file=sys.stderr)
        return 2

    import uvicorn
    from pgc.api.app import crear_app

    if puerto_en_uso(cfg.puerto_web):
        # Otra plataforma ya corre (otra ventana de iniciar.bat): sus detector y app no son restos
        print(f"Ya hay una plataforma corriendo en el puerto {cfg.puerto_web} (¿otra ventana de iniciar.bat?). "
              "Ciérrala antes de abrir otra.", file=sys.stderr)
        return 3
    sistema = construir_sistema(cfg)
    app = crear_app(sistema)
    lanzador = crear_lanzador(cfg, registro.log)     # detector + app del Kinect (o cámara del PC)
    lanzador.iniciar()
    try:
        uvicorn.run(app, host="0.0.0.0", port=cfg.puerto_web, log_level="warning",
                    ws_max_size=64 * 1024,             # el servidor no espera mensajes de los clientes
                    limit_concurrency=cfg.ws_max_conexiones + 200)
    finally:
        lanzador.detener()                         # y si Python muere a la fuerza, el Job Object los cierra
    return 0
```

## `pgc/config.py`

```python
"""Configuración centralizada.

Prioridad (de menor a mayor): valores por defecto → archivo .env → variables de
entorno PGC_* → opciones de la línea de comandos. Ningún otro módulo lee
variables de entorno: todos reciben un `Config`.
"""
import argparse
import os
from dataclasses import dataclass, fields, replace
from pathlib import Path

from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent.parent
MODOS_MANO = ("auto", "ble", "usb", "simulada")
CAPTURADORES = ("auto", "kinect", "camara_pc", "no")


class ErrorConfig(ValueError):
    """Valor inválido en .env, en una variable de entorno o en una opción."""


@dataclass(frozen=True)
class Config:
    # --- web
    puerto_web: int = 8000
    abrir_navegador: bool = True
    ping_ws: float = 20.0                  # s sin cambios antes de enviar un ping por el WebSocket
    # --- mano
    mano: str = "auto"                     # auto (Bluetooth → USB → simulada) | ble | usb | simulada
    mano_puerto: str | None = None         # None = autodetección por VID
    mano_ble_nombre: str = "Mano-LSC"      # NOMBRE de config_ble.py (con el que la placa se anuncia)
    mano_ble_token: str = ""               # secreto compartido con config_ble.py; vacío = sin Bluetooth
    mano_ble_reintento: float = 10.0       # s entre intentos de conectar por Bluetooth
    mano_baudios: int = 115200
    mano_vids: tuple[int, ...] = (0x303A, 0x1A86, 0x10C4)
    mano_timeout_letra: float = 12.0       # s máximos esperando "ok:<letra>"
    mano_tiempo_simulado: float = 1.2      # duración de una letra en modo simulado
    autodeteccion_cada: float = 3.0        # s entre búsquedas de la mano en reposo
    # --- deletreo y cola
    pausa_letra: float = 0.5               # la letra queda formada un momento para que se lea
    pausa_no_disponible: float = 0.9       # letras que la mano no hace: solo se muestran
    max_caracteres: int = 60
    max_pendientes_cliente: int = 2
    max_cola: int = 30
    historial: int = 6
    # --- voz
    voz: bool = True
    voz_modelo: str = "medium"
    audio_max_mb: int = 10
    audio_max_segundos: float = 15.0       # la página corta a 10 s
    voz_max_en_espera: int = 3             # transcripciones esperando turno (además de la que corre)
    # --- túnel
    tunel: bool = True
    # --- voz de salida (Coqui VITS): dice en los parlantes del PC las frases del Kinect
    voz_salida: bool = True
    voz_salida_modelo: str = "tts_models/es/css10/vits"
    # --- Kinect: "kinect" (detector SVM de integracion_kinect/), "simulado" o "paquete.modulo:Clase"
    reconocedor: str = "kinect"
    kinect_url: str = "http://127.0.0.1:8765"   # detector (server_web_svm.py)
    kinect_intervalo: float = 0.3          # s entre consultas a /spell/status
    kinect_lanzar: bool = True             # arrancar el detector y el capturador junto con la plataforma
    kinect_detector_paralelo: bool = True  # su server_web_svm.py envuelto con lecturas en paralelo (detector_paralelo.py)
    kinect_python: str = ""                # Python del entorno del detector; vacío = buscarlo (ver procesos.py)
    kinect_capturador: str = "auto"        # auto (app C# si está compilada) | kinect | camara_pc | no
    kinect_exe: str = ""                   # LSCKinectFramework.exe; vacío = buscarlo en bin/Release o bin/Debug
    kinect_camara: int = 0                 # cámara del PC para kinect_capturador=camara_pc
    kinect_turno_segundos: float = 120.0   # el turno de un celular se libera tras este tiempo sin usarlo
    kinect_codigo: bool = True             # para tomar el turno hay que escribir el código de 6 dígitos del proyector
    kinect_eco: bool = False               # modo eco al arrancar: la mano repite lo que reconoce el Kinect
    lim_kinect_cliente: int = 60           # controles del Kinect por minuto y celular
    # --- seguridad
    dev: bool = False                      # publica /docs y /openapi.json (opción --dev)
    texto_max_cuerpo: int = 200            # caracteres que acepta la API antes de recortar a max_caracteres
    json_max_kb: int = 16                  # tamaño máximo del cuerpo de una petición (salvo el audio)
    lim_mensaje_ip: int = 20               # peticiones por minuto
    lim_mensaje_cliente: int = 6
    lim_transcribir_ip: int = 10
    lim_transcribir_cliente: int = 4
    lim_previa_ip: int = 240
    lim_general_ip: int = 300
    ws_max_conexiones: int = 100
    ws_max_por_ip: int = 40                # por el túnel, los celulares del mismo WiFi comparten una IP
    log_textos: bool = False               # escribir los textos de los mensajes en el log (solo para depurar)

    @property
    def audio_max_bytes(self):
        return self.audio_max_mb * 1024 * 1024


# ----------------------------------------------------------------- lectura
def _a_bool(texto):
    t = texto.strip().lower()
    if t in ("1", "true", "si", "sí", "yes", "on"):
        return True
    if t in ("0", "false", "no", "off", ""):
        return False
    raise ValueError("se esperaba true o false")


def _a_vids(texto):
    return tuple(int(v.strip(), 16) for v in texto.split(",") if v.strip())


def _convertir(campo, texto):
    if campo.name == "mano_vids":
        return _a_vids(texto)
    if campo.name == "mano_puerto":
        return texto.strip() or None
    tipo = campo.type
    if tipo is bool:
        return _a_bool(texto)
    if tipo is int:
        return int(texto)
    if tipo is float:
        return float(texto)
    return texto.strip()


def _desde_variables(variables):
    """Toma solo las PGC_<CAMPO> conocidas y las convierte a su tipo."""
    valores = {}
    for campo in fields(Config):
        nombre = "PGC_" + campo.name.upper()
        if nombre in variables and variables[nombre] is not None:
            try:
                valores[campo.name] = _convertir(campo, variables[nombre])
            except ValueError as ex:
                raise ErrorConfig(f"{nombre}={variables[nombre]!r} no es válido: {ex}") from None
    return valores


def crear_parser():
    """Las mismas opciones de siempre de servidor.py."""
    ap = argparse.ArgumentParser(description="Servidor de la mano robótica LSC")
    ap.add_argument("--simular", action="store_true", help="no buscar la mano; simularla")
    ap.add_argument("--puerto", help="puerto serial de la mano (ej. COM5)")
    ap.add_argument("--puerto-web", type=int, default=None)
    ap.add_argument("--sin-tunel", action="store_true", help="no lanzar cloudflared")
    ap.add_argument("--sin-voz", action="store_true", help="no cargar Whisper")
    ap.add_argument("--no-abrir", action="store_true", help="no abrir el navegador")
    ap.add_argument("--dev", action="store_true", help="modo desarrollo: publica /docs y /openapi.json")
    return ap


def _desde_opciones(args):
    valores = {}
    if args.simular:
        valores["mano"] = "simulada"
    if args.puerto:
        valores["mano_puerto"] = args.puerto
    if args.puerto_web is not None:
        valores["puerto_web"] = args.puerto_web
    if args.sin_tunel:
        valores["tunel"] = False
    if args.sin_voz:
        valores["voz"] = False
    if args.no_abrir:
        valores["abrir_navegador"] = False
    if args.dev:
        valores["dev"] = True
    return valores


def validar(cfg):
    if cfg.mano not in MODOS_MANO:
        raise ErrorConfig(f"PGC_MANO debe ser uno de {', '.join(MODOS_MANO)} (llegó {cfg.mano!r})")
    if cfg.kinect_capturador not in CAPTURADORES:
        raise ErrorConfig(f"PGC_KINECT_CAPTURADOR debe ser uno de {', '.join(CAPTURADORES)} "
                          f"(llegó {cfg.kinect_capturador!r})")
    if not cfg.kinect_url.startswith(("http://127.0.0.1:", "http://localhost:")):
        raise ErrorConfig("PGC_KINECT_URL debe apuntar a este PC (http://127.0.0.1:<puerto>)")
    if not 1 <= cfg.puerto_web <= 65535:
        raise ErrorConfig(f"puerto web fuera de rango: {cfg.puerto_web}")
    if not cfg.mano_ble_nombre:
        raise ErrorConfig("PGC_MANO_BLE_NOMBRE no puede estar vacío")
    if cfg.mano_ble_token and len(cfg.mano_ble_token) < 16:
        raise ErrorConfig("PGC_MANO_BLE_TOKEN es muy corto (mínimo 16 caracteres)")
    if cfg.mano == "ble" and not cfg.mano_ble_token:
        raise ErrorConfig("PGC_MANO=ble necesita PGC_MANO_BLE_TOKEN (el mismo TOKEN de config_ble.py)")
    for nombre in ("max_caracteres", "max_pendientes_cliente", "max_cola", "historial", "audio_max_mb",
                   "texto_max_cuerpo", "json_max_kb", "lim_mensaje_ip", "lim_mensaje_cliente", "lim_transcribir_ip",
                   "lim_transcribir_cliente", "lim_previa_ip", "lim_general_ip", "ws_max_conexiones", "ws_max_por_ip",
                   "lim_kinect_cliente"):
        if getattr(cfg, nombre) < 1:
            raise ErrorConfig(f"PGC_{nombre.upper()} debe ser mayor que 0")
    if cfg.texto_max_cuerpo < cfg.max_caracteres:
        raise ErrorConfig("PGC_TEXTO_MAX_CUERPO no puede ser menor que PGC_MAX_CARACTERES")
    for nombre in ("pausa_letra", "pausa_no_disponible", "mano_timeout_letra", "mano_tiempo_simulado",
                   "autodeteccion_cada", "ping_ws", "audio_max_segundos", "voz_max_en_espera", "mano_ble_reintento",
                   "kinect_intervalo", "kinect_turno_segundos", "kinect_camara"):
        if getattr(cfg, nombre) < 0:
            raise ErrorConfig(f"PGC_{nombre.upper()} no puede ser negativo")
    return cfg


def cargar(argv=None, entorno=None, archivo_env=None):
    """Arma la configuración final.

    argv: opciones de línea de comandos (None = sys.argv[1:]; [] = ninguna).
    entorno: variables de entorno (None = os.environ).
    archivo_env: ruta del .env (None = .env en la carpeta del proyecto; si no existe, se ignora).
    """
    archivo_env = Path(archivo_env) if archivo_env is not None else RAIZ / ".env"
    valores = {}
    if archivo_env.is_file():
        valores.update(_desde_variables(dotenv_values(archivo_env)))
    valores.update(_desde_variables(os.environ if entorno is None else entorno))
    args = crear_parser().parse_args(argv)
    valores.update(_desde_opciones(args))
    return validar(replace(Config(), **valores))
```

## `pgc/dominio/__init__.py`

```python
"""Reglas puras del sistema: sin hilos, sin red, sin hardware, sin FastAPI.

La única lectura de archivos es la de sus propios datos (datos/letras.json).
"""
```

## `pgc/dominio/abecedario.py`

```python
"""Letras que sabe hacer la mano, como datos (datos/letras.json) y no como código."""
import json
from dataclasses import dataclass, field
from pathlib import Path

RUTA_LETRAS = Path(__file__).resolve().parent.parent.parent / "datos" / "letras.json"
LETRAS_VALIDAS = set("abcdefghijklmnñopqrstuvwxyz")


class ErrorAbecedario(ValueError):
    """letras.json mal formado."""


@dataclass(frozen=True)
class Abecedario:
    por_defecto: frozenset           # letras que hace la mano si no informa las suyas
    aproximaciones: dict = field(default_factory=dict)   # letra → letra con la que se forma (ñ → n)
    con_movimiento: frozenset = frozenset()              # j, z, ñ: la mano no tiene muñeca


def _letras(valor, nombre):
    letras = set(valor)
    raras = letras - LETRAS_VALIDAS
    if raras:
        raise ErrorAbecedario(f"letras.json: '{nombre}' tiene caracteres que no son letras: {''.join(sorted(raras))}")
    return frozenset(letras)


def cargar_abecedario(ruta=RUTA_LETRAS):
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as ex:
        raise ErrorAbecedario(f"No se pudo leer {ruta}: {ex}") from None
    por_defecto = _letras(datos.get("por_defecto", ""), "por_defecto")
    if not por_defecto:
        raise ErrorAbecedario("letras.json: 'por_defecto' está vacío")
    aproximaciones = {}
    for letra, forma in datos.get("aproximaciones", {}).items():
        _letras(letra + forma, "aproximaciones")
        if len(letra) != 1 or len(forma) != 1:
            raise ErrorAbecedario(f"letras.json: aproximación inválida {letra!r} → {forma!r}")
        aproximaciones[letra] = forma
    con_movimiento = _letras("".join(datos.get("con_movimiento", [])), "con_movimiento")
    return Abecedario(por_defecto, aproximaciones, con_movimiento)
```

## `pgc/dominio/experimento.py`

```python
"""Análisis del protocolo de letras: tabla por letra, matriz de confusión y causa probable de cada fallo.

Funciones puras (sin archivos ni gráficas): las usan el guardado de experimentos y las pruebas.

Un intento es un dict con: letra (pedida), intento (1..n), reconocida (letra o None), tiempo_s (o None),
mano_pct (0–100: imágenes con una mano), prediccion_frecuente, margen_medio, estable_max_s,
cambios (veces que cambió la predicción), sin_letra_pct, motivo_frecuente.
"""
from collections import Counter

NINGUNA = "(ninguna)"
TIEMPO_CONFIRMACION = 0.7            # el de su detector (server_deletreo_svm.py); solo para explicar causas


def resultado_de(intento):
    if intento["reconocida"] is None:
        return "no_detectada"
    return "acierto" if intento["reconocida"] == intento["letra"] else "confusion"


def resumen_por_letra(intentos):
    """[{letra, intentos, aciertos, confusiones {letra: n}, no_detectadas, exactitud_pct, tiempo_medio_s}]"""
    por_letra = {}
    for it in intentos:
        por_letra.setdefault(it["letra"], []).append(it)
    filas = []
    for letra, lista in por_letra.items():
        aciertos = [it for it in lista if resultado_de(it) == "acierto"]
        confusiones = Counter(it["reconocida"] for it in lista if resultado_de(it) == "confusion")
        tiempos = [it["tiempo_s"] for it in aciertos if it["tiempo_s"] is not None]
        filas.append({
            "letra": letra, "intentos": len(lista), "aciertos": len(aciertos),
            "confusiones": dict(confusiones.most_common()),
            "no_detectadas": sum(1 for it in lista if resultado_de(it) == "no_detectada"),
            "exactitud_pct": round(100 * len(aciertos) / len(lista), 1),
            "tiempo_medio_s": round(sum(tiempos) / len(tiempos), 2) if tiempos else None,
        })
    return filas


def matriz_confusion(intentos, letras=None):
    """(filas = letra pedida, columnas = letras reconocidas + "(ninguna)", matriz de conteos)."""
    pedidas = letras or sorted({it["letra"] for it in intentos})
    columnas = sorted(set(pedidas) | {it["reconocida"] for it in intentos if it["reconocida"]}) + [NINGUNA]
    matriz = [[0] * len(columnas) for _ in pedidas]
    for it in intentos:
        if it["letra"] in pedidas:
            matriz[pedidas.index(it["letra"])][columnas.index(it["reconocida"] or NINGUNA)] += 1
    return pedidas, columnas, matriz


def causa_probable(letra, intentos):
    """La explicación más probable de por qué la letra falla (o None si no falla), con lo que lo sugiere."""
    lista = [it for it in intentos if it["letra"] == letra]
    fallos = [it for it in lista if resultado_de(it) != "acierto"]
    if not fallos:
        return None
    media = lambda clave: sum(it.get(clave) or 0 for it in fallos) / len(fallos)
    confundida = Counter(it["reconocida"] for it in fallos if it["reconocida"])
    predicha = Counter(it["prediccion_frecuente"] for it in fallos if it.get("prediccion_frecuente"))
    if media("mano_pct") < 50:
        return ("mano", f"La mano casi no se detecta ({media('mano_pct'):.0f}% de las imágenes): "
                        "distancia, luz o la mano fuera de cuadro")
    if predicha and predicha.most_common(1)[0][0] == "sin_letra" or media("sin_letra_pct") >= 50:
        return ("sin_letra", "El modelo la ve como «sin letra»: el ángulo o la forma difieren de los ejemplos "
                             "con que se entrenó (faltan ejemplos de esa letra en esas condiciones)")
    if confundida:
        otra, n = confundida.most_common(1)[0]
        return ("parecida", f"Se confunde con {otra.upper()} ({n} de {len(lista)}): letras parecidas en los "
                            "puntos de la mano, o el ángulo hace que se vean iguales")
    if predicha and predicha.most_common(1)[0][0] not in (letra, "sin_letra"):
        otra = predicha.most_common(1)[0][0]
        return ("parecida", f"El modelo la ve casi siempre como {otra.upper()} pero sin llegar a confirmarla")
    if media("cambios") >= 3:
        return ("inestable", f"La predicción cambia mucho ({media('cambios'):.0f} veces por intento): "
                             "la mano se mueve, o está justo entre dos letras")
    if media("estable_max_s") < TIEMPO_CONFIRMACION:
        return ("tiempo", f"Se reconoce pero no se mantiene {TIEMPO_CONFIRMACION} s seguidos "
                          f"(máximo {media('estable_max_s'):.2f} s): tiempo de confirmación")
    if media("margen_medio") < 0.3:
        return ("margen", "El modelo duda (margen bajo entre la primera y la segunda letra)")
    return ("otra", "Sin una causa clara en los datos: repetirla con más cuidado y mirar la vista de diagnóstico")


def informe(intentos, letras=None):
    """Resumen para mostrar y guardar: exactitud total, por letra y causas de los fallos."""
    filas = resumen_por_letra(intentos)
    total = len(intentos)
    aciertos = sum(f["aciertos"] for f in filas)
    tiempos = [it["tiempo_s"] for it in intentos if resultado_de(it) == "acierto" and it["tiempo_s"] is not None]
    causas = {}
    for f in filas:
        c = causa_probable(f["letra"], intentos)
        if c:
            causas[f["letra"]] = {"tipo": c[0], "texto": c[1]}
    return {
        "intentos": total, "aciertos": aciertos,
        "exactitud_pct": round(100 * aciertos / total, 1) if total else 0.0,
        "tiempo_medio_s": round(sum(tiempos) / len(tiempos), 2) if tiempos else None,
        "por_letra": filas, "causas": causas,
        "fallan": [f["letra"] for f in sorted(filas, key=lambda f: f["exactitud_pct"]) if f["aciertos"] < f["intentos"]],
    }
```

## `pgc/dominio/moderacion.py`

```python
"""Filtro básico de palabras ofensivas antes de mostrar un texto en el proyector.

Es una defensa razonable para una sala, no un sistema infalible: la lista vive
en datos/palabras_bloqueadas.txt y el presentador puede saltar un mensaje.
"""
import re
import unicodedata
from pathlib import Path

RUTA_PALABRAS = Path(__file__).resolve().parent.parent.parent / "datos" / "palabras_bloqueadas.txt"
LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
LARGO_PREFIJO = 7          # raíces de 7+ letras también bloquean palabras que empiezan por ellas


def _sin_tildes(texto):
    return "".join(c if c in "ñÑ" else
                   "".join(ch for ch in unicodedata.normalize("NFD", c) if unicodedata.category(ch) != "Mn")
                   for c in texto)


def _reducir(palabra):
    """Una sola letra por grupo de repetidas: 'gonorreaaa' → 'gonorea'."""
    return re.sub(r"(.)\1+", r"\1", palabra)


def _estirada(palabra):
    """Tres o más letras iguales seguidas ('perrrra'): señal de que se quiere esquivar el filtro."""
    return re.search(r"(.)\1\1", palabra) is not None


def palabras_normalizadas(texto):
    texto = _sin_tildes((texto or "").lower()).translate(LEET)
    return re.findall(r"[a-zñ]+", texto)


class Moderador:
    def __init__(self, bloqueadas):
        self.exactas = set(palabras_normalizadas(" ".join(bloqueadas)))
        self.reducidas = {_reducir(p) for p in self.exactas}

    @staticmethod
    def _coincide(palabra, conjunto):
        if palabra in conjunto or palabra.rstrip("s") in conjunto \
                or (palabra.endswith("es") and palabra[:-2] in conjunto):
            return True
        return any(palabra.startswith(r) for r in conjunto if len(r) >= LARGO_PREFIJO)

    def _bloqueada(self, palabra):
        if self._coincide(palabra, self.exactas):
            return True
        # "pera" no es "perra"; "perrrra" sí: solo se reduce lo que viene estirado
        return _estirada(palabra) and self._coincide(_reducir(palabra), self.reducidas)

    def es_ofensivo(self, texto):
        palabras = palabras_normalizadas(texto)
        # Letras sueltas seguidas se leen juntas: "h p" → "hp", "p u t a" → "puta"
        candidatas, sueltas = list(palabras), []
        for p in palabras + [""]:
            if len(p) == 1:
                sueltas.append(p)
                continue
            if len(sueltas) >= 2:
                candidatas.append("".join(sueltas))
            sueltas = []
        return any(self._bloqueada(p) for p in candidatas)


def cargar_moderador(ruta=RUTA_PALABRAS):
    lineas = Path(ruta).read_text(encoding="utf-8").splitlines()
    return Moderador([l.strip() for l in lineas if l.strip() and not l.lstrip().startswith("#")])
```

## `pgc/dominio/ordenes.py`

```python
"""Qué órdenes recibe la mano por cada paso de la secuencia.

Reglas:
  * espacio → "reset" (mano abierta = separación entre palabras);
  * letra igual a la forma que la mano ya tiene (ll, rr, ñn...) → "reset" y luego
    la letra; sin esto los servos ya estarían en su sitio y no se notaría;
  * letra no disponible → ninguna orden (solo se muestra en pantalla).
"""
RESET = "reset"


def ordenes_para(paso, forma):
    """Órdenes para `paso` si la mano tiene formada la letra `forma` (None = abierta).

    La última orden de la lista es la que decide si el paso salió bien.
    """
    if paso["tipo"] == "espacio":
        return [RESET]
    letra = paso["l"]
    if not letra:
        return []
    return [RESET, letra] if letra == forma else [letra]


def forma_despues(paso, forma, ok):
    """Letra que queda formada tras el paso (None = mano abierta o desconocida)."""
    if paso["tipo"] == "espacio":
        return None
    if paso["l"]:
        return paso["l"] if ok else None
    return forma                       # letra no disponible: la mano no se movió


def planificar_ordenes(pasos):
    """Todas las órdenes de un mensaje si la mano confirma cada una (incluye el reset final)."""
    ordenes, forma = [], None
    for paso in pasos:
        ordenes += ordenes_para(paso, forma)
        forma = forma_despues(paso, forma, True)
    return ordenes + [RESET]
```

## `pgc/dominio/participante.py`

```python
"""Nombre opcional del participante (ADR-7): corto, legible y sin datos de más."""
import re

MAX_NOMBRE = 20
ANONIMO = "Anónimo"          # autor de los mensajes de quien no puso nombre
_PATRON = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 .'\-]+$")
MSG_NOMBRE_INVALIDO = f"Usa solo letras en tu nombre (máximo {MAX_NOMBRE})."
MSG_NOMBRE_OFENSIVO = "Ese nombre no se puede mostrar. Prueba con otro."
MSG_BLOQUEADO = "El presentador pausó tu participación en esta sesión. ¡Gracias por participar!"


def normalizar_nombre(texto):
    """'  ana   maría ' → 'ana maría'; vacío → None. ValueError si no es un nombre razonable."""
    if texto is None:
        return None
    nombre = re.sub(r"\s+", " ", texto).strip()
    if not nombre:
        return None
    if len(nombre) > MAX_NOMBRE or not _PATRON.match(nombre):
        raise ValueError(MSG_NOMBRE_INVALIDO)
    return nombre
```

## `pgc/dominio/texto.py`

```python
"""Convierte un texto libre en la secuencia de letras que la mano puede hacer."""
import re
import unicodedata

from pgc.dominio.abecedario import cargar_abecedario

_ABECEDARIO = cargar_abecedario()

# Letras por defecto (se reemplazan por las que reporte el ESP32 con "letras")
LETRAS_POR_DEFECTO = _ABECEDARIO.por_defecto

# Letras que la mano no puede hacer exactas y se aproximan con otra forma
APROXIMACIONES = _ABECEDARIO.aproximaciones

DIGITOS = {
    "0": "cero", "1": "uno", "2": "dos", "3": "tres", "4": "cuatro",
    "5": "cinco", "6": "seis", "7": "siete", "8": "ocho", "9": "nueve",
}

MAX_CARACTERES = 60


def _quitar_tilde(c: str) -> str:
    if c == "ñ":
        return c
    base = unicodedata.normalize("NFD", c)
    return "".join(ch for ch in base if unicodedata.category(ch) != "Mn")


def limpiar(texto: str, maximo: int = MAX_CARACTERES) -> str:
    texto = (texto or "").strip().lower()
    texto = re.sub(r"\d", lambda m: " " + DIGITOS[m.group()] + " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:maximo]


def a_secuencia(texto: str, letras_mano=None, maximo: int = MAX_CARACTERES):
    """Devuelve una lista de pasos: {"c": mostrar, "l": enviar|None, "tipo": ...}

    tipo: "ok" (la mano la hace), "aprox" (se aproxima con otra letra),
          "nd" (no disponible, se muestra pero no se envía), "espacio".
    """
    letras_mano = letras_mano or LETRAS_POR_DEFECTO
    pasos = []
    for c in limpiar(texto, maximo):
        if c == " ":
            if pasos and pasos[-1]["tipo"] != "espacio":
                pasos.append({"c": " ", "l": None, "tipo": "espacio"})
            continue
        c = _quitar_tilde(c)
        if c in APROXIMACIONES and APROXIMACIONES[c] in letras_mano:
            pasos.append({"c": c.upper(), "l": APROXIMACIONES[c], "tipo": "aprox"})
        elif c in letras_mano:
            pasos.append({"c": c.upper(), "l": c, "tipo": "ok"})
        elif c.isalpha():
            pasos.append({"c": c.upper(), "l": None, "tipo": "nd"})
        # signos de puntuación se ignoran
    while pasos and pasos[-1]["tipo"] == "espacio":
        pasos.pop()
    return pasos


if __name__ == "__main__":
    for t in ["Hola mundo", "Señor José 2026", "¡Gracias, jurado!"]:
        print(t, "->", [(p["c"], p["tipo"]) for p in a_secuencia(t)])
```

## `pgc/puertos/__init__.py`

```python
"""Interfaces (typing.Protocol) entre la aplicación y el mundo exterior."""
```

## `pgc/puertos/acceso.py`

```python
"""Puerto del acceso público (HTTPS) para los celulares."""
from typing import Protocol


class AccesoPublico(Protocol):
    estado: str                # "apagado" | "iniciando" | "activo" | "error" | "no instalado"
    url: str | None            # https://... cuando está activo

    def iniciar(self) -> None:
        """Arranca en segundo plano; avisa con al_cambiar cuando cambia la URL o el estado."""

    def detener(self) -> None:
        ...
```

## `pgc/puertos/mano.py`

```python
"""Puerto de la mano robótica: lo único que la aplicación sabe de ella."""
from typing import Protocol


class PuertoMano(Protocol):
    letras: set | None             # letras que informó la mano; None = usar las por defecto

    @property
    def conectada(self) -> bool:   # hay una mano física respondiendo
        ...

    @property
    def modo(self) -> str:         # "real" | "simulada"  (lo muestra la pantalla)
        ...

    @property
    def medio(self) -> str | None:    # "ble" | "usb" | None (simulada)
        ...

    @property
    def puerto(self) -> str | None:   # "COM5", el nombre de la mano por Bluetooth ("Mano-LSC"), o None
        ...

    def conectar(self) -> bool:
        """Intenta conectar la mano física; si no puede, queda simulada."""

    def cerrar(self) -> None:
        """Suelta la conexión física (la mano queda simulada)."""

    def hacer(self, orden: str) -> bool:
        """Forma una letra o 'reset'. Bloquea hasta la confirmación; True si la mano confirmó."""

    def reset(self) -> bool:
        """Abre la mano (equivale a hacer('reset'))."""

    def revisar(self) -> bool:
        """Entre mensajes: latido, respaldo y búsqueda de la mano. True si cambió la conexión."""
```

## `pgc/puertos/reconocedor.py`

```python
"""Puerto del reconocimiento de señas (Kinect + modelos). Contrato: docs/CONTRATO_KINECT.md."""
from dataclasses import dataclass
from typing import Callable, Literal, Protocol

TIPOS_EVENTO = ("letra", "espacio", "borrar", "fin")
ESTADOS = ("apagado", "cargando", "listo", "sin_persona", "error")
LETRAS_VALIDAS = set("abcdefghijklmnñopqrstuvwxyz")


@dataclass(frozen=True)
class EventoSena:
    tipo: Literal["letra", "espacio", "borrar", "fin"]
    letra: str | None = None      # "a".."z" o "ñ", en minúscula; solo si tipo == "letra"
    confianza: float = 1.0        # 0.0 – 1.0
    modelo: str = ""              # qué modelo decidió: "A-mlp", "B-gru", "C-cnn"...
    instante: float = 0.0         # time.monotonic() del cuadro que confirmó la letra
    latencia_ms: float = 0.0      # desde la captura del cuadro hasta la decisión


EstadoReconocedor = Literal["apagado", "cargando", "listo", "sin_persona", "error"]


class ReconocedorSenas(Protocol):
    estado: EstadoReconocedor
    detalle: str                  # texto corto que sale en el proyector, p. ej. "Kinect v1 · modelo A"

    def iniciar(self, al_evento: Callable[[EventoSena], None],
                al_cambiar_estado: Callable[[], None]) -> None:
        """Carga modelos y abre el Kinect EN SEGUNDO PLANO; retorna enseguida."""

    def detener(self) -> None:
        """Libera el Kinect y los hilos. Debe poder llamarse más de una vez."""


def problemas_del_evento(evento):
    """Lista de incumplimientos del contrato (vacía si el evento es válido)."""
    p = []
    if not isinstance(evento, EventoSena):
        return [f"no es un EventoSena: {type(evento).__name__}"]
    if evento.tipo not in TIPOS_EVENTO:
        p.append(f"tipo desconocido: {evento.tipo!r}")
    if evento.tipo == "letra" and (not isinstance(evento.letra, str) or evento.letra not in LETRAS_VALIDAS):
        p.append(f"letra inválida: {evento.letra!r} (debe ser a-z o ñ en minúscula)")
    if evento.tipo != "letra" and evento.letra is not None:
        p.append(f"un evento '{evento.tipo}' no lleva letra")
    if not 0.0 <= evento.confianza <= 1.0:
        p.append(f"confianza fuera de 0–1: {evento.confianza}")
    if evento.latencia_ms < 0:
        p.append("latencia negativa")
    return p
```

## `pgc/puertos/sintetizador.py`

```python
"""Puerto de texto → voz (fase 4: Coqui VITS en español)."""
from typing import Protocol


class Sintetizador(Protocol):
    estado: str                # "sin cargar" | "cargando" | "listo" | "error" | "desactivado"

    def cargar_en_segundo_plano(self) -> None:
        ...

    def decir(self, texto: str) -> None:
        """Dice el texto en voz alta. Bloquea hasta terminar de hablar."""
```

## `pgc/puertos/transcriptor.py`

```python
"""Puerto de voz → texto."""
from typing import Protocol


class Transcriptor(Protocol):
    estado: str                # "sin cargar" | "cargando" | "listo" | "error" | "desactivado"
    dispositivo: str | None    # "cuda float16" | "cpu int8" | None

    @property
    def listo(self) -> bool:
        ...

    def cargar_en_segundo_plano(self) -> None:
        """Carga el modelo en otro hilo; avisa con al_cambiar al terminar."""

    def transcribir(self, ruta_audio: str) -> str:
        """Texto reconocido (puede ser vacío). Bloquea; una transcripción a la vez."""

    def duracion(self, ruta_audio: str) -> float | None:
        """Segundos de audio, o None si no se puede saber."""
```

## `pgc/registro.py`

```python
"""Registro en consola: una línea con hora por evento, segura entre hilos."""
import threading
import time

_lock_log = threading.Lock()


def log(msg):
    with _lock_log:
        print(time.strftime("%H:%M:%S"), msg, flush=True)
```

## `web/diagnostico.html`

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="pgc-admin" content="">
<title>Diagnóstico del Kinect · Mano bidireccional LSC</title>
<script>
  try { var t = localStorage.getItem("tema"); if (t === "light" || t === "dark") document.documentElement.dataset.theme = t; } catch (e) {}
</script>
<style>
  :root {
    --fondo: #FFFFFF; --superficie: #F4F6F5; --linea: #E4E8E6;
    --texto: #141917; --texto-2: #4F5854; --texto-3: #7A837F;
    --acento: #00482B; --acento-suave: #EEF6F2; --punto-ok: #1A7A55;
    --aviso: #A86A00; --error: #C2362B; --placa-logo: transparent;
    --fuente: "Segoe UI Variable Text", -apple-system, system-ui, Roboto, "Segoe UI", sans-serif;
    color-scheme: light;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --fondo: #121615; --superficie: #1A1F1D; --linea: #2A322E;
      --texto: #EDF1EF; --texto-2: #A3ADA8; --texto-3: #7D8782;
      --acento: #74BA9A; --acento-suave: #0F2A1F; --punto-ok: #74BA9A;
      --aviso: #E2B04A; --error: #EE7A6E; --placa-logo: #F4F6F5; color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --fondo: #121615; --superficie: #1A1F1D; --linea: #2A322E;
    --texto: #EDF1EF; --texto-2: #A3ADA8; --texto-3: #7D8782;
    --acento: #74BA9A; --acento-suave: #0F2A1F; --punto-ok: #74BA9A;
    --aviso: #E2B04A; --error: #EE7A6E; --placa-logo: #F4F6F5; color-scheme: dark;
  }
  * { box-sizing: border-box; }
  [hidden] { display: none !important; }
  html, body { margin: 0; background: var(--fondo); color: var(--texto); }
  body { font-family: var(--fuente); padding: 20px 28px 32px; -webkit-font-smoothing: antialiased; }
  header { display: flex; align-items: center; gap: 12px; }
  .placa { background: var(--placa-logo); border-radius: 8px; padding: 3px 4px; display: grid; }
  .placa img { height: 40px; display: block; }
  .pgc { font-size: 12px; font-weight: 600; color: var(--acento); border: 1.5px solid var(--acento); border-radius: 999px; padding: 2px 9px; }
  h1 { margin: 0; font-size: 22px; font-weight: 600; }
  header .derecha { margin-left: auto; display: flex; gap: 8px; align-items: center; }
  a, .boton { font: inherit; font-size: 14px; color: var(--texto-2); background: transparent; border: 1px solid var(--linea);
    border-radius: 999px; padding: 6px 14px; cursor: pointer; text-decoration: none; }
  .boton:hover:not(:disabled), a:hover { color: var(--texto); border-color: var(--texto-3); }
  .boton:disabled { opacity: .45; cursor: default; }
  .boton.principal { background: var(--acento); color: var(--fondo); border-color: var(--acento); font-weight: 600; }
  main { display: grid; grid-template-columns: minmax(420px, 1.1fr) 1fr; gap: 28px; margin-top: 20px; }
  .tarjeta { background: var(--superficie); border-radius: 16px; padding: 18px 20px; }
  h2 { margin: 0 0 12px; font-size: 15px; font-weight: 600; color: var(--texto-2); text-transform: uppercase; letter-spacing: .04em; }
  #cam { width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 12px; background: var(--linea); display: block; }
  .fila-botones { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
  .datos { display: grid; grid-template-columns: auto 1fr; gap: 10px 18px; align-items: center; font-size: 17px; }
  .datos dt { color: var(--texto-2); font-size: 14px; }
  .datos dd { margin: 0; }
  .punto { display: inline-block; width: .65em; height: .65em; border-radius: 50%; margin-right: .4em; background: var(--texto-3); }
  .punto.ok { background: var(--punto-ok); } .punto.aviso { background: var(--aviso); } .punto.error { background: var(--error); }
  .glifo { font-size: 64px; font-weight: 700; line-height: 1; color: var(--acento); text-transform: uppercase; }
  .glifo.sin { color: var(--texto-3); font-size: 28px; text-transform: none; }
  .barra { position: relative; height: 12px; border-radius: 6px; background: var(--linea); overflow: hidden; }
  .barra > span { position: absolute; inset: 0 auto 0 0; background: var(--acento); border-radius: 6px; transition: width .1s linear; }
  .barra.aviso > span { background: var(--aviso); }
  .nota { font-size: 13px; color: var(--texto-3); }
  .motivo { margin-top: 16px; padding: 14px 16px; border-radius: 12px; font-size: 22px; font-weight: 600; background: var(--fondo); }
  .motivo.ok { color: var(--punto-ok); } .motivo.aviso { color: var(--aviso); } .motivo.error { color: var(--error); }
  .texto-detector { font-size: 26px; font-weight: 600; letter-spacing: .05em; min-height: 1.2em; }
  .protocolo { margin-top: 28px; }
  .config { display: flex; gap: 16px; align-items: end; flex-wrap: wrap; font-size: 14px; color: var(--texto-2); }
  .config label { display: grid; gap: 4px; }
  .config input { font: inherit; font-size: 15px; padding: 6px 10px; border-radius: 8px; border: 1px solid var(--linea);
    background: var(--fondo); color: var(--texto); }
  .config input[name=letras] { width: 360px; }
  .config input[type=number] { width: 80px; }
  .pedido { margin-top: 18px; font-size: 44px; font-weight: 700; letter-spacing: -.01em; min-height: 1.2em; }
  .pedido.retirar { color: var(--texto-2); font-size: 32px; }
  .progreso { color: var(--texto-2); }
  table { border-collapse: collapse; width: 100%; margin-top: 12px; font-size: 14px; }
  th, td { text-align: left; padding: 5px 8px; border-bottom: 1px solid var(--linea); }
  th { color: var(--texto-2); font-weight: 600; }
  .acierto { color: var(--punto-ok); } .confusion { color: var(--aviso); } .no_detectada { color: var(--error); }
  .sin-token { margin-top: 40px; font-size: 20px; }
  @media (max-width: 1000px) { main { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<header>
  <div class="placa"><img src="/logo-udec.png" alt="Universidad de Cundinamarca"></div>
  <span class="pgc">PGC</span>
  <h1>Diagnóstico del Kinect</h1>
  <div class="derecha">
    <a href="/pantalla">Volver al proyector</a>
    <button id="btnTema" class="boton" type="button">Tema</button>
  </div>
</header>

<p id="sinToken" class="sin-token" hidden>Esta vista solo funciona en el PC del proyector: abre <b>http://127.0.0.1:8000/diagnostico</b> allí.</p>

<main id="principal">
  <section class="tarjeta">
    <h2>Cámara</h2>
    <img id="cam" alt="Cámara del Kinect con los puntos de la mano">
    <div class="fila-botones">
      <button class="boton" type="button" data-kin="iniciar">Iniciar deletreo</button>
      <button class="boton" type="button" data-kin="detener">Detener</button>
      <button class="boton" type="button" data-kin="limpiar">Limpiar</button>
    </div>
    <p class="nota">Texto del detector:</p>
    <div id="texto" class="texto-detector"></div>
  </section>

  <section class="tarjeta">
    <h2>En vivo</h2>
    <dl class="datos">
      <dt>Mano</dt><dd id="mano">—</dd>
      <dt>Letra posible</dt><dd><span id="letra" class="glifo sin">—</span></dd>
      <dt>Segunda opción</dt><dd id="segunda">—</dd>
      <dt>Margen</dt><dd><div class="barra"><span id="margenBarra" style="width:0"></span></div>
        <span id="margen" class="nota">—</span> <span class="nota">· diferencia entre la 1.ª y la 2.ª letra según el SVM (no es una probabilidad: su modelo no la calcula)</span></dd>
      <dt>Estable</dt><dd><div id="estableCaja" class="barra aviso"><span id="estableBarra" style="width:0"></span></div>
        <span id="estable" class="nota">—</span></dd>
      <dt>Imágenes</dt><dd id="imagenes">—</dd>
      <dt>Lista para otra letra</dt><dd id="armado">—</dd>
      <dt>Deletreo</dt><dd id="activo">—</dd>
    </dl>
    <div id="motivo" class="motivo">Conectando…</div>
    <p id="estadoDetector" class="nota"></p>
  </section>
</main>

<section id="protocolo" class="tarjeta protocolo">
  <h2>Protocolo de prueba de letras</h2>
  <form id="formProtocolo" class="config">
    <label>Letras (vacío = todas las del modelo)<input name="letras" autocomplete="off" placeholder="a b c d e …"></label>
    <label>Repeticiones<input name="repeticiones" type="number" min="1" max="20" value="5"></label>
    <label>Máx. por intento (s)<input name="tiempo" type="number" min="2" max="30" step="0.5" value="8"></label>
    <button id="btnProtocolo" class="boton principal" type="submit">Iniciar protocolo</button>
    <button id="btnDetenerProtocolo" class="boton" type="button" disabled>Detener</button>
  </form>
  <div id="pedido" class="pedido"></div>
  <div id="progreso" class="progreso"></div>
  <div id="avisoProtocolo" class="nota"></div>
  <table id="tablaUltimos" hidden>
    <thead><tr><th>Pedida</th><th>Intento</th><th>Resultado</th><th>Reconocida</th><th>Tiempo (s)</th><th>Con mano</th><th>Lo que más pasó</th></tr></thead>
    <tbody></tbody>
  </table>
  <div id="final" hidden>
    <p id="finalResumen"></p>
    <table id="tablaFinal">
      <thead><tr><th>Letra</th><th>Aciertos</th><th>Confusiones</th><th>No detectadas</th><th>Tiempo medio (s)</th><th>Causa probable</th></tr></thead>
      <tbody></tbody>
    </table>
  </div>
</section>

<script>
(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const TOKEN = document.querySelector('meta[name="pgc-admin"]').content;
  const cab = { "X-PGC-Admin": TOKEN };
  if (!TOKEN) { $("#principal").hidden = true; $("#protocolo").hidden = true; $("#sinToken").hidden = false; return; }

  // ---------- tema
  const raiz = document.documentElement;
  $("#btnTema").addEventListener("click", () => {
    const oscuro = (raiz.dataset.theme || (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light")) === "dark";
    raiz.dataset.theme = oscuro ? "light" : "dark";
    try { localStorage.setItem("tema", raiz.dataset.theme); } catch (e) {}
  });

  const post = (ruta, cuerpo) => fetch(ruta, { method: "POST", headers: { ...cab, "Content-Type": "application/json" },
    body: JSON.stringify(cuerpo || {}) });
  document.querySelectorAll("[data-kin]").forEach((b) =>
    b.addEventListener("click", () => post("/api/kinect/control", { accion: b.dataset.kin })));

  // ---------- en vivo
  function clasificar(motivo) {
    if (!motivo) return "";
    if (motivo.startsWith("Letra confirmada") || motivo.startsWith("Confirmando")) return "ok";
    if (motivo.startsWith("Mano no detectada") || motivo.startsWith("Más de una") || motivo.startsWith("Puntos")
        || motivo.includes("sin letra")) return "error";
    return "aviso";
  }
  function pintar(d) {
    const manos = d.manos;
    $("#mano").textContent = "";
    const p = document.createElement("span");
    p.className = "punto " + (manos === 1 ? "ok" : manos ? "aviso" : "error");
    $("#mano").append(p, manos === 1 ? "1 mano" : manos ? manos + " manos (debe ser una)" : "No detectada");
    const letra = d.prediccion;
    $("#letra").className = "glifo" + (letra && letra !== "sin_letra" ? "" : " sin");
    $("#letra").textContent = letra ? (letra === "sin_letra" ? "sin letra" : letra) : "—";
    $("#segunda").textContent = d.segunda ? (d.segunda === "sin_letra" ? "sin letra" : d.segunda.toUpperCase()) : "—";
    $("#margen").textContent = d.margen == null ? "—" : d.margen.toFixed(2);
    $("#margenBarra").style.width = d.margen == null ? "0" : Math.min(100, d.margen * 50) + "%";
    const tc = d.tiempo_confirmacion || 0.7;
    $("#estable").textContent = (d.estable_s || 0).toFixed(1) + " de " + tc + " s";
    $("#estableBarra").style.width = Math.min(100, 100 * (d.estable_s || 0) / tc) + "%";
    $("#estableCaja").className = "barra" + ((d.estable_s || 0) >= tc ? "" : " aviso");
    $("#imagenes").textContent = (d.confirmaciones || 0) + " de " + (d.confirmaciones_necesarias || 4);
    $("#armado").textContent = d.armado ? "Sí" : "No: retira la mano " + (d.tiempo_liberacion || 0.5) + " s";
    $("#activo").textContent = d.activo ? "Iniciado" : "Detenido";
    $("#motivo").className = "motivo " + clasificar(d.motivo);
    $("#motivo").textContent = d.motivo || "—";
    $("#texto").textContent = d.texto || "";
    $("#estadoDetector").textContent = "Estado del detector: " + (d.estado || "—") +
      (d.edad_ms != null ? " · última imagen hace " + d.edad_ms + " ms" : "");
  }
  async function bucleDiagnostico() {
    for (;;) {
      try {
        const r = await fetch("/api/kinect/diagnostico", { headers: cab, cache: "no-store" });
        if (r.ok) pintar(await r.json());
        else {
          const e = await r.json().catch(() => ({}));
          $("#motivo").className = "motivo error";
          $("#motivo").textContent = e.detail || "Sin diagnóstico";
        }
      } catch (e) {}
      await new Promise((listo) => setTimeout(listo, 100));
    }
  }

  // ---------- cámara (la siguiente imagen apenas existe)
  let cuadro = null, urlCam = null;
  async function bucleCamara() {
    for (;;) {
      let pausa = 300;
      try {
        const r = await fetch("/api/kinect/imagen" + (cuadro === null ? "" : "?despues=" + cuadro), { headers: cab, cache: "no-store" });
        if (r.ok) {
          pausa = r.headers.has("X-Kinect-Cuadro") ? 0 : 200;
          const nuevo = r.headers.get("X-Kinect-Cuadro");
          if (nuevo !== cuadro) {
            cuadro = nuevo;
            const url = URL.createObjectURL(await r.blob());
            $("#cam").src = url;
            if (urlCam) URL.revokeObjectURL(urlCam);
            urlCam = url;
          }
        }
      } catch (e) {}
      await new Promise((listo) => setTimeout(listo, pausa));
    }
  }

  // ---------- protocolo
  const RESULTADOS = { acierto: "Acierto", confusion: "Confundida", no_detectada: "No detectada" };
  const resultadoDe = (it) => it.reconocida == null ? "no_detectada" : it.reconocida === it.letra ? "acierto" : "confusion";
  function celda(fila, texto, clase) { const td = document.createElement("td"); td.textContent = texto; if (clase) td.className = clase; fila.appendChild(td); }
  function pintarProtocolo(e) {
    const corriendo = e.fase === "pedir" || e.fase === "retirar";
    $("#btnProtocolo").disabled = corriendo;
    $("#btnDetenerProtocolo").disabled = !corriendo;
    $("#pedido").className = "pedido" + (e.fase === "retirar" ? " retirar" : "");
    $("#pedido").textContent = e.fase === "pedir" ? "Haz la letra " + e.letra.toUpperCase() + " · intento " + e.intento + " de " + e.repeticiones
      : e.fase === "retirar" ? "Retira la mano" : e.fase === "terminado" ? "Protocolo terminado" : e.fase === "detenido" ? "Protocolo detenido" : "";
    $("#progreso").textContent = e.total ? e.hecho + " de " + e.total + " intentos" : "";
    $("#avisoProtocolo").textContent = e.error ? "Error: " + e.error : e.carpeta ? "Resultados guardados en " + e.carpeta : "";
    const ult = e.ultimos || [];
    $("#tablaUltimos").hidden = !ult.length;
    const cuerpo = $("#tablaUltimos tbody");
    cuerpo.textContent = "";
    ult.forEach((it) => {
      const fila = document.createElement("tr");
      const r = resultadoDe(it);
      celda(fila, it.letra.toUpperCase()); celda(fila, it.intento); celda(fila, RESULTADOS[r], r);
      celda(fila, it.reconocida ? it.reconocida.toUpperCase() : "—"); celda(fila, it.tiempo_s != null ? it.tiempo_s : "—");
      celda(fila, it.mano_pct + " %"); celda(fila, it.motivo_frecuente || "—");
      cuerpo.appendChild(fila);
    });
    const inf = e.informe;
    $("#final").hidden = !inf;
    if (inf) {
      $("#finalResumen").textContent = "Exactitud: " + inf.exactitud_pct + " % (" + inf.aciertos + " de " + inf.intentos + ")" +
        (inf.tiempo_medio_s ? " · tiempo medio hasta confirmar: " + inf.tiempo_medio_s + " s" : "") +
        (inf.fallan.length ? " · fallan: " + inf.fallan.map((l) => l.toUpperCase()).join(", ") : "");
      const tf = $("#tablaFinal tbody");
      tf.textContent = "";
      inf.por_letra.forEach((f) => {
        const fila = document.createElement("tr");
        celda(fila, f.letra.toUpperCase()); celda(fila, f.aciertos + "/" + f.intentos);
        celda(fila, Object.entries(f.confusiones).map(([k, v]) => k.toUpperCase() + "×" + v).join(", ") || "—");
        celda(fila, f.no_detectadas); celda(fila, f.tiempo_medio_s != null ? f.tiempo_medio_s : "—");
        celda(fila, (inf.causas[f.letra] || {}).texto || "—");
        tf.appendChild(fila);
      });
    }
  }
  async function bucleProtocolo() {
    for (;;) {
      try {
        const r = await fetch("/api/kinect/protocolo", { headers: cab, cache: "no-store" });
        if (r.ok) pintarProtocolo(await r.json());
      } catch (e) {}
      await new Promise((listo) => setTimeout(listo, 300));
    }
  }
  $("#formProtocolo").addEventListener("submit", async (ev) => {
    ev.preventDefault();
    const f = ev.currentTarget;
    const r = await post("/api/kinect/protocolo/iniciar", {
      letras: f.letras.value.trim().toLowerCase() || null,
      repeticiones: Number(f.repeticiones.value), tiempo_max: Number(f.tiempo.value) });
    if (!r.ok) $("#avisoProtocolo").textContent = "No se pudo iniciar: " + ((await r.json().catch(() => ({}))).detail || r.status);
  });
  $("#btnDetenerProtocolo").addEventListener("click", () => post("/api/kinect/protocolo/detener"));

  bucleDiagnostico();
  bucleCamara();
  bucleProtocolo();
})();
</script>
</body>
</html>
```

## `web/movil.html`

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#FFFFFF">
<title>Mano bidireccional LSC</title>
<script>
  // Tema elegido antes de pintar (evita el parpadeo al cargar)
  try { var t = localStorage.getItem("tema"); if (t === "light" || t === "dark") document.documentElement.dataset.theme = t; } catch (e) {}
</script>
<style>
  /* ---------- colores: tema claro ---------- */
  :root {
    --fondo: #FFFFFF; --superficie: #F4F6F5; --linea: #E4E8E6; --pestana: #FFFFFF;
    --texto: #141917; --texto-2: #4F5854; --texto-3: #7A837F;
    --acento: #00482B; --acento-boton: #00482B; --acento-presionado: #0B5F40; --sobre-acento: #FFFFFF;
    --acento-suave: #EEF6F2; --punto-ok: #1A7A55;
    --aviso: #A86A00; --error: #C2362B; --error-suave: #FBECEA; --sobre-error: #FFFFFF;
    --placa-logo: transparent;
    --sombra: 0 1px 2px rgba(20, 25, 23, .08), 0 2px 8px rgba(20, 25, 23, .06);
    --velo: rgba(10, 14, 12, .45); --sombra-hoja: 0 -8px 32px rgba(20, 25, 23, .18);
    --fuente: -apple-system, "SF Pro Text", "Segoe UI Variable Text", system-ui, Roboto, "Segoe UI", sans-serif;
    color-scheme: light;
  }
  /* ---------- colores: tema oscuro (sistema o elegido) ---------- */
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --fondo: #121615; --superficie: #1A1F1D; --linea: #2A322E; --pestana: #2A322E;
      --texto: #EDF1EF; --texto-2: #A3ADA8; --texto-3: #7D8782;
      --acento: #74BA9A; --acento-boton: #4FA37F; --acento-presionado: #74BA9A; --sobre-acento: #0A1A13;
      --acento-suave: #0F2A1F; --punto-ok: #74BA9A;
      --aviso: #E2B04A; --error: #EE7A6E; --error-suave: #2E1714; --sobre-error: #1B0A08;
      --placa-logo: #F4F6F5;
      --sombra: 0 1px 2px rgba(0, 0, 0, .3);
      --velo: rgba(0, 0, 0, .6); --sombra-hoja: 0 -8px 32px rgba(0, 0, 0, .5);
      color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --fondo: #121615; --superficie: #1A1F1D; --linea: #2A322E; --pestana: #2A322E;
    --texto: #EDF1EF; --texto-2: #A3ADA8; --texto-3: #7D8782;
    --acento: #74BA9A; --acento-boton: #4FA37F; --acento-presionado: #74BA9A; --sobre-acento: #0A1A13;
    --acento-suave: #0F2A1F; --punto-ok: #74BA9A;
    --aviso: #E2B04A; --error: #EE7A6E; --error-suave: #2E1714; --sobre-error: #1B0A08;
    --placa-logo: #F4F6F5;
    --sombra: 0 1px 2px rgba(0, 0, 0, .3);
    --velo: rgba(0, 0, 0, .6); --sombra-hoja: 0 -8px 32px rgba(0, 0, 0, .5);
    color-scheme: dark;
  }
  html.cambiando, html.cambiando * {
    transition: background-color .25s ease, color .25s ease, border-color .25s ease, box-shadow .25s ease !important;
  }

  * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
  html, body { margin: 0; background: var(--fondo); color: var(--texto); }
  body { font-family: var(--fuente); font-size: 17px; line-height: 1.4; -webkit-font-smoothing: antialiased;
    -webkit-text-size-adjust: 100%; max-width: 560px; margin: 0 auto;
    padding: max(14px, env(safe-area-inset-top)) max(18px, env(safe-area-inset-right)) max(36px, env(safe-area-inset-bottom)) max(18px, env(safe-area-inset-left)); }
  :focus-visible { outline: 2px solid var(--acento); outline-offset: 2px; }
  button { font: inherit; color: inherit; cursor: pointer; }

  /* ---------- encabezado ---------- */
  .marcas { display: flex; align-items: center; gap: 10px; }
  .placa { display: grid; place-items: center; background: var(--placa-logo); border-radius: 8px; padding: 3px 4px; }
  .placa img { height: 34px; width: auto; display: block; }
  .pgc { font-size: 12px; font-weight: 600; color: var(--acento); border: 1.5px solid var(--acento);
    border-radius: 999px; padding: 2px 9px; letter-spacing: .04em; }
  .icono { margin-left: auto; width: 44px; height: 44px; border: 0; border-radius: 50%; background: transparent;
    color: var(--texto-2); display: grid; place-items: center; }
  .icono:active { background: var(--superficie); }
  .icono svg { width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  h1 { margin: 14px 0 4px; font-size: 26px; font-weight: 700; letter-spacing: -.02em; line-height: 1.15; }
  .estado { display: inline-flex; align-items: center; gap: 7px; font-size: 14px; color: var(--texto-2); }
  .punto { width: 8px; height: 8px; border-radius: 50%; background: var(--texto-3); flex: none; }
  .estado.ok .punto { background: var(--punto-ok); }
  .estado.aviso .punto { background: var(--aviso); }
  .estado.error .punto { background: var(--error); }

  /* ---------- pestañas (control segmentado) ---------- */
  .tabs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 4px; margin-top: 20px; padding: 4px;
    background: var(--superficie); border-radius: 14px; }
  .tabs button { min-height: 46px; border: 0; border-radius: 10px; background: transparent;
    font-size: 16px; font-weight: 600; color: var(--texto-2); transition: background-color .2s, color .2s; }
  .tabs button[aria-selected="true"] { background: var(--pestana); color: var(--acento); box-shadow: var(--sombra); }

  /* ---------- zonas ---------- */
  .panel { margin-top: 24px; }
  .panel.suave { background: var(--superficie); border-radius: 20px; padding: 18px; }
  h2 { margin: 0 0 12px; font-size: 20px; font-weight: 600; letter-spacing: -.01em; line-height: 1.25; }
  .panel.suave h2 { font-size: 16px; color: var(--texto-2); margin-bottom: 10px; }
  .oculto, [hidden] { display: none !important; }   /* [hidden] también: .btn { display: flex } no debe ganarle */

  /* escribir */
  textarea { display: block; width: 100%; min-height: 96px; resize: none; padding: 14px 16px; border: 0;
    border-radius: 14px; background: var(--superficie); color: var(--texto); font: inherit; font-size: 19px; line-height: 1.35;
    box-shadow: inset 0 0 0 1px var(--linea); transition: box-shadow .2s; }
  textarea::placeholder { color: var(--texto-3); }
  textarea:focus { outline: none; box-shadow: inset 0 0 0 2px var(--acento); }
  .fila { display: flex; justify-content: space-between; align-items: baseline; gap: 12px; margin-top: 8px;
    font-size: 14px; color: var(--texto-2); }
  #contador { font-variant-numeric: tabular-nums; flex: none; }
  .btn { position: relative; display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%;
    min-height: 56px; margin-top: 16px; border: 0; border-radius: 16px; background: var(--acento-boton);
    color: var(--sobre-acento); font-size: 18px; font-weight: 600; transition: opacity .2s, background-color .2s, transform .1s; }
  .btn:active:not(:disabled) { transform: scale(.985); background: var(--acento-presionado); }
  .btn:disabled { opacity: .4; cursor: default; }
  .btn.hecho, .btn.hecho:disabled { opacity: 1; }
  .btn.hecho .btn-txt { animation: aparece .3s cubic-bezier(.2, .7, .2, 1); }

  /* letras (vista previa y "la mano ahora") */
  .letras { display: flex; flex-wrap: wrap; column-gap: .32em; row-gap: .2em; margin-top: 12px;
    font-size: 24px; font-weight: 500; line-height: 1.25; }
  .letras:empty { margin-top: 0; }
  .grupo { display: inline-flex; flex-wrap: wrap; column-gap: .32em; row-gap: .2em; max-width: 100%; }
  .l { color: var(--texto); padding-bottom: 3px; border-bottom: 3px solid transparent;
    transition: color .3s ease, border-color .3s ease; }
  .l.esp { width: .4em; }
  .l.nd { color: var(--texto-3); text-decoration: underline dotted; text-decoration-thickness: 2px; text-underline-offset: 5px; }
  .l.aprox { color: var(--aviso); }
  .en-curso .l { color: var(--texto-3); }
  .en-curso .l.hecha { color: var(--texto); }
  .en-curso .l.ahora { color: var(--acento); font-weight: 700; border-bottom-color: var(--acento); }

  /* avisos */
  .nota { margin: 10px 0 0; font-size: 15px; color: var(--texto-2); line-height: 1.45; }
  .aviso { display: none; margin-top: 12px; padding: 12px 14px; border-radius: 12px; font-size: 15px; line-height: 1.4; }
  .aviso.mostrar { display: block; animation: aparece .25s ease; }
  .aviso.ok { background: var(--acento-suave); color: var(--texto); }
  .aviso.info { background: var(--acento-suave); color: var(--texto); }
  .aviso.error { background: var(--error-suave); color: var(--error); }

  /* voz */
  .centro { text-align: center; }
  .grabar-caja { position: relative; width: 168px; height: 168px; margin: 18px auto 6px; display: grid; place-items: center; }
  .anillo { position: absolute; inset: 0; transform: rotate(-90deg); }
  .anillo circle { fill: none; stroke-width: 3; }
  .anillo .pista { stroke: var(--linea); }
  .anillo .progreso { stroke: var(--error); stroke-linecap: round; stroke-dasharray: 490; stroke-dashoffset: 490; opacity: 0; }
  .grabar { position: relative; width: 140px; height: 140px; border: 0; border-radius: 50%;
    background: var(--acento-boton); color: var(--sobre-acento); display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 6px; font-size: 17px; font-weight: 600;
    box-shadow: var(--sombra); transition: background-color .25s, transform .1s, opacity .2s; }
  .grabar:active:not(:disabled) { transform: scale(.97); }
  .grabar:disabled { opacity: .4; cursor: default; }
  .grabar svg { width: 34px; height: 34px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }
  .grabar .ic-stop { display: none; fill: currentColor; stroke: none; width: 26px; height: 26px; }
  .grabar-caja::after { content: ""; position: absolute; width: 140px; height: 140px; border-radius: 50%;
    border: 2px solid var(--error); opacity: 0; pointer-events: none; }
  .grabar-caja.activo .grabar { background: var(--error); color: var(--sobre-error); }
  .grabar-caja.activo .ic-mic { display: none; }
  .grabar-caja.activo .ic-stop { display: block; }
  .grabar-caja.activo .progreso { opacity: 1; animation: progreso 10s linear forwards; }
  .grabar-caja.activo::after { animation: pulso 1.6s ease-out infinite; }
  #grabarTxt { font-variant-numeric: tabular-nums; }
  @keyframes progreso { to { stroke-dashoffset: 0; } }
  @keyframes pulso { from { transform: scale(1); opacity: .5; } to { transform: scale(1.18); opacity: 0; } }
  input[type=file] { margin-top: 12px; max-width: 100%; font: inherit; font-size: 15px; }

  /* kinect (diseño de Camila con la paleta de la plataforma) */
  textarea.kin-texto { margin-top: 14px; min-height: 0; font-size: 26px; font-weight: 600; letter-spacing: .04em;
    text-transform: uppercase; cursor: default; }
  textarea.kin-texto::placeholder { font-size: 19px; font-weight: 400; letter-spacing: 0; text-transform: none; }
  textarea.kin-texto:focus { box-shadow: inset 0 0 0 1px var(--linea); }
  textarea.kin-texto.vivo { box-shadow: inset 0 0 0 2px var(--acento); }
  .kin-detalle { min-height: 1.45em; }
  .kin-acceso { margin-top: 18px; padding: 16px 18px; border-radius: 16px; background: var(--superficie); }
  .kin-modo { margin-top: 0; font-weight: 600; color: var(--texto); }
  .kin-acceso label { display: block; margin-top: 12px; font-size: 15px; font-weight: 600; color: var(--texto-2); }
  .kin-acceso input { display: block; width: 100%; margin-top: 6px; padding: 12px 16px; border: 0; border-radius: 14px;
    background: var(--fondo); color: var(--texto); font: inherit; font-size: 22px; letter-spacing: .3em;
    font-variant-numeric: tabular-nums; box-shadow: inset 0 0 0 1px var(--linea); }
  .kin-acceso input::placeholder { font-size: 16px; letter-spacing: 0; color: var(--texto-3); }
  .kin-acceso input:focus { outline: none; box-shadow: inset 0 0 0 2px var(--acento); }
  .kin-acceso .btn { margin-top: 12px; min-height: 52px; }
  .kin-acceso .aviso.mostrar { margin-top: 12px; }
  .kin-botones { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px; }
  .kin-botones .btn { margin-top: 0; min-height: 52px; font-size: 17px; }
  .kin-botones .ancho { grid-column: 1 / -1; }
  .kin-botones .destacado { min-height: 58px; font-size: 18px; }
  .btn.sec2 { background: var(--superficie); color: var(--texto); box-shadow: inset 0 0 0 1px var(--linea); }
  .btn.sec2:active:not(:disabled) { background: var(--linea); }
  .btn.eco { background: var(--acento-suave); color: var(--acento); box-shadow: inset 0 0 0 1.5px var(--acento); }
  .btn.eco.encendido { background: var(--acento-boton); color: var(--sobre-acento); box-shadow: none; }

  /* tus mensajes */
  .mensaje { display: grid; grid-template-columns: minmax(52px, auto) 1fr; gap: 14px; align-items: center;
    padding: 12px 0; border-top: 1px solid var(--linea); }
  .mensaje:first-child { border-top: 0; padding-top: 2px; }
  .mensaje.entra { animation: entra .4s cubic-bezier(.2, .7, .2, 1); }
  .pos { font-size: 40px; font-weight: 700; line-height: 1; letter-spacing: -.03em; color: var(--acento);
    font-variant-numeric: tabular-nums; text-align: center; }
  .pos.palabra-pos { font-size: 22px; letter-spacing: -.01em; }
  .pos.apagado { color: var(--texto-3); }
  .vivo-punto { display: block; width: 14px; height: 14px; margin: 0 auto; border-radius: 50%; background: var(--acento);
    animation: latido 1.4s ease-in-out infinite; }
  .mensaje .e { font-size: 15px; color: var(--texto-2); }
  .mensaje .e.vivo { color: var(--acento); font-weight: 600; }
  .mensaje .t { margin-top: 2px; font-size: 17px; font-weight: 600; word-break: break-word; }
  .mensaje .quien-msg { color: var(--texto-2); font-weight: 500; }
  .mensaje .acciones { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
  .enlace { min-height: 40px; padding: 0 4px; border: 0; background: none; color: var(--error); font-size: 15px; font-weight: 500; }

  /* participante: nombre y aviso de pausa */
  .quien { display: flex; align-items: baseline; gap: 6px; margin-top: 2px; font-size: 14px; color: var(--texto-2); }
  .enlace-sec { min-height: 32px; padding: 0 2px; border: 0; background: none; color: var(--acento);
    font-size: 14px; font-weight: 600; }
  .pausa { margin-top: 18px; padding: 16px 18px; border-radius: 16px; background: var(--acento-suave);
    font-size: 16px; line-height: 1.45; animation: aparece .3s ease; }
  .pausa strong { display: block; margin-bottom: 2px; }
  .velo { position: fixed; inset: 0; z-index: 10; background: var(--velo); display: flex;
    align-items: flex-end; justify-content: center; animation: fundido .2s ease; }
  .hoja { width: 100%; max-width: 560px; background: var(--fondo); border-radius: 24px 24px 0 0;
    padding: 24px max(20px, env(safe-area-inset-right)) max(24px, env(safe-area-inset-bottom)) max(20px, env(safe-area-inset-left));
    box-shadow: var(--sombra-hoja); animation: sube .32s cubic-bezier(.2, .7, .2, 1); }
  .hoja h2 { font-size: 22px; margin-bottom: 6px; }
  .hoja input { display: block; width: 100%; margin-top: 16px; padding: 14px 16px; border: 0; border-radius: 14px;
    background: var(--superficie); color: var(--texto); font: inherit; font-size: 19px;
    box-shadow: inset 0 0 0 1px var(--linea); }
  .hoja input:focus { outline: none; box-shadow: inset 0 0 0 2px var(--acento); }
  .hoja .btn.sec { background: transparent; color: var(--texto-2); margin-top: 6px; }
  @keyframes sube { from { transform: translateY(100%); } to { transform: none; } }
  @keyframes fundido { from { opacity: 0; } to { opacity: 1; } }

  @keyframes aparece { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: none; } }
  @keyframes entra { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
  @keyframes latido { 50% { opacity: .35; } }
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 1ms !important; animation-iteration-count: 1 !important; transition-duration: 1ms !important; }
    .grabar-caja.activo .progreso { animation-duration: 10s !important; }
  }
</style>
</head>
<body>
<header>
  <div class="marcas">
    <div class="placa"><img src="/logo-udec.png" alt="Universidad de Cundinamarca"></div>
    <span class="pgc">PGC</span>
    <button id="btnTema" class="icono" type="button"></button>
  </div>
  <h1>Mano bidireccional LSC</h1>
  <div id="chipConexion" class="estado"><span class="punto"></span><span class="txt">Conectando…</span></div>
  <div class="quien"><span id="quienTexto">Sin nombre</span><button id="cambiarNombre" class="enlace-sec" type="button">Ponerte un nombre</button></div>
</header>

<div id="avisoPausa" class="pausa oculto" role="status">
  <strong>Gracias por participar</strong>
  El presentador pausó tu participación en esta sesión.
</div>

<!-- Nombre opcional (se pide al abrir la página la primera vez) -->
<div id="veloNombre" class="velo oculto">
  <form id="hojaNombre" class="hoja" role="dialog" aria-modal="true" aria-labelledby="tituloNombre" novalidate>
    <h2 id="tituloNombre">¿Cómo te llamas?</h2>
    <p class="nota">Es opcional. Se verá en el proyector junto a tus mensajes y se borra al terminar la sesión.</p>
    <input id="nombre" maxlength="20" autocomplete="given-name" autocapitalize="words" placeholder="Tu nombre" enterkeyhint="done">
    <div id="avisoNombre" class="aviso"></div>
    <button id="guardarNombre" class="btn" type="submit">Continuar</button>
    <button id="sinNombre" class="btn sec" type="button">Prefiero no decirlo</button>
  </form>
</div>

<nav class="tabs" role="tablist">
  <button role="tab" data-tab="escribir" aria-selected="true">Escribir</button>
  <button role="tab" data-tab="voz" aria-selected="false">Voz</button>
  <button role="tab" data-tab="kinect" aria-selected="false">Kinect</button>
</nav>

<!-- ======================= ESCRIBIR ======================= -->
<section id="tab-escribir" class="panel">
  <h2>¿Qué quieres que deletree la mano?</h2>
  <textarea id="texto" maxlength="60" rows="2" placeholder="Ej.: Hola jurado" autocomplete="off" autocapitalize="sentences"></textarea>
  <div class="fila"><span id="leyenda"></span><span id="contador">0/60</span></div>
  <div id="previa" class="letras" aria-live="polite"></div>
  <div id="avisoEscribir" class="aviso"></div>
  <button id="enviar" class="btn" disabled><span class="btn-txt">Enviar a la mano</span></button>
</section>

<!-- ========================= VOZ ========================== -->
<section id="tab-voz" class="panel oculto">
  <h2>Dilo en voz alta</h2>
  <div id="vozMic" class="centro">
    <div id="grabarCaja" class="grabar-caja">
      <svg class="anillo" viewBox="0 0 168 168" aria-hidden="true"><circle class="pista" cx="84" cy="84" r="78"/><circle class="progreso" cx="84" cy="84" r="78"/></svg>
      <button id="grabar" class="grabar" type="button">
        <svg class="ic-mic" viewBox="0 0 24 24" aria-hidden="true"><rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5.5 11a6.5 6.5 0 0 0 13 0M12 17.5V21"/></svg>
        <svg class="ic-stop" viewBox="0 0 24 24" aria-hidden="true"><rect x="5" y="5" width="14" height="14" rx="3"/></svg>
        <span id="grabarTxt">Grabar</span>
      </button>
    </div>
    <p id="vozEstado" class="nota">Habla claro, máximo 10 segundos. Luego podrás revisar el texto.</p>
  </div>
  <div id="vozArchivo" class="oculto">
    <p class="nota">Tu navegador no deja usar el micrófono en esta página. Graba una nota de voz con el botón de abajo:</p>
    <input id="archivoAudio" type="file" accept="audio/*" capture>
  </div>
  <div id="avisoVoz" class="aviso"></div>
</section>

<!-- ======================= KINECT ========================= -->
<!-- Diseño de Camila (pestaña de iniciar_pgc_integrado.py): texto grande, estado, código del PC y botones en cuadrícula -->
<section id="tab-kinect" class="panel oculto">
  <h2>De tus manos al texto</h2>
  <div id="kinEstado" class="estado"><span class="punto"></span><span class="txt">Conectando con el Kinect…</span></div>
  <p class="nota">Mantén la letra hasta verla escrita. Retira la mano entre letras.</p>

  <textarea id="kinTexto" class="kin-texto" rows="3" readonly aria-label="Texto deletreado"
            placeholder="Tus letras aparecerán aquí"></textarea>
  <p id="kinDetalle" class="nota kin-detalle" role="status">Conectando...</p>
  <p id="kinFrase" class="nota"></p>

  <!-- Acceso: un jurado a la vez (turno), con el código que muestra el proyector -->
  <div id="kinAcceso" class="kin-acceso">
    <p id="kinModo" class="nota kin-modo" role="status">Modo espectador.</p>
    <form id="kinLibre" class="oculto" novalidate>
      <label id="kinCodigoEtq" for="kinCodigo">Código del PC</label>
      <input id="kinCodigo" type="password" inputmode="numeric" pattern="[0-9]{6}" maxlength="6"
             autocomplete="off" enterkeyhint="go" placeholder="6 dígitos del proyector">
      <button id="kinTomar" class="btn" type="submit">Activar control</button>
      <div id="avisoAcceso" class="aviso"></div>
    </form>
    <div id="kinOcupado" class="aviso info"></div>
    <button id="kinSoltar" class="btn sec2 oculto" type="button">Volver a espectador</button>
  </div>

  <!-- Botones en cuadrícula. Los del deletreo necesitan el turno; Guardar, Leer y Detener voz, no -->
  <div id="kinMios" class="kin-botones">
    <button class="btn" type="button" data-kin="iniciar">Iniciar</button>
    <button class="btn sec2" type="button" data-kin="detener">Detener</button>
    <button class="btn sec2" type="button" data-kin="espacio">Espacio</button>
    <button class="btn sec2" type="button" data-kin="borrar">Borrar</button>
    <button class="btn sec2" type="button" data-kin="limpiar">Limpiar</button>
    <button id="kinGuardar" class="btn sec2" type="button">Guardar TXT</button>
    <button id="kinLeer" class="btn sec2" type="button">Leer frase</button>
    <button id="kinCallar" class="btn sec2" type="button">Detener voz</button>
    <button class="btn ancho destacado" type="button" data-kin="terminar">Terminar y decirlo</button>
    <button id="kinEco" class="btn ancho eco" type="button" title="La mano repite lo que reconoce el Kinect">Eco: no</button>
  </div>
  <p id="kinVoz" class="nota" role="status"></p>
  <div id="avisoKinect" class="aviso"></div>
</section>

<!-- ===================== MIS MENSAJES ===================== -->
<section id="misMensajes" class="panel suave oculto">
  <h2>Tus mensajes</h2>
  <div id="listaMios"></div>
</section>

<!-- ======================== AHORA ========================= -->
<section class="panel suave">
  <h2>La mano ahora</h2>
  <div id="ahora" class="nota">Esperando mensajes…</div>
  <div id="ahoraLetras" class="letras en-curso"></div>
  <p id="enCola" class="nota"></p>
</section>

<script>
(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const MAX = 60;

  // ---------- identidad del celular (para el límite de 2 mensajes y "tus mensajes")
  const guardar = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
  const leer = (k) => { try { return localStorage.getItem(k); } catch (e) { return null; } };
  let cliente = leer("cliente");
  if (!cliente) { cliente = Math.random().toString(36).slice(2) + Date.now().toString(36); guardar("cliente", cliente); }
  let mios = [];
  try { mios = JSON.parse(leer("mios") || "[]"); } catch (e) { mios = []; }
  const guardarMios = () => guardar("mios", JSON.stringify(mios.slice(-5)));
  // El nombre solo dura mientras la pestaña esté abierta (sessionStorage)
  const guardarSesion = (k, v) => { try { sessionStorage.setItem(k, v); } catch (e) {} };
  const leerSesion = (k) => { try { return sessionStorage.getItem(k); } catch (e) { return null; } };
  try { localStorage.removeItem("nombre"); localStorage.removeItem("nombre_preguntado"); } catch (e) {}

  let estado = null;
  let miPid = null, sesionRegistrada = null, bloqueado = false;
  let miNombre = leerSesion("nombre") || "";

  // ---------- tema claro / oscuro
  const raiz = document.documentElement;
  const oscuroSistema = matchMedia("(prefers-color-scheme: dark)");
  const SOL = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg>';
  const LUNA = '<svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>';
  const temaActual = () => raiz.dataset.theme || (oscuroSistema.matches ? "dark" : "light");
  function pintarTema() {
    const oscuro = temaActual() === "dark";
    const b = $("#btnTema");
    b.innerHTML = oscuro ? SOL : LUNA;
    b.setAttribute("aria-label", oscuro ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
    document.querySelector('meta[name="theme-color"]').content = oscuro ? "#121615" : "#FFFFFF";
  }
  $("#btnTema").addEventListener("click", () => {
    const nuevo = temaActual() === "dark" ? "light" : "dark";
    raiz.classList.add("cambiando");
    raiz.dataset.theme = nuevo;
    guardar("tema", nuevo);
    pintarTema();
    setTimeout(() => raiz.classList.remove("cambiando"), 300);
  });
  oscuroSistema.addEventListener("change", pintarTema);
  pintarTema();

  // ---------- pestañas
  document.querySelectorAll(".tabs button").forEach((b) => b.addEventListener("click", () => irA(b.dataset.tab)));
  function irA(tab) {
    document.querySelectorAll(".tabs button").forEach((b) => b.setAttribute("aria-selected", b.dataset.tab === tab));
    ["escribir", "voz", "kinect"].forEach((t) => $("#tab-" + t).classList.toggle("oculto", t !== tab));
  }

  function aviso(el, tipo, txt) {
    el.className = "aviso" + (txt ? " mostrar " + tipo : "");
    el.textContent = txt || "";
  }

  function chipsLetras(cont, pasos, i) {
    cont.textContent = "";
    let grupo = null;                              // letras de una misma palabra, para no partirla
    pasos.forEach((p, k) => {
      const s = document.createElement("span");
      s.className = "l";
      if (p.tipo === "espacio") s.classList.add("esp");
      else s.textContent = p.c;
      if (p.tipo === "nd") { s.classList.add("nd"); s.title = "La mano no puede hacer esta letra"; }
      if (p.tipo === "aprox") { s.classList.add("aprox"); s.title = "Se aproxima con otra forma"; }
      if (i !== undefined) {
        if (k < i) s.classList.add("hecha");
        else if (k === i) s.classList.add("ahora");
      }
      if (p.tipo === "espacio") { cont.appendChild(s); grupo = null; return; }
      if (!grupo) { grupo = document.createElement("span"); grupo.className = "grupo"; cont.appendChild(grupo); }
      grupo.appendChild(s);
    });
  }

  // Explica las marcas de la vista previa solo cuando aparecen
  function leyenda(pasos) {
    const partes = [];
    if (pasos.some((p) => p.tipo === "nd")) partes.push("Las letras con puntos debajo la mano aún no las hace.");
    if (pasos.some((p) => p.tipo === "aprox")) partes.push("La Ñ se forma como la N.");
    $("#leyenda").textContent = partes.join(" ");
  }

  // ---------- escribir + vista previa
  const texto = $("#texto");
  let tPrevia = null;
  texto.addEventListener("input", () => {
    $("#contador").textContent = texto.value.length + "/" + MAX;
    $("#enviar").disabled = bloqueado || !/[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ0-9]/.test(texto.value);
    clearTimeout(tPrevia);
    tPrevia = setTimeout(previa, 250);
  });
  async function previa() {
    const v = texto.value;
    if (!v.trim()) { $("#previa").textContent = ""; leyenda([]); return; }
    try {
      const r = await fetch("/api/previa", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: v, cliente }) });
      if (r.ok && v === texto.value) {
        const pasos = (await r.json()).pasos;
        chipsLetras($("#previa"), pasos);
        leyenda(pasos);
      }
    } catch (e) {}
  }

  // Confirmación breve dentro del propio botón
  let tHecho = null;
  function confirmarEnvio() {
    const b = $("#enviar");
    clearTimeout(tHecho);
    b.classList.add("hecho");
    b.querySelector(".btn-txt").textContent = "Enviado ✓";
    tHecho = setTimeout(() => {
      b.classList.remove("hecho");
      b.querySelector(".btn-txt").textContent = "Enviar a la mano";
    }, 1400);
  }

  $("#enviar").addEventListener("click", async () => {
    const v = texto.value.trim();
    if (!v) return;
    $("#enviar").disabled = true;
    aviso($("#avisoEscribir"), "", "");
    try {
      const r = await fetch("/api/mensaje", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: v, cliente }) });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(d.detail || "No se pudo enviar.");
      mios.push({ id: d.id, texto: d.texto, nombre: d.nombre, sesion: d.sesion });
      guardarMios();
      texto.value = "";
      texto.dispatchEvent(new Event("input"));
      confirmarEnvio();
      pintar();
    } catch (e) {
      aviso($("#avisoEscribir"), "error", e.message || "Sin conexión con el servidor.");
      $("#enviar").disabled = false;
    }
  });

  // ---------- voz
  const puedeGrabar = window.isSecureContext && navigator.mediaDevices && navigator.mediaDevices.getUserMedia && window.MediaRecorder;
  if (!puedeGrabar) { $("#vozMic").classList.add("oculto"); $("#vozArchivo").classList.remove("oculto"); }

  function ponerGrabar(activo, txt) {
    $("#grabarCaja").classList.toggle("activo", activo);
    $("#grabarTxt").textContent = txt;
    $("#grabar").setAttribute("aria-label", activo ? "Detener grabación" : "Grabar");
  }

  let grabador = null, corte = null, cuenta = null;
  const SEGUNDOS = 10;
  $("#grabar").addEventListener("click", async () => {
    if (grabador && grabador.state === "recording") { grabador.stop(); return; }
    aviso($("#avisoVoz"), "", "");
    let flujo;
    try {
      flujo = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: true, noiseSuppression: true } });
    } catch (e) {
      aviso($("#avisoVoz"), "error", "No se pudo usar el micrófono. Revisa el permiso o usa la pestaña Escribir.");
      return;
    }
    const tipos = ["audio/webm;codecs=opus", "audio/webm", "audio/mp4", "audio/ogg;codecs=opus"];
    const tipo = tipos.find((t) => MediaRecorder.isTypeSupported(t)) || "";
    grabador = new MediaRecorder(flujo, tipo ? { mimeType: tipo } : undefined);
    const trozos = [];
    grabador.ondataavailable = (e) => { if (e.data && e.data.size) trozos.push(e.data); };
    grabador.onstop = () => {
      clearTimeout(corte); clearInterval(cuenta);
      flujo.getTracks().forEach((t) => t.stop());
      ponerGrabar(false, "Grabar");
      const mime = grabador.mimeType || tipo || "audio/webm";
      const ext = mime.includes("mp4") ? ".m4a" : mime.includes("ogg") ? ".ogg" : ".webm";
      enviarAudio(new Blob(trozos, { type: mime }), "voz" + ext);
    };
    grabador.start();
    let quedan = SEGUNDOS;
    ponerGrabar(true, quedan + " s");
    cuenta = setInterval(() => { quedan--; $("#grabarTxt").textContent = Math.max(quedan, 0) + " s"; }, 1000);
    corte = setTimeout(() => grabador.state === "recording" && grabador.stop(), SEGUNDOS * 1000);
  });

  $("#archivoAudio").addEventListener("change", (e) => {
    const f = e.target.files && e.target.files[0];
    if (f) enviarAudio(f, f.name || "voz.m4a");
    e.target.value = "";
  });

  async function enviarAudio(blob, nombre) {
    $("#grabar").disabled = true;
    aviso($("#avisoVoz"), "info", "Transcribiendo…");
    try {
      const fd = new FormData();
      fd.append("audio", blob, nombre);
      fd.append("cliente", cliente);
      const r = await fetch("/api/transcribir", { method: "POST", body: fd });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(d.detail || "No se pudo transcribir.");
      if (!d.texto) throw new Error("No escuché nada. Intenta otra vez, más cerca del celular.");
      aviso($("#avisoVoz"), "", "");
      texto.value = d.texto.slice(0, MAX);
      texto.dispatchEvent(new Event("input"));
      irA("escribir");
      aviso($("#avisoEscribir"), "info", "Esto fue lo que entendí. Corrígelo si hace falta y toca «Enviar a la mano».");
    } catch (e) {
      aviso($("#avisoVoz"), "error", e.message || "Sin conexión con el servidor.");
    } finally {
      actualizarVoz();
    }
  }

  function actualizarVoz() {
    const v = estado && estado.voz ? estado.voz.estado : "";
    const listo = v === "listo";
    const ocupado = grabador && grabador.state === "recording";
    $("#grabar").disabled = (!listo && !ocupado) || bloqueado;
    $("#archivoAudio").disabled = !listo || bloqueado;
    if (!listo) $("#vozEstado").textContent = v === "error" || v === "desactivado"
      ? "El reconocimiento de voz no está disponible ahora. Usa la pestaña Escribir."
      : "Cargando el reconocimiento de voz…";
    else $("#vozEstado").textContent = "Habla claro, máximo " + SEGUNDOS + " segundos. Luego podrás revisar el texto.";
  }

  // ---------- Kinect: todo llega por el WebSocket (sin consultas propias); los botones necesitan el turno
  const hayKinect = !!$("#kinTexto");          // el lanzador antiguo (iniciar_pgc_integrado.py) reemplaza esta sección
  let kinOcupado = false, ultimaFrase = null, tAvisoKinect = null;

  function textoEstadoKinect(k) {
    if (!k.controles && k.estado !== "error") return ["", "Kinect simulado"];
    if (k.estado === "apagado" || k.estado === "cargando") return ["aviso", "Conectando con el Kinect…"];
    if (!k.conectado || !k.camara || k.estado === "error") return ["error", "Kinect no conectado"];
    if (k.activo) return ["ok", "Reconociendo señas"];
    return ["", "Kinect listo · deletreo detenido"];
  }

  function pintarKinect() {
    if (!hayKinect || !estado || !estado.kinect) return;
    const k = estado.kinect;
    const [clase, txt] = textoEstadoKinect(k);
    const chipK = $("#kinEstado");
    chipK.className = "estado " + clase;
    chipK.querySelector(".txt").textContent = txt;
    $("#kinTexto").value = (k.texto || "").toUpperCase();
    $("#kinTexto").classList.toggle("vivo", !!k.activo);
    // El estado del detector tal cual ("Deletreo detenido.", "Posible letra: A | Estable: 0.4 s"...)
    $("#kinDetalle").textContent = txt === "Kinect no conectado"
      ? "El presentador debe encender el Kinect y su detector."
      : k.conectado ? (k.detalle || (k.activo ? "" : "Deletreo detenido.")) : "Conectando...";
    const frase = (k.frases || []).slice(-1)[0];
    $("#kinFrase").textContent = frase ? "Última frase: «" + frase + "»" : "";
    if (frase && frase !== ultimaFrase && ultimaFrase !== null) {
      const dicha = estado.voz_salida && estado.voz_salida.estado === "listo";
      aviso($("#avisoKinect"), "ok", (dicha ? "Se dijo en voz alta: «" : "Frase terminada: «") + frase + "»");
      clearTimeout(tAvisoKinect);
      tAvisoKinect = setTimeout(() => aviso($("#avisoKinect"), "", ""), 6000);
    }
    ultimaFrase = frase || "";

    // Sin Kinect conectado no hay nada que controlar: los botones del deletreo quedan apagados
    const conControles = k.controles && !bloqueado && k.conectado && k.camara;
    const mio = !!(k.turno && miPid && k.turno.pid === miPid);
    const libre = conControles && !k.turno;
    $("#kinLibre").classList.toggle("oculto", !libre);
    $("#kinCodigoEtq").classList.toggle("oculto", !k.codigo);       // PGC_KINECT_CODIGO=false: basta el botón
    $("#kinCodigo").classList.toggle("oculto", !k.codigo);
    if (!libre) aviso($("#avisoAcceso"), "", "");
    $("#kinSoltar").classList.toggle("oculto", !conControles || !mio);
    const otro = conControles && k.turno && !mio;
    $("#kinOcupado").className = "aviso info" + (otro ? " mostrar" : "");
    $("#kinOcupado").textContent = otro ? "Lo está usando " + (k.turno.nombre || "otra persona") + ". Espera tu turno." : "";
    $("#kinModo").textContent = mio && conControles
      ? "Control del teléfono activo (se libera solo tras 2 minutos sin usarlo)."
      : libre && k.codigo ? "Modo espectador. Introduce el código del PC para controlar."
      : libre ? "Modo espectador. Toca «Activar control» para controlar." : "Modo espectador.";
    actualizarPropios();
    const puede = mio && conControles && !kinOcupado;
    document.querySelectorAll("[data-kin]").forEach((b) => {
      const accion = b.dataset.kin;
      b.disabled = !puede || (accion === "iniciar" && k.activo) || (accion === "detener" && !k.activo);
    });
    $("#kinTomar").disabled = kinOcupado;
    $("#kinEco").textContent = "Eco: " + (k.eco ? "sí" : "no");
    $("#kinEco").classList.toggle("encendido", !!k.eco);
    $("#kinEco").disabled = !puede;
  }

  async function pedirKinect(ruta, cuerpo, donde = $("#avisoKinect")) {
    kinOcupado = true;
    pintarKinect();
    try {
      const r = await fetch(ruta, { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ cliente, ...cuerpo }) });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(d.detail || "No se pudo completar.");
      aviso(donde, "", "");
      return true;
    } catch (e) {
      aviso(donde, "error", e.message || "Sin conexión con el servidor.");
      return false;
    } finally {
      kinOcupado = false;
      pintarKinect();
    }
  }
  // ---------- En tu celular (también los espectadores): guardar y leer el texto deletreado
  // Es el texto en curso o, si ya se terminó, la última frase
  const textoKinect = () => {
    const k = (estado && estado.kinect) || {};
    return (k.texto || (k.frases || []).slice(-1)[0] || "").trim();
  };
  const tieneVoz = "speechSynthesis" in window;
  if (tieneVoz) speechSynthesis.getVoices();          // algunos navegadores cargan las voces tarde
  function actualizarPropios() {
    const t = textoKinect();
    $("#kinGuardar").disabled = !t;
    $("#kinLeer").disabled = !tieneVoz || !t;
    $("#kinCallar").disabled = !tieneVoz;
  }
  function guardarTxt() {
    const t = textoKinect();
    if (!t) return;
    const url = URL.createObjectURL(new Blob([t.toUpperCase() + "\r\n"], { type: "text/plain;charset=utf-8" }));
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = "texto_lsc.txt";
    document.body.appendChild(enlace);
    enlace.click();
    enlace.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }
  function leerFrase() {
    const t = textoKinect();
    if (!tieneVoz || !t) return;
    // Primero una voz de Colombia; si no hay, de Latinoamérica; si no, cualquiera en español
    const espanolas = speechSynthesis.getVoices().filter((v) => v.lang.toLowerCase().startsWith("es"));
    const preferida = (prefijos) => espanolas.find((v) => prefijos.some((p) => v.lang.toLowerCase().replace("_", "-") === p));
    const voz = preferida(["es-co"]) || preferida(["es-419", "es-mx", "es-us", "es-pe", "es-ec", "es-ve", "es-cl", "es-ar"])
      || espanolas[0];
    if (!voz) {
      $("#kinVoz").textContent = "No hay una voz en español disponible. Revisa las voces del celular o vuelve a intentarlo cuando carguen.";
      return;
    }
    speechSynthesis.cancel();
    const lectura = new SpeechSynthesisUtterance(t.toLowerCase());
    lectura.voice = voz;
    lectura.lang = voz.lang;
    lectura.onstart = () => { $("#kinVoz").textContent = "Leyendo..."; };
    lectura.onend = () => { $("#kinVoz").textContent = "Lectura terminada."; };
    lectura.onerror = () => { $("#kinVoz").textContent = "Lectura detenida o audio no disponible."; };
    speechSynthesis.speak(lectura);
  }
  function detenerVoz() {
    if (tieneVoz) speechSynthesis.cancel();
    $("#kinVoz").textContent = "Lectura detenida.";
  }

  if (hayKinect) {
    $("#kinGuardar").addEventListener("click", guardarTxt);
    $("#kinLeer").addEventListener("click", leerFrase);
    $("#kinCallar").addEventListener("click", detenerVoz);
    addEventListener("pagehide", () => { if (tieneVoz) speechSynthesis.cancel(); });
    // Activar control: con el código que muestra el proyector (si PGC_KINECT_CODIGO=true)
    $("#kinLibre").addEventListener("submit", async (e) => {
      e.preventDefault();
      const campo = $("#kinCodigo");
      if (await pedirKinect("/api/kinect/turno", { codigo: campo.value.trim() }, $("#avisoAcceso"))) campo.value = "";
    });
    $("#kinSoltar").addEventListener("click", () => pedirKinect("/api/kinect/turno/soltar", {}));
    // Modo eco: la mano repite lo que reconoce el Kinect (con el turno, igual que en el proyector)
    $("#kinEco").addEventListener("click", () =>
      pedirKinect("/api/kinect/eco", { activo: !(estado && estado.kinect && estado.kinect.eco) }));
    document.querySelectorAll("[data-kin]").forEach((b) =>
      b.addEventListener("click", () => pedirKinect("/api/kinect/control", { accion: b.dataset.kin })));
  }

  // ---------- mis mensajes
  async function cancelar(id) {
    try {
      await fetch("/api/mensaje/" + id + "?cliente=" + encodeURIComponent(cliente), { method: "DELETE" });
    } catch (e) {}
    mios = mios.filter((m) => m.id !== id);
    guardarMios();
    pintar();
  }

  const vistos = new Set();                        // para animar solo los mensajes nuevos
  function pintarMios() {
    const lista = $("#listaMios");
    lista.textContent = "";
    const cola = estado ? estado.cola : [];
    const actual = estado ? estado.actual : null;
    const historial = estado ? estado.historial : [];
    // Se olvidan los mensajes de otra sesión del servidor o que ya salieron del historial
    // (los más nuevos que el estado recibido se conservan: el estado aún no los incluye)
    const conocidos = [...cola, ...historial].concat(actual ? [actual] : []).map((x) => x.id);
    const maxId = Math.max(0, ...conocidos);
    const visibles = mios.filter((m) => estado && m.sesion === estado.sesion && (m.id > maxId || conocidos.includes(m.id)));
    if (estado && visibles.length !== mios.length) { mios = visibles; guardarMios(); }
    $("#misMensajes").classList.toggle("oculto", !mios.length);
    mios.slice().reverse().forEach((m) => {
      const div = document.createElement("div");
      div.className = "mensaje" + (vistos.has(m.id) ? "" : " entra");
      vistos.add(m.id);
      const pos = document.createElement("div");
      pos.className = "pos";
      const cuerpo = document.createElement("div");
      const fila = document.createElement("div");
      fila.className = "acciones";
      const e = document.createElement("div");
      e.className = "e";
      fila.appendChild(e);
      const enCola = cola.findIndex((c) => c.id === m.id);
      const hist = historial.find((h) => h.id === m.id);
      // El nombre con el que el servidor guardó el mensaje (el mismo que ve el proyector)
      const delServidor = (actual && actual.id === m.id) ? actual : enCola >= 0 ? cola[enCola] : hist;
      const t = document.createElement("div");
      t.className = "t";
      const n = document.createElement("span");    // "Jean: hola jurado"
      n.className = "quien-msg"; n.textContent = (m.nombre || (delServidor && delServidor.nombre) || "Anónimo") + ": ";
      t.append(n, m.texto);
      if ((actual && actual.id === m.id && actual.saltado) || (hist && hist.saltado)) {
        pos.classList.add("apagado"); pos.textContent = "–";
        e.textContent = "El presentador lo saltó";
      } else if (actual && actual.id === m.id) {
        pos.innerHTML = '<span class="vivo-punto"></span>';
        e.classList.add("vivo"); e.textContent = "La mano lo está deletreando ahora";
      } else if (enCola >= 0) {
        const antes = enCola + (actual ? 1 : 0);
        if (antes === 0) { pos.classList.add("palabra-pos"); pos.textContent = "Sigue"; e.textContent = "el tuyo"; }
        else { pos.textContent = antes; e.textContent = antes === 1 ? "mensaje antes del tuyo" : "mensajes antes del tuyo"; }
        const b = document.createElement("button");
        b.className = "enlace"; b.textContent = "Cancelar";
        b.addEventListener("click", () => cancelar(m.id));
        fila.appendChild(b);
      } else {
        pos.textContent = "✓";
        e.textContent = "Listo";
      }
      cuerpo.append(fila, t);
      div.append(pos, cuerpo);
      lista.appendChild(div);
    });
  }

  // ---------- estado general
  function pintar() {
    if (!estado) return;
    const a = estado.actual;
    if (a) {
      $("#ahora").textContent = "Deletreando «" + a.texto + "»";
      chipsLetras($("#ahoraLetras"), a.pasos, a.i);
    } else {
      $("#ahora").textContent = "Esperando mensajes…";
      $("#ahoraLetras").textContent = "";
    }
    const n = estado.cola.length;
    $("#enCola").textContent = n ? n + (n === 1 ? " mensaje en cola" : " mensajes en cola") : "";
    pintarMios();
    actualizarVoz();
    pintarKinect();
  }

  // ---------- participante: nombre opcional y pausa del presentador
  function pintarQuien() {
    $("#quienTexto").textContent = miNombre ? "Participas como " + miNombre : "Sin nombre";
    $("#cambiarNombre").textContent = miNombre ? "Cambiar" : "Ponerte un nombre";
  }

  function ponerBloqueo(si) {
    bloqueado = si;
    $("#avisoPausa").classList.toggle("oculto", !si);
    $("#enviar").disabled = si || !/[a-zA-ZñÑáéíóúÁÉÍÓÚüÜ0-9]/.test(texto.value);
    actualizarVoz();
  }

  // El servidor recuerda el nombre solo en memoria y devuelve el alias del celular (pid)
  async function registrar(nombre) {
    const r = await fetch("/api/participante", { method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ cliente, nombre: nombre || null }) });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.detail || "No se pudo guardar el nombre.");
    miPid = d.pid;
    if (!d.bloqueado) { miNombre = d.nombre || ""; guardarSesion("nombre", miNombre); }
    ponerBloqueo(d.bloqueado);
    pintarQuien();
  }

  function abrirNombre() {
    $("#nombre").value = miNombre;
    aviso($("#avisoNombre"), "", "");
    $("#veloNombre").classList.remove("oculto");
    setTimeout(() => $("#nombre").focus(), 60);
  }
  function cerrarNombre() {
    $("#veloNombre").classList.add("oculto");
    guardarSesion("nombre_preguntado", "1");
  }
  $("#hojaNombre").addEventListener("submit", async (e) => {
    e.preventDefault();
    $("#guardarNombre").disabled = true;
    try { await registrar($("#nombre").value.trim()); cerrarNombre(); }
    catch (x) { aviso($("#avisoNombre"), "error", x.message || "Sin conexión con el servidor."); }
    finally { $("#guardarNombre").disabled = false; }
  });
  $("#sinNombre").addEventListener("click", () => { registrar("").catch(() => {}); cerrarNombre(); });
  $("#veloNombre").addEventListener("click", (e) => { if (e.target === e.currentTarget) cerrarNombre(); });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !$("#veloNombre").classList.contains("oculto")) cerrarNombre();
  });
  $("#cambiarNombre").addEventListener("click", abrirNombre);
  pintarQuien();
  if (!leerSesion("nombre_preguntado")) abrirNombre();

  // ---------- conexión en vivo (WebSocket con reconexión; sondeo mientras tanto)
  const chip = $("#chipConexion");
  function ponerChip(clase, txt) { chip.className = "estado " + clase; chip.querySelector(".txt").textContent = txt; }
  function aplicar(d) {
    if (d.tipo !== "estado") return;
    estado = d;
    if (d.sesion !== sesionRegistrada) {            // servidor nuevo: volver a presentarse
      sesionRegistrada = d.sesion;
      registrar(miNombre).catch(() => registrar("").catch(() => {}));
    } else if (miPid) {
      const ahora = (d.bloqueados || []).includes(miPid);
      if (ahora !== bloqueado) ponerBloqueo(ahora);
    }
    ponerChip(d.mano.modo === "real" ? "ok" : "aviso", d.mano.modo === "real" ? "Mano conectada" : "Mano simulada");
    pintar();
  }
  let ws = null, espera = 1000, sondeo = null;
  function conectar() {
    if (ws && ws.readyState <= 1) return;          // ya hay una conexión abierta o abriéndose
    ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws");
    ws.onopen = () => { espera = 1000; clearInterval(sondeo); sondeo = null; };
    ws.onmessage = (e) => { try { aplicar(JSON.parse(e.data)); } catch (x) {} };
    ws.onclose = () => {
      ponerChip("error", "Reconectando…");
      if (!sondeo) sondeo = setInterval(sondear, 3000);
      setTimeout(conectar, espera);
      espera = Math.min(espera * 2, 10000);
    };
  }
  async function sondear() {
    try { const r = await fetch("/api/estado"); if (r.ok) aplicar(await r.json()); } catch (e) {}
  }
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && (!ws || ws.readyState > 1)) { espera = 1000; conectar(); }
  });
  conectar();
})();
</script>
</body>
</html>
```

## `web/pantalla.html`

```html
<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="pgc-admin" content="">
<title>Mano bidireccional LSC · Pantalla</title>
<script>
  // Tema elegido antes de pintar (evita el parpadeo al cargar)
  try { var t = localStorage.getItem("tema"); if (t === "light" || t === "dark") document.documentElement.dataset.theme = t; } catch (e) {}
</script>
<style>
  /* ---------- colores: tema claro ---------- */
  :root {
    --fondo: #FFFFFF; --superficie: #F4F6F5; --linea: #E4E8E6;
    --texto: #141917; --texto-2: #4F5854; --texto-3: #7A837F;
    --acento: #00482B; --punto-ok: #1A7A55;
    --aviso: #A86A00; --error: #C2362B; --sobre-error: #FFFFFF;
    --placa-logo: transparent;
    --sombra-qr: 0 1px 2px rgba(20, 25, 23, .06), 0 12px 32px rgba(20, 25, 23, .10);
    --fuente: "Segoe UI Variable Display", "Segoe UI Variable Text", -apple-system, "SF Pro Display", system-ui, Roboto, "Segoe UI", sans-serif;
    color-scheme: light;
  }
  /* ---------- colores: tema oscuro (sistema o elegido) ---------- */
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --fondo: #121615; --superficie: #1A1F1D; --linea: #2A322E;
      --texto: #EDF1EF; --texto-2: #A3ADA8; --texto-3: #7D8782;
      --acento: #74BA9A; --punto-ok: #74BA9A;
      --aviso: #E2B04A; --error: #EE7A6E; --sobre-error: #1B0A08;
      --placa-logo: #F4F6F5;
      --sombra-qr: 0 12px 32px rgba(0, 0, 0, .35);
      color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --fondo: #121615; --superficie: #1A1F1D; --linea: #2A322E;
    --texto: #EDF1EF; --texto-2: #A3ADA8; --texto-3: #7D8782;
    --acento: #74BA9A; --punto-ok: #74BA9A;
    --aviso: #E2B04A; --error: #EE7A6E; --sobre-error: #1B0A08;
    --placa-logo: #F4F6F5;
    --sombra-qr: 0 12px 32px rgba(0, 0, 0, .35);
    color-scheme: dark;
  }
  html.cambiando, html.cambiando * {
    transition: background-color .25s ease, color .25s ease, border-color .25s ease, box-shadow .25s ease !important;
  }

  * { box-sizing: border-box; }
  html, body { margin: 0; height: 100%; overflow: hidden; }
  body { background: var(--fondo); color: var(--texto); font-family: var(--fuente);
    -webkit-font-smoothing: antialiased; display: grid; grid-template-rows: auto 1fr auto;
    gap: 2.4vh; padding: 3vh 3.2vw 2.4vh; }
  :focus-visible { outline: 2px solid var(--acento); outline-offset: 3px; }

  /* ---------- encabezado ---------- */
  header { display: flex; align-items: center; gap: 1.1vw; }
  .placa { display: grid; place-items: center; background: var(--placa-logo); border-radius: 1.2vh; padding: .5vh .6vh; }
  .placa img { height: clamp(34px, 5.4vh, 60px); width: auto; display: block; }
  .pgc { font-size: clamp(11px, 1.5vh, 16px); font-weight: 600; color: var(--acento); border: 1.5px solid var(--acento);
    border-radius: 999px; padding: .2em .7em; letter-spacing: .04em; }
  header h1 { margin: 0; font-size: clamp(18px, 2.9vh, 32px); font-weight: 600; letter-spacing: -.01em; }
  .acciones { margin-left: auto; display: flex; gap: .4vw; }
  .icono { width: clamp(40px, 5vh, 54px); height: clamp(40px, 5vh, 54px); border: 0; border-radius: 50%;
    background: transparent; color: var(--texto-2); display: grid; place-items: center; cursor: pointer; }
  .icono:hover { background: var(--superficie); color: var(--texto); }
  .icono svg { width: 48%; height: 48%; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }

  /* ---------- tres columnas ---------- */
  main { display: grid; grid-template-columns: minmax(280px, 23vw) 1fr minmax(260px, 20vw); gap: 3vw; min-height: 0; }

  /* izquierda: QR + estado */
  .izq { display: flex; flex-direction: column; min-height: 0; }
  .qr { background: #FFFFFF; border-radius: 2.2vh; padding: 1.4vh; box-shadow: var(--sombra-qr);
    width: 100%; max-width: 38vh; aspect-ratio: 1; }
  .qr img { width: 100%; height: 100%; display: block; image-rendering: pixelated; }
  .invita { font-size: clamp(18px, 3vh, 34px); font-weight: 600; line-height: 1.2; letter-spacing: -.01em;
    margin: 2.6vh 0 .8vh; max-width: 13em; text-wrap: balance; }
  .url { font-size: clamp(12px, 1.6vh, 18px); color: var(--texto-2); overflow-wrap: anywhere; }
  /* código para tomar el turno del Kinect desde un celular (solo lo ve quien está en la sala) */
  .codigo-kinect { display: flex; align-items: baseline; justify-content: space-between; gap: .8vw; margin-top: 1.6vh;
    padding: .9vh 1vw; border-radius: 1.4vh; background: var(--acento-suave); box-shadow: inset 0 0 0 1px var(--linea); }
  .codigo-kinect span { font-size: clamp(12px, 1.6vh, 18px); color: var(--texto-2); }
  .codigo-kinect b { font-size: clamp(22px, 3.6vh, 44px); font-weight: 700; line-height: 1.1; letter-spacing: .06em;
    color: var(--acento); font-variant-numeric: tabular-nums; white-space: nowrap; }
  .izq.con-codigo .qr { max-width: 26vh; }
  .izq.con-codigo .estados { padding-top: 2vh; }
  .estados { margin: auto 0 0; padding-top: 3vh; display: grid; grid-template-columns: auto 1fr;
    gap: 1.2vh 1.4vw; font-size: clamp(13px, 1.9vh, 21px); }
  .estados dt { color: var(--texto-2); display: flex; align-items: center; gap: .6em; }
  .estados dd { margin: 0; }
  .punto { width: .62em; height: .62em; border-radius: 50%; flex: none; background: var(--texto-3); }
  .punto.ok { background: var(--punto-ok); }
  .punto.aviso { background: var(--aviso); }
  .punto.error { background: var(--error); }
  .punto.pendiente { background: transparent; box-shadow: inset 0 0 0 1.5px var(--texto-3); }

  /* centro: lo que se deletrea */
  .centro { display: grid; min-height: 0; text-align: center; }
  .vista { grid-area: 1 / 1; align-self: center; width: 100%; min-height: 0; display: flex; flex-direction: column; align-items: center;
    transition: opacity .45s ease, transform .45s cubic-bezier(.2, .7, .2, 1), visibility 0s; }
  #vDeletreo { align-self: stretch; justify-content: center; }
  .vista.oculta { opacity: 0; transform: translateY(1.5vh); visibility: hidden; pointer-events: none;
    transition: opacity .3s ease, transform .3s ease, visibility 0s .3s; }

  .rotulo { font-size: clamp(16px, 2.4vh, 28px); color: var(--texto-2); min-height: 1.3em;
    max-width: 90%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  /* La letra ocupa el alto que dejan libre el rótulo, la palabra y las notas */
  .escenario { position: relative; flex: 1 1 0; min-height: 0; max-height: 50vh; width: 100%; container-type: size; }
  .glifo { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;
    font-size: min(100cqh, 62cqw); line-height: 1; font-weight: 600; letter-spacing: -.04em; color: var(--acento);
    animation: entra .38s cubic-bezier(.2, .7, .2, 1) .12s both; }   /* entra cuando la anterior ya casi salió */
  .glifo.nd { color: var(--texto-3); }
  .glifo.texto { font-size: min(22cqh, 9cqw); letter-spacing: -.02em; color: var(--texto); }
  .glifo.sale { animation: sale .16s ease-in both; }
  @keyframes entra { from { opacity: 0; transform: translateY(4%); } to { opacity: 1; transform: none; } }
  @keyframes sale { to { opacity: 0; transform: translateY(-3%); } }
  .detalle { font-size: clamp(16px, 2.6vh, 30px); color: var(--texto-2); min-height: 1.3em; margin-top: .4vh; }
  .detalle.aviso { color: var(--aviso); }

  .palabra { position: relative; display: flex; flex-wrap: wrap; justify-content: center; column-gap: .34em; row-gap: .45em;
    margin-top: 3vh; padding-bottom: .3em; max-width: 100%; font-size: clamp(22px, 5.4vh, 62px); font-weight: 500; }
  .palabra.larga { font-size: clamp(18px, 4vh, 46px); }
  .grupo { display: inline-flex; flex-wrap: wrap; justify-content: center; column-gap: .34em; row-gap: .45em; max-width: 100%; }
  .l { color: var(--texto-3); line-height: 1.1; transition: color .3s ease; }
  .l.hecha { color: var(--texto); }
  .l.ahora { color: var(--acento); font-weight: 600; }
  .l.nd { text-decoration: underline dotted; text-decoration-thickness: .08em; text-underline-offset: .2em; }
  .l.error { color: var(--error); }
  .l.esp { width: .45em; }
  .marca { position: absolute; left: 0; top: 0; width: 0; height: max(3px, .45vh); border-radius: 3px;
    background: var(--acento); opacity: 0;
    transition: left .3s cubic-bezier(.2, .7, .2, 1), top .3s cubic-bezier(.2, .7, .2, 1), width .3s ease, opacity .2s; }
  .nota-nd { font-size: clamp(13px, 1.8vh, 20px); color: var(--texto-2); margin-top: 2.4vh; min-height: 1.3em; }

  /* reposo */
  .reposo h2 { margin: 0; font-size: clamp(34px, 7.6vh, 90px); font-weight: 600; letter-spacing: -.025em; line-height: 1.05; }
  .reposo p { margin: 2.4vh auto 0; max-width: 28em; font-size: clamp(17px, 2.7vh, 32px); line-height: 1.4; color: var(--texto-2); }
  .alfabeto { display: flex; flex-wrap: wrap; justify-content: center; gap: .2em .55em; margin-top: 6.5vh; max-width: 82%;
    font-size: clamp(20px, 3.8vh, 44px); font-weight: 500; color: var(--texto-3); }
  .alfabeto span { transition: color .6s ease; }
  .alfabeto span.activa { color: var(--acento); }
  .alfabeto-nota { margin-top: 1.4vh; font-size: clamp(13px, 1.7vh, 19px); color: var(--texto-2); }

  /* derecha: cola */
  .der { display: flex; flex-direction: column; min-height: 0; }
  .der h3 { margin: 0 0 1.6vh; font-size: clamp(15px, 2vh, 22px); font-weight: 600; color: var(--texto-2); }
  .der ol, .der ul { list-style: none; margin: 0; padding: 0; display: grid; overflow: hidden; }
  .der ol { gap: 1.5vh; }
  .der ol li { display: grid; grid-template-columns: 1.5em 1fr; gap: .3em; font-size: clamp(16px, 2.5vh, 28px);
    line-height: 1.25; color: var(--texto-2); word-break: break-word; }
  .der ol li:first-child { color: var(--texto); }
  .der ol li.mas { display: block; font-size: clamp(14px, 2vh, 22px); }
  .der ol li { position: relative; }
  .autor { display: block; margin-top: .15em; font-size: .7em; color: var(--texto-2); }
  /* Bloquear desde la cola: solo aparece al pasar el ratón (no ensucia lo que se proyecta) */
  .bloquear-li { position: absolute; right: 0; top: 0; opacity: 0; font: inherit; font-size: clamp(11px, 1.4vh, 15px);
    color: var(--error); background: var(--fondo); border: 1px solid var(--linea); border-radius: 999px;
    padding: .2em .7em; cursor: pointer; transition: opacity .15s; }
  .der ol li:hover .bloquear-li, .bloquear-li:focus-visible { opacity: 1; }
  .num { color: var(--acento); font-weight: 600; font-variant-numeric: tabular-nums; }
  .vacio { font-size: clamp(14px, 2vh, 22px); color: var(--texto-2); }
  .recientes { margin-top: auto; padding-top: 3vh; }
  .der ul { gap: 1.1vh; }
  .der ul li { font-size: clamp(14px, 2.05vh, 23px); line-height: 1.3; color: var(--texto-2); word-break: break-word; }
  .quien-hist { color: var(--texto); font-weight: 600; }
  .etiqueta { margin-left: .45em; font-size: .8em; color: var(--texto-3); }

  /* ---------- pie ---------- */
  footer { display: flex; align-items: flex-end; justify-content: space-between; gap: 3vw;
    border-top: 1px solid var(--linea); padding-top: 1.8vh; }
  .creditos { margin: 0; max-width: 76%; font-size: clamp(11px, 1.45vh, 16px); line-height: 1.5; color: var(--texto-2); }
  .creditos .completo { color: var(--texto); }
  .controles { display: flex; gap: .5vw; flex: none; }
  .controles button { font: inherit; font-size: clamp(12px, 1.6vh, 17px); font-weight: 500; color: var(--texto-2);
    background: transparent; border: 1px solid var(--linea); border-radius: 999px; padding: .7vh 1.1vw; cursor: pointer; }
  .controles button:hover:not(:disabled) { color: var(--texto); border-color: var(--texto-3); }
  .controles button:disabled { opacity: .45; cursor: default; }
  .controles { align-items: center; }
  .aviso-admin { font-size: clamp(12px, 1.6vh, 17px); color: var(--texto-2); margin-right: .4vw; }
  .aviso-admin button { border: 0; padding: 0 .2em; color: var(--acento); font-weight: 600; text-decoration: underline; }

  [hidden] { display: none !important; }

  /* kinect: lo que se deletrea con señas */
  #vKinect { align-self: stretch; justify-content: center; gap: 1.4vh; }
  /* Con la cámara a la vista, la imagen manda: ocupa casi todo el centro y el texto se achica */
  #vKinect.con-camara { gap: 1vh; }
  #vKinect.con-camara .kin-camara { height: 58vh; }
  #vKinect.con-camara .kin-texto { font-size: clamp(26px, 6.5vh, 80px); }
  #vKinect.con-camara .kin-detalle { font-size: clamp(14px, 2.1vh, 24px); }
  .kin-camara { height: 34vh; max-width: 100%; aspect-ratio: 4 / 3; object-fit: cover; border-radius: 1.6vh;
    background: var(--superficie); }
  .kin-texto { max-width: 100%; min-height: 1.1em; font-size: clamp(30px, 9vh, 110px); font-weight: 600; line-height: 1.1;
    letter-spacing: .04em; text-transform: uppercase; color: var(--texto); overflow-wrap: anywhere; }
  .kin-texto:empty::before { content: "Haz una letra frente al Kinect"; font-size: .42em; font-weight: 500;
    letter-spacing: 0; text-transform: none; color: var(--texto-3); }
  .kin-texto.vivo:not(:empty)::after { content: ""; display: inline-block; width: .06em; height: .9em; margin-left: .08em;
    vertical-align: -.08em; border-radius: 2px; background: var(--acento); animation: parpadeo 1s steps(2) infinite; }
  @keyframes parpadeo { 50% { opacity: 0; } }
  .kin-detalle { min-height: 1.3em; font-size: clamp(15px, 2.4vh, 28px); color: var(--texto-2); }
  .kin-frase { min-height: 1.3em; font-size: clamp(14px, 2.2vh, 26px); color: var(--texto-2); }
  .kin-frase b { color: var(--texto); font-weight: 600; }
  .kin-tira { margin-top: 1.6vh; min-height: 1.3em; font-size: clamp(14px, 2.2vh, 26px); color: var(--texto-2); }
  .kin-tira b { color: var(--texto); font-weight: 600; letter-spacing: .04em; }
  .grupos { display: flex; flex-direction: column; align-items: flex-end; gap: .9vh; flex: none; }
  .controles .etq { font-size: clamp(12px, 1.6vh, 17px); color: var(--texto-3); margin-right: .2vw; }
  .controles button.encendido { color: var(--acento); border-color: var(--acento); font-weight: 600; }

  .desconectado { position: fixed; top: 0; left: 0; right: 0; z-index: 5; padding: .9vh; text-align: center;
    background: var(--error); color: var(--sobre-error); font-weight: 600; font-size: clamp(13px, 1.8vh, 20px);
    transform: translateY(-100%); transition: transform .3s ease; }
  .desconectado.si { transform: none; }

  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after { animation-duration: 1ms !important; transition-duration: 1ms !important; }
  }
</style>
</head>
<body>
<div id="desconectado" class="desconectado" role="status">Sin conexión con el servidor. Reconectando…</div>

<header>
  <div class="placa"><img src="/logo-udec.png" alt="Universidad de Cundinamarca"></div>
  <span class="pgc">PGC</span>
  <h1>Mano bidireccional LSC</h1>
  <div class="acciones">
    <button id="btnTema" class="icono" type="button"></button>
    <button id="btnCompleta" class="icono" type="button" title="Pantalla completa (F)" aria-label="Pantalla completa">
      <svg viewBox="0 0 24 24"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>
    </button>
  </div>
</header>

<main>
  <section class="izq">
    <div class="qr"><img id="qr" alt="Código QR para abrir la página en el celular"></div>
    <div class="invita">Escanea y escribe o habla a la mano</div>
    <div id="url" class="url"></div>
    <div id="kinCodigoCaja" class="codigo-kinect" hidden>
      <span>Código del Kinect</span>
      <b id="kinCodigo">——————</b>
    </div>
    <dl class="estados">
      <dt><span id="pMano" class="punto"></span>Mano</dt><dd id="eMano">—</dd>
      <dt><span id="pVoz" class="punto"></span>Voz</dt><dd id="eVoz">—</dd>
      <dt><span id="pTunel" class="punto"></span>HTTPS</dt><dd id="eTunel">—</dd>
      <dt><span id="pKinect" class="punto"></span>Kinect</dt><dd id="eKinect">—</dd>
    </dl>
  </section>

  <section class="centro" aria-live="polite">
    <div id="vReposo" class="vista reposo">
      <h2>Mano bidireccional LSC</h2>
      <p>Escanea el código con tu celular y escribe o di algo. La mano lo deletreará en Lengua de Señas Colombiana.</p>
      <div id="alfabeto" class="alfabeto" aria-hidden="true"></div>
      <div id="alfabetoNota" class="alfabeto-nota"></div>
    </div>
    <div id="vDeletreo" class="vista oculta">
      <div id="rotulo" class="rotulo"></div>
      <div id="escenario" class="escenario"></div>
      <div id="detalle" class="detalle"></div>
      <div id="palabra" class="palabra"><div id="marca" class="marca"></div></div>
      <div id="notaNd" class="nota-nd"></div>
      <div id="kinTira" class="kin-tira"></div>
    </div>
    <div id="vKinect" class="vista oculta">
      <div id="kinRotulo" class="rotulo">Kinect</div>
      <img id="kinCamara" class="kin-camara" alt="Cámara del Kinect con los puntos de la mano" hidden>
      <div id="kinTexto" class="kin-texto"></div>
      <div id="kinDetalle" class="kin-detalle"></div>
      <div id="kinFrase" class="kin-frase"></div>
    </div>
  </section>

  <section class="der">
    <h3>En cola</h3>
    <ol id="cola"></ol>
    <div id="colaVacia" class="vacio">Nadie en espera.</div>
    <div class="recientes">
      <h3>Recientes</h3>
      <ul id="historial"></ul>
      <div id="histVacio" class="vacio">Todavía no hay mensajes.</div>
    </div>
  </section>
</main>

<footer>
  <p class="creditos">
    <span class="completo">Diseño e implementación de un sistema robótico bidireccional para la traducción de Lengua de Señas Colombiana (LSC) mediante visión por computador, control de mano robótica y síntesis/reconocimiento de voz</span><br>
    Jean Paul Miranda Díaz, Lina Tatiana Maldonado Rivera, Paula Camila Enríquez Galindo, Jean Harry Raigozo<br>
    Ingeniería de Sistemas y Computación, Universidad de Cundinamarca, extensión Facatativá
  </p>
  <div id="grupos" class="grupos">
  <div id="ctrlKinect" class="controles" hidden>
    <span class="etq">Kinect</span>
    <button type="button" data-kin="iniciar">Iniciar</button>
    <button type="button" data-kin="detener">Detener</button>
    <button type="button" data-kin="espacio">Espacio</button>
    <button type="button" data-kin="borrar">Borrar</button>
    <button type="button" data-kin="limpiar">Limpiar</button>
    <button type="button" data-kin="terminar" title="Dice la frase en voz alta (y, con el eco, la mano la deletrea)">Terminar y decir</button>
    <button id="kinEco" type="button" title="La mano repite lo que reconoce el Kinect">Eco: no</button>
    <button id="kinLiberar" type="button" title="Quita el control del Kinect al celular que lo tiene" disabled>Liberar turno</button>
    <button id="kinNuevoCodigo" type="button" title="Código nuevo para tomar el turno; quien lo tenía lo pierde" hidden>Cambiar código</button>
    <button id="kinDiagnostico" type="button" title="Por qué una letra se confirma o no, y el protocolo de prueba (solo en este PC)">Diagnóstico</button>
  </div>
  <div class="controles">
    <span id="avisoAdmin" class="aviso-admin" role="status"></span>
    <button id="btnBloquear" type="button" title="Pausa a esta persona durante la sesión y cancela sus mensajes en espera" disabled>Bloquear participante</button>
    <button id="btnSaltar" type="button" title="Cancela el mensaje en curso y deja la mano abierta" disabled>Saltar mensaje</button>
    <button id="btnReconectar" type="button" title="Volver a buscar la mano por USB">Reconectar mano</button>
  </div>
  </div>
</footer>

<script>
(() => {
  "use strict";
  const $ = (s) => document.querySelector(s);
  const MAX_COLA_VISIBLE = 7;
  let urlQr = null;

  // Token de administrador: el servidor solo lo pone cuando esta página se abre en el propio PC
  const TOKEN = document.querySelector('meta[name="pgc-admin"]').content;
  const admin = (ruta) => fetch(ruta, { method: "POST", headers: { "X-PGC-Admin": TOKEN } });

  // ---------- bloquear participantes (con aviso para deshacer)
  let tAviso = null;
  function avisoAdmin(texto, deshacer) {
    const el = $("#avisoAdmin");
    el.textContent = texto;
    if (deshacer) {
      const b = document.createElement("button");
      b.type = "button"; b.textContent = "Deshacer";
      b.addEventListener("click", () => { deshacer(); el.textContent = ""; });
      el.append(" ", b);
    }
    clearTimeout(tAviso);
    tAviso = setTimeout(() => { el.textContent = ""; }, 10000);
  }
  async function bloquear(pid, nombre) {
    const r = await admin("/api/participantes/" + encodeURIComponent(pid) + "/bloquear");
    if (!r.ok) { avisoAdmin("No se pudo bloquear."); return; }
    const d = await r.json();
    const quien = nombre || "el participante";
    const partes = [];
    if (d.saltado) partes.push("se saltó su mensaje");
    if (d.cancelados) partes.push("se " + (d.cancelados === 1 ? "canceló 1 mensaje" : "cancelaron " + d.cancelados + " mensajes"));
    avisoAdmin("Bloqueaste a " + quien + (partes.length ? ": " + partes.join(" y ") : "") + ".",
      () => admin("/api/participantes/" + encodeURIComponent(pid) + "/desbloquear"));
  }
  const autorDe = (m) => m && m.nombre ? "Mensaje de: " + m.nombre : "";

  // ---------- tema claro / oscuro
  const raiz = document.documentElement;
  const oscuroSistema = matchMedia("(prefers-color-scheme: dark)");
  const SOL = '<svg viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M5.3 18.7l1.4-1.4M17.3 6.7l1.4-1.4"/></svg>';
  const LUNA = '<svg viewBox="0 0 24 24"><path d="M20 14.5A8 8 0 0 1 9.5 4a8 8 0 1 0 10.5 10.5z"/></svg>';
  const temaActual = () => raiz.dataset.theme || (oscuroSistema.matches ? "dark" : "light");
  function pintarBotonTema() {
    const oscuro = temaActual() === "dark";
    const b = $("#btnTema");
    b.innerHTML = oscuro ? SOL : LUNA;
    b.title = oscuro ? "Tema claro" : "Tema oscuro (recomendado con la sala oscura)";
    b.setAttribute("aria-label", oscuro ? "Cambiar a tema claro" : "Cambiar a tema oscuro");
  }
  $("#btnTema").addEventListener("click", () => {
    const nuevo = temaActual() === "dark" ? "light" : "dark";
    raiz.classList.add("cambiando");
    raiz.dataset.theme = nuevo;
    try { localStorage.setItem("tema", nuevo); } catch (e) {}
    pintarBotonTema();
    setTimeout(() => raiz.classList.remove("cambiando"), 300);
  });
  oscuroSistema.addEventListener("change", pintarBotonTema);
  pintarBotonTema();

  // ---------- estado de los componentes
  function estadoFila(clave, clase, txt) {
    $("#p" + clave).className = "punto " + clase;
    $("#e" + clave).textContent = txt;
  }
  const mayus = (s) => s.charAt(0).toUpperCase() + s.slice(1);

  // ---------- reposo: letras que la mano sabe hacer
  let letrasAlfabeto = "", letrasPorDefecto = null, pidiendoDefecto = false, iAlf = 0;
  function ponerAlfabeto(letras) {
    if (!letras || letras === letrasAlfabeto) return;
    letrasAlfabeto = letras;
    const cont = $("#alfabeto");
    cont.textContent = "";
    [...letras].forEach((c) => { const s = document.createElement("span"); s.textContent = c; cont.appendChild(s); });
    iAlf = 0;
    $("#alfabetoNota").textContent = "Las " + letras.length + " letras que la mano sabe hacer";
  }
  async function pedirLetrasPorDefecto() {
    // En modo simulado la mano no reporta letras: se usan las del servidor por defecto
    if (pidiendoDefecto) return;
    pidiendoDefecto = true;
    try {
      const r = await fetch("/api/previa", { method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ texto: "abcdefghijklmnopqrstuvwxyz" }) });
      if (r.ok) {
        letrasPorDefecto = (await r.json()).pasos.filter((p) => p.tipo === "ok").map((p) => p.c).join("");
        if (!letrasAlfabeto) ponerAlfabeto(letrasPorDefecto);
      }
    } catch (e) {}
    pidiendoDefecto = false;
  }
  setInterval(() => {
    const spans = $("#alfabeto").children;
    if (!spans.length || $("#vReposo").classList.contains("oculta")) return;
    for (const s of spans) s.classList.remove("activa");
    spans[iAlf % spans.length].classList.add("activa");
    iAlf++;
  }, 1500);

  // ---------- centro: letra grande con transición
  let claveGlifo = null, idPalabra = null, spansPalabra = [];
  function ponerGlifo(clave, txt, clase) {
    if (clave === claveGlifo) return;
    claveGlifo = clave;
    const esc = $("#escenario");
    esc.querySelectorAll(".glifo:not(.sale)").forEach((g) => {
      g.classList.add("sale");
      setTimeout(() => g.remove(), 200);
    });
    const g = document.createElement("div");
    g.className = "glifo" + (clase ? " " + clase : "");
    g.textContent = txt;
    esc.appendChild(g);
  }
  function detalle(txt, clase) {
    const el = $("#detalle");
    el.className = "detalle" + (clase ? " " + clase : "");
    el.textContent = txt;
  }

  function moverMarca(sinAnimar) {
    const marca = $("#marca");
    const s = $("#palabra .l.ahora");
    if (!s || s.classList.contains("esp")) { marca.style.opacity = 0; return; }
    if (sinAnimar) marca.style.transition = "none";
    marca.style.left = s.offsetLeft + "px";
    marca.style.top = (s.offsetTop + s.offsetHeight + 4) + "px";
    marca.style.width = s.offsetWidth + "px";
    marca.style.opacity = 1;
    if (sinAnimar) { void marca.offsetWidth; marca.style.transition = ""; }
  }

  function pintarPalabra(a) {
    const cont = $("#palabra");
    const nuevo = a.id !== idPalabra;
    if (nuevo) {
      idPalabra = a.id;
      cont.querySelectorAll(".grupo, .l").forEach((s) => s.remove());
      cont.classList.toggle("larga", a.pasos.length > 22);
      // Las letras de cada palabra van juntas para que una palabra no se parta entre líneas
      spansPalabra = [];
      let grupo = null;
      a.pasos.forEach((q) => {
        const s = document.createElement("span");
        spansPalabra.push(s);
        if (q.tipo === "espacio") { cont.appendChild(s); grupo = null; return; }
        s.textContent = q.c;
        if (!grupo) { grupo = document.createElement("span"); grupo.className = "grupo"; cont.appendChild(grupo); }
        grupo.appendChild(s);
      });
    }
    a.pasos.forEach((q, k) => {
      spansPalabra[k].className = "l" + (q.tipo === "espacio" ? " esp" : "") + (q.tipo === "nd" ? " nd" : "") +
        (k < a.i ? " hecha" : k === a.i && !a.saltado ? " ahora" : "") + (q.r === "error" ? " error" : "");
    });
    moverMarca(nuevo);
    $("#notaNd").textContent = a.pasos.some((q) => q.tipo === "nd") ? "Las letras con puntos debajo la mano aún no las hace." : "";
  }

  function pintarDeletreo(a) {
    if (a.saltado) {
      $("#rotulo").textContent = "«" + a.texto + "»";
      ponerGlifo("saltado:" + a.id, "Mensaje saltado", "texto");
      detalle("Abriendo la mano");
    } else {
      $("#rotulo").textContent = autorDe(a) || "Deletreando";
      const p = a.pasos[a.i];
      if (a.i < 0) { ponerGlifo("prep:" + a.id, "", ""); detalle(""); }
      else if (!p) { ponerGlifo("fin:" + a.id, "✓", ""); detalle("Mensaje completo"); }
      else if (p.tipo === "espacio") { ponerGlifo(a.id + ":" + a.i, "Espacio", "texto"); detalle("Mano abierta"); }
      else {
        ponerGlifo(a.id + ":" + a.i, p.c, p.tipo === "nd" ? "nd" : "");
        if (p.tipo === "nd") detalle("La mano aún no hace esta letra");
        else if (p.tipo === "aprox") detalle("Se forma como la N", "aviso");
        else detalle("");
      }
    }
    pintarPalabra(a);
  }

  function mostrarVista(vista) {            // "deletreo" (la mano) | "kinect" | "reposo"
    $("#vDeletreo").classList.toggle("oculta", vista !== "deletreo");
    $("#vKinect").classList.toggle("oculta", vista !== "kinect");
    $("#vReposo").classList.toggle("oculta", vista !== "reposo");
  }

  // ---------- Kinect: estado, texto deletreado y (solo en este PC) la cámara
  function estadoKinect(k) {
    if (!k.controles && k.estado !== "error") return ["pendiente", "Simulado"];
    if (k.estado === "apagado" || k.estado === "cargando") return ["aviso", "Conectando…"];
    if (!k.conectado || !k.camara || k.estado === "error") return ["error", "No conectado"];
    if (k.activo) return ["ok", "Reconociendo"];
    return ["ok", "Listo"];
  }
  let verCamara = false, urlCamara = null;
  function pintarKinect(k, mano) {
    const [clase, txt] = estadoKinect(k);
    estadoFila("Kinect", clase, txt + (k.turno ? " · " + (k.turno.nombre || "un jurado") : ""));
    $("#kinRotulo").textContent = k.turno && k.turno.nombre ? "Kinect · " + k.turno.nombre : "Kinect";
    // Con la cámara a la vista, texto y estado los pone la imagen (son del mismo momento); si no, el WebSocket
    if (!camaraAlDia()) {
      $("#kinTexto").textContent = k.texto || "";
      $("#kinDetalle").textContent = k.activo ? k.detalle : "Deletreo detenido";
    }
    $("#kinTexto").classList.toggle("vivo", !!k.activo);
    const frase = (k.frases || []).slice(-1)[0];
    $("#kinFrase").textContent = "";
    if (frase) { const b = document.createElement("b"); b.textContent = frase; $("#kinFrase").append("Dijo: «", b, "»"); }
    // Mientras la mano deletrea, lo del Kinect sigue visible en una línea
    $("#kinTira").textContent = "";
    if (mano && k.activo) { const b = document.createElement("b"); b.textContent = (k.texto || "…").toUpperCase(); $("#kinTira").append("Kinect: ", b); }
    verCamara = !!(TOKEN && k.camara);
    if (!verCamara) { $("#kinCamara").hidden = true; $("#vKinect").classList.remove("con-camara"); }
    // Controles del presentador
    $("#ctrlKinect").hidden = !TOKEN || !k.controles;
    document.querySelectorAll("#ctrlKinect [data-kin]").forEach((b) => {
      b.disabled = (b.dataset.kin === "iniciar" && k.activo) || (b.dataset.kin === "detener" && !k.activo);
    });
    $("#kinEco").textContent = "Eco: " + (k.eco ? "sí" : "no");
    $("#kinEco").classList.toggle("encendido", !!k.eco);
    $("#kinLiberar").disabled = !k.turno;
    // Código del turno: lo pide solo este PC (con el token); el WebSocket solo dice si cambió
    const conCodigo = !!(TOKEN && k.controles && k.codigo);
    $("#kinCodigoCaja").hidden = !conCodigo;
    document.querySelector(".izq").classList.toggle("con-codigo", conCodigo);
    $("#kinNuevoCodigo").hidden = !conCodigo;
    if (conCodigo && k.codigo_version !== versionCodigo) pedirCodigo(k.codigo_version);
  }
  let versionCodigo = null;
  const ponerCodigo = (c) => { $("#kinCodigo").textContent = c ? c.slice(0, 3) + " " + c.slice(3) : "——————"; };
  async function pedirCodigo(version) {
    versionCodigo = version;
    try {
      const r = await fetch("/api/kinect/codigo", { headers: { "X-PGC-Admin": TOKEN }, cache: "no-store" });
      if (r.ok) ponerCodigo((await r.json()).codigo);
      else versionCodigo = null;
    } catch (e) { versionCodigo = null; }
  }
  // La cámara solo se pide en el PC del proyector (el servidor la niega por el túnel o la red).
  // Pide "la imagen siguiente a la última que mostré" (?despues=N): el servidor responde apenas existe,
  // así cada cuadro llega una sola vez y sin esperas fijas. La decodifica antes de mostrarla (sin
  // parpadeo) y pone el texto y el estado que el servidor leyó junto con ESA imagen.
  let ultimoCuadro = null, tSincronia = 0;
  const camaraAlDia = () => verCamara && performance.now() - tSincronia < 600;
  async function bucleCamara() {
    for (;;) {
      let pausa = 300;                                  // sin cámara a la vista, o si algo falló
      if (verCamara && !$("#vKinect").classList.contains("oculta")) {
        try {
          const despues = ultimoCuadro === null ? "" : "?despues=" + encodeURIComponent(ultimoCuadro);
          const r = await fetch("/api/kinect/imagen" + despues, { headers: { "X-PGC-Admin": TOKEN }, cache: "no-store" });
          if (r.ok) {
            pausa = 0;
            const cuadro = r.headers.get("X-Kinect-Cuadro");
            if (cuadro === null) pausa = 200;               // sin número de cuadro no se puede esperar la siguiente
            if (cuadro === null || cuadro !== ultimoCuadro) {
              ultimoCuadro = cuadro;
              const url = URL.createObjectURL(await r.blob());
              const lista = new Image();
              lista.src = url;
              await lista.decode().catch(() => {});
              const img = $("#kinCamara");
              img.src = url;
              img.hidden = false;
              $("#vKinect").classList.add("con-camara");
              if (urlCamara) URL.revokeObjectURL(urlCamara);
              urlCamara = url;
              if (r.headers.has("X-Kinect-Detalle")) {
                $("#kinTexto").textContent = decodeURIComponent(r.headers.get("X-Kinect-Texto") || "").toLowerCase();
                $("#kinDetalle").textContent = decodeURIComponent(r.headers.get("X-Kinect-Detalle"));
                tSincronia = performance.now();
              }
            }
          } else {
            $("#kinCamara").hidden = true;
            $("#vKinect").classList.remove("con-camara");
          }
        } catch (e) {}
      }
      await new Promise((listo) => setTimeout(listo, pausa));
    }
  }
  if (TOKEN) bucleCamara();
  const adminJSON = (ruta, cuerpo) => fetch(ruta, { method: "POST",
    headers: { "X-PGC-Admin": TOKEN, "Content-Type": "application/json" }, body: JSON.stringify(cuerpo) });
  async function ordenKinect(cuerpo, ruta = "/api/kinect/control") {
    const r = await adminJSON(ruta, cuerpo).catch(() => null);
    if (!r || !r.ok) avisoAdmin(r ? ((await r.json().catch(() => ({}))).detail || "No se pudo.") : "Sin conexión con el servidor.");
  }
  let ecoActivo = false;
  document.querySelectorAll("#ctrlKinect [data-kin]").forEach((b) =>
    b.addEventListener("click", () => ordenKinect({ accion: b.dataset.kin })));
  $("#kinEco").addEventListener("click", () => ordenKinect({ activo: !ecoActivo }, "/api/kinect/eco"));
  $("#kinLiberar").addEventListener("click", () => ordenKinect({}, "/api/kinect/liberar"));
  $("#kinNuevoCodigo").addEventListener("click", async () => {
    const r = await adminJSON("/api/kinect/codigo", {}).catch(() => null);
    if (r && r.ok) { const d = await r.json(); versionCodigo = d.version; ponerCodigo(d.codigo); avisoAdmin("Código nuevo para el Kinect"); }
    else avisoAdmin("No se pudo cambiar el código.");
  });
  $("#kinDiagnostico").addEventListener("click", () => window.open("/diagnostico", "_blank"));

  // ---------- derecha: cola y recientes
  function pintarCola(cola) {
    const ol = $("#cola");
    ol.textContent = "";
    cola.slice(0, MAX_COLA_VISIBLE).forEach((m, k) => {
      const li = document.createElement("li");
      const n = document.createElement("span");
      n.className = "num"; n.textContent = k + 1;
      const t = document.createElement("span");
      t.textContent = m.texto;
      if (m.nombre) {
        const a = document.createElement("span");
        a.className = "autor"; a.textContent = autorDe(m);
        t.appendChild(a);
      }
      li.append(n, t);
      if (TOKEN && m.pid) {
        const b = document.createElement("button");
        b.type = "button"; b.className = "bloquear-li"; b.textContent = "Bloquear";
        b.title = "Pausa a esta persona durante la sesión";
        b.addEventListener("click", () => bloquear(m.pid, m.nombre));
        li.appendChild(b);
      }
      ol.appendChild(li);
    });
    if (cola.length > MAX_COLA_VISIBLE) {
      const li = document.createElement("li");
      li.className = "mas";
      li.textContent = "y " + (cola.length - MAX_COLA_VISIBLE) + " más";
      ol.appendChild(li);
    }
    $("#colaVacia").style.display = cola.length ? "none" : "block";
  }
  function pintarHistorial(hist) {
    const ul = $("#historial");
    ul.textContent = "";
    hist.slice(0, 4).forEach((m) => {
      const li = document.createElement("li");
      const n = document.createElement("span");      // "Jean: hola jurado"
      n.className = "quien-hist"; n.textContent = (m.nombre || "Anónimo") + ": ";
      li.append(n, m.texto);
      if (m.saltado) {
        const e = document.createElement("span");
        e.className = "etiqueta"; e.textContent = "saltado";
        li.appendChild(e);
      }
      ul.appendChild(li);
    });
    $("#histVacio").style.display = hist.length ? "none" : "block";
  }

  // ---------- aplicar el estado recibido
  function aplicar(d) {
    if (d.tipo !== "estado") return;

    // QR y URL pública
    if (d.url_publica !== urlQr) {
      urlQr = d.url_publica;
      $("#qr").src = "/qr.png?u=" + encodeURIComponent(urlQr);
      // Corte de línea solo después de los puntos: "…-uploaded." / "trycloudflare.com"
      $("#url").textContent = urlQr.replace(/^https?:\/\//, "").replace(/\./g, ".​");
    }

    // Estados
    const m = d.mano;
    estadoFila("Mano", m.modo === "real" ? "ok" : "aviso",
      m.modo !== "real" ? "Simulada" : (m.medio === "ble" ? "Bluetooth · " : "USB · ") + m.puerto);
    const v = d.voz;
    estadoFila("Voz", v.estado === "listo" ? "ok" : v.estado === "cargando" ? "aviso" : v.estado === "error" ? "error" : "",
      v.estado === "listo" ? "Lista en " + ((v.dispositivo || "").startsWith("cuda") ? "GPU" : "CPU")
        : v.estado === "cargando" ? "Cargando…" : mayus(v.estado));
    const t = d.tunel;
    estadoFila("Tunel", t.estado === "activo" ? "ok" : t.estado === "iniciando" ? "aviso" : "error",
      t.estado === "activo" ? "Activo" : t.estado === "iniciando" ? "Iniciando…" : t.estado === "apagado" ? "Solo red local" : mayus(t.estado));

    // Letras que sabe hacer la mano (reposo)
    if (m.letras) ponerAlfabeto(m.letras.toUpperCase());
    else if (letrasPorDefecto) ponerAlfabeto(letrasPorDefecto);
    else pedirLetrasPorDefecto();

    // Centro
    const a = d.actual;
    $("#btnSaltar").disabled = !a || a.saltado;
    actualPid = a && !a.saltado && !(d.bloqueados || []).includes(a.pid) ? a.pid : null;
    actualNombre = a ? a.nombre : null;
    $("#btnBloquear").disabled = !actualPid;
    $("#btnBloquear").textContent = actualPid && actualNombre ? "Bloquear a " + actualNombre : "Bloquear participante";
    const k = d.kinect || {};
    ecoActivo = !!k.eco;
    pintarKinect(k, !!a);
    // La mano tiene prioridad; si no deletrea, se ve el Kinect mientras se usa
    const verKinect = k.controles && k.conectado && (k.activo || !!k.texto);
    mostrarVista(a ? "deletreo" : verKinect ? "kinect" : "reposo");
    if (a) pintarDeletreo(a);
    else { claveGlifo = null; idPalabra = null; }

    pintarCola(d.cola);
    pintarHistorial(d.historial);
  }
  addEventListener("resize", () => moverMarca(true));

  // ---------- conexión en vivo
  let ws = null, espera = 1000;
  function conectar() {
    if (ws && ws.readyState <= 1) return;
    ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "/ws");
    ws.onopen = () => { espera = 1000; $("#desconectado").classList.remove("si"); };
    ws.onmessage = (e) => { try { aplicar(JSON.parse(e.data)); } catch (x) { console.error(x); } };
    ws.onclose = () => {
      $("#desconectado").classList.add("si");
      setTimeout(conectar, espera);
      espera = Math.min(espera * 2, 5000);
    };
  }
  conectar();

  // ---------- controles
  function completa() {
    if (document.fullscreenElement) document.exitFullscreen();
    else document.documentElement.requestFullscreen().catch(() => {});
  }
  $("#btnCompleta").addEventListener("click", completa);
  document.addEventListener("keydown", (e) => { if (e.key === "f" || e.key === "F") completa(); });
  if (!TOKEN) $("#grupos").style.display = "none";      // abierta desde otro equipo: sin controles
  let actualPid = null, actualNombre = null;
  $("#btnBloquear").addEventListener("click", () => {
    if (!actualPid) return;
    $("#btnBloquear").disabled = true;
    bloquear(actualPid, actualNombre);
  });
  $("#btnReconectar").addEventListener("click", () => admin("/api/mano/reconectar"));
  $("#btnSaltar").addEventListener("click", () => {
    $("#btnSaltar").disabled = true;               // el estado nuevo lo vuelve a habilitar si hace falta
    admin("/api/mano/saltar");
  });
})();
</script>
</body>
</html>
```

## `firmware/esp32/config_ble.example.py`

```python
# config_ble.example.py  —  EJEMPLO con datos ficticios
# -----------------------------------------------------------------------------
# Copia este archivo en la placa con el nombre config_ble.py y pon tu token.
# NO guardes config_ble.py con el token real en el proyecto ni lo compartas.
# Sin config_ble.py en la placa, la mano funciona solo por USB.
# -----------------------------------------------------------------------------

NOMBRE = "Mano-LSC"                 # nombre con el que la placa aparece por Bluetooth

# Mismo valor que PGC_MANO_BLE_TOKEN en el .env del PC (mínimo 16 caracteres).
# Para generar uno:  py -3.11 -c "import secrets; print(secrets.token_urlsafe(24))"
TOKEN = "cambia-este-token-por-uno-aleatorio"
```

## `firmware/esp32/main - copia.py`

```python
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
# =============================================================================
# >>> INICIO DE LO AGREGADO: este bloque reemplaza el BUCLE PRINCIPAL original.
# Recibe las MISMAS órdenes por USB y, si existe config_ble.py, también por
# Bluetooth (BLE, servicio "UART" de Nordic, con token), y responde con los
# MISMOS textos del código original.
# Todo lo que está arriba de este bloque es el código original sin cambios.
# =============================================================================
import bluetooth
from micropython import const

try:
    import uselect as select
except ImportError:
    import select

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_READ | _FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE)


def _ble_aviso(texto):
    print("# " + texto)            # avisos del Bluetooth: se ven en Thonny, el PC los ignora


def atender_orden(cmd, responder):
    """Lo mismo que hacía el bucle original con cada orden. Devuelve False con 'salir'."""
    cmd = cmd.strip().lower()
    if not cmd:
        return True
    if cmd == "salir":
        return False
    elif cmd == "reset" or cmd == "1":
        reset_all()
        responder("reset_ok")
    elif cmd in acciones:
        reset_all()
        acciones[cmd]()
        responder("gesto_" + cmd + "_ok")
    elif len(cmd) > 1:
        if responder is print:
            deletrear(cmd)          # por USB: la función original tal cual
        else:
            # por Bluetooth: los mismos pasos y textos de deletrear(), enviados al PC
            for letra in cmd:
                if letra in acciones:
                    reset_all()
                    acciones[letra]()
                    responder("gesto_" + letra + "_ok")
                    responder("letra_actual:" + letra)
                    time.sleep(PAUSA_LETRA)
                else:
                    responder("letra_" + letra + "_no_disponible")
            responder("deletreo_completo")
            reset_all()
    else:
        responder("comando_no_reconocido")
    return True


class LectorUSB:
    """Lee órdenes por USB sin quedarse esperando (para poder atender también el Bluetooth)."""

    def __init__(self):
        self.poll = select.poll()
        self.poll.register(sys.stdin, select.POLLIN)
        self.buffer = ""

    def leer(self):
        while self.poll.poll(0):
            c = sys.stdin.read(1)
            if c in ("\n", "\r", ""):
                if self.buffer:
                    linea, self.buffer = self.buffer, ""
                    return linea
                if c == "":
                    return None
                continue
            if len(self.buffer) < 64:
                self.buffer += c
        return None


class ServidorBLE:
    """La mano como periférico BLE con el servicio UART de Nordic. Nunca bloquea el bucle.

    Un solo PC a la vez (al conectarse uno, la placa deja de anunciarse). La primera
    línea debe ser "auth <TOKEN>" en 3 s; si no, la placa lo desconecta.
    """

    def __init__(self, cfg):
        self.nombre = getattr(cfg, "NOMBRE", "Mano-LSC")
        self.token = cfg.TOKEN
        if not self.token or len(self.token) < 16:
            raise ValueError("TOKEN de config_ble.py muy corto (minimo 16 caracteres)")
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        try:
            self.ble.config(gap_name=self.nombre)
        except Exception:
            pass
        self.ble.irq(self._irq)
        ((self.h_tx, self.h_rx),) = self.ble.gatts_register_services(((_UART_UUID, (_UART_TX, _UART_RX)),))
        self.ble.gatts_set_buffer(self.h_rx, 256, True)
        self.conexion = None
        self.autenticado = False
        self.desde = time.ticks_ms()
        self.trozos = []            # lo que llega por Bluetooth (lo llena _irq)
        self.buffer = b""
        self.eventos = []           # avisos de conexión/desconexión para imprimirlos fuera de _irq
        nombre = self.nombre.encode()
        self.anuncio = b"\x02\x01\x06" + bytes((len(nombre) + 1, 0x09)) + nombre
        self.respuesta = bytes((17, 0x07)) + bytes(_UART_UUID)
        self._anunciar()
        _ble_aviso("Bluetooth listo: se anuncia como {}".format(self.nombre))

    def _anunciar(self):
        self.ble.gap_advertise(100000, adv_data=self.anuncio, resp_data=self.respuesta)

    def _irq(self, evento, datos):
        if evento == _IRQ_CENTRAL_CONNECT:
            self.conexion = datos[0]
            self.autenticado = False
            self.desde = time.ticks_ms()
            self.trozos = []
            self.buffer = b""
            self.eventos.append("PC conectado por Bluetooth")
        elif evento == _IRQ_CENTRAL_DISCONNECT:
            self.conexion = None
            self.autenticado = False
            self.eventos.append("PC desconectado; anunciando de nuevo")
            self._anunciar()
        elif evento == _IRQ_GATTS_WRITE:
            if datos[1] == self.h_rx:
                self.trozos.append(self.ble.gatts_read(self.h_rx))

    def _enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), 20):             # paquetes de 20 bytes: sirve con cualquier MTU
            try:
                self.ble.gatts_notify(self.conexion, self.h_tx, datos[k:k + 20])
            except Exception:
                return

    def _desconectar(self):
        try:
            self.ble.gap_disconnect(self.conexion)
        except Exception:
            pass

    def atender(self, atender_orden):
        """Una pasada: avisos, token y órdenes recibidas. Devuelve False con 'salir'."""
        while self.eventos:
            _ble_aviso(self.eventos.pop(0))
        if self.conexion is None:
            return True
        while self.trozos:
            self.buffer += self.trozos.pop(0)
        if len(self.buffer) > 256:
            self.buffer = b""
        lineas = []
        while b"\n" in self.buffer:
            linea, self.buffer = self.buffer.split(b"\n", 1)
            lineas.append(linea.decode("utf-8", "ignore").strip("\r"))
        if not self.autenticado:
            if lineas and lineas[0].strip() == "auth " + self.token:
                self.autenticado = True
                lineas = lineas[1:]
                self._enviar("ok:auth")
            elif lineas:
                self._enviar("error:auth")
                _ble_aviso("Conexion rechazada (token incorrecto)")
                self._desconectar()
                return True
            elif time.ticks_diff(time.ticks_ms(), self.desde) > 3000:
                self._desconectar()                    # no se presentó a tiempo
                return True
        for linea in lineas:
            if not atender_orden(linea, self._enviar):
                return False
        return True


usb = LectorUSB()
ble = None
try:
    import config_ble
    ble = ServidorBLE(config_ble)
except ImportError:
    pass                            # sin config_ble.py: solo USB, igual que el original
except Exception as error:
    _ble_aviso("Bluetooth desactivado: {}".format(error))

print("Listo. Esperando comandos...")
seguir = True
while seguir:
    try:
        linea = usb.leer()
        if linea is not None:
            seguir = atender_orden(linea, print)
        if seguir and ble is not None:
            seguir = ble.atender(atender_orden)
        time.sleep_ms(5)
    except KeyboardInterrupt:
        break

reset_all()
print("Programa terminado.")
# =============================================================================
# <<< FIN DE LO AGREGADO
# =============================================================================
```

## `firmware/esp32/main.py`

```python
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
# =============================================================================
# >>> INICIO DE LO AGREGADO: este bloque reemplaza el BUCLE PRINCIPAL original.
# Recibe las MISMAS órdenes por USB y, si existe config_ble.py, también por
# Bluetooth (BLE, servicio "UART" de Nordic, con token), y responde con los
# MISMOS textos del código original.
# Todo lo que está arriba de este bloque es el código original sin cambios.
# =============================================================================
import bluetooth
from micropython import const

try:
    import uselect as select
except ImportError:
    import select

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_READ | _FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE)


def _ble_aviso(texto):
    print("# " + texto)            # avisos del Bluetooth: se ven en Thonny, el PC los ignora


def atender_orden(cmd, responder):
    """Lo mismo que hacía el bucle original con cada orden. Devuelve False con 'salir'."""
    cmd = cmd.strip().lower()
    if not cmd:
        return True
    if cmd == "salir":
        return False
    elif cmd == "reset" or cmd == "1":
        reset_all()
        responder("reset_ok")
    elif cmd in acciones:
        reset_all()
        acciones[cmd]()
        responder("gesto_" + cmd + "_ok")
    elif len(cmd) > 1:
        if responder is print:
            deletrear(cmd)          # por USB: la función original tal cual
        else:
            # por Bluetooth: los mismos pasos y textos de deletrear(), enviados al PC
            for letra in cmd:
                if letra in acciones:
                    reset_all()
                    acciones[letra]()
                    responder("gesto_" + letra + "_ok")
                    responder("letra_actual:" + letra)
                    time.sleep(PAUSA_LETRA)
                else:
                    responder("letra_" + letra + "_no_disponible")
            responder("deletreo_completo")
            reset_all()
    else:
        responder("comando_no_reconocido")
    return True


class LectorUSB:
    """Lee órdenes por USB sin quedarse esperando (para poder atender también el Bluetooth)."""

    def __init__(self):
        self.poll = select.poll()
        self.poll.register(sys.stdin, select.POLLIN)
        self.buffer = ""

    def leer(self):
        while self.poll.poll(0):
            c = sys.stdin.read(1)
            if c in ("\n", "\r", ""):
                if self.buffer:
                    linea, self.buffer = self.buffer, ""
                    return linea
                if c == "":
                    return None
                continue
            if len(self.buffer) < 64:
                self.buffer += c
        return None


class ServidorBLE:
    """La mano como periférico BLE con el servicio UART de Nordic. Nunca bloquea el bucle.

    Un solo PC a la vez (al conectarse uno, la placa deja de anunciarse). La primera
    línea debe ser "auth <TOKEN>" en 3 s; si no, la placa lo desconecta.
    """

    def __init__(self, cfg):
        self.nombre = getattr(cfg, "NOMBRE", "Mano-LSC")
        self.token = cfg.TOKEN
        if not self.token or len(self.token) < 16:
            raise ValueError("TOKEN de config_ble.py muy corto (minimo 16 caracteres)")
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        try:
            self.ble.config(gap_name=self.nombre)
        except Exception:
            pass
        self.ble.irq(self._irq)
        ((self.h_tx, self.h_rx),) = self.ble.gatts_register_services(((_UART_UUID, (_UART_TX, _UART_RX)),))
        self.ble.gatts_set_buffer(self.h_rx, 256, True)
        self.conexion = None
        self.autenticado = False
        self.desde = time.ticks_ms()
        self.trozos = []            # lo que llega por Bluetooth (lo llena _irq)
        self.buffer = b""
        self.eventos = []           # avisos de conexión/desconexión para imprimirlos fuera de _irq
        nombre = self.nombre.encode()
        self.anuncio = b"\x02\x01\x06" + bytes((len(nombre) + 1, 0x09)) + nombre
        self.respuesta = bytes((17, 0x07)) + bytes(_UART_UUID)
        self._anunciar()
        _ble_aviso("Bluetooth listo: se anuncia como {}".format(self.nombre))

    def _anunciar(self):
        self.ble.gap_advertise(100000, adv_data=self.anuncio, resp_data=self.respuesta)

    def _irq(self, evento, datos):
        if evento == _IRQ_CENTRAL_CONNECT:
            self.conexion = datos[0]
            self.autenticado = False
            self.desde = time.ticks_ms()
            self.trozos = []
            self.buffer = b""
            self.eventos.append("PC conectado por Bluetooth")
        elif evento == _IRQ_CENTRAL_DISCONNECT:
            self.conexion = None
            self.autenticado = False
            self.eventos.append("PC desconectado; anunciando de nuevo")
            self._anunciar()
        elif evento == _IRQ_GATTS_WRITE:
            if datos[1] == self.h_rx:
                self.trozos.append(self.ble.gatts_read(self.h_rx))

    def _enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), 20):             # paquetes de 20 bytes: sirve con cualquier MTU
            try:
                self.ble.gatts_notify(self.conexion, self.h_tx, datos[k:k + 20])
            except Exception:
                return

    def _desconectar(self):
        try:
            self.ble.gap_disconnect(self.conexion)
        except Exception:
            pass

    def atender(self, atender_orden):
        """Una pasada: avisos, token y órdenes recibidas. Devuelve False con 'salir'."""
        while self.eventos:
            _ble_aviso(self.eventos.pop(0))
        if self.conexion is None:
            return True
        while self.trozos:
            self.buffer += self.trozos.pop(0)
        if len(self.buffer) > 256:
            self.buffer = b""
        lineas = []
        while b"\n" in self.buffer:
            linea, self.buffer = self.buffer.split(b"\n", 1)
            lineas.append(linea.decode("utf-8", "ignore").strip("\r"))
        if not self.autenticado:
            if lineas and lineas[0].strip() == "auth " + self.token:
                self.autenticado = True
                lineas = lineas[1:]
                self._enviar("ok:auth")
            elif lineas:
                self._enviar("error:auth")
                _ble_aviso("Conexion rechazada (token incorrecto)")
                self._desconectar()
                return True
            elif time.ticks_diff(time.ticks_ms(), self.desde) > 3000:
                self._desconectar()                    # no se presentó a tiempo
                return True
        for linea in lineas:
            if not atender_orden(linea, self._enviar):
                return False
        return True


usb = LectorUSB()
ble = None
try:
    import config_ble
    ble = ServidorBLE(config_ble)
except ImportError:
    pass                            # sin config_ble.py: solo USB, igual que el original
except Exception as error:
    _ble_aviso("Bluetooth desactivado: {}".format(error))

print("Listo. Esperando comandos...")
seguir = True
while seguir:
    try:
        linea = usb.leer()
        if linea is not None:
            seguir = atender_orden(linea, print)
        if seguir and ble is not None:
            seguir = ble.atender(atender_orden)
        time.sleep_ms(5)
    except KeyboardInterrupt:
        break

reset_all()
print("Programa terminado.")
# =============================================================================
# <<< FIN DE LO AGREGADO
# =============================================================================
```

## `firmware/esp32/main_mano.py`

```python
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
# =============================================================================
# >>> INICIO DE LO AGREGADO: este bloque reemplaza el BUCLE PRINCIPAL original.
# Recibe las MISMAS órdenes por USB y, si existe config_ble.py, también por
# Bluetooth (BLE, servicio "UART" de Nordic, con token), y responde con los
# MISMOS textos del código original.
# Todo lo que está arriba de este bloque es el código original sin cambios.
# =============================================================================
import bluetooth
from micropython import const

try:
    import uselect as select
except ImportError:
    import select

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_READ | _FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE)


def _ble_aviso(texto):
    print("# " + texto)            # avisos del Bluetooth: se ven en Thonny, el PC los ignora


def atender_orden(cmd, responder):
    """Lo mismo que hacía el bucle original con cada orden. Devuelve False con 'salir'."""
    cmd = cmd.strip().lower()
    if not cmd:
        return True
    if cmd == "salir":
        return False
    elif cmd == "reset" or cmd == "1":
        reset_all()
        responder("reset_ok")
    elif cmd in acciones:
        reset_all()
        acciones[cmd]()
        responder("gesto_" + cmd + "_ok")
    elif len(cmd) > 1:
        if responder is print:
            deletrear(cmd)          # por USB: la función original tal cual
        else:
            # por Bluetooth: los mismos pasos y textos de deletrear(), enviados al PC
            for letra in cmd:
                if letra in acciones:
                    reset_all()
                    acciones[letra]()
                    responder("gesto_" + letra + "_ok")
                    responder("letra_actual:" + letra)
                    time.sleep(PAUSA_LETRA)
                else:
                    responder("letra_" + letra + "_no_disponible")
            responder("deletreo_completo")
            reset_all()
    else:
        responder("comando_no_reconocido")
    return True


class LectorUSB:
    """Lee órdenes por USB sin quedarse esperando (para poder atender también el Bluetooth)."""

    def __init__(self):
        self.poll = select.poll()
        self.poll.register(sys.stdin, select.POLLIN)
        self.buffer = ""

    def leer(self):
        while self.poll.poll(0):
            c = sys.stdin.read(1)
            if c in ("\n", "\r", ""):
                if self.buffer:
                    linea, self.buffer = self.buffer, ""
                    return linea
                if c == "":
                    return None
                continue
            if len(self.buffer) < 64:
                self.buffer += c
        return None


class ServidorBLE:
    """La mano como periférico BLE con el servicio UART de Nordic. Nunca bloquea el bucle.

    Un solo PC a la vez (al conectarse uno, la placa deja de anunciarse). La primera
    línea debe ser "auth <TOKEN>" en 3 s; si no, la placa lo desconecta.
    """

    def __init__(self, cfg):
        self.nombre = getattr(cfg, "NOMBRE", "Mano-LSC")
        self.token = cfg.TOKEN
        if not self.token or len(self.token) < 16:
            raise ValueError("TOKEN de config_ble.py muy corto (minimo 16 caracteres)")
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        try:
            self.ble.config(gap_name=self.nombre)
        except Exception:
            pass
        self.ble.irq(self._irq)
        ((self.h_tx, self.h_rx),) = self.ble.gatts_register_services(((_UART_UUID, (_UART_TX, _UART_RX)),))
        self.ble.gatts_set_buffer(self.h_rx, 256, True)
        self.conexion = None
        self.autenticado = False
        self.desde = time.ticks_ms()
        self.trozos = []            # lo que llega por Bluetooth (lo llena _irq)
        self.buffer = b""
        self.eventos = []           # avisos de conexión/desconexión para imprimirlos fuera de _irq
        nombre = self.nombre.encode()
        self.anuncio = b"\x02\x01\x06" + bytes((len(nombre) + 1, 0x09)) + nombre
        self.respuesta = bytes((17, 0x07)) + bytes(_UART_UUID)
        self._anunciar()
        _ble_aviso("Bluetooth listo: se anuncia como {}".format(self.nombre))

    def _anunciar(self):
        self.ble.gap_advertise(100000, adv_data=self.anuncio, resp_data=self.respuesta)

    def _irq(self, evento, datos):
        if evento == _IRQ_CENTRAL_CONNECT:
            self.conexion = datos[0]
            self.autenticado = False
            self.desde = time.ticks_ms()
            self.trozos = []
            self.buffer = b""
            self.eventos.append("PC conectado por Bluetooth")
        elif evento == _IRQ_CENTRAL_DISCONNECT:
            self.conexion = None
            self.autenticado = False
            self.eventos.append("PC desconectado; anunciando de nuevo")
            self._anunciar()
        elif evento == _IRQ_GATTS_WRITE:
            if datos[1] == self.h_rx:
                self.trozos.append(self.ble.gatts_read(self.h_rx))

    def _enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), 20):             # paquetes de 20 bytes: sirve con cualquier MTU
            try:
                self.ble.gatts_notify(self.conexion, self.h_tx, datos[k:k + 20])
            except Exception:
                return

    def _desconectar(self):
        try:
            self.ble.gap_disconnect(self.conexion)
        except Exception:
            pass

    def atender(self, atender_orden):
        """Una pasada: avisos, token y órdenes recibidas. Devuelve False con 'salir'."""
        while self.eventos:
            _ble_aviso(self.eventos.pop(0))
        if self.conexion is None:
            return True
        while self.trozos:
            self.buffer += self.trozos.pop(0)
        if len(self.buffer) > 256:
            self.buffer = b""
        lineas = []
        while b"\n" in self.buffer:
            linea, self.buffer = self.buffer.split(b"\n", 1)
            lineas.append(linea.decode("utf-8", "ignore").strip("\r"))
        if not self.autenticado:
            if lineas and lineas[0].strip() == "auth " + self.token:
                self.autenticado = True
                lineas = lineas[1:]
                self._enviar("ok:auth")
            elif lineas:
                self._enviar("error:auth")
                _ble_aviso("Conexion rechazada (token incorrecto)")
                self._desconectar()
                return True
            elif time.ticks_diff(time.ticks_ms(), self.desde) > 3000:
                self._desconectar()                    # no se presentó a tiempo
                return True
        for linea in lineas:
            if not atender_orden(linea, self._enviar):
                return False
        return True


usb = LectorUSB()
ble = None
try:
    import config_ble
    ble = ServidorBLE(config_ble)
except ImportError:
    pass                            # sin config_ble.py: solo USB, igual que el original
except Exception as error:
    _ble_aviso("Bluetooth desactivado: {}".format(error))

print("Listo. Esperando comandos...")
seguir = True
while seguir:
    try:
        linea = usb.leer()
        if linea is not None:
            seguir = atender_orden(linea, print)
        if seguir and ble is not None:
            seguir = ble.atender(atender_orden)
        time.sleep_ms(5)
    except KeyboardInterrupt:
        break

reset_all()
print("Programa terminado.")
# =============================================================================
# <<< FIN DE LO AGREGADO
# =============================================================================
```

## `firmware/esp32/original/bucle_ble.py`

```python
# =============================================================================
# >>> INICIO DE LO AGREGADO: este bloque reemplaza el BUCLE PRINCIPAL original.
# Recibe las MISMAS órdenes por USB y, si existe config_ble.py, también por
# Bluetooth (BLE, servicio "UART" de Nordic, con token), y responde con los
# MISMOS textos del código original.
# Todo lo que está arriba de este bloque es el código original sin cambios.
# =============================================================================
import bluetooth
from micropython import const

try:
    import uselect as select
except ImportError:
    import select

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)
_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_READ | _FLAG_NOTIFY)
_UART_RX = (bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"), _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE)


def _ble_aviso(texto):
    print("# " + texto)            # avisos del Bluetooth: se ven en Thonny, el PC los ignora


def atender_orden(cmd, responder):
    """Lo mismo que hacía el bucle original con cada orden. Devuelve False con 'salir'."""
    cmd = cmd.strip().lower()
    if not cmd:
        return True
    if cmd == "salir":
        return False
    elif cmd == "reset" or cmd == "1":
        reset_all()
        responder("reset_ok")
    elif cmd in acciones:
        reset_all()
        acciones[cmd]()
        responder("gesto_" + cmd + "_ok")
    elif len(cmd) > 1:
        if responder is print:
            deletrear(cmd)          # por USB: la función original tal cual
        else:
            # por Bluetooth: los mismos pasos y textos de deletrear(), enviados al PC
            for letra in cmd:
                if letra in acciones:
                    reset_all()
                    acciones[letra]()
                    responder("gesto_" + letra + "_ok")
                    responder("letra_actual:" + letra)
                    time.sleep(PAUSA_LETRA)
                else:
                    responder("letra_" + letra + "_no_disponible")
            responder("deletreo_completo")
            reset_all()
    else:
        responder("comando_no_reconocido")
    return True


class LectorUSB:
    """Lee órdenes por USB sin quedarse esperando (para poder atender también el Bluetooth)."""

    def __init__(self):
        self.poll = select.poll()
        self.poll.register(sys.stdin, select.POLLIN)
        self.buffer = ""

    def leer(self):
        while self.poll.poll(0):
            c = sys.stdin.read(1)
            if c in ("\n", "\r", ""):
                if self.buffer:
                    linea, self.buffer = self.buffer, ""
                    return linea
                if c == "":
                    return None
                continue
            if len(self.buffer) < 64:
                self.buffer += c
        return None


class ServidorBLE:
    """La mano como periférico BLE con el servicio UART de Nordic. Nunca bloquea el bucle.

    Un solo PC a la vez (al conectarse uno, la placa deja de anunciarse). La primera
    línea debe ser "auth <TOKEN>" en 3 s; si no, la placa lo desconecta.
    """

    def __init__(self, cfg):
        self.nombre = getattr(cfg, "NOMBRE", "Mano-LSC")
        self.token = cfg.TOKEN
        if not self.token or len(self.token) < 16:
            raise ValueError("TOKEN de config_ble.py muy corto (minimo 16 caracteres)")
        self.ble = bluetooth.BLE()
        self.ble.active(True)
        try:
            self.ble.config(gap_name=self.nombre)
        except Exception:
            pass
        self.ble.irq(self._irq)
        ((self.h_tx, self.h_rx),) = self.ble.gatts_register_services(((_UART_UUID, (_UART_TX, _UART_RX)),))
        self.ble.gatts_set_buffer(self.h_rx, 256, True)
        self.conexion = None
        self.autenticado = False
        self.desde = time.ticks_ms()
        self.trozos = []            # lo que llega por Bluetooth (lo llena _irq)
        self.buffer = b""
        self.eventos = []           # avisos de conexión/desconexión para imprimirlos fuera de _irq
        nombre = self.nombre.encode()
        self.anuncio = b"\x02\x01\x06" + bytes((len(nombre) + 1, 0x09)) + nombre
        self.respuesta = bytes((17, 0x07)) + bytes(_UART_UUID)
        self._anunciar()
        _ble_aviso("Bluetooth listo: se anuncia como {}".format(self.nombre))

    def _anunciar(self):
        self.ble.gap_advertise(100000, adv_data=self.anuncio, resp_data=self.respuesta)

    def _irq(self, evento, datos):
        if evento == _IRQ_CENTRAL_CONNECT:
            self.conexion = datos[0]
            self.autenticado = False
            self.desde = time.ticks_ms()
            self.trozos = []
            self.buffer = b""
            self.eventos.append("PC conectado por Bluetooth")
        elif evento == _IRQ_CENTRAL_DISCONNECT:
            self.conexion = None
            self.autenticado = False
            self.eventos.append("PC desconectado; anunciando de nuevo")
            self._anunciar()
        elif evento == _IRQ_GATTS_WRITE:
            if datos[1] == self.h_rx:
                self.trozos.append(self.ble.gatts_read(self.h_rx))

    def _enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), 20):             # paquetes de 20 bytes: sirve con cualquier MTU
            try:
                self.ble.gatts_notify(self.conexion, self.h_tx, datos[k:k + 20])
            except Exception:
                return

    def _desconectar(self):
        try:
            self.ble.gap_disconnect(self.conexion)
        except Exception:
            pass

    def atender(self, atender_orden):
        """Una pasada: avisos, token y órdenes recibidas. Devuelve False con 'salir'."""
        while self.eventos:
            _ble_aviso(self.eventos.pop(0))
        if self.conexion is None:
            return True
        while self.trozos:
            self.buffer += self.trozos.pop(0)
        if len(self.buffer) > 256:
            self.buffer = b""
        lineas = []
        while b"\n" in self.buffer:
            linea, self.buffer = self.buffer.split(b"\n", 1)
            lineas.append(linea.decode("utf-8", "ignore").strip("\r"))
        if not self.autenticado:
            if lineas and lineas[0].strip() == "auth " + self.token:
                self.autenticado = True
                lineas = lineas[1:]
                self._enviar("ok:auth")
            elif lineas:
                self._enviar("error:auth")
                _ble_aviso("Conexion rechazada (token incorrecto)")
                self._desconectar()
                return True
            elif time.ticks_diff(time.ticks_ms(), self.desde) > 3000:
                self._desconectar()                    # no se presentó a tiempo
                return True
        for linea in lineas:
            if not atender_orden(linea, self._enviar):
                return False
        return True


usb = LectorUSB()
ble = None
try:
    import config_ble
    ble = ServidorBLE(config_ble)
except ImportError:
    pass                            # sin config_ble.py: solo USB, igual que el original
except Exception as error:
    _ble_aviso("Bluetooth desactivado: {}".format(error))

print("Listo. Esperando comandos...")
seguir = True
while seguir:
    try:
        linea = usb.leer()
        if linea is not None:
            seguir = atender_orden(linea, print)
        if seguir and ble is not None:
            seguir = ble.atender(atender_orden)
        time.sleep_ms(5)
    except KeyboardInterrupt:
        break

reset_all()
print("Programa terminado.")
# =============================================================================
# <<< FIN DE LO AGREGADO
# =============================================================================
```

## `firmware/esp32/original/main_original.py`

```python
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
```

## `firmware/esp32/protocolo.md`

````markdown
# Firmware de la mano: archivos, órdenes, Bluetooth y carga con Thonny

ESP32-S3 N16R8 con MicroPython y 6 servos.

## 0. Regla del hardware: USB **o** 12 V, nunca los dos

En la PCB de la mano **no se pueden conectar el USB y los 12 V a la vez**.

| Conectado | Para qué |
|---|---|
| **Solo USB** (sin 12 V) | Subir archivos con Thonny y probar las respuestas. Los servos **no** se mueven |
| **Solo 12 V** (sin USB) | La mano funcionando. El PC la maneja **solo por Bluetooth** |

Por eso, en el PC el `.env` lleva `PGC_MANO=ble`. Con la mano encendida no hay respaldo por USB.

## 1. Archivos

| Archivo | Va a la placa | Qué es |
|---|---|---|
| `main.py` | **Sí** | **Tu código original, idéntico en las líneas 1–225**. Desde la línea 226 va el bloque agregado, marcado `>>> INICIO DE LO AGREGADO` … `<<< FIN DE LO AGREGADO`, que atiende las mismas órdenes también por Bluetooth |
| `config_ble.py` | **Sí** | Nombre y token. Solo existe en la placa. En el proyecto está `config_ble.example.py`, con datos ficticios |
| `prueba_dedos.py` | Solo para probar | Mueve cada dedo por separado, sin PC (sección 5) |
| `prueba.py` | Solo para probar | Cierra y abre cada dedo, uno por uno, y al final cierra toda la mano. Se usa igual que `prueba_dedos.py` |
| `original/main_original.py` | No | Tu código tal cual. Es la referencia de las pruebas |
| `original/bucle_ble.py` | No | El bloque agregado. `scripts/armar_main_placa.py` arma `main.py` con los dos |
| `referencia_doby/` | No | Otro proyecto |

Para cambiar pines, valores o letras, sigue `docs/GUIA_MODIFICAR_MANO.md`: ahí están los números de línea y el procedimiento.

## 2. Órdenes y respuestas (las de tu código, iguales por USB y por Bluetooth)

| Orden | Qué hace | Respuesta |
|---|---|---|
| una letra de `acciones` (a b c d e f i k l m n o p q r t u v w x y) | `reset_all()` y la función de la letra | `gesto_<letra>_ok` |
| `reset` o `1` | `reset_all()` | `reset_ok` |
| una palabra (más de una letra) | `deletrear()` | `gesto_…_ok`, `letra_actual:…`, `letra_…_no_disponible`, …, `deletreo_completo` |
| `salir` | Termina el programa (`reset_all()` y "Programa terminado.") | — |
| otra cosa de una letra | Nada | `comando_no_reconocido` |

- Al arrancar imprime "Iniciando motores...", "Mano lista." y "Listo. Esperando comandos...".
- Si hay `config_ble.py`, también imprime avisos que empiezan por `# `, por ejemplo `# Bluetooth listo: se anuncia como Mano-LSC` o `# PC conectado por Bluetooth`.
- **El PC envía siempre letra por letra** y `reset`, nunca palabras. Tu firmware no tiene `ping` ni `letras` (una palabra se deletrearía), así que el PC comprueba la conexión con `reset` → `reset_ok`.

### Solo por Bluetooth (BLE)
El ESP32-S3 solo tiene **Bluetooth de bajo consumo (BLE)**. No crea un puerto COM, así que **no hace falta emparejarlo en Windows**. La placa usa el servicio "UART" de Nordic, el estándar para enviar texto por BLE:

| Característica | UUID | Uso |
|---|---|---|
| Servicio | `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` | |
| RX | `6E400002-…` | el PC escribe las órdenes (una por línea) |
| TX | `6E400003-…` | la placa notifica las respuestas (una por línea) |

1. El PC busca el dispositivo por su nombre (`NOMBRE` de `config_ble.py`, que debe coincidir con `PGC_MANO_BLE_NOMBRE`; por defecto `Mano-LSC`) y se conecta.
2. **Primera línea**: `auth <TOKEN>`. La placa responde `ok:auth`. Si el token es incorrecto, responde `error:auth` y desconecta. Si el token no llega en 3 s, también desconecta.
3. Desde ahí se usan las órdenes de la tabla, con las mismas respuestas.

- **Un solo PC a la vez**: mientras hay uno conectado, la placa deja de anunciarse. Al desconectarse, vuelve a anunciarse sola.
- Los datos viajan en paquetes de 20 bytes (sirve con cualquier adaptador).
- El Bluetooth nunca bloquea el bucle, y el USB sigue funcionando igual que en el original.
- **Alcance**: unos 10 m sin paredes. En la sustentación, deja el PC cerca de la mano.

## 3. Pines (los de `dedos_config`, líneas 12–17 de `main.py`)

| Dedo | GPIO | Nota |
|---|---|---|
| Índice | 8 | |
| Meñique | 3 | **Pin de arranque (strapping) del S3**: si la placa no arranca con los servos conectados, mueve el meñique a otro GPIO |
| Medio | 10 | |
| Anular | 4 | Invertido (abierto 2200, cerrado 500) |
| Pulgar | 6 | Invertido (abierto 1500, cerrado 500) |
| Pulgar 2 | 7 | |

La placa es **exclusiva de la mano**. Si algún día se vuelve a usar para Doby, hay conflicto en los GPIO 4, 6, 7 y 10.

## 4. Cargar el firmware con Thonny

**Antes de empezar:**
1. Cierra el servidor del PC.
2. **Quita los 12 V.**
3. Conecta el USB.

**Pasos:**
1. Abre Thonny. En **Herramientas › Opciones › Intérprete**, elige **MicroPython (ESP32)** y el puerto COM. Pulsa **Detener/Reiniciar** (el octágono rojo).
2. Abre **Ver › Archivos**. Abajo aparece **"Dispositivo MicroPython"**.
3. **Respaldo** (opcional): selecciona los archivos de la placa, clic derecho › **Descargar a …** una carpeta de tu PC.
4. **Borra de la placa** lo que ya no se usa (clic derecho › **Eliminar**): `config_wifi.py`, `mano_movimientos.py`, `mano_protocolo.py`, `mano_red.py`, `mano_vigilante.py`, `mano_servos.py`, `letras.json` y `secretos.py`, si existen.
5. Arriba, ve a `ProyectoPGC\firmware\esp32`, clic derecho sobre **`main.py`** › **Subir a /**, y acepta reemplazarlo.
6. **Crea `config_ble.py` en la placa**:
   1. En Thonny, **Archivo › Nuevo**, y pega:
      ```python
      NOMBRE = "Mano-LSC"
      TOKEN = "<el mismo valor de PGC_MANO_BLE_TOKEN del .env del PC>"
      ```
   2. **Archivo › Guardar como… › Dispositivo MicroPython**, con el nombre `config_ble.py`.
   3. No lo guardes en la carpeta del proyecto.
7. Pulsa **Detener/Reiniciar**. Deben aparecer "Iniciando motores...", "Mano lista.", `# Bluetooth listo: se anuncia como Mano-LSC` y "Listo. Esperando comandos...".
8. Prueba en la consola de Thonny: `a` → `gesto_a_ok`; `reset` → `reset_ok`. Sin 12 V, los servos no se mueven.
9. **Cierra Thonny**, desconecta el USB y conecta los 12 V. La mano arranca sola y queda esperando por Bluetooth.

**En el PC:**
1. **Enciende el Bluetooth**: Configuración › Bluetooth y dispositivos › Bluetooth **Activado**. **No emparejes la mano** ("Agregar dispositivo"): Windows guardaría claves que la placa no conoce y la conexión se cortaría. Si ya la emparejaste, quítala en Dispositivos (menú **⋯** › **Quitar dispositivo**) y reinicia la mano.
2. El `.env` debe tener:
   ```
   PGC_MANO=ble
   PGC_MANO_BLE_TOKEN=<el mismo TOKEN de config_ble.py>
   ```
3. Ejecuta `iniciar.bat`. En la pantalla debe salir **"Mano: Bluetooth · Mano-LSC"**.

Si sale "Simulada", revisa el log del servidor:
- `el Bluetooth del PC está apagado` → enciéndelo en Windows.
- `no se encontró` → revisa que la mano tenga 12 V, que esté cerca y que ningún otro PC o celular esté conectado a ella.
- `rechazó el token` → el TOKEN de `config_ble.py` y el del `.env` no coinciden.

Después usa **«Reconectar mano»** en la pantalla, o espera: el PC lo reintenta solo cada 10 s.

## 5. Probar cada dedo por separado (`prueba_dedos.py`)

Mueve un dedo a la vez (cerrado → mitad → abierto), 3 vueltas, sin PC. Sirve para revisar el cableado y la calibración.

1. **Sin 12 V y con USB**, en Thonny: clic derecho sobre `prueba_dedos.py` › **Subir a /**.
2. Luego, abajo, renombra en la placa `main.py` a `main_mano.py` y `prueba_dedos.py` a `main.py`. La placa solo ejecuta sola el archivo que se llama `main.py`.
3. Cierra Thonny, desconecta el USB y conecta los 12 V: la placa mueve los dedos uno por uno y termina con la mano abierta.
4. Para volver a la mano:
   1. Quita los 12 V y conecta el USB.
   2. En Thonny, borra el `main.py` (la prueba).
   3. Renombra `main_mano.py` a `main.py`, o vuelve a subir `firmware\esp32\main.py`.
````

## `firmware/esp32/prueba.py`

```python
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
```

## `firmware/esp32/prueba_dedos.py`

```python
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
```

## `tests/arnes_firmware.py`

```python
"""Arnés para ejecutar el firmware de la mano en el PC (CPython), sin la placa.

Ejecuta TAL CUAL el código original (original/main_original.py) y el main.py de la
placa, con piezas falsas de MicroPython:
- `machine`: registra cada pulso enviado a cada pin;
- `time`: registra cada time.sleep() (las pausas del código original);
- `sys.stdin`: las órdenes "por USB";
- `uselect`, `micropython` y `bluetooth`: el bucle sin bloqueo y una radio BLE falsa
  (RadioBLE) que conecta la placa con un "PC" falso (y con el adaptador real del PC
  a través de un bleak falso, ver BleakFalso).
"""
import asyncio
import io
import sys
import threading
import time as _time
import types
from contextlib import contextmanager
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
FIRMWARE = RAIZ / "firmware" / "esp32"
ORIGINAL = FIRMWARE / "original" / "main_original.py"
MAIN = FIRMWARE / "main.py"
MARCA = "# ---------------- BUCLE PRINCIPAL ----------------"
ARRANQUE = 12                      # eventos del arranque: 6 dedos × (pulso + pausa de 0,5 s)
UART_RX = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"     # el PC escribe aquí
UART_TX = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"     # la placa notifica aquí


class Registro(list):
    """Eventos: ("pulso", pin, ns) y ("pausa", segundos)."""


class StdinFalso:
    """El USB: se le escriben órdenes; el firmware las lee con readline() o read(1)."""

    def __init__(self, texto=""):
        self._datos = texto
        self._lock = threading.Lock()

    def escribir(self, texto):
        with self._lock:
            self._datos += texto

    def hay_datos(self):
        return bool(self._datos)

    def read(self, n=1):
        with self._lock:
            c, self._datos = self._datos[:n], self._datos[n:]
            return c

    def readline(self):
        while True:                                 # el original espera (bloqueante) una línea
            with self._lock:
                if "\n" in self._datos:
                    linea, self._datos = self._datos.split("\n", 1)
                    return linea + "\n"
            _time.sleep(0.001)


class Salida(io.StringIO):
    """Lo que el firmware imprime."""

    def lineas(self):
        return self.getvalue().splitlines()


def machine_falso(registro):
    class Pin:
        def __init__(self, numero, *args, **kwargs):
            self.numero = numero

    class PWM:
        def __init__(self, pin, freq=50):
            self.pin = pin.numero

        def duty_ns(self, ns):
            registro.append(("pulso", self.pin, int(ns)))

    return types.SimpleNamespace(Pin=Pin, PWM=PWM)


def tiempo_falso(registro, escala=0.0, pausa_bucle=None):
    """time de MicroPython: sleep() se registra (y opcionalmente dura escala×segundos)."""
    def sleep(s):
        registro.append(("pausa", s))
        if escala:
            _time.sleep(s * escala)

    def sleep_ms(ms):
        if pausa_bucle:
            pausa_bucle()                            # para "colgar" la placa en las pruebas
        _time.sleep(ms / 1000)

    return types.SimpleNamespace(sleep=sleep, sleep_ms=sleep_ms,
                                 ticks_ms=lambda: int(_time.monotonic() * 1000),
                                 ticks_diff=lambda a, b: a - b)


def uselect_falso():
    class Poll:
        def __init__(self):
            self.objetos = []

        def register(self, obj, eventos=1):
            self.objetos.append(obj)

        def poll(self, timeout=0):
            return [(o, 1) for o in self.objetos if o.hay_datos()]

    return types.SimpleNamespace(poll=Poll, POLLIN=1)


# =============================================================================
#  Bluetooth falso
# =============================================================================
class UUIDFalso:
    def __init__(self, texto):
        self.texto = texto.upper()

    def __bytes__(self):                             # como en MicroPython: 16 bytes al revés
        return bytes.fromhex(self.texto.replace("-", ""))[::-1]


class RadioBLE:
    """El aire entre la placa (bluetooth.BLE de MicroPython) y un PC (central)."""
    H_TX, H_RX = 1, 2

    def __init__(self):
        self.irq = None
        self.nombre = None
        self.anunciando = False
        self.anuncio = None
        self.conexion = None                         # conn_handle de MicroPython
        self.al_notificar = None                     # callback del PC conectado
        self.al_desconectar = None
        self.rx = b""
        self.fuera_de_alcance = False
        self.conexiones = 0
        self._lock = threading.Lock()

    # --- lado de la placa (lo que llama el firmware)
    def active(self, valor=None):
        return True

    def config(self, *args, **kw):
        if "gap_name" in kw:
            self.nombre = kw["gap_name"]

    def irq_handler(self, handler):
        self.irq = handler

    def gatts_register_services(self, servicios):
        return ((self.H_TX, self.H_RX),)

    def gatts_set_buffer(self, handle, largo, agregar=False):
        pass

    def gatts_read(self, handle):
        with self._lock:
            datos, self.rx = self.rx, b""
        return datos

    def gatts_notify(self, conexion, handle, datos):
        if conexion == self.conexion and self.al_notificar:
            self.al_notificar(bytes(datos))

    def gap_advertise(self, intervalo, adv_data=None, resp_data=None):
        self.anunciando = intervalo is not None
        self.anuncio = adv_data

    def gap_disconnect(self, conexion):
        if conexion == self.conexion:
            self._cortar()

    # --- lado del PC (central)
    def visible(self, nombre):
        return self.anunciando and not self.fuera_de_alcance and self.nombre == nombre

    def conectar(self, al_notificar, al_desconectar):
        if not self.anunciando or self.fuera_de_alcance:
            raise OSError("la mano no está disponible")
        self.conexiones += 1
        self.conexion = 100 + self.conexiones
        self.anunciando = False                      # MicroPython deja de anunciarse al conectarse
        self.al_notificar, self.al_desconectar = al_notificar, al_desconectar
        self.irq(1, (self.conexion, 0, b""))

    def escribir(self, datos):
        if self.conexion is None or self.fuera_de_alcance:
            raise OSError("no hay conexión")
        with self._lock:
            self.rx += bytes(datos)
        self.irq(3, (self.conexion, self.H_RX))

    def desconectar_central(self):
        if self.conexion is not None:
            self._cortar()

    def _cortar(self):
        conexion, avisar = self.conexion, self.al_desconectar
        self.conexion, self.al_notificar, self.al_desconectar = None, None, None
        self.irq(2, (conexion, 0, b""))
        if avisar:
            avisar()

    def salir_de_alcance(self):
        """Como alejarse o apagar la placa: se corta la conexión y deja de verse."""
        self.fuera_de_alcance = True
        if self.conexion is not None:
            self._cortar()

    def volver(self):
        self.fuera_de_alcance = False


def bluetooth_falso(radio):
    ble = types.SimpleNamespace(active=radio.active, config=radio.config, irq=radio.irq_handler,
                                gatts_register_services=radio.gatts_register_services,
                                gatts_set_buffer=radio.gatts_set_buffer, gatts_read=radio.gatts_read,
                                gatts_notify=radio.gatts_notify, gap_advertise=radio.gap_advertise,
                                gap_disconnect=radio.gap_disconnect)
    return types.SimpleNamespace(BLE=lambda: ble, UUID=UUIDFalso)


class BleakFalso:
    """El mismo uso de bleak que hace pgc/adaptadores/mano_ble.py, contra la RadioBLE."""

    def __init__(self, radio):
        self.radio = radio
        radio_ = radio

        class Escaner:
            @staticmethod
            async def find_device_by_name(nombre, timeout=5.0):
                limite = _time.monotonic() + min(timeout, 1.0)
                while _time.monotonic() < limite:
                    if radio_.visible(nombre):
                        return types.SimpleNamespace(name=nombre, address="AA:BB:CC:DD:EE:FF")
                    await asyncio.sleep(0.02)
                return None

        class Cliente:
            def __init__(self, dispositivo, disconnected_callback=None):
                self.dispositivo = dispositivo
                self.al_desconectar = disconnected_callback
                self.al_notificar = None
                self.is_connected = False

            async def connect(self, timeout=10.0):
                radio_.conectar(self._notificar, self._desconectado)
                self.is_connected = True

            def _notificar(self, datos):
                if self.al_notificar:
                    self.al_notificar(None, bytearray(datos))

            def _desconectado(self):
                self.is_connected = False
                if self.al_desconectar:
                    self.al_desconectar(self)

            async def start_notify(self, caracteristica, callback):
                assert caracteristica.upper() == UART_TX
                self.al_notificar = callback

            async def write_gatt_char(self, caracteristica, datos, response=False):
                assert caracteristica.upper() == UART_RX
                assert len(datos) <= 20, "paquetes de más de 20 bytes"
                radio_.escribir(datos)

            async def disconnect(self):
                if self.is_connected:
                    radio_.desconectar_central()
                self.is_connected = False

        self.Escaner, self.Cliente = Escaner, Cliente


# =============================================================================
#  Ejecutar el firmware
# =============================================================================
@contextmanager
def modulos(**reemplazos):
    """Pone módulos falsos en sys.modules mientras corre el firmware (None = 'no existe')."""
    antes = {n: sys.modules.get(n, KeyError) for n in reemplazos}
    sys.modules.update(reemplazos)
    try:
        yield
    finally:
        for n, v in antes.items():
            if v is KeyError:
                sys.modules.pop(n, None)
            else:
                sys.modules[n] = v


def ejecutar(ruta, registro, stdin, salida, config_ble=None, radio=None, escala=0.0, pausa_bucle=None,
             espacio=None):
    """Ejecuta un main.py de MicroPython hasta que termine (con 'salir').

    espacio: diccionario de variables globales del programa (para mirarlo mientras corre).
    """
    fuente = ruta.read_text(encoding="utf-8")
    for linea in ("from machine import Pin, PWM\n", "import time\n", "import sys\n"):
        fuente = fuente.replace(linea, "", 1)
    m = machine_falso(registro)
    espacio = {} if espacio is None else espacio
    espacio.update({"__name__": "__main__", "Pin": m.Pin, "PWM": m.PWM,
                    "time": tiempo_falso(registro, escala, pausa_bucle),
                    "sys": types.SimpleNamespace(stdin=stdin)})
    original_print = print

    def imprimir(*args, **kw):                      # print() del firmware → Salida
        original_print(*args, file=salida, **{k: v for k, v in kw.items() if k != "file"})

    espacio["print"] = imprimir
    with modulos(uselect=uselect_falso(), micropython=types.SimpleNamespace(const=lambda x: x),
                 bluetooth=bluetooth_falso(radio or RadioBLE()), config_ble=config_ble):
        exec(compile(fuente, str(ruta), "exec"), espacio)
    return espacio


def correr(ruta, ordenes, **kw):
    """Corre el firmware con estas órdenes por USB (y 'salir'). Devuelve (registro, líneas impresas)."""
    registro, salida = Registro(), Salida()
    stdin = StdinFalso("".join(o + "\n" for o in ordenes) + "salir\n")
    ejecutar(ruta, registro, stdin, salida, **kw)
    return registro, salida.lineas()


def config_ble_falso(token, nombre="Mano-LSC"):
    return types.SimpleNamespace(NOMBRE=nombre, TOKEN=token)


class PlacaEnHilo:
    """El main.py REAL corriendo en un hilo, con Bluetooth (radio falsa)."""

    def __init__(self, token, nombre="Mano-LSC", escala=0.0):
        self.registro, self.salida = Registro(), Salida()
        self.stdin = StdinFalso()
        self.radio = RadioBLE()
        self.callada = threading.Event()             # set(): la placa se "cuelga"
        self.error = None
        self.espacio = {}                            # variables globales del main.py en marcha
        self.ordenes = []                            # órdenes que recibió (USB o Bluetooth)
        cfg = config_ble_falso(token, nombre)

        def bucle_colgado():
            while self.callada.is_set():
                _time.sleep(0.01)

        def correr_main():
            try:
                ejecutar(MAIN, self.registro, self.stdin, self.salida, config_ble=cfg, radio=self.radio,
                         escala=escala, pausa_bucle=bucle_colgado, espacio=self.espacio)
            except Exception as ex:                  # para verlo en la prueba
                self.error = ex

        self.hilo = threading.Thread(target=correr_main, daemon=True, name="placa")
        self.hilo.start()
        limite = _time.time() + 5
        while _time.time() < limite and "Listo. Esperando comandos..." not in self.salida.lineas():
            _time.sleep(0.01)
        # El bucle busca `atender_orden` en cada vuelta: se envuelve para anotar las órdenes
        atender = self.espacio.get("atender_orden")
        if atender:
            def anotar(cmd, responder):
                self.ordenes.append(cmd.strip())
                return atender(cmd, responder)
            self.espacio["atender_orden"] = anotar

    def detener(self):
        self.callada.clear()
        self.stdin.escribir("salir\n")
        self.hilo.join(5)


class CentralFalsa:
    """Un PC conectado por Bluetooth, escribiendo directo a la radio (para probar la placa)."""

    def __init__(self, placa):
        self.radio = placa.radio
        self.recibido = b""
        self.desconectado = threading.Event()
        self.radio.conectar(self._notificar, self.desconectado.set)

    def _notificar(self, datos):
        assert len(datos) <= 20
        self.recibido += datos

    def enviar(self, texto):
        datos = (texto + "\n").encode()
        for k in range(0, len(datos), 20):
            self.radio.escribir(datos[k:k + 20])

    def lineas(self, cuantas, timeout=5):
        limite = _time.time() + timeout
        while self.recibido.count(b"\n") < cuantas and _time.time() < limite:
            _time.sleep(0.005)
        partes = self.recibido.split(b"\n")
        listas, self.recibido = partes[:cuantas], b"\n".join(partes[cuantas:])
        return [p.decode() for p in listas]
```

## `tests/ble_falso_hijo.py`

```python
"""Para el proceso hijo del puente Bluetooth en las pruebas: la placa falsa (main.py real) y un bleak falso.

    python -m pgc.adaptadores.ble_puente --bleak ble_falso_hijo:crear
(con la carpeta tests en PYTHONPATH y el token en PGC_PRUEBA_TOKEN)
"""
import os

from arnes_firmware import BleakFalso, PlacaEnHilo


def crear():
    placa = PlacaEnHilo(os.environ["PGC_PRUEBA_TOKEN"])
    if placa.error:
        raise placa.error
    return BleakFalso(placa.radio)
```

## `tests/conftest.py`

```python
"""Red de seguridad: pruebas de caracterización del comportamiento actual.

ÚNICO punto de acoplamiento con la estructura del código: los imports y la
forma de armar el sistema con dobles están solo aquí. Cuando se reorganicen los
módulos, se cambia este archivo y las pruebas deben seguir pasando sin tocarlas.
"""
import os
import sys
import threading
import time
import types
from contextlib import contextmanager
from dataclasses import replace
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from pgc import arranque, config  # noqa: E402
from pgc.adaptadores import acceso, mano_respaldo, mano_simulada, mano_usb, whisper  # noqa: E402
from pgc.api.app import crear_app  # noqa: E402
from pgc.dominio import ordenes as modulo_ordenes  # noqa: E402,F401
from pgc.dominio import texto as modulo_texto      # noqa: E402

from fastapi.testclient import TestClient  # noqa: E402

def pytest_addoption(parser):
    parser.addoption("--reconocedor", default="pgc.adaptadores.reconocedor_simulado:ReconocedorSimulado",
                     help="clase a revisar con tests/contratos (paquete.modulo:Clase)")


# Valores que tenía servidor.py antes de la migración (los compara test_config)
servidor = types.SimpleNamespace(PAUSA_ENTRE_LETRAS=0.5, PAUSA_NO_DISPONIBLE=0.9, MAX_PENDIENTES_CLIENTE=2,
                                 MAX_COLA=30, MAX_AUDIO_BYTES=10 * 1024 * 1024)


# =============================================================================
#  Dobles de prueba
# =============================================================================
class ManoFalsa:
    """Misma interfaz que mano_serial.Mano; registra cada orden que recibiría el ESP32."""

    def __init__(self, puerto=None, baudios=115200, simular=False, log=print):
        self.ordenes = []
        self.letras = None             # None = la mano no reportó letras (usa las por defecto)
        self.conectada = False
        self.puerto = None
        self.conexiones = 0
        self.fallar = set()            # órdenes a las que la mano "no confirma" (devuelve False)
        self.bloquear_en = None        # la primera vez que llegue esta orden, espera a `soltar`
        self.llego = threading.Event()
        self.soltar = threading.Event()

    @property
    def modo(self):
        return "real" if self.conectada else "simulada"

    @property
    def medio(self):
        return "usb" if self.conectada else None

    def conectar(self):
        self.conexiones += 1
        return self.conectada

    def revisar(self):
        self.revisiones = getattr(self, "revisiones", 0) + 1
        return False

    def latido(self):
        return self.conectada

    def cerrar(self):
        self.conectada = False

    _cerrar = cerrar

    def hacer(self, orden):
        self.ordenes.append(orden)
        if orden == self.bloquear_en and not self.llego.is_set():
            self.llego.set()
            self.soltar.wait(5)
        return orden not in self.fallar

    def reset(self):
        return self.hacer("reset")


class TranscriptorFalso:
    """Misma interfaz que voz_entrada.Transcriptor, sin cargar Whisper."""

    def __init__(self, log=print, al_cambiar=None):
        self.estado = "listo"
        self.dispositivo = "cuda float16"
        self.texto = "hola jurado"
        self.segundos = 3.0            # lo que respondería PyAV
        self.error = None
        self.cargado = False
        self.recibidos = []            # (ruta, existía durante la transcripción, bytes)

    @property
    def listo(self):
        return self.estado == "listo"

    def cargar_en_segundo_plano(self):
        self.cargado = True

    def transcribir(self, ruta):
        with open(ruta, "rb") as f:
            self.recibidos.append((ruta, os.path.exists(ruta), f.read()))
        if self.error:
            raise self.error
        return self.texto

    def duracion(self, ruta):
        return self.segundos


class TunelFalso:
    """Misma interfaz que tunel.Tunel, sin lanzar cloudflared."""
    URL = "https://prueba-pgc.trycloudflare.com"

    def __init__(self, puerto, log=print, al_cambiar=None):
        self.url = None
        self.estado = "apagado"
        self.iniciado = False
        self.detenido = False

    def iniciar(self):
        self.iniciado = True
        self.estado = "activo"
        self.url = self.URL

    def detener(self):
        self.detenido = True


class FabricaMano:
    """Arma la mano de verdad (USB + simulada) con la forma del antiguo módulo mano_serial.

    Las pruebas del protocolo reemplazan `serial`, `time` y `TIMEOUT_LETRA` con
    monkeypatch sobre este objeto; aquí se inyectan en el constructor.
    """
    VIDS_ESP32 = mano_usb.VIDS_ESP32
    TIEMPO_SIMULADO = mano_simulada.TIEMPO_SIMULADO

    def __init__(self):
        self.serial = mano_usb.serial
        self.time = time
        self.TIMEOUT_LETRA = mano_usb.TIMEOUT_LETRA

    def Mano(self, puerto=None, simular=False, log=print):
        return mano_respaldo.Mano(puerto=puerto, simular=simular, log=log, timeout_letra=self.TIMEOUT_LETRA,
                                  modulo_serial=self.serial, dormir=self.time.sleep, reloj=self.time.time)

    def buscar_puerto(self):
        return mano_usb.buscar_puerto(modulo_serial=self.serial)


mano_serial = FabricaMano()     # constantes del adaptador (las usa test_config)

IP_LOCAL = "192.168.0.10"


# =============================================================================
#  Utilidades
# =============================================================================
def esperar(condicion, timeout=5.0, paso=0.01):
    limite = time.time() + timeout
    while time.time() < limite:
        if condicion():
            return True
        time.sleep(paso)
    raise AssertionError("La condición no se cumplió a tiempo")


def tipos(pasos):
    """[('S','nd'), ('E','ok'), ...] para comparar secuencias de forma legible."""
    return [(p["c"], p["tipo"]) for p in pasos]


# =============================================================================
#  Fixtures
# =============================================================================
@pytest.fixture
def texto():
    """Módulo de texto → secuencia (limpiar, a_secuencia, constantes)."""
    return modulo_texto


@pytest.fixture
def modulo_mano():
    return FabricaMano()


@pytest.fixture
def modulo_tunel():
    return acceso


@pytest.fixture
def modulo_voz():
    return whisper


@pytest.fixture
def registro():
    """Líneas que el servidor escribe en el log."""
    return []


def configuracion(simular=True, puerto=None, puerto_web=8000, sin_tunel=False, sin_voz=False, no_abrir=True,
                  dev=False, **ajustes):
    """Config como la daría la línea de comandos de siempre, sin pausas (las pruebas corren en ms).

    ajustes: otros campos de Config (p. ej. lim_mensaje_ip=2) para una prueba concreta.
    """
    argv = ["--puerto-web", str(puerto_web)]
    argv += ["--simular"] * simular + ["--sin-tunel"] * sin_tunel + ["--sin-voz"] * sin_voz + ["--no-abrir"] * no_abrir
    argv += ["--dev"] * dev
    if puerto:
        argv += ["--puerto", puerto]
    cfg = config.cargar(argv, entorno={}, archivo_env=RAIZ / "tests" / "no-existe.env")
    # Sin Kinect real ni voz de salida salvo que la prueba los pida (con un detector falso o un sintetizador falso).
    # El turno del Kinect sin código del proyector, salvo que se pida: test_kinect_codigo.py lo prueba con él.
    ajustes = {"reconocedor": "simulado", "voz_salida": False, "kinect_lanzar": False, "kinect_codigo": False,
               **ajustes}
    return replace(cfg, pausa_letra=0, pausa_no_disponible=0, **ajustes)


@pytest.fixture
def crear_sistema(registro):
    """Arma el sistema con dobles de mano, Whisper, túnel y red; por defecto sin hilo de la mano."""
    def crear(**opciones):
        return arranque.construir_sistema(
            configuracion(**opciones), log=registro.append,
            crear_mano=lambda cfg, log: ManoFalsa(),
            crear_transcriptor=lambda cfg, log, al_cambiar: TranscriptorFalso(log, al_cambiar),
            crear_tunel=lambda cfg, log, al_cambiar: TunelFalso(cfg.puerto_web, log, al_cambiar),
            ip_local=lambda: IP_LOCAL)
    return crear


@pytest.fixture
def sistema_con_mano(crear_sistema):
    """Sistema con el hilo de la mano corriendo (deletrea de verdad contra la ManoFalsa)."""
    s = crear_sistema()
    s.iniciar_trabajador()
    esperar(lambda: s.mano.conexiones >= 1)
    yield s
    s.mano.soltar.set()


@pytest.fixture
def abrir_api(crear_sistema):
    """Abre la app con TestClient (ejecuta el ciclo de vida: hilo de la mano, voz, túnel).

    desde: IP de origen ("testclient" = un celular cualquiera; "127.0.0.1" o "::1" = el PC).
    Desde el PC se usa Host: 127.0.0.1:8000, como el navegador del proyector.
    """
    pendientes = []

    @contextmanager
    def abrir(desde="testclient", **opciones):
        sistema = crear_sistema(**opciones)
        app = crear_app(sistema, abrir_navegador=lambda url: None)
        base = "http://127.0.0.1:8000" if desde in ("127.0.0.1", "::1") else "http://testserver"
        with TestClient(app, client=(desde, 50000), base_url=base) as cliente:
            pendientes.append(sistema)
            yield cliente, sistema
    yield abrir
    for s in pendientes:
        s.mano.soltar.set()


def token_de_pantalla(cliente):
    """El token como lo obtiene el navegador: del <meta> de /pantalla ('' si no lo hay)."""
    import re
    m = re.search(r'<meta name="pgc-admin" content="([^"]*)">', cliente.get("/pantalla").text)
    return m.group(1) if m else ""


def admin(cliente):
    """Encabezados del presentador para las rutas /api/mano/*."""
    return {"X-PGC-Admin": token_de_pantalla(cliente)}


# Comienzo de un archivo webm (firma EBML): pasa la revisión de "parece audio"
AUDIO_WEBM = b"\x1a\x45\xdf\xa3" + b"\x00" * 12


@pytest.fixture
def carpeta_web():
    return RAIZ / "web"
```

## `tests/contratos/test_reconocedor.py`

```python
"""Pruebas de contrato del puerto ReconocedorSenas (docs/CONTRATO_KINECT.md).

Para revisar la implementación del Kinect antes de entregarla:
    py -3.11 -m pytest tests/contratos --reconocedor=pgc.adaptadores.kinect.reconocedor:ReconocedorKinect
Sin la opción se revisa el ReconocedorSimulado.
"""
import importlib
import threading
import time

import pytest

from pgc.puertos.reconocedor import ESTADOS, EventoSena, problemas_del_evento


@pytest.fixture
def reconocedor(request):
    ruta = request.config.getoption("--reconocedor")
    modulo, clase = ruta.split(":")
    r = getattr(importlib.import_module(modulo), clase)()      # regla 6: sin argumentos
    yield r
    r.detener()


def test_tiene_estado_y_detalle(reconocedor):
    assert reconocedor.estado in ESTADOS
    assert isinstance(reconocedor.detalle, str)


def test_iniciar_no_bloquea(reconocedor):
    t0 = time.monotonic()
    reconocedor.iniciar(lambda e: None, lambda: None)
    assert time.monotonic() - t0 < 1.0, "iniciar() debe cargar en segundo plano y retornar enseguida"
    assert reconocedor.estado in ESTADOS


def test_detener_se_puede_llamar_dos_veces(reconocedor):
    reconocedor.iniciar(lambda e: None, lambda: None)
    reconocedor.detener()
    reconocedor.detener()
    assert reconocedor.estado in ESTADOS


def test_detener_sin_iniciar(reconocedor):
    reconocedor.detener()


def test_eventos_cumplen_el_formato(reconocedor):
    """Revisa todos los eventos que emita en 3 s (con el simulado, se le pide un texto)."""
    eventos, cambios = [], []
    reconocedor.iniciar(eventos.append, lambda: cambios.append(reconocedor.estado))
    if hasattr(reconocedor, "simular"):
        reconocedor.simular("hola mundo")
    time.sleep(3)
    for e in eventos:
        assert not problemas_del_evento(e), problemas_del_evento(e)
    assert all(estado in ESTADOS for estado in cambios)


def test_problemas_del_evento_detecta_errores():
    assert problemas_del_evento(EventoSena("letra", letra="a", confianza=0.9)) == []
    assert problemas_del_evento(EventoSena("letra", letra="A"))
    assert problemas_del_evento(EventoSena("letra", letra="ab"))
    assert problemas_del_evento(EventoSena("fin", letra="a"))
    assert problemas_del_evento(EventoSena("letra", letra="a", confianza=1.5))
    assert problemas_del_evento(EventoSena("saludo"))
    assert problemas_del_evento("a")


def test_callbacks_desde_otro_hilo(reconocedor):
    hilos = set()
    reconocedor.iniciar(lambda e: hilos.add(threading.get_ident()), lambda: None)
    if hasattr(reconocedor, "simular"):
        reconocedor.simular("ab", esperar=True)
        assert hilos and threading.get_ident() not in hilos
```

## `tests/detector_falso.py`

```python
"""Detector falso: habla igual que integracion_kinect/detector/server_web_svm.py, sin MediaPipe ni Kinect.

Reproduce su protocolo (server_deletreo_svm.py + server_web_svm.py):
    GET  /spell/status  "Texto: <texto o —>\\nEstado: <mensaje>"   (texto plano, como el original)
    POST /spell/start | stop | space | backspace | clear            ("OK"; 400 con el motivo si falla)
    GET  /preview.jpg   la última imagen recibida, o 503 si no llega ninguna hace más de 3 s
    POST /detect        recibe un JPEG (lo que manda la app C# o camara_pc.py)
La prueba "hace" las señas con reconocer("h"), como si el SVM hubiera confirmado la letra.
"""
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

JPEG = b"\xff\xd8\xff\xe0" + b"\x00" * 60 + b"\xff\xd9"       # basta con que parezca un JPEG


class DetectorFalso:
    def __init__(self, con_modelo=True):
        self.con_modelo = con_modelo
        self.texto = ""
        self.activo = False
        self.estado = "Deletreo detenido."
        self.imagen = None
        self.t_imagen = 0.0
        self.ordenes = []
        self.consultas = 0
        self._lock = threading.Lock()
        self._servidor = ThreadingHTTPServer(("127.0.0.1", 0), self._manejador())
        self._servidor.daemon_threads = True
        self.url = f"http://127.0.0.1:{self._servidor.server_address[1]}"
        threading.Thread(target=self._servidor.serve_forever, daemon=True).start()

    # ---------------------------------------------------------- lo que hace la prueba
    def reconocer(self, letra):
        """Como si el SVM hubiera confirmado una letra (el original la agrega en mayúscula)."""
        with self._lock:
            if self.activo:
                self.texto += letra.upper()
                self.armado = False
                self.t_cuadro = time.monotonic()
                self.estado = "Letra añadida. Retira la mano medio segundo para continuar."

    def camara(self, encendida=True):
        """Simula que llegan (o dejan de llegar) imágenes del Kinect."""
        self.imagen, self.t_imagen = (JPEG, time.monotonic()) if encendida else (None, 0.0)

    def mantener_camara(self, por_segundo=10):
        """Llegan cuadros nuevos sin parar, como de una cámara real: cada uno distinto del anterior.

        Se agrega un contador después del final del JPEG (los navegadores lo ignoran). La base es la
        imagen que haya puesto la prueba (detector.imagen = ...) o JPEG.
        """
        self.camara(True)
        self.cuadros = 0

        def bucle():
            base = None
            while self.imagen is not None:
                if base is None or not self.imagen.startswith(base):
                    base = self.imagen
                self.cuadros += 1
                self.imagen = base + self.cuadros.to_bytes(4, "big")
                self.t_imagen = time.monotonic()
                time.sleep(1 / por_segundo)
        threading.Thread(target=bucle, daemon=True).start()

    def congelar(self):
        """La app deja de mandar cuadros: el detector repite la última imagen (hasta 3 s)."""
        imagen = self.imagen
        self.imagen = None                     # detiene el bucle de mantener_camara
        time.sleep(0.2)
        self.imagen, self.t_imagen = imagen, time.monotonic()

    # ---------------------------------------------------------- diagnóstico (lo agrega detector_paralelo.py)
    con_diagnostico = True
    manos = 0
    prediccion = None
    armado = True
    t_cuadro = 0.0

    def mostrar(self, letra):
        """La persona muestra una mano y el SVM predice `letra` (o "sin_letra")."""
        self.manos, self.prediccion, self.t_cuadro = 1, letra, time.monotonic()

    def retirar(self):
        self.manos, self.prediccion, self.armado, self.t_cuadro = 0, None, True, time.monotonic()

    def _diagnostico(self):
        return {"t": self.t_cuadro, "activo": self.activo, "manos": self.manos, "prediccion": self.prediccion,
                "segunda": "sin_letra" if self.prediccion else None, "margen": 0.8 if self.prediccion else None,
                "estable_s": 0.0, "confirmaciones": 0, "armado": self.armado, "texto": self.texto,
                "estado": self.estado, "motivo": "Mano no detectada" if not self.manos else "Confirmando…",
                "tiempo_confirmacion": 0.7, "tiempo_liberacion": 0.5, "confirmaciones_necesarias": 4,
                "categorias": list("abcdefghijklmnopqrs") + ["sin_letra"] + list("tuvwxyz")}

    def cerrar(self):
        self.imagen = None
        self._servidor.shutdown()
        self._servidor.server_close()

    # ---------------------------------------------------------- protocolo (igual que DeletreadorSVM)
    def _comando(self, accion):
        if accion == "start":
            if not self.con_modelo:
                raise ValueError("No existe modelo_estaticas.joblib.")
            self.activo, self.estado = True, "Mantén una letra estática visible."
        elif accion == "stop":
            self.activo, self.estado = False, "Deletreo detenido."
        elif accion == "space":
            if self.texto and not self.texto.endswith(" "):
                self.texto += " "
        elif accion == "backspace":
            self.texto = self.texto[:-1]
        elif accion == "clear":
            self.texto = ""

    def _estado(self):
        return "Texto: " + (self.texto or "—") + "\nEstado: " + self.estado

    def _manejador(self):
        detector = self

        class Manejador(BaseHTTPRequestHandler):
            def responder(self, codigo, cuerpo, tipo="text/plain; charset=utf-8"):
                self.send_response(codigo)
                self.send_header("Content-Type", tipo)
                self.send_header("Content-Length", str(len(cuerpo)))
                self.end_headers()
                self.wfile.write(cuerpo)

            def do_GET(self):
                if self.path == "/spell/status":
                    detector.consultas += 1
                    with detector._lock:
                        return self.responder(200, detector._estado().encode("utf-8"))
                if self.path == "/diagnostico" and detector.con_diagnostico:
                    import json
                    return self.responder(200, json.dumps(detector._diagnostico()).encode(), "application/json")
                if self.path == "/preview.jpg":
                    if detector.imagen is None or time.monotonic() - detector.t_imagen > 3:
                        return self.responder(503, b"Esperando imagen del Kinect")
                    return self.responder(200, detector.imagen, "image/jpeg")
                self.send_error(404)

            def do_POST(self):
                largo = int(self.headers.get("Content-Length", "0"))
                datos = self.rfile.read(largo)
                if self.path == "/detect":
                    detector.camara(True)
                    detector.imagen = datos
                    return self.responder(200, datos, "image/jpeg")
                accion = self.path.removeprefix("/spell/")
                if accion not in {"start", "stop", "space", "backspace", "clear"}:
                    return self.send_error(404)
                detector.ordenes.append(accion)
                try:
                    with detector._lock:
                        detector._comando(accion)
                except ValueError as ex:
                    return self.responder(400, str(ex).encode("utf-8"))
                self.responder(200, b"OK")

            def log_message(self, *args):
                pass

        return Manejador
```

## `tests/esp32_falso.py`

```python
"""ESP32 falso por Bluetooth: el main.py REAL de la placa corriendo en un hilo (servos y radio falsos).

Se usa en las pruebas y en scripts/prueba_e2e.py --ble. `bleak` es un bleak falso que
habla con esta placa: se le pasa a ManoBLE(bleak=esp.bleak).
"""
import time

from arnes_firmware import BleakFalso, PlacaEnHilo

TOKEN = "token-de-prueba-0123456789"


class Esp32Falso:
    """Interfaz cómoda sobre PlacaEnHilo: órdenes recibidas, colgarse, salir y volver al alcance."""

    def __init__(self, token=TOKEN, nombre="Mano-LSC", pausa_letra=0.0):
        self.placa = PlacaEnHilo(token, nombre, escala=pausa_letra)
        if self.placa.error:
            raise self.placa.error
        self.nombre = nombre
        self.bleak = BleakFalso(self.placa.radio)

    @property
    def ordenes(self):
        return self.placa.ordenes

    @property
    def registro(self):
        return self.placa.registro

    @property
    def log(self):
        return self.placa.salida.lineas()

    @property
    def callada(self):
        return self.placa.callada.is_set()

    @callada.setter
    def callada(self, valor):
        (self.placa.callada.set if valor else self.placa.callada.clear)()
        if valor:
            time.sleep(0.1)            # que el bucle llegue a su pausa y quede detenido ahí

    def apagar(self):
        """Como alejarse o quitar los 12 V: se corta la conexión y la placa deja de verse."""
        self.placa.radio.salir_de_alcance()
        time.sleep(0.05)

    def encender(self):
        self.placa.radio.volver()
        time.sleep(0.05)

    def detener(self):
        self.placa.detener()
```

## `tests/test_acceso_huerfanos.py`

```python
"""cloudflared no queda huérfano si Python se cierra a la fuerza (Job Object de Windows)."""
import os
import subprocess
import sys
import time

import pytest

from conftest import RAIZ

PADRE = (
    "import subprocess, sys, time;"
    f"sys.path.insert(0, {str(RAIZ)!r});"
    "from pgc.adaptadores.acceso import atar_al_proceso_actual;"
    "h = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']);"
    "print(h.pid, atar_al_proceso_actual(h) is not None, flush=True);"
    "time.sleep(60)"
)


def vivo(pid):
    salida = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
    return str(pid) in salida


@pytest.mark.skipif(os.name != "nt", reason="solo aplica en Windows")
def test_el_hijo_muere_con_el_padre():
    padre = subprocess.Popen([sys.executable, "-c", PADRE], stdout=subprocess.PIPE, text=True)
    try:
        pid_hijo, atado = padre.stdout.readline().split()
        assert atado == "True"
        assert vivo(pid_hijo)
        padre.kill()                                   # como cerrar la ventana o taskkill /F
        padre.wait(5)
        limite = time.time() + 5
        while vivo(pid_hijo) and time.time() < limite:
            time.sleep(0.2)
        assert not vivo(pid_hijo), "el proceso hijo quedó huérfano"
    finally:
        if padre.poll() is None:
            padre.kill()
```

## `tests/test_api.py`

```python
"""API HTTP y WebSocket (caracterización de servidor.crear_app con TestClient)."""
import io
import os
from unittest.mock import ANY

import pytest

from conftest import AUDIO_WEBM, IP_LOCAL, TunelFalso, admin, esperar

PC = "127.0.0.1"


# =============================================================================
#  Páginas y recursos
# =============================================================================
@pytest.mark.parametrize("ruta, texto", [("/", "Mano bidireccional LSC"), ("/pantalla", "Mano bidireccional LSC")])
def test_paginas(abrir_api, ruta, texto):
    with abrir_api() as (c, _):
        r = c.get(ruta)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert r.headers["cache-control"] == "no-store"
    assert texto in r.text


def test_logo(abrir_api):
    with abrir_api() as (c, _):
        r = c.get("/logo-udec.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.content[:8] == b"\x89PNG\r\n\x1a\n"


def test_qr_apunta_a_la_url_publica(abrir_api):
    cv2 = pytest.importorskip("cv2")
    np = pytest.importorskip("numpy")
    with abrir_api() as (c, _):
        r = c.get("/qr.png")
    assert r.status_code == 200
    assert r.headers["content-type"] == "image/png"
    assert r.headers["cache-control"] == "no-store"
    img = cv2.imdecode(np.frombuffer(r.content, np.uint8), cv2.IMREAD_COLOR)
    texto, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    assert texto == TunelFalso.URL


def test_documentacion_automatica(abrir_api):
    with abrir_api() as (c, _):
        assert c.get("/docs").status_code == 404
        assert c.get("/redoc").status_code == 404
        assert c.get("/openapi.json").status_code == 404        # E7: solo con --dev o con el token


def test_sin_cors(abrir_api):
    with abrir_api() as (c, _):
        r = c.get("/api/estado", headers={"Origin": "https://otro-sitio.example"})
    assert "access-control-allow-origin" not in r.headers


# =============================================================================
#  Estado y ciclo de vida
# =============================================================================
def test_estado_con_tunel(abrir_api):
    with abrir_api() as (c, s):
        d = c.get("/api/estado").json()
        assert s.voz.cargado and s.tunel.iniciado
    assert s.tunel.detenido                                       # al cerrar se detiene el túnel
    assert d["tunel"] == {"estado": "activo", "url": TunelFalso.URL}
    assert d["url_publica"] == TunelFalso.URL
    assert d["url_local"] == f"http://{IP_LOCAL}:8000"
    assert d["sesion"] == s.sesion


def test_estado_sin_tunel_y_sin_voz(abrir_api):
    with abrir_api(sin_tunel=True, sin_voz=True) as (c, s):
        d = c.get("/api/estado").json()
        assert not s.tunel.iniciado and not s.voz.cargado
    assert d["url_publica"] == f"http://{IP_LOCAL}:8000"
    assert d["voz"]["estado"] == "desactivado"


def test_previa(abrir_api):
    with abrir_api() as (c, _):
        r = c.post("/api/previa", json={"texto": "Señor"})
    assert r.status_code == 200
    assert r.json() == {"pasos": [{"c": "S", "tipo": "nd"}, {"c": "E", "tipo": "ok"}, {"c": "Ñ", "tipo": "aprox"},
                                  {"c": "O", "tipo": "ok"}, {"c": "R", "tipo": "ok"}]}


# =============================================================================
#  Mensajes
# =============================================================================
def test_enviar_mensaje_y_deletrearlo(abrir_api):
    with abrir_api() as (c, s):
        r = c.post("/api/mensaje", json={"texto": "Hola", "cliente": "A"})
        assert r.status_code == 200
        assert r.json() == {"id": 1, "texto": "hola", "nombre": "Anónimo", "sesion": s.sesion}
        esperar(lambda: len(s.historial) == 1)
        assert s.mano.ordenes == ["o", "l", "a", "reset"]


@pytest.mark.parametrize("cuerpo, codigo, detalle", [
    ({"texto": "a" * 61, "cliente": "A"}, 400, "Máximo 60 caracteres."),
    ({"texto": "  " + "a" * 60 + "  ", "cliente": "A"}, 200, None),       # se cuenta sin espacios de los bordes
    ({"texto": "gh", "cliente": "A"}, 400, "La mano todavía no puede hacer esas letras"),
    ({"texto": "¡¿?!", "cliente": "A"}, 400, "Escribe al menos una letra."),
])
def test_validaciones_de_mensaje(abrir_api, cuerpo, codigo, detalle):
    with abrir_api() as (c, _):
        r = c.post("/api/mensaje", json=cuerpo)
    assert r.status_code == codigo
    if detalle:
        assert r.json() == {"detail": detalle}


@pytest.mark.parametrize("cuerpo", [{}, {"texto": 5}, {"cliente": "A"}])
def test_cuerpo_invalido(abrir_api, cuerpo):
    with abrir_api() as (c, _):
        assert c.post("/api/mensaje", json=cuerpo).status_code == 422


def test_cliente_por_defecto_y_recortado(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "a"
        c.post("/api/mensaje", json={"texto": "a"})
        s.mano.llego.wait(5)
        r = c.post("/api/mensaje", json={"texto": "b", "cliente": "x" * 100})
        assert s.actual["cliente"] == "anonimo"
        assert r.status_code == 422 and s.cola == []                   # E7: ya no se recorta, se rechaza


def test_limite_por_cliente_y_cancelar(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "a"
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "A"}).status_code == 200
        s.mano.llego.wait(5)
        assert c.post("/api/mensaje", json={"texto": "b", "cliente": "A"}).status_code == 200
        r = c.post("/api/mensaje", json={"texto": "c", "cliente": "A"})
        assert r.status_code == 400
        assert r.json() == {"detail": "Ya tienes 2 mensajes en espera. Espera a que la mano los haga."}
        assert c.post("/api/mensaje", json={"texto": "d", "cliente": "B"}).status_code == 200

        r = c.delete("/api/mensaje/2", params={"cliente": "B"})          # no es suyo
        assert r.status_code == 404 and r.json() == {"detail": "Ese mensaje ya no se puede cancelar."}
        assert c.delete("/api/mensaje/1", params={"cliente": "A"}).status_code == 404   # en curso
        r = c.delete("/api/mensaje/2", params={"cliente": "A"})
        assert r.status_code == 200 and r.json() == {"ok": True}
        assert c.delete("/api/mensaje/2").status_code == 422                 # falta ?cliente=
        assert [m["id"] for m in s.cola] == [3]


# =============================================================================
#  Voz
# =============================================================================
def subir(c, datos=AUDIO_WEBM, nombre="voz.m4a"):
    return c.post("/api/transcribir", files={"audio": (nombre, io.BytesIO(datos), "audio/mp4")})


def test_transcribir(abrir_api):
    with abrir_api() as (c, s):
        r = subir(c)
        assert r.status_code == 200 and r.json() == {"texto": "hola jurado"}
        ruta, existia, datos = s.voz.recibidos[0]
    assert existia and datos == AUDIO_WEBM
    assert ruta.endswith(".m4a") and os.path.basename(ruta).startswith("voz_")
    assert not os.path.exists(ruta)                                   # el archivo temporal se borra


def test_transcribir_sufijo_por_defecto(abrir_api):
    with abrir_api() as (c, s):
        subir(c, nombre="grabacion")
        assert s.voz.recibidos[0][0].endswith(".webm")


def test_transcripcion_se_recorta_a_60(abrir_api):
    with abrir_api() as (c, s):
        s.voz.texto = "x" * 80
        assert subir(c).json() == {"texto": "x" * 60}


def test_transcribir_errores(abrir_api):
    with abrir_api() as (c, s):
        r = subir(c, datos=b"")
        assert r.status_code == 400 and r.json() == {"detail": "No llegó audio."}
        relleno = 10 * 1024 * 1024 - len(AUDIO_WEBM)
        r = subir(c, datos=AUDIO_WEBM + b"0" * (relleno + 1))
        assert r.status_code == 413 and r.json() == {"detail": "El audio es muy largo. Graba máximo 10 segundos."}
        assert subir(c, datos=AUDIO_WEBM + b"0" * relleno).status_code == 200

        s.voz.error = RuntimeError("audio dañado")
        r = subir(c)
        assert r.status_code == 500
        assert r.json() == {"detail": "No se pudo entender el audio. Intenta de nuevo o escríbelo."}
        assert not os.path.exists(s.voz.recibidos[-1][0])             # también se borra si falla

        s.voz.estado = "cargando"
        r = subir(c)
        assert r.status_code == 503
        assert r.json() == {"detail": "El reconocimiento de voz se está cargando, intenta en unos segundos."}


# =============================================================================
#  Rutas solo desde el PC
# =============================================================================
@pytest.mark.parametrize("ruta", ["/api/mano/reconectar", "/api/mano/saltar"])
def test_admin_rechaza_celulares_y_tunel(abrir_api, ruta):
    with abrir_api() as (c, _):                                       # IP de un celular
        r = c.post(ruta)
        assert r.status_code == 403 and r.json() == {"detail": "Solo desde el PC del proyector."}
    with abrir_api(desde=PC) as (c, _):                               # por el túnel: llega de 127.0.0.1
        r = c.post(ruta, headers={"cf-connecting-ip": "203.0.113.7"})
        assert r.status_code == 403


def test_reconectar_desde_el_pc(abrir_api):
    with abrir_api(desde=PC) as (c, s):
        esperar(lambda: s.mano.conexiones >= 1)
        n = s.mano.conexiones
        r = c.post("/api/mano/reconectar", headers=admin(c))           # E7: con el token de /pantalla
        assert r.status_code == 200 and r.json() == {"ok": True}
        esperar(lambda: s.mano.conexiones == n + 1)


def test_saltar_desde_el_pc(abrir_api):
    with abrir_api(desde="::1") as (c, s):
        encabezados = admin(c)                                          # E7: con el token de /pantalla
        r = c.post("/api/mano/saltar", headers=encabezados)
        assert r.status_code == 404 and r.json() == {"detail": "No hay ningún mensaje en curso."}
        s.mano.bloquear_en = "b"
        c.post("/api/mensaje", json={"texto": "abcd", "cliente": "A"})
        s.mano.llego.wait(5)
        assert c.post("/api/mano/saltar", headers=encabezados).json() == {"ok": True}
        s.mano.soltar.set()
        esperar(lambda: len(s.historial) == 1)
        assert s.mano.ordenes == ["a", "b", "reset"]
        assert c.get("/api/estado").json()["historial"][0]["saltado"] is True


# =============================================================================
#  WebSocket
# =============================================================================
def recibir_hasta(ws, condicion, maximo=50):
    for _ in range(maximo):
        d = ws.receive_json()
        if d.get("tipo") == "estado" and condicion(d):
            return d
    raise AssertionError("no llegó el estado esperado")


def test_websocket_estado_inicial(abrir_api):
    with abrir_api() as (c, s):
        with c.websocket_connect("/ws") as ws:
            d = ws.receive_json()
    assert d["tipo"] == "estado"
    assert d["sesion"] == s.sesion
    assert d["actual"] is None and d["cola"] == []


def test_websocket_sigue_un_mensaje(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "b"
        with c.websocket_connect("/ws") as ws:
            ws.receive_json()
            c.post("/api/mensaje", json={"texto": "ab", "cliente": "A"})
            d = recibir_hasta(ws, lambda d: d["actual"] and d["actual"]["i"] == 1)
            assert d["actual"]["texto"] == "ab"
            assert [p["r"] for p in d["actual"]["pasos"]] == ["ok", None]
            c.post("/api/mensaje", json={"texto": "c", "cliente": "B"})
            d = recibir_hasta(ws, lambda d: d["cola"])
            assert d["cola"] == [{"id": 2, "texto": "c", "pid": ANY, "nombre": "Anónimo"}]    # E8: autor (sin nombre)
            s.mano.soltar.set()
            d = recibir_hasta(ws, lambda d: len(d["historial"]) == 2 and d["actual"] is None)
    assert [m["texto"] for m in d["historial"]] == ["c", "ab"]


def test_varios_websockets_reciben_lo_mismo(abrir_api):
    with abrir_api() as (c, _):
        with c.websocket_connect("/ws") as w1, c.websocket_connect("/ws") as w2:
            w1.receive_json(); w2.receive_json()
            c.post("/api/mensaje", json={"texto": "a", "cliente": "A"})
            for ws in (w1, w2):
                recibir_hasta(ws, lambda d: d["historial"])
```

## `tests/test_atajos.py`

```python
"""servidor.py se conserva como forma corta de arrancar (py -3.11 servidor.py ...)."""
import importlib

from conftest import RAIZ


def test_servidor_es_un_atajo():
    assert importlib.import_module("servidor").main is importlib.import_module("pgc.arranque").main


def test_ya_no_quedan_los_atajos_de_la_migracion():
    for nombre in ("texto_util.py", "mano_serial.py", "voz_entrada.py", "tunel.py"):
        assert not (RAIZ / nombre).exists(), nombre


def test_iniciar_bat_usa_el_paquete():
    texto = (RAIZ / "iniciar.bat").read_text(encoding="utf-8")
    assert "py -3.11 -m pgc %*" in texto
```

## `tests/test_ble_puente.py`

```python
"""Puente Bluetooth: bleak en un proceso aparte (WinRT y Whisper no conviven en el mismo proceso).

El hijo es un proceso de verdad que corre el main.py real de la placa con una radio falsa.
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

from pgc.adaptadores.ble_puente import BleakRemoto
from pgc.adaptadores.mano_ble import ManoBLE

TESTS = Path(__file__).resolve().parent
TOKEN = "token-de-prueba-0123456789"


def remoto():
    entorno = {**os.environ, "PYTHONPATH": str(TESTS), "PGC_PRUEBA_TOKEN": TOKEN}
    return BleakRemoto([sys.executable, "-m", "pgc.adaptadores.ble_puente", "--bleak", "ble_falso_hijo:crear"],
                       entorno=entorno)


@pytest.fixture
def puente():
    r = remoto()
    yield r
    r.cerrar()


def mano(puente, log, token=TOKEN):
    return ManoBLE("Mano-LSC", token, log=log.append, bleak=puente, timeout_letra=3.0, tiempo_busqueda=1.0)


def test_mano_por_el_puente(puente):
    log = []
    m = mano(puente, log)
    assert m.conectar() is True, log
    assert m.hacer("a") is True and m.hacer("g") is False and m.hacer("reset") is True
    assert m.latido() is True
    assert log[-1] == "[mano] Conectada por Bluetooth a Mano-LSC"
    m.cerrar()
    assert m.conectar() is True                                 # reconexión por el mismo hijo
    m.cerrar()


def test_token_incorrecto_por_el_puente(puente):
    log = []
    assert mano(puente, log, token="otro-token-de-veinte-caracteres").conectar() is False
    assert "rechazó el token" in log[-1]


def test_si_el_puente_se_cae_se_nota_y_se_recupera(puente):
    log = []
    m = mano(puente, log)
    assert m.conectar() is True
    puente._proc.kill()                                         # el proceso del Bluetooth muere
    puente._proc.wait(5)
    assert m.hacer("a") is False and not m.conectada            # el servidor sigue vivo
    assert m.conectar() is True                                 # se arranca un hijo nuevo
    assert m.hacer("b") is True
    m.cerrar()


def test_el_servidor_nunca_carga_el_bluetooth_de_windows():
    """WinRT (bleak) + ctranslate2 (Whisper) en el mismo proceso = access violation."""
    codigo = ("import sys; from pgc import arranque; from pgc.adaptadores import mano_ble, ble_puente; "
              "m = mano_ble.ManoBLE('Mano-LSC', 't' * 20); "
              "print(sorted(n for n in sys.modules if n.split('.')[0] in ('bleak', 'winrt')))")
    r = subprocess.run([sys.executable, "-c", codigo], capture_output=True, text=True, cwd=TESTS.parent, timeout=60)
    assert r.returncode == 0, r.stderr
    assert r.stdout.strip() == "[]"


def test_el_hijo_termina_cuando_se_cierra_el_servidor(puente):
    m = mano(puente, [])
    assert m.conectar() is True
    proc = puente._proc
    puente.cerrar()                                             # stdin cerrado = el servidor se fue
    assert proc.wait(5) is not None
```

## `tests/test_capas.py`

```python
"""Regla de dependencias de la arquitectura hexagonal (las flechas apuntan hacia adentro)."""
import pytest

from conftest import RAIZ
from test_dominio import imports_de

EXTERNOS = {"serial", "fastapi", "starlette", "uvicorn", "qrcode", "faster_whisper", "ctranslate2",
            "subprocess", "socket", "servidor", "mano_serial", "texto_util", "tunel", "voz_entrada"}
PERMITIDO_EN_APLICACION = ("pgc.dominio", "pgc.puertos", "pgc.aplicacion")


@pytest.mark.parametrize("ruta", sorted((RAIZ / "pgc" / "aplicacion").glob("*.py")), ids=lambda r: r.name)
def test_la_aplicacion_solo_usa_dominio_y_puertos(ruta):
    for nombre in imports_de(ruta):
        raiz = nombre.split(".")[0]
        assert raiz not in EXTERNOS, f"{ruta.name} importa {nombre}"
        if raiz == "pgc":
            assert nombre.startswith(PERMITIDO_EN_APLICACION), f"{ruta.name} importa {nombre}"


@pytest.mark.parametrize("ruta", sorted((RAIZ / "pgc" / "api").rglob("*.py")), ids=lambda r: r.name)
def test_la_api_no_conoce_los_adaptadores(ruta):
    for nombre in imports_de(ruta):
        assert not nombre.startswith(("pgc.adaptadores", "pgc.arranque")), f"{ruta.name} importa {nombre}"
        assert nombre.split(".")[0] not in {"servidor", "mano_serial", "tunel", "voz_entrada", "serial"}, nombre


@pytest.mark.parametrize("ruta", sorted((RAIZ / "pgc" / "puertos").glob("*.py")), ids=lambda r: r.name)
def test_los_puertos_no_dependen_de_implementaciones(ruta):
    for nombre in imports_de(ruta):
        assert not nombre.startswith(("pgc.adaptadores", "pgc.aplicacion", "pgc.api")), f"{ruta.name} importa {nombre}"
        assert nombre.split(".")[0] not in EXTERNOS, f"{ruta.name} importa {nombre}"
```

## `tests/test_cola.py`

```python
"""Cola de mensajes y deletreo (caracterización de servidor.Sistema con una mano falsa)."""
import re
from unittest.mock import ANY

import pytest

from conftest import esperar


# =============================================================================
#  Cola (sin hilo de la mano: los mensajes se quedan pendientes)
# =============================================================================
def test_encolar_limpia_y_numera(crear_sistema):
    s = crear_sistema()
    m1 = s.encolar("  HOLA  ", "c1")
    m2 = s.encolar("Uña", "c2")
    assert (m1["id"], m1["texto"]) == (1, "hola")
    assert (m2["id"], m2["texto"]) == (2, "uña")
    assert m1["i"] == -1 and m1["cliente"] == "c1"
    assert [m["id"] for m in s.cola] == [1, 2]


def test_maximo_dos_pendientes_por_cliente(crear_sistema):
    s = crear_sistema()
    s.encolar("hola", "c1")
    s.encolar("uña", "c1")
    with pytest.raises(ValueError, match=r"^Ya tienes 2 mensajes en espera\. Espera a que la mano los haga\.$"):
        s.encolar("otro", "c1")
    s.encolar("ve mi", "c2")                       # otro celular sí puede
    assert len(s.cola) == 3


@pytest.mark.parametrize("entrada, error", [
    ("¡¿?!", "Escribe al menos una letra."),
    ("", "Escribe al menos una letra."),
    ("gh", "La mano todavía no puede hacer esas letras"),
    ("Jhs", "La mano todavía no puede hacer esas letras"),
    ("zz gg", "La mano todavía no puede hacer esas letras"),
])
def test_rechazos(crear_sistema, entrada, error):
    s = crear_sistema()
    with pytest.raises(ValueError) as ex:
        s.encolar(entrada, "c1")
    assert str(ex.value) == error
    assert s.cola == []


@pytest.mark.parametrize("entrada", ["hola gh", "Ñ", "a"])
def test_se_acepta_si_hay_al_menos_una_letra_posible(crear_sistema, entrada):
    s = crear_sistema()
    s.encolar(entrada, "c1")
    assert len(s.cola) == 1


def test_cola_global_de_30(crear_sistema):
    s = crear_sistema()
    for k in range(30):
        s.encolar("a", f"c{k}")
    with pytest.raises(ValueError, match=r"^La cola está llena, intenta en un momento\.$"):
        s.encolar("a", "otro")


def test_cancelar_solo_lo_propio(crear_sistema):
    s = crear_sistema()
    m1 = s.encolar("hola", "A")
    m2 = s.encolar("uña", "A")
    m3 = s.encolar("ve mi", "B")
    assert s.cancelar(m2["id"], "B") is False      # B no puede cancelar el de A
    assert s.cancelar(m2["id"], "A") is True
    assert s.cancelar(m2["id"], "A") is False      # ya no existe
    assert s.cancelar(999, "A") is False
    assert [m["id"] for m in s.cola] == [m1["id"], m3["id"]]


def test_instantanea_no_expone_el_cliente(crear_sistema):
    s = crear_sistema()
    s.encolar("hola", "secreto-del-celular")
    d = s.instantanea()
    assert d["cola"] == [{"id": 1, "texto": "hola", "pid": ANY, "nombre": "Anónimo"}]     # E8: autor (sin nombre)
    assert re.fullmatch(r"p[0-9a-f]{8}", d["cola"][0]["pid"])
    assert "secreto-del-celular" not in repr(d)


def test_instantanea_estructura(crear_sistema):
    s = crear_sistema()
    d = s.instantanea()
    assert set(d) == {"tipo", "sesion", "mano", "voz", "tunel", "url_local", "url_publica", "kinect",
                      "max_caracteres", "actual", "cola", "historial", "bloqueados", "voz_salida"}     # E8, Kinect
    assert d["bloqueados"] == []
    assert d["tipo"] == "estado"
    assert d["mano"] == {"modo": "simulada", "medio": None, "puerto": None, "letras": None}   # E10: medio
    assert d["voz"] == {"estado": "listo", "dispositivo": "cuda float16"}
    assert d["tunel"] == {"estado": "apagado", "url": None}
    assert d["url_local"] == d["url_publica"] == "http://192.168.0.10:8000"
    assert set(d["kinect"]) == {"estado", "detalle", "texto", "conectado", "camara", "activo", "controles",
                                "frases", "turno", "eco", "codigo", "codigo_version"}      # Kinect integrado
    assert d["kinect"]["estado"] == "apagado" and d["kinect"]["turno"] is None and d["kinect"]["eco"] is False
    assert d["voz_salida"] == {"estado": "desactivado"}
    assert d["max_caracteres"] == 60
    assert (d["actual"], d["cola"], d["historial"]) == (None, [], [])


def test_saltar_sin_mensaje_en_curso(crear_sistema):
    assert crear_sistema().saltar_actual() is False


# =============================================================================
#  Deletreo: órdenes que recibe la mano (con el hilo de la mano)
# =============================================================================
def deletrear(s, texto, cliente="c1"):
    """Encola, espera a que termine y devuelve las órdenes enviadas a la mano."""
    antes = len(s.mano.ordenes)
    m = s.encolar(texto, cliente)
    esperar(lambda: s.historial and s.historial[0]["id"] == m["id"])
    return s.mano.ordenes[antes:]


@pytest.mark.parametrize("entrada, ordenes", [
    ("calle", "c a l reset l e reset"),
    ("carro", "c a r reset r o reset"),
    ("ll ll", "l reset l reset l reset l reset"),
    ("ñn", "n reset n reset"),                     # la Ñ se hace con la forma de la N
    ("lgl", "l reset l reset"),                    # la g no se envía; la mano seguía en l
    ("hola", "o l a reset"),                       # la h no se envía
    ("ve mi", "v e reset m i reset"),              # espacio = mano abierta
    ("a", "a reset"),
])
def test_ordenes_a_la_mano(sistema_con_mano, entrada, ordenes):
    assert deletrear(sistema_con_mano, entrada) == ordenes.split()


def test_si_la_mano_no_confirma_no_se_abre_antes_de_repetir(sistema_con_mano):
    s = sistema_con_mano
    s.mano.fallar = {"l"}
    assert deletrear(s, "ll") == ["l", "l", "reset"]
    assert [p["r"] for p in s.historial[0]["pasos"]] == ["error", "error"]


def test_resultado_por_paso_y_fin(sistema_con_mano):
    s = sistema_con_mano
    deletrear(s, "ha b")
    m = s.historial[0]
    assert [(p["c"], p["r"]) for p in m["pasos"]] == [("H", "nd"), ("A", "ok"), (" ", "ok"), ("B", "ok")]
    assert m["i"] == len(m["pasos"])
    assert s.actual is None
    d = s.instantanea()
    assert d["historial"][0] == {"id": m["id"], "texto": "ha b", "nombre": "Anónimo", "saltado": False}


def test_secuencia_se_recalcula_con_las_letras_de_la_mano(sistema_con_mano):
    s = sistema_con_mano
    s.mano.letras = set("agh")
    assert deletrear(s, "gha") == ["g", "h", "a", "reset"]


def test_mensajes_en_orden_de_llegada(sistema_con_mano):
    s = sistema_con_mano
    s.mano.bloquear_en = "a"
    s.encolar("a", "c1")
    s.mano.llego.wait(5)
    s.encolar("b", "c2")
    s.encolar("c", "c3")
    s.mano.soltar.set()
    esperar(lambda: len(s.historial) == 3)
    assert s.mano.ordenes == ["a", "reset", "b", "reset", "c", "reset"]
    assert [m["texto"] for m in s.historial] == ["c", "b", "a"]      # el más reciente primero


def test_historial_guarda_los_ultimos_6(sistema_con_mano):
    s = sistema_con_mano
    for k in range(8):
        deletrear(s, "a", cliente=f"c{k}")
    assert len(s.historial) == 6
    assert len(s.instantanea()["historial"]) == 6


def test_el_mensaje_en_curso_cuenta_para_el_limite(sistema_con_mano):
    s = sistema_con_mano
    s.mano.bloquear_en = "a"
    s.encolar("a", "c1")
    s.mano.llego.wait(5)
    assert s.actual is not None and s.cola == []
    s.encolar("b", "c1")
    with pytest.raises(ValueError, match="Ya tienes 2"):
        s.encolar("c", "c1")
    assert s.cancelar(s.actual["id"], "c1") is False                 # el que está en curso no se cancela


def test_estado_durante_el_deletreo(sistema_con_mano):
    s = sistema_con_mano
    s.mano.bloquear_en = "c"
    s.encolar("abc", "c1")
    s.mano.llego.wait(5)
    a = s.instantanea()["actual"]
    assert a == {"id": 1, "texto": "abc", "i": 2, "saltado": False, "pid": ANY, "nombre": "Anónimo", "pasos": [
        {"c": "A", "tipo": "ok", "r": "ok"}, {"c": "B", "tipo": "ok", "r": "ok"}, {"c": "C", "tipo": "ok", "r": None}]}


def test_saltar_mensaje(sistema_con_mano):
    s = sistema_con_mano
    s.mano.bloquear_en = "c"
    s.encolar("abcdefiklmnop", "c1")
    s.mano.llego.wait(5)
    assert s.saltar_actual() is True
    s.mano.soltar.set()
    esperar(lambda: len(s.historial) == 1)
    assert s.mano.ordenes == ["a", "b", "c", "reset"]                 # la letra en curso termina
    assert s.historial[0]["saltado"] is True
    assert s.instantanea()["historial"][0]["saltado"] is True
    # El siguiente mensaje se deletrea normal
    assert deletrear(s, "ok", cliente="c2") == ["o", "k", "reset"]
    assert s.instantanea()["historial"][0] == {"id": 2, "texto": "ok", "nombre": "Anónimo", "saltado": False}


def test_reconexion_pedida(sistema_con_mano):
    s = sistema_con_mano
    n = s.mano.conexiones
    s.pedir_reconexion = True
    with s.cv:
        s.cv.notify_all()
    esperar(lambda: s.mano.conexiones == n + 1)
    assert s.pedir_reconexion is False
```

## `tests/test_config.py`

```python
"""Configuración centralizada (pgc.config)."""
import pytest

from conftest import RAIZ, mano_serial, modulo_texto, servidor

from pgc import config as cfgmod


def cargar(argv=(), entorno=None, archivo_env=None, tmp_path=None):
    if archivo_env is None:
        archivo_env = (tmp_path or RAIZ) / "no-existe.env"
    return cfgmod.cargar(list(argv), entorno or {}, archivo_env)


def test_valores_por_defecto_iguales_a_los_del_codigo_actual():
    c = cargar()
    assert c.puerto_web == 8000 and c.abrir_navegador and c.tunel and c.voz
    assert c.mano == "auto" and c.mano_puerto is None
    assert c.mano_baudios == 115200
    assert set(c.mano_vids) == mano_serial.VIDS_ESP32
    assert c.mano_timeout_letra == mano_serial.TIMEOUT_LETRA
    assert c.mano_tiempo_simulado == mano_serial.TIEMPO_SIMULADO
    assert c.pausa_letra == servidor.PAUSA_ENTRE_LETRAS
    assert c.pausa_no_disponible == servidor.PAUSA_NO_DISPONIBLE
    assert c.max_caracteres == modulo_texto.MAX_CARACTERES
    assert c.max_pendientes_cliente == servidor.MAX_PENDIENTES_CLIENTE
    assert c.max_cola == servidor.MAX_COLA
    assert c.audio_max_bytes == servidor.MAX_AUDIO_BYTES
    assert c.historial == 6 and c.ping_ws == 20.0 and c.autodeteccion_cada == 3.0
    assert c.voz_modelo == "medium"


@pytest.mark.parametrize("argv, esperado", [
    (["--simular"], {"mano": "simulada"}),
    (["--puerto", "COM5"], {"mano_puerto": "COM5", "mano": "auto"}),
    (["--puerto-web", "8001"], {"puerto_web": 8001}),
    (["--sin-tunel", "--sin-voz", "--no-abrir"], {"tunel": False, "voz": False, "abrir_navegador": False}),
])
def test_opciones_de_siempre(argv, esperado):
    c = cargar(argv)
    for k, v in esperado.items():
        assert getattr(c, k) == v


def test_prioridad_env_variables_opciones(tmp_path):
    env = tmp_path / ".env"
    env.write_text("PGC_PUERTO_WEB=8100\nPGC_MAX_COLA=10   # comentario\nPGC_MANO=simulada\n", encoding="utf-8")
    c = cargar(archivo_env=env)
    assert (c.puerto_web, c.max_cola, c.mano) == (8100, 10, "simulada")
    c = cargar(entorno={"PGC_PUERTO_WEB": "8200"}, archivo_env=env)
    assert (c.puerto_web, c.max_cola) == (8200, 10)                  # la variable gana al .env
    c = cargar(["--puerto-web", "8300"], entorno={"PGC_PUERTO_WEB": "8200"}, archivo_env=env)
    assert c.puerto_web == 8300                                      # la opción gana a todo


@pytest.mark.parametrize("variables, esperado", [
    ({"PGC_VOZ": "false"}, ("voz", False)),
    ({"PGC_TUNEL": "0"}, ("tunel", False)),
    ({"PGC_MANO_VIDS": "303a, 1A86"}, ("mano_vids", (0x303A, 0x1A86))),
    ({"PGC_MANO_PUERTO": ""}, ("mano_puerto", None)),
    ({"PGC_PAUSA_LETRA": "0.25"}, ("pausa_letra", 0.25)),
])
def test_conversion_de_tipos(variables, esperado):
    assert getattr(cargar(entorno=variables), esperado[0]) == esperado[1]


@pytest.mark.parametrize("variables, fragmento", [
    ({"PGC_PUERTO_WEB": "ocho mil"}, "PGC_PUERTO_WEB"),
    ({"PGC_VOZ": "quizas"}, "PGC_VOZ"),
    ({"PGC_MANO": "bluetooth"}, "PGC_MANO"),
    ({"PGC_MAX_COLA": "0"}, "PGC_MAX_COLA"),
    ({"PGC_PAUSA_LETRA": "-1"}, "PGC_PAUSA_LETRA"),
])
def test_valores_invalidos_dan_un_error_claro(variables, fragmento):
    with pytest.raises(cfgmod.ErrorConfig, match=fragmento):
        cargar(entorno=variables)


def test_variables_ajenas_se_ignoran():
    assert cargar(entorno={"PATH": "x", "PGC_DESCONOCIDA": "1"}) == cfgmod.Config()


def test_env_example_documenta_todas_las_variables():
    ejemplo = (RAIZ / ".env.example").read_text(encoding="utf-8")
    from dataclasses import fields
    for campo in fields(cfgmod.Config):
        assert f"PGC_{campo.name.upper()}=" in ejemplo, campo.name


def test_config_es_inmutable():
    with pytest.raises(Exception):
        cargar().puerto_web = 1
```

## `tests/test_dominio.py`

```python
"""Dominio puro: regla de órdenes, abecedario y aislamiento de la capa."""
import ast
import json

import pytest

from conftest import RAIZ, modulo_ordenes, modulo_texto

from pgc.dominio import abecedario


def plan(texto, letras=None):
    return " ".join(modulo_ordenes.planificar_ordenes(modulo_texto.a_secuencia(texto, letras)))


# ---------------------------------------------------------------- órdenes
@pytest.mark.parametrize("entrada, ordenes", [
    ("calle", "c a l reset l e reset"),
    ("carro", "c a r reset r o reset"),
    ("ll ll", "l reset l reset l reset l reset"),
    ("ñn", "n reset n reset"),
    ("lgl", "l reset l reset"),
    ("hola", "o l a reset"),
    ("ve mi", "v e reset m i reset"),
    ("a", "a reset"),
])
def test_planificar_ordenes_igual_que_el_hilo_de_la_mano(entrada, ordenes):
    assert plan(entrada) == ordenes


def test_ordenes_para_cada_tipo_de_paso():
    letra = {"c": "L", "l": "l", "tipo": "ok"}
    assert modulo_ordenes.ordenes_para(letra, None) == ["l"]
    assert modulo_ordenes.ordenes_para(letra, "a") == ["l"]
    assert modulo_ordenes.ordenes_para(letra, "l") == ["reset", "l"]
    assert modulo_ordenes.ordenes_para({"c": " ", "l": None, "tipo": "espacio"}, "l") == ["reset"]
    assert modulo_ordenes.ordenes_para({"c": "H", "l": None, "tipo": "nd"}, "l") == []
    assert modulo_ordenes.ordenes_para({"c": "Ñ", "l": "n", "tipo": "aprox"}, "n") == ["reset", "n"]


def test_forma_despues():
    letra = {"c": "L", "l": "l", "tipo": "ok"}
    assert modulo_ordenes.forma_despues(letra, None, True) == "l"
    assert modulo_ordenes.forma_despues(letra, None, False) is None          # sin confirmar: forma desconocida
    assert modulo_ordenes.forma_despues({"c": " ", "l": None, "tipo": "espacio"}, "l", True) is None
    assert modulo_ordenes.forma_despues({"c": "H", "l": None, "tipo": "nd"}, "l", None) == "l"


# ---------------------------------------------------------------- abecedario
def test_letras_json_da_las_21_letras_de_hoy():
    a = abecedario.cargar_abecedario()
    assert "".join(sorted(a.por_defecto)) == "abcdefiklmnopqrtuvwxy"
    assert a.aproximaciones == {"ñ": "n"}
    assert a.con_movimiento == frozenset("jzñ")
    assert modulo_texto.LETRAS_POR_DEFECTO == a.por_defecto


def test_agregar_letras_es_editar_datos(tmp_path):
    ruta = tmp_path / "letras.json"
    ruta.write_text(json.dumps({"por_defecto": "abcghs", "aproximaciones": {"ñ": "n"}}), encoding="utf-8")
    assert abecedario.cargar_abecedario(ruta).por_defecto == frozenset("abcghs")


@pytest.mark.parametrize("contenido, fragmento", [
    ("{no es json", "No se pudo leer"),
    (json.dumps({"por_defecto": ""}), "vacío"),
    (json.dumps({"por_defecto": "ab1"}), "no son letras"),
    (json.dumps({"por_defecto": "ab", "aproximaciones": {"ñ": "nn"}}), "aproximación inválida"),
])
def test_letras_json_invalido(tmp_path, contenido, fragmento):
    ruta = tmp_path / "letras.json"
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(abecedario.ErrorAbecedario, match=fragmento):
        abecedario.cargar_abecedario(ruta)


# ---------------------------------------------------------------- aislamiento
PROHIBIDOS = {"threading", "socket", "serial", "fastapi", "starlette", "uvicorn", "asyncio", "subprocess",
              "servidor", "mano_serial", "tunel", "voz_entrada"}


def imports_de(ruta):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            yield from (a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            yield nodo.module


@pytest.mark.parametrize("ruta", sorted((RAIZ / "pgc" / "dominio").glob("*.py")), ids=lambda r: r.name)
def test_el_dominio_no_depende_de_nada_externo(ruta):
    for nombre in imports_de(ruta):
        raiz = nombre.split(".")[0]
        assert raiz not in PROHIBIDOS, f"{ruta.name} importa {nombre}"
        if raiz == "pgc":
            assert nombre.startswith("pgc.dominio"), f"{ruta.name} importa {nombre} (fuera del dominio)"
```

## `tests/test_firmware.py`

```python
"""El main.py de la placa = el código ORIGINAL del autor + solo el bloque agregado (Bluetooth).

Se ejecutan los dos programas TAL CUAL en el PC (machine/time/uselect/bluetooth falsos)
y se comparan los pulsos, las pausas y los textos que imprimen o envían.
"""
import ast
import importlib.util
import time

import pytest

from arnes_firmware import (ARRANQUE, FIRMWARE, MAIN, MARCA, ORIGINAL, CentralFalsa, PlacaEnHilo, correr)

LETRAS = "abcdefiklmnopqrtuvwxy"
TOKEN = "token-de-prueba-0123456789"


def armar_main():
    ruta = FIRMWARE.parent.parent / "scripts" / "armar_main_placa.py"
    spec = importlib.util.spec_from_file_location("armar_main_placa", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.armar()


# =============================================================================
#  Texto: todo lo de arriba del BUCLE PRINCIPAL es idéntico, línea por línea
# =============================================================================
def hasta_el_bucle(ruta):
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    return lineas[:lineas.index(MARCA) + 1]


def test_arriba_del_bucle_principal_identico_linea_por_linea():
    original, placa = hasta_el_bucle(ORIGINAL), hasta_el_bucle(MAIN)
    assert len(placa) == len(original) == 225
    for numero, (a, b) in enumerate(zip(original, placa), start=1):
        assert a == b, f"línea {numero} distinta"


def test_main_es_el_original_mas_el_bloque_agregado():
    texto = MAIN.read_text(encoding="utf-8")
    assert texto == armar_main()                         # nada más se tocó
    bloque = texto[texto.index(MARCA) + len(MARCA):]
    assert ">>> INICIO DE LO AGREGADO" in bloque and "<<< FIN DE LO AGREGADO" in bloque
    assert "import bluetooth" in bloque
    assert "network" not in texto and "socket" not in texto            # sin WiFi
    assert "letras.json" not in texto


# =============================================================================
#  Por USB: mismos pulsos, pausas y textos que el original
# =============================================================================
@pytest.mark.parametrize("orden", list(LETRAS) + ["reset", "1", "g", "ñ", "hola", "calle"])
def test_por_usb_igual_que_el_original(orden):
    reg_o, txt_o = correr(ORIGINAL, [orden])
    reg_p, txt_p = correr(MAIN, [orden])
    assert reg_p == reg_o
    assert txt_p == txt_o


def test_secuencia_larga_por_usb():
    ordenes = list("hola") + ["reset", "jurado", "1"] + list(LETRAS) + ["xyz", "g", "", "   ", "a"]
    reg_o, txt_o = correr(ORIGINAL, ordenes)
    reg_p, txt_p = correr(MAIN, ordenes)
    assert reg_p == reg_o and txt_p == txt_o
    assert len(reg_p) > 400
    assert txt_p[0] == "Iniciando motores..." and txt_p[-1] == "Programa terminado."


def test_textos_de_respuesta():
    _, txt = correr(MAIN, ["a", "reset", "1", "g", "ab"])
    assert txt == ["Iniciando motores...", "Mano lista.", "Listo. Esperando comandos...",
                   "gesto_a_ok", "reset_ok", "reset_ok", "comando_no_reconocido",
                   "gesto_a_ok", "letra_actual:a", "gesto_b_ok", "letra_actual:b", "deletreo_completo",
                   "Programa terminado."]


# =============================================================================
#  Por Bluetooth: mismas órdenes, mismos textos y mismos movimientos
# =============================================================================
@pytest.fixture
def placa():
    p = PlacaEnHilo(TOKEN)
    assert p.error is None, p.error
    yield p
    p.detener()


def pc(placa, token=TOKEN):
    c = CentralFalsa(placa)
    if token is not None:
        c.enviar(f"auth {token}")
    return c


def test_se_anuncia_como_mano_lsc(placa):
    assert placa.radio.nombre == "Mano-LSC" and placa.radio.anunciando
    assert b"Mano-LSC" in placa.radio.anuncio
    assert "# Bluetooth listo: se anuncia como Mano-LSC" in placa.salida.lineas()


def test_ble_mismas_respuestas_que_el_original(placa):
    c = pc(placa)
    assert c.lineas(1) == ["ok:auth"]
    ordenes = ["a", "reset", "g", "hola", "1"]
    respuestas = []
    for o in ordenes:
        c.enviar(o)
        respuestas += c.lineas({"hola": 8}.get(o, 1))               # "hola" responde como deletrear()
    _, txt_o = correr(ORIGINAL, ordenes)
    assert respuestas == txt_o[3:-1]                                 # sin arranque ni "Programa terminado."


def test_ble_mueve_igual_que_el_original_por_usb(placa):
    c = pc(placa)
    c.lineas(1)
    ordenes = list("calle") + ["reset"] + list(LETRAS) + ["reset"]   # termina abierta, como el original al salir
    for o in ordenes:
        c.enviar(o)
        c.lineas(1)
    reg_o, _ = correr(ORIGINAL, ordenes)
    assert list(placa.registro) == list(reg_o)
    assert len(reg_o) > 300


def test_ble_token_incorrecto(placa):
    c = pc(placa, token="otro-token-cualquiera-xx")
    assert c.lineas(1) == ["error:auth"]
    assert c.desconectado.wait(2)                                    # la placa lo desconectó
    assert len(placa.registro) == ARRANQUE                           # no se movió nada
    time.sleep(0.05)
    assert placa.radio.anunciando                                    # y se anuncia de nuevo


def test_ble_sin_token_no_ejecuta(placa):
    c = pc(placa, token=None)
    c.enviar("a")
    assert c.lineas(1) == ["error:auth"]
    assert len(placa.registro) == ARRANQUE


def test_ble_sin_presentarse_a_tiempo(placa):
    c = pc(placa, token=None)
    assert c.desconectado.wait(5)                                    # a los 3 s
    assert placa.radio.anunciando


def test_ble_un_solo_pc_a_la_vez(placa):
    c = pc(placa)
    c.lineas(1)
    assert not placa.radio.anunciando                                # nadie más puede conectarse
    with pytest.raises(OSError):
        CentralFalsa(placa)
    c.enviar("a")
    assert c.lineas(1) == ["gesto_a_ok"]


def test_ble_desconexion_y_reconexion(placa):
    c = pc(placa)
    c.lineas(1)
    placa.radio.desconectar_central()
    time.sleep(0.05)
    assert placa.radio.anunciando
    c2 = pc(placa)                                                   # el PC vuelve a conectarse
    assert c2.lineas(1) == ["ok:auth"]
    c2.enviar("b")
    assert c2.lineas(1) == ["gesto_b_ok"]
    assert any("desconectado" in l for l in placa.salida.lineas())


def test_ble_paquetes_de_20_bytes(placa):
    c = pc(placa)
    c.lineas(1)
    c.enviar("hola")                                                 # respuestas largas: se parten en 20 bytes
    assert c.lineas(8)[-1] == "deletreo_completo"


def test_usb_sigue_funcionando_con_bluetooth(placa):
    placa.stdin.escribir("a\n")
    limite = time.time() + 5
    while time.time() < limite and "gesto_a_ok" not in placa.salida.lineas():
        time.sleep(0.01)
    assert "gesto_a_ok" in placa.salida.lineas()


def test_sin_config_ble_funciona_solo_por_usb():
    _, txt = correr(MAIN, ["a"])                                     # config_ble = None
    assert not any("Bluetooth" in l for l in txt)


def test_token_corto_desactiva_el_bluetooth():
    from arnes_firmware import config_ble_falso
    _, txt = correr(MAIN, ["a"], config_ble=config_ble_falso("corto"))
    assert any("Bluetooth desactivado" in l for l in txt) and "gesto_a_ok" in txt


# =============================================================================
#  prueba_dedos.py, MicroPython y secretos
# =============================================================================
def dedos_config_de(ruta):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and getattr(nodo.targets[0], "id", None) == "dedos_config":
            return ast.literal_eval(nodo.value)
    raise AssertionError("sin dedos_config")


def test_prueba_dedos_usa_la_misma_calibracion():
    assert dedos_config_de(FIRMWARE / "prueba_dedos.py") == dedos_config_de(MAIN) == dedos_config_de(ORIGINAL)


def test_prueba_dedos_mueve_un_dedo_a_la_vez():
    reg, txt = correr(FIRMWARE / "prueba_dedos.py", [])
    pulsos = [e for e in reg if e[0] == "pulso"][6:]
    assert len(pulsos) == 3 * 6 * 3                                  # 3 vueltas × 6 dedos × 3 posiciones
    for k in range(0, len(pulsos), 3):
        assert len({p[1] for p in pulsos[k:k + 3]}) == 1
    assert txt[-1] == "Prueba de dedos terminada: mano abierta."


def test_prueba_usa_la_misma_calibracion():
    assert dedos_config_de(FIRMWARE / "prueba.py") == dedos_config_de(ORIGINAL)


def test_prueba_cierra_y_abre_dedo_por_dedo_y_termina_cerrada():
    cfg = dedos_config_de(ORIGINAL)
    pines = {c["pin"]: n for n, c in cfg.items()}
    reg, txt = correr(FIRMWARE / "prueba.py", [])
    pulsos = [(pines[e[1]], e[2] // 1000) for e in reg if e[0] == "pulso"]      # duty_ns → µs
    abierto = {n: c["abierto"] for n, c in cfg.items()}
    cerrado = {n: c["cerrado"] for n, c in cfg.items()}
    abrir = ["pulgar2", "pulgar", "indice", "medio", "anular", "menique"]        # dedo gordo de primeras
    esperado = [(n, abierto[n]) for n in abrir]                                  # arranque: todos arriba
    for n in ["indice", "medio", "anular", "menique"]:                           # uno por uno, en ese orden
        esperado += [(n, cerrado[n]), (n, abierto[n])]
    esperado += [("pulgar", cerrado["pulgar"]), ("pulgar2", cerrado["pulgar2"]),  # gira y se recoge
                 ("pulgar2", abierto["pulgar2"]), ("pulgar", abierto["pulgar"])]  # se reinicia, como en l()
    cerrar = ["pulgar", "pulgar2", "indice", "medio", "anular", "menique"]       # dedo gordo de primeras
    esperado += [(n, cerrado[n]) for n in cerrar]
    abrir_final = ["indice", "medio", "anular", "menique", "pulgar2", "pulgar"]  # dedo gordo de últimas
    esperado += [(n, abierto[n]) for n in abrir_final]
    assert pulsos == esperado                                                    # termina abierta
    assert txt[-1] == "Prueba terminada: mano abierta."


PERMITIDOS = {"machine", "time", "sys", "uselect", "select", "bluetooth", "micropython", "config_ble"}


@pytest.mark.parametrize("archivo", ["main.py", "prueba_dedos.py", "prueba.py", "config_ble.example.py"])
def test_solo_modulos_de_micropython(archivo):
    arbol = ast.parse((FIRMWARE / archivo).read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres = [a.name for a in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            nombres = [nodo.module]
        else:
            continue
        for n in nombres:
            assert n.split(".")[0] in PERMITIDOS, f"{archivo} importa {n}"


def test_en_la_placa_solo_va_main_py():
    sobrantes = {"mano_movimientos.py", "mano_protocolo.py", "mano_red.py", "mano_vigilante.py",
                 "mano_servos.py", "letras.json", "config_wifi.example.py"}
    assert not {p.name for p in FIRMWARE.iterdir()} & sobrantes


def test_config_ble_de_ejemplo_no_tiene_datos_reales():
    texto = (FIRMWARE / "config_ble.example.py").read_text(encoding="utf-8")
    assert 'NOMBRE = "Mano-LSC"' in texto and 'TOKEN = "cambia-este-token' in texto
    assert not (FIRMWARE / "config_ble.py").exists()
```

## `tests/test_kinect_adaptador.py`

```python
"""ReconocedorKinect contra un detector falso que habla como el de integracion_kinect/."""
import time

import pytest

from conftest import esperar
from detector_falso import JPEG, DetectorFalso

from pgc.adaptadores.kinect.reconocedor import (NO_CONECTADO, ErrorKinect, ReconocedorKinect,
                                                eventos_por_cambio, leer_estado)
from pgc.puertos.reconocedor import ESTADOS, problemas_del_evento


def resumen(eventos):
    return [e.letra if e.tipo == "letra" else e.tipo for e in eventos]


# ---------------------------------------------------------------- cambios de texto → eventos
@pytest.mark.parametrize("antes, despues, esperado", [
    ("", "", []),
    ("", "HO", ["h", "o"]),
    ("HO", "HOL", ["l"]),
    ("HOL", "HOL ", ["espacio"]),
    ("HOLA", "HOL", ["borrar"]),
    ("HOLA", "", ["borrar"] * 4),
    ("HOLA", "HOJA", ["borrar", "borrar", "j", "a"]),          # se borra hasta lo común y se escribe el resto
    ("", "A?Ñ", ["a", "ñ"]),                                   # lo que no es letra no se emite
])
def test_eventos_por_cambio(antes, despues, esperado):
    eventos = eventos_por_cambio(antes, despues)
    assert resumen(eventos) == esperado
    assert all(not problemas_del_evento(e) for e in eventos)     # cumplen el contrato (minúsculas, etc.)


def test_leer_estado_texto_y_json():
    assert leer_estado("Texto: —\nEstado: Deletreo detenido.")[:2] == ("", "Deletreo detenido.")
    assert leer_estado("Texto: HOLA\r\nEstado: Posible letra: A")[:2] == ("HOLA", "Posible letra: A")
    # Si el detector pasa a JSON (lo que le pedimos), se usa sin cambiar el adaptador
    assert leer_estado('{"texto": "HO", "estado": "x", "activo": true, "confianza": 0.9, "latencia_ms": 80}') == \
        ("HO", "x", True, 0.9, 80)
    with pytest.raises(ValueError):
        leer_estado("cualquier cosa")


# ---------------------------------------------------------------- con el detector falso
@pytest.fixture
def detector():
    d = DetectorFalso()
    yield d
    d.cerrar()


@pytest.fixture
def kinect(detector):
    eventos, cambios = [], []
    r = ReconocedorKinect(url=detector.url, intervalo=0.05)
    r.iniciar(eventos.append, lambda: cambios.append((r.estado, r.detalle)))
    yield r, eventos, cambios
    r.detener()


def test_sin_detector_dice_kinect_no_conectado():
    r = ReconocedorKinect(url="http://127.0.0.1:9", intervalo=0.05)    # puerto cerrado
    r.iniciar(lambda e: None, lambda: None)
    try:
        esperar(lambda: r.estado == "error")
        assert r.detalle == NO_CONECTADO and not r.conectado
        with pytest.raises(ErrorKinect, match=NO_CONECTADO):
            r.controlar("iniciar")
    finally:
        r.detener()


def test_detector_sin_camara_tambien_es_no_conectado(kinect, detector):
    r, _, _ = kinect
    esperar(lambda: r.conectado)
    assert (r.estado, r.detalle, r.camara) == ("error", NO_CONECTADO, False)
    detector.mantener_camara()
    esperar(lambda: r.camara and r.estado == "sin_persona")
    assert r.detalle == "Deletreo detenido."


def test_deletreo_completo(kinect, detector):
    r, eventos, _ = kinect
    detector.mantener_camara()
    esperar(lambda: r.camara)
    r.controlar("iniciar")
    assert r.activo and detector.ordenes == ["start"]
    for letra in "HOLA":
        detector.reconocer(letra)
    esperar(lambda: resumen(eventos) == ["h", "o", "l", "a"])
    assert r.estado == "listo" and r.detalle.startswith("Letra añadida")
    r.controlar("borrar")
    r.controlar("espacio")                           # tras borrar: "HOL" + " "
    esperar(lambda: resumen(eventos)[4:] == ["borrar", "espacio"])
    detector.reconocer("x")                          # una letra que llega justo antes de «Terminar»
    r.controlar("terminar")                          # la recoge, emite fin y deja el detector en blanco
    assert resumen(eventos)[6:] == ["x", "fin"]
    assert detector.texto == "" and detector.ordenes[-1] == "clear"
    r.controlar("detener")
    assert not r.activo
    assert all(not problemas_del_evento(e) for e in eventos)


def test_un_detector_reiniciado_queda_detenido(kinect, detector):
    r, _, _ = kinect
    detector.mantener_camara()
    esperar(lambda: r.camara)
    r.controlar("iniciar")
    detector.activo, detector.estado = False, "Deletreo detenido."     # p. ej. alguien lo detuvo en la app C#
    esperar(lambda: not r.activo)


def test_error_del_detector_llega_con_su_motivo(detector):
    detector.con_modelo = False
    r = ReconocedorKinect(url=detector.url, intervalo=0.05)
    r.iniciar(lambda e: None, lambda: None)
    try:
        with pytest.raises(ErrorKinect, match="modelo_estaticas.joblib"):
            r.controlar("iniciar")
        with pytest.raises(ErrorKinect):
            r.controlar("saludar")
    finally:
        r.detener()


def test_imagen_solo_si_llegan_cuadros(kinect, detector):
    r, _, _ = kinect
    esperar(lambda: r.conectado)
    assert r.imagen() is None
    detector.mantener_camara()
    esperar(lambda: (r.imagen() or b"").startswith(JPEG))       # cuadros nuevos: JPEG + contador


def test_estados_validos_y_detener_dos_veces(kinect):
    r, _, cambios = kinect
    esperar(lambda: len(cambios) >= 2)
    r.detener()
    r.detener()
    assert r.estado == "apagado"
    assert all(estado in ESTADOS for estado, _ in cambios)


def test_desde_config():
    from conftest import configuracion
    r = ReconocedorKinect.desde_config(configuracion(kinect_url="http://127.0.0.1:8799", kinect_intervalo=0.5))
    assert (r.url, r.intervalo) == ("http://127.0.0.1:8799", 0.5)


# ---------------------------------------------------------------- vista previa: ritmo, pareja estado+imagen, congelada
def test_mirando_lee_estado_e_imagen_juntos_y_rapido(kinect, detector):
    r, _, _ = kinect
    detector.mantener_camara(por_segundo=30)
    esperar(lambda: r.camara)
    r.controlar("iniciar")
    detector.reconocer("A")
    r.imagen_con_estado()                                   # el proyector empieza a mirar
    antes, t0 = detector.consultas, time.monotonic()
    vistos = set()
    while time.monotonic() - t0 < 1.0:
        foto = r.imagen_con_estado()
        vistos.add(foto["cuadro"])
        time.sleep(0.01)
    por_segundo = (detector.consultas - antes) / (time.monotonic() - t0)
    # ~20 vueltas/s (antes ~3). La prueba exige 10 para no fallar con el PC cargado; la cifra real se mide en Edge
    assert por_segundo >= 10, por_segundo
    assert len(vistos) >= 10, len(vistos)                   # imágenes distintas por segundo
    foto = r.imagen_con_estado()
    assert foto["texto"] == "A" and foto["detalle"].startswith("Letra añadida")   # el estado de ESA imagen
    assert foto["desfase_ms"] < 50 and foto["edad_ms"] < 200


def test_sin_mirar_no_carga_al_detector(kinect, detector):
    r, _, _ = kinect                                        # intervalo 0,05 en la prueba; nadie pide la imagen
    detector.mantener_camara()
    esperar(lambda: r.camara)
    r._t_pedida = -1e9
    antes, t0 = detector.consultas, time.monotonic()
    time.sleep(1)
    assert (detector.consultas - antes) / (time.monotonic() - t0) <= 25    # solo el estado, a su ritmo normal


def test_imagen_congelada_es_kinect_no_conectado(kinect, detector):
    r, _, _ = kinect
    detector.mantener_camara()
    r.imagen_con_estado()                                   # mirando
    esperar(lambda: r.camara and r.estado == "sin_persona")
    detector.congelar()                                     # el detector sigue repitiendo la última imagen
    t0 = time.monotonic()
    esperar(lambda: r.estado == "error" and r.detalle == NO_CONECTADO, timeout=4)
    assert time.monotonic() - t0 < 2.5                      # antes: 3 s después de que el detector diera 503
```

## `tests/test_kinect_codigo.py`

```python
"""Código del proyector para tomar el turno del Kinect (el «Código del PC» del diseño de Camila).

Con PGC_KINECT_CODIGO=true (por defecto) el proyector muestra 6 dígitos que cambian en
cada arranque; el celular los escribe para «Activar control». Sigue habiendo un solo
turno a la vez, con liberación por inactividad, y bloquear a alguien le quita el turno.
"""
import re

import pytest

from conftest import admin, configuracion, esperar
from pgc import config
from pgc.aplicacion.turno import CodigoIncorrecto, TurnoKinect, TurnoOcupado


def tomar(c, cliente, codigo=None):
    return c.post("/api/kinect/turno", json={"cliente": cliente, "codigo": codigo})


def codigo_del_proyector(c):
    return c.get("/api/kinect/codigo", headers=admin(c)).json()["codigo"]


# ---------------------------------------------------------------- configuración
def test_el_codigo_esta_activo_por_defecto_y_se_desactiva_en_el_env(tmp_path):
    assert config.Config().kinect_codigo is True
    env = tmp_path / ".env"
    env.write_text("PGC_KINECT_CODIGO=false\n", encoding="utf-8")
    assert config.cargar([], entorno={}, archivo_env=env).kinect_codigo is False


# ---------------------------------------------------------------- dominio del turno
def test_codigo_de_6_digitos_distinto_en_cada_arranque():
    codigos = {TurnoKinect(con_codigo=True).codigo for _ in range(20)}
    assert all(re.fullmatch(r"\d{6}", c) for c in codigos)
    assert len(codigos) > 1


def test_sin_el_codigo_correcto_no_hay_turno():
    t = TurnoKinect(con_codigo=True)
    for malo in (None, "", "12345", "abcdef", str((int(t.codigo) + 1) % 10**6).zfill(6)):
        with pytest.raises(CodigoIncorrecto):
            t.tomar("A", "p1", "Ana", malo)
    assert t.instantanea() is None
    t.tomar("A", "p1", "Ana", " " + t.codigo[:3] + " " + t.codigo[3:])    # espacios del teclado: se aceptan
    assert t.es_dueno("A")


def test_con_el_codigo_sigue_habiendo_un_solo_turno_y_se_libera_solo():
    reloj = [0.0]
    t = TurnoKinect(segundos=120, reloj=lambda: reloj[0], con_codigo=True)
    t.tomar("A", "p1", "Ana", t.codigo)
    with pytest.raises(TurnoOcupado):
        t.tomar("B", "p2", "Beto", t.codigo)          # aunque sepa el código
    reloj[0] = 121
    t.tomar("B", "p2", "Beto", t.codigo)
    assert t.es_dueno("B")


def test_regenerar_cambia_el_codigo_y_quita_el_turno():
    t = TurnoKinect(con_codigo=True)
    viejo = t.codigo
    t.tomar("A", "p1", "Ana", viejo)
    nuevos = {t.regenerar_codigo() for _ in range(5)}
    assert t.version_codigo == 5 and t.instantanea() is None
    assert viejo != t.codigo or len(nuevos) > 1
    if viejo != t.codigo:
        with pytest.raises(CodigoIncorrecto):
            t.tomar("A", "p1", "Ana", viejo)


def test_sin_codigo_configurado_no_se_pide():
    t = TurnoKinect(con_codigo=False)
    assert t.codigo is None and t.regenerar_codigo() is None
    t.tomar("A", "p1", "Ana")
    assert t.es_dueno("A")


# ---------------------------------------------------------------- API
@pytest.fixture
def con_codigo(abrir_api, detector):
    def abrir(desde="testclient", **opciones):
        return abrir_api(desde, reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05,
                         kinect_codigo=True, **opciones)
    return abrir


@pytest.fixture
def detector():
    from detector_falso import DetectorFalso
    d = DetectorFalso()
    d.mantener_camara()
    yield d
    d.cerrar()


def test_el_celular_necesita_el_codigo_del_proyector(con_codigo):
    with con_codigo() as (c, s):
        codigo = s.senas.turno.codigo
        r = tomar(c, "A")
        assert r.status_code == 403 and "código" in r.json()["detail"].lower()
        assert tomar(c, "A", "000000" if codigo != "000000" else "111111").status_code == 403
        assert tomar(c, "A", "x" * 40).status_code == 422          # validación amable, en español
        assert "proyector" in tomar(c, "A", "x" * 40).json()["detail"]
        assert tomar(c, "A", codigo).status_code == 200
        assert s.senas.turno.es_dueno("A")
        assert tomar(c, "B", codigo).status_code == 409             # un solo turno a la vez


def test_el_codigo_nunca_va_a_los_celulares(con_codigo):
    with con_codigo() as (c, s):
        codigo = s.senas.turno.codigo
        estado = c.get("/api/estado")
        assert codigo not in estado.text
        assert estado.json()["kinect"]["codigo"] is True
        assert c.get("/api/kinect/codigo").status_code in (401, 403)            # sin token
        assert c.post("/api/kinect/codigo").status_code in (401, 403)
        assert codigo not in c.get("/").text


def test_el_proyector_ve_y_regenera_el_codigo(con_codigo):
    with con_codigo("127.0.0.1") as (pc, s):
        d = pc.get("/api/kinect/codigo", headers=admin(pc)).json()
        assert d == {"activo": True, "codigo": s.senas.turno.codigo, "version": 0}
        tomar(pc, "A", d["codigo"])
        assert s.senas.turno.es_dueno("A")
        nuevo = pc.post("/api/kinect/codigo", headers=admin(pc)).json()
        assert nuevo["version"] == 1 and re.fullmatch(r"\d{6}", nuevo["codigo"])
        assert s.senas.turno.instantanea() is None                              # quien lo tenía lo pierde
        esperar(lambda: pc.get("/api/estado").json()["kinect"]["codigo_version"] == 1)


def test_bloquear_quita_el_turno_tambien_con_codigo(con_codigo):
    with con_codigo("127.0.0.1") as (pc, s):
        pid = pc.post("/api/participante", json={"cliente": "A", "nombre": "Ana"}).json()["pid"]
        assert tomar(pc, "A", s.senas.turno.codigo).status_code == 200
        pc.post(f"/api/participantes/{pid}/bloquear", headers=admin(pc))
        assert s.senas.turno.instantanea() is None
        assert tomar(pc, "A", s.senas.turno.codigo).status_code == 403


def test_sin_codigo_en_el_env_basta_activar_control(abrir_api, detector):
    with abrir_api(reconocedor="kinect", kinect_url=detector.url, kinect_codigo=False) as (c, s):
        assert c.get("/api/estado").json()["kinect"]["codigo"] is False
        assert tomar(c, "A").status_code == 200


def test_adivinar_el_codigo_tiene_limite(con_codigo):
    with con_codigo(lim_kinect_cliente=1000) as (c, s):
        codigos = [str(n).zfill(6) for n in range(40) if str(n).zfill(6) != s.senas.turno.codigo]
        respuestas = [tomar(c, f"c{n}", cod).status_code for n, cod in enumerate(codigos)]
        assert 429 in respuestas and respuestas.count(403) <= 30


# ---------------------------------------------------------------- páginas
def test_la_pestana_tiene_el_diseno_de_camila(carpeta_web):
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    pestana = html[html.index('<section id="tab-kinect"'):html.index("<!-- ===================== MIS MENSAJES")]
    # En su orden: texto grande, estado, acceso con el código y botones en cuadrícula
    orden = ["Tus letras aparecerán aquí", 'id="kinDetalle"', 'id="kinModo"', "Código del PC", "Activar control",
             "Volver a espectador", 'data-kin="iniciar"', 'data-kin="detener"', 'data-kin="espacio"',
             'data-kin="borrar"', 'data-kin="limpiar"', ">Guardar TXT<", ">Leer frase<", ">Detener voz<",
             'data-kin="terminar"', 'id="kinEco"']
    posiciones = [pestana.index(t) for t in orden]
    assert posiciones == sorted(posiciones), orden
    assert 'class="kin-botones"' in pestana and "grid-template-columns" in html
    assert 'inputmode="numeric"' in pestana and 'maxlength="6"' in pestana
    assert "Terminar y decirlo" in pestana


def test_el_proyector_muestra_y_regenera_el_codigo(carpeta_web):
    html = (carpeta_web / "pantalla.html").read_text(encoding="utf-8")
    assert 'id="kinCodigo"' in html and 'id="kinNuevoCodigo"' in html
    assert "/api/kinect/codigo" in html


def test_la_pagina_del_celular_envia_el_codigo(carpeta_web):
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    assert '"/api/kinect/turno", { codigo' in html
    assert "/api/kinect/codigo" not in html          # el celular nunca pide el código


def test_configuracion_de_pruebas_sin_codigo_por_defecto():
    assert configuracion().kinect_codigo is False
```

## `tests/test_kinect_lanzador.py`

```python
"""Arranque del detector y del capturador junto con la plataforma (sin abrir procesos de verdad)."""
import subprocess
import threading
import time

import pytest

from conftest import configuracion, esperar

from pgc.adaptadores.kinect import procesos
from pgc.adaptadores.kinect.procesos import LanzadorKinect


class ProcesoFalso:
    def __init__(self, comando, **kw):
        self.comando, self.kw = comando, kw
        self.terminado = threading.Event()
        self._handle = 0
        self.pid = 4242

    def wait(self, timeout=None):
        if not self.terminado.wait(timeout if timeout is not None else 30):
            raise subprocess.TimeoutExpired(self.comando, timeout)
        return 0

    def poll(self):
        return 0 if self.terminado.is_set() else None

    def terminate(self):
        self.terminado.set()

    kill = terminate


@pytest.fixture
def lanzados(monkeypatch, tmp_path):
    lista = []
    monkeypatch.setattr(procesos, "REGISTROS", tmp_path)
    monkeypatch.setattr(procesos, "puerto_ocupado", lambda url: False)
    monkeypatch.setattr(procesos, "atar_al_proceso_actual", lambda proc: None)

    def popen(comando, **kw):
        p = ProcesoFalso(comando, **kw)
        lista.append(p)
        return p
    return lista, popen, tmp_path


def lanzador(lanzados, python=True, exe=True, listo=lambda url: True, ventanas=None, restos=(), cerrados=None,
             **ajustes):
    lista, popen, carpeta = lanzados
    (carpeta / "python.exe").write_bytes(b"")
    (carpeta / "LSCKinectFramework.exe").write_bytes(b"")
    cfg = configuracion(**{"reconocedor": "kinect", "kinect_lanzar": True, **ajustes})
    log = []
    l = LanzadorKinect(cfg, log.append, popen=popen,
                       pythons=[carpeta / ("python.exe" if python else "no-existe.exe")],
                       exes=[carpeta / ("LSCKinectFramework.exe" if exe else "no-existe.exe")],
                       listo=listo, minimizar=lambda pid: (ventanas if ventanas is not None else [("Kinect", True)]),
                       espera_detector=2.0,
                       # nunca buscar ni cerrar procesos reales desde las pruebas
                       buscar_restos=lambda: list(restos),
                       cerrar=(cerrados.append if cerrados is not None else (lambda pid: None)))
    return l, log


def test_lanza_detector_y_app_del_kinect_y_los_cierra(lanzados):
    lista, _, carpeta = lanzados
    l, log = lanzador(lanzados)
    l.iniciar()
    esperar(lambda: len(lista) == 2)
    detector = next(p for p in lista if "detector_paralelo.py" in " ".join(p.comando))
    assert detector.comando[-1] == str(procesos.DETECTOR)           # envuelve SU server_web_svm.py, sin cambiarlo
    app = next(p for p in lista if p.comando[0].endswith("LSCKinectFramework.exe"))
    assert detector.comando[0] == str(carpeta / "python.exe")
    assert detector.kw["cwd"] == str(procesos.DETECTOR)                 # su carpeta, sus archivos, tal cual
    assert detector.kw["env"]["PYTHONDONTWRITEBYTECODE"] == "1"           # sin __pycache__ en su carpeta
    assert app.kw["startupinfo"] is None or app.kw["startupinfo"].wShowWindow == procesos.MINIMIZADA
    l.detener()
    assert all(p.terminado.is_set() for p in lista)


def test_camara_del_pc_en_lugar_del_kinect(lanzados):
    lista, _, carpeta = lanzados
    l, log = lanzador(lanzados, kinect_capturador="camara_pc", kinect_camara=1)
    l.iniciar()
    esperar(lambda: len(lista) == 2)
    camara = next(p for p in lista if "camara_pc.py" in " ".join(p.comando))
    assert camara.comando[0] == str(carpeta / "python.exe")            # el Python del detector (trae OpenCV)
    assert camara.comando[-2:] == ["--camara", "1"]
    l.detener()


def test_sin_entorno_ni_exe_avisa_y_no_lanza_nada(lanzados):
    lista, _, _ = lanzados
    l, log = lanzador(lanzados, python=False, exe=False)
    l.iniciar()
    esperar(lambda: any("No está la app del Kinect" in x for x in log))
    assert lista == []
    texto = " ".join(log)
    assert "Falta el entorno del detector" in texto and "No está la app del Kinect compilada" in texto


def test_detector_ya_corriendo_no_se_duplica(lanzados, monkeypatch):
    lista, _, _ = lanzados
    monkeypatch.setattr(procesos, "puerto_ocupado", lambda url: True)
    l, log = lanzador(lanzados, kinect_capturador="no")
    l.iniciar()
    assert lista == [] and any("Ya hay un detector" in x for x in log)


@pytest.mark.parametrize("ajustes", [{"kinect_lanzar": False}, {"reconocedor": "simulado"}])
def test_no_lanza_si_no_corresponde(lanzados, ajustes):
    lista, _, _ = lanzados
    l, _ = lanzador(lanzados, **ajustes)
    l.iniciar()
    assert lista == []


def test_el_detector_se_reinicia_si_se_cae(lanzados):
    lista, _, _ = lanzados
    l, log = lanzador(lanzados, kinect_capturador="no")
    l._parar.wait = lambda s: False                        # sin esperar los 3 s entre intentos
    l.iniciar()
    esperar(lambda: len(lista) == 1)
    lista[0].terminate()                                  # se cae
    esperar(lambda: len(lista) == 2)
    assert any("se reinicia" in x for x in log)
    l.detener()


def test_config_del_capturador_se_valida():
    from pgc.config import Config, ErrorConfig, validar
    with pytest.raises(ErrorConfig, match="PGC_KINECT_CAPTURADOR"):
        validar(Config(kinect_capturador="webcam"))
    with pytest.raises(ErrorConfig, match="PGC_KINECT_URL"):          # el detector siempre en este PC
        validar(Config(kinect_url="http://192.168.0.5:8765"))


def test_la_app_espera_a_que_el_detector_responda(lanzados):
    """Antes se abrían a la vez y la app mandaba imágenes ~4,5 s a un detector que aún no existía."""
    lista, _, _ = lanzados
    listo = threading.Event()
    l, log = lanzador(lanzados, listo=lambda url: listo.is_set())
    l.iniciar()
    esperar(lambda: len(lista) == 1)                     # solo el detector
    time.sleep(0.6)
    assert len(lista) == 1 and "detector_paralelo.py" in " ".join(lista[0].comando)
    listo.set()                                          # el detector ya responde
    esperar(lambda: len(lista) == 2)
    assert lista[1].comando[0].endswith("LSCKinectFramework.exe")
    assert any("Detector listo en" in x for x in log)
    l.detener()


def test_si_el_detector_no_responde_la_app_se_abre_igual(lanzados):
    lista, _, _ = lanzados
    l, log = lanzador(lanzados, listo=lambda url: False)          # espera_detector = 2 s en la prueba
    l.iniciar()
    esperar(lambda: len(lista) == 2, timeout=6)
    assert any("no respondió en 2 s" in x for x in log)
    l.detener()


def test_si_la_ventana_se_abre_en_grande_se_minimiza(lanzados):
    lista, _, _ = lanzados
    l, log = lanzador(lanzados, kinect_capturador="kinect", ventanas=[("Kinect - Ejemplos de LSC", False)])
    l.iniciar()
    esperar(lambda: any("se minimizó" in x for x in log))
    l.detener()


def test_se_puede_volver_a_su_servidor_original(lanzados):
    lista, _, _ = lanzados
    l, _ = lanzador(lanzados, kinect_capturador="no", kinect_detector_paralelo=False)
    l.iniciar()
    esperar(lambda: len(lista) == 1)
    assert lista[0].comando[-1] == "server_web_svm.py"
    l.detener()


def test_cierra_los_restos_antes_de_lanzar(lanzados):
    lista, _, _ = lanzados
    cerrados = []
    restos = [(111, "python.exe", "python.exe -u detector_paralelo.py carpeta"),
              (112, "python.exe", "python.exe -u server_web_svm.py"),
              (113, "LSCKinectFramework.exe", "LSCKinectFramework.exe")]
    l, log = lanzador(lanzados, restos=restos, cerrados=cerrados)
    l.iniciar()
    assert cerrados == [111, 112, 113]                      # se cierran ANTES de lanzar los nuevos
    assert any("restos de una ejecución anterior: 1 app del Kinect, 2 detector" in x for x in log)
    esperar(lambda: len(lista) == 2)                         # y luego uno de cada uno
    l.detener()


def test_tipos_de_resto():
    assert procesos.tipo_de_resto("LSCKinectFramework.exe", "") == "app del Kinect"
    assert procesos.tipo_de_resto("python.exe", "python camara_pc.py --camara 0") == "cámara del PC"
    assert procesos.tipo_de_resto("python.exe", "python -u detector_paralelo.py carpeta") == "detector"


def test_no_arranca_una_segunda_plataforma(monkeypatch, capsys):
    from pgc import arranque
    monkeypatch.setattr(arranque, "puerto_en_uso", lambda puerto: True)
    lanzados = []
    monkeypatch.setattr(arranque, "crear_lanzador", lambda cfg, log: lanzados.append(1))
    assert arranque.main(["--simular", "--no-abrir", "--puerto-web", "8799"]) == 3
    assert lanzados == []                                    # no se tocó nada de la otra plataforma
    assert "Ya hay una plataforma corriendo" in capsys.readouterr().err


def test_buscar_restos_cuenta_el_lanzador_del_entorno_y_su_hijo_como_uno(monkeypatch):
    import json
    import types
    datos = [{"ProcessId": 10, "ParentProcessId": 1, "Name": "python.exe", "CommandLine": "python -u detector_paralelo.py c"},
             {"ProcessId": 11, "ParentProcessId": 10, "Name": "python.exe", "CommandLine": "python -u detector_paralelo.py c"},
             {"ProcessId": 12, "ParentProcessId": 1, "Name": "LSCKinectFramework.exe", "CommandLine": "x"},
             {"ProcessId": 13, "ParentProcessId": 1, "Name": "python.exe", "CommandLine": "python -m pgc"}]
    monkeypatch.setattr(procesos.os, "name", "nt")
    monkeypatch.setattr(procesos.subprocess, "run", lambda *a, **k: types.SimpleNamespace(stdout=json.dumps(datos)))
    assert [r[0] for r in procesos.buscar_restos()] == [10, 12]          # ni el hijo 11 ni la plataforma 13
```

## `tests/test_kinect_paginas.py`

```python
"""Pestaña Kinect del celular y vista Kinect del proyector (contenido de las páginas)."""
import importlib
import re
import sys

import pytest

from conftest import RAIZ


def test_el_celular_ya_no_dice_siguiente_fase(carpeta_web):
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    assert "siguiente fase" not in html.lower()
    for id_ in ("kinEstado", "kinTexto", "kinDetalle", "kinTomar", "kinSoltar", "kinOcupado", "avisoKinect",
                "kinModo", "kinGuardar", "kinLeer", "kinCallar", "kinVoz"):
        assert f'id="{id_}"' in html, id_
    for accion in ("iniciar", "detener", "espacio", "borrar", "limpiar", "terminar"):   # los controles que ella diseñó
        assert f'data-kin="{accion}"' in html, accion
    assert "Kinect no conectado" in html
    # Sus funciones y mensajes (pestaña de iniciar_pgc_integrado.py, incorporada a movil.html)
    for texto in ("Activar control", "Volver a espectador", "Guardar TXT", "Leer frase", "Detener voz",
                  "Modo espectador.", "Control del teléfono activo", "Leyendo...", "Lectura terminada.",
                  "Lectura detenida.", "Lectura detenida o audio no disponible.", "No hay una voz en español disponible",
                  'download = "texto_lsc.txt"', "speechSynthesis"):
        assert texto in html, texto


def test_guardar_y_leer_no_dependen_del_turno(carpeta_web):
    """Los espectadores también guardan y leen: esos botones no son controles del deletreo (data-kin),
    que son los únicos que el turno apaga."""
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    botones = html[html.index('<div id="kinMios"'):html.index('<p id="kinVoz"')]
    for id_ in ("kinGuardar", "kinLeer", "kinCallar"):
        boton = re.search(rf'<button id="{id_}"[^>]*>', botones).group(0)
        assert "data-kin" not in boton, id_
    assert 'data-kin="limpiar"' in botones
    assert 'querySelectorAll("[data-kin]")' in html and "!puede" in html


@pytest.mark.parametrize("pagina", ["movil.html", "pantalla.html"])
def test_hidden_siempre_oculta(carpeta_web, pagina):
    """El error de «Volver a espectador»: .btn { display: flex } le ganaba al atributo hidden."""
    assert "[hidden] { display: none !important; }" in (carpeta_web / pagina).read_text(encoding="utf-8") or \
        ".oculto, [hidden] { display: none !important; }" in (carpeta_web / pagina).read_text(encoding="utf-8")


def test_los_celulares_no_consultan_el_kinect(carpeta_web):
    """Todo llega por el WebSocket: la página del celular no consulta rutas del Kinect ni del detector."""
    html = (carpeta_web / "movil.html").read_text(encoding="utf-8")
    assert "/api/deletreo" not in html and "8765" not in html and "/api/kinect/imagen" not in html


def test_el_proyector_tiene_la_vista_kinect(carpeta_web):
    html = (carpeta_web / "pantalla.html").read_text(encoding="utf-8")
    for id_ in ("vKinect", "kinTexto", "kinCamara", "kinFrase", "kinTira", "ctrlKinect", "kinEco", "kinLiberar"):
        assert f'id="{id_}"' in html, id_
    assert "Próxima fase" not in html


def test_el_lanzador_antiguo_aun_arma_su_pagina():
    """iniciar_pgc_integrado.py (obsoleto, de Camila) busca marcas en movil.html: no se le rompe nada."""
    sys.path.insert(0, str(RAIZ))
    modulo = importlib.import_module("iniciar_pgc_integrado")
    html = modulo.construir_html()
    assert "De tus manos al texto" in html and 'id="codigoControlKinect"' in html     # su panel reemplazó al mío
    assert 'id="kinTomar"' not in html
```

## `tests/test_kinect_plataforma.py`

```python
"""Kinect integrado en la plataforma: turno, controles, imagen solo en el PC, voz, eco y varios celulares."""
import time
from contextlib import ExitStack

import pytest

from conftest import admin, esperar
from detector_falso import JPEG, DetectorFalso

PC = "127.0.0.1"
TUNEL = {"CF-Connecting-IP": "181.50.1.2"}       # así llega cloudflared: desde 127.0.0.1 con este encabezado


class SintetizadorFalso:
    estado = "listo"

    def __init__(self):
        self.dichas = []

    def cargar_en_segundo_plano(self):
        pass

    def decir(self, texto):
        self.dichas.append(texto)


@pytest.fixture
def detector():
    d = DetectorFalso()
    d.mantener_camara()
    yield d
    d.cerrar()


@pytest.fixture
def con_kinect(abrir_api, detector):
    """API con el ReconocedorKinect real apuntando al detector falso."""
    def abrir(desde="testclient", **opciones):
        return abrir_api(desde, reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05, **opciones)
    return abrir


SECRETO = "celular-secreto-de-ana"


def registrar(c, cliente, nombre=None):
    return c.post("/api/participante", json={"cliente": cliente, "nombre": nombre}).json()


def control(c, accion, cliente=None, **kw):
    return c.post("/api/kinect/control", json={"accion": accion, "cliente": cliente}, **kw)


# ---------------------------------------------------------------- turno: un jurado a la vez
def test_un_solo_jurado_controla_el_kinect(con_kinect):
    with con_kinect() as (c, s):
        registrar(c, SECRETO, "Ana")
        registrar(c, "B", "Beto")
        assert control(c, "iniciar", SECRETO).status_code == 403          # sin turno no hay controles
        assert c.post("/api/kinect/turno", json={"cliente": SECRETO}).status_code == 200
        r = c.post("/api/kinect/turno", json={"cliente": "B"})
        assert r.status_code == 409 and "Ana" in r.json()["detail"]
        assert control(c, "iniciar", SECRETO).status_code == 200
        assert control(c, "detener", "B").status_code == 403
        turno = c.get("/api/estado").json()["kinect"]["turno"]
        assert turno["nombre"] == "Ana" and turno["pid"] and SECRETO not in repr(turno)   # nunca el id privado
        assert c.post("/api/kinect/turno/soltar", json={"cliente": SECRETO}).status_code == 200
        assert c.post("/api/kinect/turno", json={"cliente": "B"}).status_code == 200


def test_el_turno_se_libera_solo_por_inactividad(con_kinect):
    with con_kinect() as (c, s):
        reloj = [1000.0]
        s.senas.turno._reloj = lambda: reloj[0]
        c.post("/api/kinect/turno", json={"cliente": "A"})
        reloj[0] += 60
        assert control(c, "iniciar", "A").status_code == 200           # usarlo reinicia la espera
        reloj[0] += 100
        assert c.post("/api/kinect/turno", json={"cliente": "B"}).status_code == 409
        reloj[0] += 21                                                 # 121 s sin usarlo
        esperar(lambda: c.get("/api/estado").json()["kinect"]["turno"] is None)     # lo libera el hilo de señas
        assert c.post("/api/kinect/turno", json={"cliente": "B"}).status_code == 200


def test_bloquear_quita_el_turno(con_kinect):
    with con_kinect(PC) as (pc, s2):
        pid = registrar(pc, "A", "Ana")["pid"]
        pc.post("/api/kinect/turno", json={"cliente": "A"})
        assert pc.post(f"/api/participantes/{pid}/bloquear", headers=admin(pc)).status_code == 200
        assert s2.senas.turno.instantanea() is None
        r = pc.post("/api/kinect/turno", json={"cliente": "A"})
        assert r.status_code == 403 and "pausó" in r.json()["detail"]


def test_el_presentador_controla_siempre_y_libera_el_turno(con_kinect):
    with con_kinect(PC) as (c, s):
        c.post("/api/kinect/turno", json={"cliente": "A"})
        assert control(c, "iniciar", headers=admin(c)).status_code == 200      # aunque A tenga el turno
        assert control(c, "iniciar").status_code == 403                         # sin token, no
        assert c.post("/api/kinect/liberar").status_code == 403
        assert c.post("/api/kinect/liberar", headers=admin(c)).status_code == 200
        assert s.senas.turno.instantanea() is None


def test_controles_con_detector_caido_o_sin_controles(abrir_api, con_kinect, detector):
    with abrir_api(PC) as (c, s):                                   # reconocedor simulado: no tiene controles
        assert control(c, "iniciar", headers=admin(c)).status_code == 409
    detector.cerrar()
    with con_kinect(PC) as (c, s):
        r = control(c, "iniciar", headers=admin(c))
        assert r.status_code == 503 and r.json()["detail"] == "Kinect no conectado"
        esperar(lambda: c.get("/api/estado").json()["kinect"]["detalle"] == "Kinect no conectado")


# ---------------------------------------------------------------- imagen: solo el PC del proyector
def test_imagen_solo_en_el_pc_con_token(con_kinect):
    with con_kinect(PC) as (c, s):
        esperar(lambda: s.senas.reconocedor.camara)
        esperar(lambda: c.get("/api/kinect/imagen", headers=admin(c)).status_code == 200)
        r = c.get("/api/kinect/imagen", headers=admin(c))
        assert r.content.startswith(JPEG) and r.headers["content-type"] == "image/jpeg"
        assert c.get("/api/kinect/imagen").status_code == 403                        # PC sin token
        assert c.get("/api/kinect/imagen", headers={**admin(c), **TUNEL}).status_code == 403   # por el túnel
    with con_kinect() as (c, s):
        assert c.get("/api/kinect/imagen").status_code == 403                        # un celular


# ---------------------------------------------------------------- en vivo, voz y eco
def test_texto_en_vivo_voz_y_eco(con_kinect, detector):
    with con_kinect(PC) as (c, s):
        s.voz_salida = voz = SintetizadorFalso()
        esperar(lambda: s.senas.reconocedor.camara)
        control(c, "iniciar", headers=admin(c))
        with c.websocket_connect("/ws") as ws:
            for letra in "HOGA":
                detector.reconocer(letra)
            while True:                                            # el celular lo ve por el WebSocket
                d = ws.receive_json()
                if d.get("tipo") == "estado" and d["kinect"]["texto"] == "hoga":
                    break
        assert d["kinect"]["activo"] and d["kinect"]["camara"] and d["kinect"]["estado"] == "listo"
        # Sin eco: se dice en voz alta y no va a la mano
        control(c, "terminar", headers=admin(c))
        esperar(lambda: voz.dichas == ["hoga"])
        assert s.instantanea()["kinect"]["frases"] == ["hoga"] and s.cola == [] and s.actual is None
        # Con eco: además, la mano la deletrea (la G y la H se muestran como no disponibles)
        assert c.post("/api/kinect/eco", json={"activo": True}, headers=admin(c)).json() == {"eco": True}
        for letra in "HOGA":
            detector.reconocer(letra)
        esperar(lambda: s.senas.texto == "hoga")
        control(c, "terminar", headers=admin(c))
        esperar(lambda: voz.dichas == ["hoga", "hoga"])
        esperar(lambda: s.historial and s.historial[0]["nombre"] == "Kinect", timeout=10)
        tipos = [(p["c"], p["tipo"]) for p in s.historial[0]["pasos"]]
        assert tipos == [("H", "nd"), ("O", "ok"), ("G", "nd"), ("A", "ok")]


def test_eco_solo_el_presentador(con_kinect):
    with con_kinect() as (c, s):
        assert c.post("/api/kinect/eco", json={"activo": True}).status_code == 403
    with con_kinect(PC) as (c, s):
        assert c.post("/api/kinect/eco", json={"activo": True}, headers={**admin(c), **TUNEL}).status_code == 403


def test_eco_sin_letras_posibles_no_tumba_nada(crear_sistema, registro):
    s = crear_sistema(kinect_eco=True)
    s._frase_reconocida("gh")
    assert s.cola == [] and any("Eco: la frase no va a la mano" in l for l in registro)


# ---------------------------------------------------------------- varios celulares (límites)
def test_muchos_celulares_con_la_pestana_kinect_no_cargan_al_detector(con_kinect, detector):
    """Los celulares no consultan nada: el servidor lee el detector a ritmo fijo y lo reparte por el WebSocket."""
    with con_kinect() as (c, s):                    # todos "desde el mismo WiFi": una sola IP
        esperar(lambda: detector.consultas > 3)
        antes, t0 = detector.consultas, time.monotonic()
        time.sleep(1)
        solo = (detector.consultas - antes) / (time.monotonic() - t0)
        with ExitStack() as pila:
            conexiones = [pila.enter_context(c.websocket_connect("/ws")) for _ in range(30)]
            for ws in conexiones:
                assert ws.receive_json()["tipo"] == "estado"          # aceptadas (antes el límite era 8 por IP)
            antes, t0 = detector.consultas, time.monotonic()
            time.sleep(1)
            con_30 = (detector.consultas - antes) / (time.monotonic() - t0)
        assert con_30 < solo * 1.5 + 5, (solo, con_30)              # no crece con el número de celulares


def test_limpiar_borra_todo_y_solo_con_turno(con_kinect, detector):
    with con_kinect() as (c, s):
        esperar(lambda: s.senas.reconocedor.camara)
        c.post("/api/kinect/turno", json={"cliente": "A"})
        assert control(c, "iniciar", "A").status_code == 200
        for letra in "HOLA":
            detector.reconocer(letra)
        esperar(lambda: s.senas.texto == "hola")
        assert control(c, "limpiar", "B").status_code == 403          # un espectador no limpia
        assert control(c, "limpiar", "A").status_code == 200
        assert detector.texto == "" and detector.ordenes[-1] == "clear"
        esperar(lambda: s.senas.texto == "" and c.get("/api/estado").json()["kinect"]["texto"] == "")
        assert s.senas.frases == []                                    # limpiar no es terminar: no se dice nada


def test_la_imagen_siguiente_llega_apenas_existe(con_kinect, detector):
    """?despues=N: el proyector recibe cada cuadro una sola vez, sin pedirlo una y otra vez."""
    with con_kinect(PC) as (c, s):
        detector.mantener_camara(por_segundo=20)
        esperar(lambda: c.get("/api/kinect/imagen", headers=admin(c)).status_code == 200)
        cuadros, t0 = [], time.monotonic()
        ultimo = int(c.get("/api/kinect/imagen", headers=admin(c)).headers["X-Kinect-Cuadro"])
        while time.monotonic() - t0 < 1.0:
            r = c.get(f"/api/kinect/imagen?despues={ultimo}", headers=admin(c))
            ultimo = int(r.headers["X-Kinect-Cuadro"])
            cuadros.append(ultimo)
        assert len(cuadros) == len(set(cuadros))                # ningún cuadro repetido
        assert len(cuadros) >= 10, len(cuadros)                 # la prueba exige 10/s; en Edge se mide la cifra real
        assert float(r.headers["X-Kinect-Desfase-Ms"]) < 100    # estado e imagen del mismo momento
```

## `tests/test_mano_ble.py`

```python
"""Mano por Bluetooth y respaldo por USB, contra el main.py REAL de la placa (en un hilo, radio BLE falsa)."""
import time
import types

import pytest

from conftest import esperar
from esp32_falso import TOKEN, Esp32Falso
from test_mano_serial import SerialFalso

from pgc.adaptadores.mano_ble import ManoBLE
from pgc.adaptadores.mano_respaldo import Mano

RESPUESTAS_USB = {"reset": ["reset_ok"], "a": ["gesto_a_ok"], "b": ["gesto_b_ok"]}


@pytest.fixture
def esp():
    e = Esp32Falso()
    yield e
    e.detener()


@pytest.fixture
def log():
    return []


def ble(esp, log, token=TOKEN, **kw):
    kw.setdefault("timeout_letra", 1.0)
    kw.setdefault("tiempo_busqueda", 0.5)
    return ManoBLE(esp.nombre, token, log=log.append, bleak=esp.bleak, **kw)


def serial_falso(respuestas=RESPUESTAS_USB, puertos=(("COM5", 0x303A),)):
    falso = SerialFalso(respuestas)
    lista = [types.SimpleNamespace(device=d, vid=v) for d, v in puertos]
    return falso, types.SimpleNamespace(
        Serial=lambda: falso,
        tools=types.SimpleNamespace(list_ports=types.SimpleNamespace(comports=lambda: lista)))


def mano(esp, log, modo="auto", usb=True, **kw_ble):
    falso, modulo = serial_falso(puertos=(("COM5", 0x303A),) if usb else ())
    m = Mano(log=log.append, modo=modo, ble=ble(esp, log, **kw_ble), modulo_serial=modulo,
             dormir=lambda s: None, timeout_letra=0.3)
    return m, falso


# ---------------------------------------------------------------- conexión
def test_conexion_por_bluetooth(esp, log):
    b = ble(esp, log)
    assert b.conectar() is True
    assert b.conectada and b.puerto == "Mano-LSC" and b.medio == "ble"
    assert b.letras is None                                     # el firmware no las informa
    assert b.hacer("a") is True and b.hacer("g") is False      # g: comando_no_reconocido
    assert b.hacer("reset") is True and b.latido() is True
    assert esp.ordenes == ["reset", "a", "g", "reset"]          # el latido no manda nada
    assert log[-1] == "[mano] Conectada por Bluetooth a Mano-LSC"
    assert TOKEN not in "\n".join(log)                          # el token nunca va al log
    b.cerrar()


def test_mueve_igual_que_el_original(esp, log):
    from arnes_firmware import ORIGINAL, correr
    b = ble(esp, log)
    b.conectar()
    for letra in "calle":
        b.hacer(letra)
    b.hacer("reset")
    reg_o, _ = correr(ORIGINAL, ["reset"] + list("calle") + ["reset"])
    assert list(esp.registro) == list(reg_o)
    b.cerrar()


def test_token_incorrecto(esp, log):
    b = ble(esp, log, token="otro-token-de-veinte-caracteres")
    assert b.conectar() is False and not b.conectada
    assert "rechazó el token" in log[-1]
    assert esp.ordenes == []                                    # no ejecutó nada
    assert any("token incorrecto" in l for l in esp.log)


def test_sin_placa(esp, log):
    esp.apagar()
    b = ble(esp, log)
    assert b.conectar() is False
    assert "no disponible" in log[-1] and "no se encontró" in log[-1]


def test_sin_bluetooth_en_el_pc(log):
    class Escaner:
        @staticmethod
        async def find_device_by_name(nombre, timeout=5.0):
            raise OSError("Bluetooth apagado")
    b = ManoBLE("Mano-LSC", TOKEN, log=log.append, bleak=types.SimpleNamespace(Escaner=Escaner, Cliente=None))
    assert b.conectar() is False
    assert "Bluetooth apagado" in log[-1]
    BleakBluetoothNotAvailableError = type("BleakBluetoothNotAvailableError", (Exception,), {})

    class EscanerApagado:
        @staticmethod
        async def find_device_by_name(nombre, timeout=5.0):
            raise BleakBluetoothNotAvailableError("Bluetooth radio is not powered on.", 3)
    b = ManoBLE("Mano-LSC", TOKEN, log=log.append, bleak=types.SimpleNamespace(Escaner=EscanerApagado, Cliente=None))
    b.conectar()
    assert "el Bluetooth del PC está apagado" in log[-1]


def test_no_llena_el_log_si_la_placa_esta_apagada(esp, log):
    esp.apagar()
    b = ble(esp, log, tiempo_busqueda=0.1, reintento=0)
    for _ in range(3):
        b.conectar()
    assert len(log) == 1


def test_espera_entre_intentos(esp, log):
    esp.apagar()
    reloj = [100.0]
    b = ble(esp, log, tiempo_busqueda=0.1, reintento=10, reloj=lambda: reloj[0])
    assert b.puede_intentar()
    b.conectar()
    assert not b.puede_intentar()
    reloj[0] += 10
    assert b.puede_intentar()


# ---------------------------------------------------------------- fallas
def test_timeout_de_una_letra(esp, log):
    b = ble(esp, log, timeout_letra=0.3)
    b.conectar()
    esp.callada = True                                          # la placa se colgó
    t0 = time.monotonic()
    assert b.hacer("a") is False
    assert 0.25 < time.monotonic() - t0 < 2
    assert "timeout" in log[-1]
    assert not b.conectada                                      # sin "ping", un timeout la da por perdida
    esp.callada = False


def test_perdida_del_bluetooth(esp, log):
    b = ble(esp, log)
    b.conectar()
    esp.apagar()
    assert b.latido() is False                                  # se nota sin enviar nada
    assert "Se perdió la conexión Bluetooth" in log[-1]
    assert b.hacer("a") is False and not b.conectada


def test_reconecta_cuando_vuelve(esp, log):
    b = ble(esp, log)
    b.conectar()
    esp.apagar()
    b.latido()
    esp.encender()
    assert b.conectar() is True and b.hacer("b") is True


# ---------------------------------------------------------------- respaldo Bluetooth → USB
def test_auto_prefiere_bluetooth(esp, log):
    m, falso = mano(esp, log)
    assert m.conectar() is True
    assert (m.modo, m.medio, m.puerto) == ("real", "ble", "Mano-LSC")
    assert falso.escrito == []                                  # el USB ni se abrió
    m.cerrar()


def test_cambio_a_usb_sin_perder_la_letra(esp, log):
    m, falso = mano(esp, log)
    m.conectar()
    assert m.hacer("a") is True
    esp.apagar()                                                # se pierde el Bluetooth
    assert m.hacer("b") is True                                 # la letra sale por USB
    assert (m.medio, m.puerto) == ("usb", "COM5")
    assert falso.escrito[-1] == b"b\n"
    assert "Respaldo: ahora por USB" in "\n".join(log)


def test_caida_entre_mensajes_se_detecta_con_el_latido(esp, log):
    m, _ = mano(esp, log)
    m.conectar()
    esp.apagar()
    assert m.revisar() is True                                  # el latido falla → USB
    assert m.medio == "usb"


def test_vuelve_al_bluetooth_cuando_reaparece(esp, log):
    m, falso = mano(esp, log, reintento=0)
    m.conectar()
    esp.apagar()
    m.hacer("a")
    assert m.medio == "usb"
    esp.encender()
    esperar(lambda: m.revisar() or m.medio == "ble", timeout=5)
    assert m.medio == "ble"
    assert falso.abierto is False                               # el USB se soltó
    assert "Cambio a Bluetooth" in "\n".join(log)
    m.cerrar()


def test_sin_bluetooth_ni_usb_queda_simulada(esp, log):
    m, _ = mano(esp, log, usb=False)
    m.conectar()
    esp.apagar()
    assert m.hacer("a") is True                                 # bleak avisó la caída: ya va simulada
    assert (m.modo, m.medio) == ("simulada", None)
    assert m.hacer("b") is True                                 # las siguientes, simuladas


def test_modo_usb_ignora_el_bluetooth(esp, log):
    m, _ = mano(esp, log, modo="usb")
    m.conectar()
    assert m.medio == "usb" and esp.ordenes == []


def test_modo_ble_nunca_usa_usb(esp, log):
    m, falso = mano(esp, log, modo="ble")
    m.conectar()
    esp.apagar()
    m.hacer("a")
    assert m.modo == "simulada" and falso.escrito == []


def test_reconectar_desde_la_pantalla(esp, log):
    m, _ = mano(esp, log)
    m.conectar()
    m.cerrar()
    time.sleep(0.05)
    assert m.conectar() is True and m.medio == "ble"
    m.cerrar()


# ---------------------------------------------------------------- de punta a punta
def test_de_punta_a_punta_por_bluetooth(esp, log):
    """Celular → API → cola → Deletreador → ManoBLE → main.py real de la placa."""
    from fastapi.testclient import TestClient
    from conftest import IP_LOCAL, TranscriptorFalso, TunelFalso, configuracion
    from pgc import arranque
    from pgc.api.app import crear_app

    def crear_mano(cfg, log_):
        return Mano(log=log_, modo="ble", ble=ble(esp, log), timeout_letra=1.0)

    sistema = arranque.construir_sistema(
        configuracion(simular=False, mano="ble", mano_ble_token=TOKEN), log=log.append, crear_mano=crear_mano,
        crear_transcriptor=lambda cfg, l, al: TranscriptorFalso(l, al),
        crear_tunel=lambda cfg, l, al: TunelFalso(cfg.puerto_web, l, al), ip_local=lambda: IP_LOCAL)
    with TestClient(crear_app(sistema, abrir_navegador=lambda url: None)) as cliente:
        esperar(lambda: cliente.get("/api/estado").json()["mano"]["modo"] == "real", timeout=5)
        mano_ = cliente.get("/api/estado").json()["mano"]
        assert (mano_["medio"], mano_["puerto"]) == ("ble", "Mano-LSC")
        antes = len(esp.ordenes)
        assert cliente.post("/api/mensaje", json={"texto": "calle", "cliente": "c1"}).status_code == 200
        esperado = "c a l reset l e reset".split()               # regla de repetidas: abrir entre las dos l
        esperar(lambda: esp.ordenes[antes:] == esperado, timeout=10)
    sistema.mano.cerrar()


# ---------------------------------------------------------------- configuración
def test_configuracion_de_la_mano():
    from conftest import configuracion
    from pgc import arranque, config
    cfg = configuracion(simular=False, mano_ble_token="t" * 20, mano_ble_nombre="Mano-2")
    m = arranque.crear_mano(cfg, lambda x: None)
    assert m.ble is not None and m.ble.nombre == "Mano-2" and m.modo_config == "auto"
    assert arranque.crear_mano(configuracion(simular=False), lambda x: None).ble is None   # sin token: solo USB
    with pytest.raises(config.ErrorConfig, match="necesita PGC_MANO_BLE_TOKEN"):
        config.cargar([], {"PGC_MANO": "ble"}, "no-existe.env")
    with pytest.raises(config.ErrorConfig, match="muy corto"):
        config.cargar([], {"PGC_MANO_BLE_TOKEN": "corto"}, "no-existe.env")
    with pytest.raises(config.ErrorConfig, match="PGC_MANO debe ser"):
        config.cargar([], {"PGC_MANO": "wifi"}, "no-existe.env")
```

## `tests/test_mano_serial.py`

```python
"""Protocolo serial con el ESP32 (caracterización de mano_serial con un puerto falso)."""
import time
import types
from collections import deque

import pytest


class SerialFalso:
    """Imita serial.Serial: responde según `respuestas[orden]` (lista de líneas)."""

    def __init__(self, respuestas, falla_al_escribir=False):
        self.respuestas = respuestas
        self.falla_al_escribir = falla_al_escribir
        self.escrito = []
        self.entrada = deque()
        self.abierto = False
        self.reinicios = 0
        self.port = self.baudrate = self.timeout = None
        self.dtr = self.rts = None
        self.dtr_al_abrir = self.rts_al_abrir = None

    def open(self):
        self.abierto = True
        self.dtr_al_abrir, self.rts_al_abrir = self.dtr, self.rts

    def close(self):
        self.abierto = False

    def reset_input_buffer(self):
        self.entrada.clear()

    def write(self, datos):
        if self.falla_al_escribir:
            raise OSError("el puerto desapareció")
        self.escrito.append(datos)
        if datos == b"\x03\x04":
            self.reinicios += 1
            return
        orden = datos.decode().strip()
        r = self.respuestas.get(orden, [])
        self.entrada.extend(r(self) if callable(r) else r)

    def readline(self):
        if self.entrada:
            return (self.entrada.popleft() + "\r\n").encode()
        return b""


@pytest.fixture
def puerto(monkeypatch, modulo_mano):
    """Reemplaza pyserial por un falso; devuelve una función para configurarlo."""
    monkeypatch.setattr(modulo_mano, "time", types.SimpleNamespace(sleep=lambda s: None, time=time.time))
    monkeypatch.setattr(modulo_mano, "TIMEOUT_LETRA", 0.05)
    estado = {}

    def configurar(respuestas, puertos=(), **kw):
        falso = SerialFalso(respuestas, **kw)
        lista = [types.SimpleNamespace(device=d, vid=v) for d, v in puertos]
        modulo = types.SimpleNamespace(
            Serial=lambda: falso,
            tools=types.SimpleNamespace(list_ports=types.SimpleNamespace(comports=lambda: lista)))
        monkeypatch.setattr(modulo_mano, "serial", modulo)
        estado["falso"] = falso
        return falso
    return configurar


def nueva_mano(modulo_mano, **kw):
    log = []
    return modulo_mano.Mano(log=log.append, **kw), log


# Respuestas del firmware = las del código original del autor (sin "ping" ni "letras")
RESPUESTAS_OK = {"reset": ["reset_ok"], "a": ["gesto_a_ok"], "b": ["gesto_b_ok"]}


def test_buscar_puerto_por_vid(puerto, modulo_mano):
    puerto({}, puertos=[("COM1", None), ("COM3", 0x1234), ("COM7", 0x303A)])
    assert modulo_mano.buscar_puerto() == "COM7"
    for vid in (0x1A86, 0x10C4):
        puerto({}, puertos=[("COM4", vid)])
        assert modulo_mano.buscar_puerto() == "COM4"
    puerto({}, puertos=[("COM1", 0x1234)])
    assert modulo_mano.buscar_puerto() is None


def test_conectar(puerto, modulo_mano):
    s = puerto(RESPUESTAS_OK)
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    assert mano.conectar() is True
    assert (mano.conectada, mano.modo, mano.puerto) == (True, "real", "COM9")
    assert mano.letras is None                                       # el firmware no las informa
    assert (s.port, s.baudrate) == ("COM9", 115200)
    assert (s.dtr_al_abrir, s.rts_al_abrir) == (False, False)          # no reinicia la placa
    assert s.escrito == [b"reset\n"]                                   # comprobación sin "ping"
    assert log[-1] == "[mano] Conectada por USB en COM9"


def test_conectar_tras_reinicio_suave(puerto, modulo_mano):
    s = puerto({"reset": lambda falso: ["reset_ok"] if falso.reinicios else []})
    mano, _ = nueva_mano(modulo_mano, puerto="COM9")
    assert mano.conectar() is True
    assert s.escrito == [b"reset\n", b"\x03\x04", b"reset\n"]


def test_nunca_manda_ping_ni_letras(puerto, modulo_mano):
    """El código original deletrearía "ping" o "letras" como palabras: el PC no los envía."""
    s = puerto(RESPUESTAS_OK)
    mano, _ = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    mano.hacer("a")
    mano.latido()
    mano.reset()
    assert all(len(o.strip()) == 1 or o in (b"reset\n", b"\x03\x04") for o in s.escrito)


def test_conectar_sin_respuesta(puerto, modulo_mano):
    s = puerto({})
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    assert mano.conectar() is False
    assert (mano.conectada, mano.modo) == (False, "simulada")
    assert s.abierto is False
    assert "el ESP32 no responde" in log[-1]


def test_conectar_sin_esp32(puerto, modulo_mano):
    puerto({}, puertos=[])
    mano, log = nueva_mano(modulo_mano)
    assert mano.conectar() is False
    assert log == ["[mano] No se encontró el ESP32 -> modo simulado"]


def test_modo_simulado(puerto, modulo_mano):
    puerto(RESPUESTAS_OK, puertos=[("COM7", 0x303A)])
    mano, _ = nueva_mano(modulo_mano, simular=True)
    assert mano.conectar() is False
    assert mano.modo == "simulada"
    assert mano.hacer("a") is True and mano.reset() is True


@pytest.mark.parametrize("respuesta, esperado", [
    (["gesto_a_ok"], True),
    (["comando_no_reconocido"], False),
    (["Mano lista.", "GESTO_A_OK"], True),   # ignora líneas ajenas; no distingue mayúsculas
    (["gesto_b_ok", "gesto_a_ok"], True),    # la respuesta de otra letra no cuenta
    ([], False),                             # sin respuesta: timeout
])
def test_hacer_letra(puerto, modulo_mano, respuesta, esperado):
    s = puerto({**RESPUESTAS_OK, "a": respuesta})
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    assert mano.hacer("a") is esperado
    assert s.escrito[-1] == b"a\n"
    if not respuesta:
        assert log[-1] == "[mano] Sin confirmación para 'a' (timeout)"
        assert mano.conectada                 # un timeout no desconecta


def test_errores_del_firmware_se_registran(puerto, modulo_mano):
    puerto({**RESPUESTAS_OK, "a": ["error:algo falló", "gesto_a_ok"]})
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    assert mano.hacer("a") is True
    assert "[mano] error:algo falló" in log


def test_reset(puerto, modulo_mano):
    s = puerto(RESPUESTAS_OK)
    mano, _ = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    assert mano.reset() is True
    assert s.escrito[-1] == b"reset\n"


def test_perder_la_conexion(puerto, modulo_mano):
    s = puerto(RESPUESTAS_OK)
    mano, log = nueva_mano(modulo_mano, puerto="COM9")
    mano.conectar()
    s.falla_al_escribir = True
    assert mano.hacer("a") is False
    assert mano.conectada is False and mano.modo == "simulada"
    assert log[-1].startswith("[mano] Se perdió la conexión")
```

## `tests/test_moderacion.py`

```python
"""Filtro de palabras ofensivas (pgc.dominio.moderacion)."""
import pytest

from pgc.dominio.moderacion import Moderador, cargar_moderador


@pytest.fixture(scope="module")
def mod():
    return cargar_moderador()


@pytest.mark.parametrize("texto", [
    "gonorrea", "Gonorreaaa", "GONORREA!!", "hijueputa", "hijueputas", "malparido", "marica", "maricones",
    "h p", "H.P.", "p u t a", "put4", "puta", "mierda", "perrrra", "c0ño", "coño",
    "eres un hp", "hola gonorrea", "nazi", "venecos", "culos", "estúpido", "imbécil",
])
def test_bloquea(mod, texto):
    assert mod.es_ofensivo(texto), texto


@pytest.mark.parametrize("texto", [
    "hola jurado", "calle", "carro", "pera", "Maricarmen", "mondadientes", "computador", "disputa",
    "Puerto", "señor José", "bienvenidos a la sustentación", "a e i o u", "uña", "gracias", "chimenea",
    "perro", "zorro", "pendiente", "cultivo", "cono", "hipótesis",
])
def test_no_bloquea_palabras_normales(mod, texto):
    assert not mod.es_ofensivo(texto), texto


def test_lista_editable(tmp_path):
    ruta = tmp_path / "lista.txt"
    ruta.write_text("# comentario\nbrocoli\n\n", encoding="utf-8")
    m = cargar_moderador(ruta)
    assert m.es_ofensivo("odio el brócoli") and not m.es_ofensivo("gonorrea")


def test_moderador_vacio_no_bloquea_nada():
    assert not Moderador([]).es_ofensivo("lo que sea")
```

## `tests/test_otros.py`

```python
"""Túnel, voz y páginas web (caracterización)."""
import re

import pytest


# ---------------------------------------------------------------- túnel
def test_patron_url_del_tunel(modulo_tunel):
    linea = "2026-10-14T10:00:00Z INF |  https://ips-jews-saints-textbooks.trycloudflare.com  |"
    assert modulo_tunel.PATRON_URL.search(linea).group(0) == "https://ips-jews-saints-textbooks.trycloudflare.com"
    assert modulo_tunel.PATRON_URL.search("https://example.com") is None


def test_tunel_sin_cloudflared(monkeypatch, modulo_tunel):
    monkeypatch.setattr(modulo_tunel, "buscar_cloudflared", lambda: None)
    cambios = []
    t = modulo_tunel.Tunel(8000, log=lambda m: None, al_cambiar=lambda: cambios.append(t.estado))
    assert (t.estado, t.url) == ("apagado", None)
    t._bucle()
    assert (t.estado, t.url) == ("no instalado", None)
    assert cambios == ["no instalado"]


def test_ip_local_devuelve_una_ipv4(modulo_tunel):
    assert re.fullmatch(r"\d+\.\d+\.\d+\.\d+", modulo_tunel.ip_local())


# ---------------------------------------------------------------- voz
def test_transcriptor_antes_de_cargar(modulo_voz):
    t = modulo_voz.Transcriptor(log=lambda m: None)
    assert (t.estado, t.dispositivo, t.listo) == ("sin cargar", None, False)
    with pytest.raises(RuntimeError):
        t.transcribir("no-existe.webm")


# ---------------------------------------------------------------- páginas
@pytest.mark.parametrize("pagina", ["movil.html", "pantalla.html"])
def test_paginas_sin_dependencias_de_internet(carpeta_web, pagina):
    html = (carpeta_web / pagina).read_text(encoding="utf-8")
    assert not re.search(r"""(src|href)\s*=\s*["']?(https?:)?//""", html)
    assert "@import" not in html and "url(http" not in html


@pytest.mark.parametrize("pagina, ids", [
    ("movil.html", ["texto", "enviar", "previa", "grabar", "archivoAudio", "listaMios", "ahoraLetras", "chipConexion", "btnTema"]),
    ("pantalla.html", ["qr", "escenario", "palabra", "cola", "historial", "btnSaltar",
                       "btnReconectar", "btnCompleta", "btnTema", "desconectado", "alfabeto"]),
])
def test_paginas_tienen_sus_controles(carpeta_web, pagina, ids):
    html = (carpeta_web / pagina).read_text(encoding="utf-8")
    for i in ids:
        assert f'id="{i}"' in html, i


@pytest.mark.parametrize("pagina, rutas", [
    ("movil.html", ["/api/previa", "/api/mensaje", "/api/transcribir", "/api/estado", "/ws", "/logo-udec.png"]),
    ("pantalla.html", ["/qr.png", "/api/mano/reconectar", "/api/mano/saltar", "/api/previa", "/ws", "/logo-udec.png"]),
])
def test_paginas_usan_la_api(carpeta_web, pagina, rutas):
    html = (carpeta_web / pagina).read_text(encoding="utf-8")
    for r in rutas:
        assert r in html, r
```

## `tests/test_participantes.py`

```python
"""Participantes (E8): nombre opcional, «Mensaje de», bloqueo por sesión y nada en disco."""
import ast

import pytest

from conftest import AUDIO_WEBM, RAIZ, admin, esperar

from pgc.dominio.participante import MAX_NOMBRE, normalizar_nombre

PC = "127.0.0.1"
PAUSA = "El presentador pausó tu participación en esta sesión. ¡Gracias por participar!"


def registrar(c, cliente, nombre=None):
    return c.post("/api/participante", json={"cliente": cliente, "nombre": nombre})


def enviar(c, cliente, texto="hola"):
    return c.post("/api/mensaje", json={"texto": texto, "cliente": cliente})


# ---------------------------------------------------------------- nombre
@pytest.mark.parametrize("entrada, esperado", [
    ("Ana", "Ana"), ("  ana   maría ", "ana maría"), ("José-Luis", "José-Luis"), ("O'Neil", "O'Neil"),
    ("Jurado 2", "Jurado 2"), ("", None), ("   ", None), (None, None), ("x" * MAX_NOMBRE, "x" * MAX_NOMBRE),
])
def test_normalizar_nombre(entrada, esperado):
    assert normalizar_nombre(entrada) == esperado


@pytest.mark.parametrize("entrada", ["x" * 21, "<b>Ana</b>", "Ana😀", "ana@correo.com", "a/b"])
def test_nombre_invalido(entrada):
    with pytest.raises(ValueError, match="Usa solo letras"):
        normalizar_nombre(entrada)


def test_registrar_devuelve_un_alias_opaco(abrir_api):
    with abrir_api() as (c, _):
        r = registrar(c, "celular-de-ana", "  Ana ")
        assert r.status_code == 200
        d = r.json()
        assert d["nombre"] == "Ana" and d["bloqueado"] is False
        assert d["pid"].startswith("p") and "celular-de-ana" not in d["pid"]
        assert registrar(c, "celular-de-ana", "Ana María").json()["pid"] == d["pid"]   # mismo celular, mismo alias
        assert registrar(c, "otro", "Ana").json()["pid"] != d["pid"]


@pytest.mark.parametrize("nombre, codigo, detalle", [
    ("x" * 21, 400, "Usa solo letras en tu nombre (máximo 20)."),
    ("<script>", 400, "Usa solo letras en tu nombre (máximo 20)."),
    ("gonorrea", 400, "Ese nombre no se puede mostrar. Prueba con otro."),
    ("x" * 61, 422, "Usa solo letras en tu nombre (máximo 20)."),
    ("Ana\x00", 422, "Usa solo letras en tu nombre (máximo 20)."),
])
def test_nombre_rechazado_con_mensaje_amable(abrir_api, nombre, codigo, detalle):
    with abrir_api() as (c, _):
        r = registrar(c, "A", nombre)
    assert r.status_code == codigo and r.json() == {"detail": detalle}


def test_mensaje_de_en_el_proyector(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "o"                               # la H no la hace la mano: se bloquea en la O
        registrar(c, "A", "Ana")
        enviar(c, "A", "hola")
        s.mano.llego.wait(5)
        enviar(c, "B", "uña")                                  # B no dio nombre
        registrar(c, "A", "Ana María")                         # cambiar el nombre no cambia lo ya enviado
        d = c.get("/api/estado").json()
        assert d["actual"]["nombre"] == "Ana"
        assert [(m["texto"], m["nombre"]) for m in d["cola"]] == [("uña", "Anónimo")]


def test_el_nombre_viaja_con_el_mensaje_hasta_recientes(abrir_api):
    with abrir_api() as (c, s):
        registrar(c, "A", "Jean")
        r = enviar(c, "A", "Hola jurado")
        assert r.json()["nombre"] == "Jean"                    # el celular sabe con qué nombre se guardó
        r = enviar(c, "B", "ok")                               # B no dio nombre
        assert r.json()["nombre"] == "Anónimo"
        esperar(lambda: len(c.get("/api/estado").json()["historial"]) == 2, timeout=30)
        hist = c.get("/api/estado").json()["historial"]
        assert [(m["nombre"], m["texto"]) for m in hist] == [("Anónimo", "ok"), ("Jean", "hola jurado")]


def test_el_nombre_conserva_sus_mayusculas(abrir_api):
    with abrir_api() as (c, s):
        for nombre in ("Jean", "jean", "JEAN", "María José"):
            assert registrar(c, "A", nombre).json()["nombre"] == nombre
        assert enviar(c, "A", "hola").json()["nombre"] == "María José"


# ---------------------------------------------------------------- bloqueo
def test_bloquear_exige_el_token(abrir_api):
    with abrir_api() as (c, _):
        pid = registrar(c, "A").json()["pid"]
        assert c.post(f"/api/participantes/{pid}/bloquear").status_code == 403
    with abrir_api(desde=PC) as (c, _):
        pid = registrar(c, "A").json()["pid"]
        r = c.post(f"/api/participantes/{pid}/bloquear", headers={**admin(c), "cf-connecting-ip": "1.2.3.4"})
        assert r.status_code == 403


def test_bloquear_cancela_pendientes_y_avisa(abrir_api):
    with abrir_api(desde=PC, max_pendientes_cliente=5) as (c, s):
        s.mano.bloquear_en = "a"
        pid = registrar(c, "A", "Pedro").json()["pid"]
        enviar(c, "A", "a")                                    # en curso
        s.mano.llego.wait(5)
        enviar(c, "A", "b"); enviar(c, "A", "c"); enviar(c, "B", "d")
        with c.websocket_connect("/ws") as ws:
            ws.receive_json()
            r = c.post(f"/api/participantes/{pid}/bloquear", headers=admin(c))
            assert r.status_code == 200 and r.json() == {"ok": True, "cancelados": 2, "saltado": True}
            d = ws.receive_json()
            while pid not in d.get("bloqueados", []):
                d = ws.receive_json()
        assert [m["texto"] for m in d["cola"]] == ["d"]        # solo quedan los de otros
        assert s.cola[0]["texto"] == "d"
        s.mano.soltar.set()
        esperar(lambda: s.historial and s.historial[-1]["texto"] == "a")
        assert s.historial[-1]["saltado"] is True              # su mensaje en curso también se saltó
        # Su celular recibe un aviso amable al intentar participar
        r = enviar(c, "A", "otro")
        assert r.status_code == 403 and r.json() == {"detail": PAUSA}
        r = c.post("/api/transcribir", files={"audio": ("v.webm", AUDIO_WEBM, "audio/webm")}, data={"cliente": "A"})
        assert r.status_code == 403 and r.json() == {"detail": PAUSA}
        assert registrar(c, "A", "Otro nombre").json() == {"pid": pid, "nombre": "Pedro", "bloqueado": True}
        assert enviar(c, "B", "e").status_code == 200          # los demás siguen igual
        s.mano.soltar.set()


def test_desbloquear(abrir_api):
    with abrir_api(desde=PC) as (c, _):
        pid = registrar(c, "A").json()["pid"]
        h = admin(c)
        c.post(f"/api/participantes/{pid}/bloquear", headers=h)
        assert enviar(c, "A").status_code == 403
        assert c.post(f"/api/participantes/{pid}/desbloquear", headers=h).json() == {"ok": True}
        assert enviar(c, "A").status_code == 200
        assert c.get("/api/estado").json()["bloqueados"] == []


def test_bloquear_a_otro_no_salta_el_mensaje_en_curso(abrir_api):
    with abrir_api(desde=PC) as (c, s):
        s.mano.bloquear_en = "a"
        enviar(c, "A", "a")
        s.mano.llego.wait(5)
        pid_b = registrar(c, "B").json()["pid"]
        assert c.post(f"/api/participantes/{pid_b}/bloquear", headers=admin(c)).json()["saltado"] is False
        s.mano.soltar.set()
        esperar(lambda: len(s.historial) == 1)
        assert not s.historial[0].get("saltado")


def test_deshacer_no_recupera_el_mensaje_saltado(abrir_api):
    with abrir_api(desde=PC) as (c, s):
        s.mano.bloquear_en = "b"
        pid = registrar(c, "A").json()["pid"]
        enviar(c, "A", "abc")
        s.mano.llego.wait(5)
        h = admin(c)
        c.post(f"/api/participantes/{pid}/bloquear", headers=h)
        c.post(f"/api/participantes/{pid}/desbloquear", headers=h)
        s.mano.soltar.set()
        esperar(lambda: len(s.historial) == 1)
        assert s.historial[0]["saltado"] is True and s.mano.ordenes == ["a", "b", "reset"]
        assert s.cola == []


def test_participante_desconocido(abrir_api):
    with abrir_api(desde=PC) as (c, _):
        r = c.post("/api/participantes/pdeadbeef/bloquear", headers=admin(c))
    assert r.status_code == 404 and r.json() == {"detail": "No encontramos a ese participante."}


def test_quien_envia_sin_registrarse_tambien_tiene_alias(abrir_api):
    with abrir_api() as (c, s):
        s.mano.bloquear_en = "a"
        enviar(c, "nuevo", "a")
        s.mano.llego.wait(5)
        assert c.get("/api/estado").json()["actual"]["pid"].startswith("p")


# ---------------------------------------------------------------- privacidad
def test_el_nombre_no_queda_en_el_log(abrir_api, registro):
    with abrir_api(desde=PC) as (c, s):
        pid = registrar(c, "A", "Zacarías").json()["pid"]
        enviar(c, "A", "hola")
        c.post(f"/api/participantes/{pid}/bloquear", headers=admin(c))
        esperar(lambda: len(s.historial) == 1)
    assert not any("Zacar" in linea for linea in registro)


@pytest.mark.parametrize("ruta", ["pgc/aplicacion/participantes.py", "pgc/dominio/participante.py"])
def test_participantes_no_escriben_en_disco(ruta):
    arbol = ast.parse((RAIZ / ruta).read_text(encoding="utf-8"))
    nombres = {n.id for n in ast.walk(arbol) if isinstance(n, ast.Name)} | \
              {n.attr for n in ast.walk(arbol) if isinstance(n, ast.Attribute)}
    assert not nombres & {"open", "write_text", "write_bytes", "dump", "Path", "sqlite3", "shelve"}
```

## `tests/test_protocolo.py`

```python
"""Protocolo de prueba de letras: análisis, máquina de estados, guardado y API (sin Kinect)."""
import csv
import threading
import time

import pytest

from conftest import admin, esperar
from detector_falso import DetectorFalso

from pgc.adaptadores import experimentos
from pgc.aplicacion.protocolo import ProtocoloLetras, ServicioProtocolo
from pgc.dominio import experimento as ex

PC = "127.0.0.1"
TUNEL = {"CF-Connecting-IP": "181.50.1.2"}


def intento(letra, reconocida, **kw):
    base = {"letra": letra, "intento": 1, "reconocida": reconocida, "tiempo_s": 1.2 if reconocida else None,
            "mano_pct": 90.0, "prediccion_frecuente": reconocida or letra, "margen_medio": 0.9,
            "estable_max_s": 1.0, "cambios": 0, "sin_letra_pct": 0.0, "motivo_frecuente": "Confirmando…"}
    return {**base, **kw}


# ---------------------------------------------------------------- análisis
def test_resumen_y_matriz():
    datos = [intento("a", "a"), intento("a", "a"), intento("a", "e"), intento("a", None),
             intento("b", "b")]
    por = {f["letra"]: f for f in ex.resumen_por_letra(datos)}
    assert por["a"] == {"letra": "a", "intentos": 4, "aciertos": 2, "confusiones": {"e": 1}, "no_detectadas": 1,
                        "exactitud_pct": 50.0, "tiempo_medio_s": 1.2}
    filas, columnas, matriz = ex.matriz_confusion(datos, ["a", "b"])
    assert columnas == ["a", "b", "e", ex.NINGUNA]
    assert matriz == [[2, 0, 1, 1], [0, 1, 0, 0]]
    inf = ex.informe(datos)
    assert inf["exactitud_pct"] == 60.0 and inf["fallan"] == ["a"] and "b" not in inf["causas"]


@pytest.mark.parametrize("cambios, tipo", [
    ({"mano_pct": 20.0}, "mano"),
    ({"prediccion_frecuente": "sin_letra", "sin_letra_pct": 80.0}, "sin_letra"),
    ({"reconocida": "e"}, "parecida"),
    ({"cambios": 6}, "inestable"),
    ({"estable_max_s": 0.4}, "tiempo"),
    ({"margen_medio": 0.1}, "margen"),
])
def test_causa_probable(cambios, tipo):
    fallo = intento("a", None, **{k: v for k, v in cambios.items() if k != "reconocida"})
    if "reconocida" in cambios:
        fallo = intento("a", cambios["reconocida"])
    assert ex.causa_probable("a", [fallo, intento("a", "a")])[0] == tipo
    assert ex.causa_probable("a", [intento("a", "a")]) is None


# ---------------------------------------------------------------- máquina de estados
def diag(t, manos=0, pred=None, texto="", armado=True, estable=0.0):
    return {"t": t, "manos": manos, "prediccion": pred, "segunda": None, "margen": 0.5 if pred else None,
            "estable_s": estable, "confirmaciones": 0, "armado": armado, "texto": texto, "motivo": "x"}


def test_acierto_confusion_y_no_detectada():
    p = ProtocoloLetras(["a", "b", "c"], repeticiones=1, tiempo_max=3.0)
    assert p.iniciar(0.0) == ["iniciar", "limpiar"]
    p.muestra(diag(1, 0), 0.5)                                     # sin mano: el tiempo aún no corre
    p.muestra(diag(2, 1, "a"), 1.0)                                # aparece la mano
    p.muestra(diag(3, 1, "a", estable=0.8), 1.8)
    p.muestra(diag(4, 1, "a", texto="A", armado=False), 2.0)       # su lógica confirmó A
    assert p.fase == "retirar" and p.intentos[0]["reconocida"] == "a" and p.intentos[0]["tiempo_s"] == 1.0
    assert p.muestra(diag(5, 0, None, texto="A", armado=False), 2.2) == []      # aún no está lista
    assert p.muestra(diag(6, 0, None, texto="A", armado=True), 2.8) == ["limpiar"]
    assert p.estado()["letra"] == "b"
    p.muestra(diag(7, 1, "e", texto=""), 3.0)
    p.muestra(diag(8, 1, "e", texto="E", armado=False), 3.9)       # confundida con E
    p.muestra(diag(9, 0, texto="E"), 4.2)                          # retira la mano
    p.muestra(diag(10, 1, "sin_letra", texto=""), 4.5)
    p.muestra(diag(11, 1, "sin_letra", texto=""), 7.6)             # pasan 3 s: no detectada
    assert [(i["letra"], i["reconocida"]) for i in p.intentos] == [("a", "a"), ("b", "e"), ("c", None)]
    assert p.intentos[2]["sin_letra_pct"] == 100.0
    p.muestra(diag(12, 0), 7.8)
    assert p.fase == "terminado"


def test_tras_limpiar_no_cuenta_el_texto_viejo():
    """El diagnóstico se actualiza con cada imagen: justo tras limpiar puede traer aún la letra anterior."""
    p = ProtocoloLetras(["a"], repeticiones=2, tiempo_max=5.0)
    p.iniciar(0.0)
    p.muestra(diag(1, 1, "a", texto="A", armado=False), 1.0)       # intento 1: A
    p.muestra(diag(2, 0, texto="A", armado=True), 1.5)             # retirar → limpiar, intento 2
    assert p.estado()["intento"] == 2
    p.muestra(diag(2, 0, texto="A", armado=True), 1.6)             # MISMA imagen (t=2), aún con "A": no cuenta
    assert p.fase == "pedir"
    p.muestra(diag(3, 1, "a", texto=""), 1.7)                      # imagen nueva, ya limpio
    p.muestra(diag(4, 1, "a", texto="A", armado=False), 2.6)       # ahora sí: A otra vez
    assert [i["reconocida"] for i in p.intentos] == ["a", "a"]


def test_el_servicio_corre_y_guarda():
    ordenes, guardado = [], []
    muestras = iter([diag(1, 1, "a"), diag(2, 1, "a", texto="A", armado=False), diag(3, 0, texto="A")]
                    + [diag(4, 0)] * 50)

    class Senas:
        def diagnostico(self):
            return next(muestras)

        def controlar(self, accion):
            ordenes.append(accion)

    s = ServicioProtocolo(Senas(), guardar=lambda p, info: (guardado.append(p) or "experimentos/x", {"ok": 1}),
                          periodo=0.001)
    s.iniciar(["a"], repeticiones=1)
    esperar(lambda: s.estado()["fase"] == "terminado" and s.carpeta)
    assert ordenes[:2] == ["iniciar", "limpiar"] and guardado and s.estado()["carpeta"] == "experimentos/x"


# ---------------------------------------------------------------- guardado
def test_guardar_archivos(tmp_path):
    p = ProtocoloLetras(["a", "b"], repeticiones=2)
    p.intentos = [intento("a", "a"), intento("a", "e"), intento("b", None, mano_pct=10.0), intento("b", "b")]
    p.muestras = [{"t": 0.1, "fase": "pedir", "letra": "a", "intento": 1, "manos": 1, "prediccion": "a",
                   "segunda": "e", "margen": 0.5, "estable_s": 0.3, "confirmaciones": 2, "motivo": "x", "texto": ""}]
    carpeta, informe = experimentos.guardar(p, {}, carpeta_base=tmp_path)
    archivos = {f.name for f in next(tmp_path.iterdir()).iterdir()}
    assert {"intentos.csv", "muestras.csv", "resumen_por_letra.csv", "matriz_confusion.csv", "matriz_confusion.png",
            "aciertos_por_letra.png", "tiempos_por_letra.png", "informe.md"} <= archivos
    with open(next(tmp_path.iterdir()) / "intentos.csv", encoding="utf-8-sig") as f:
        filas = list(csv.reader(f, delimiter=";"))
    assert filas[0][:4] == ["letra", "intento", "resultado", "reconocida"] and filas[1][4] == "1,2"   # coma decimal
    assert informe["exactitud_pct"] == 50.0 and informe["causas"]["b"]["tipo"] == "mano"


# ---------------------------------------------------------------- API (detector falso)
@pytest.fixture
def detector():
    d = DetectorFalso()
    d.mantener_camara()
    yield d
    d.cerrar()


def test_diagnostico_solo_en_el_pc(abrir_api, detector):
    with abrir_api(PC, reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05) as (c, s):
        detector.mostrar("l")
        r = c.get("/api/kinect/diagnostico", headers=admin(c))
        assert r.status_code == 200 and r.json()["prediccion"] == "l"
        assert c.get("/api/kinect/diagnostico").status_code == 403
        assert c.get("/api/kinect/diagnostico", headers={**admin(c), **TUNEL}).status_code == 403
        assert "pgc-admin" in c.get("/diagnostico").text
        detector.con_diagnostico = False                            # su servidor original no lo tiene
        assert c.get("/api/kinect/diagnostico", headers=admin(c)).status_code == 503


def test_protocolo_completo_por_la_api(abrir_api, detector, monkeypatch, tmp_path):
    monkeypatch.setattr(experimentos, "CARPETA", tmp_path)
    with abrir_api(PC, reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05) as (c, s):
        s.protocolo.periodo = 0.02
        esperar(lambda: s.senas.reconocedor.camara)
        assert c.post("/api/kinect/protocolo/iniciar", json={"letras": "a x"}).status_code == 403   # sin token
        assert c.post("/api/kinect/protocolo/iniciar", json={"letras": "a ñ"}, headers=admin(c)).status_code == 400
        r = c.post("/api/kinect/protocolo/iniciar", json={"letras": "a b", "repeticiones": 2, "tiempo_max": 2},
                   headers=admin(c))
        assert r.status_code == 200 and r.json()["total"] == 4

        def persona():                                              # hace lo que le piden; la B la confunde con D
            hechas = 0
            while hechas < 4:
                e = c.get("/api/kinect/protocolo", headers=admin(c)).json()
                if e["fase"] == "pedir" and e["hecho"] == hechas:
                    letra = "d" if e["letra"] == "b" and e["intento"] == 2 else e["letra"]
                    detector.mostrar(letra)
                    time.sleep(0.15)
                    detector.reconocer(letra)
                    esperar(lambda: c.get("/api/kinect/protocolo", headers=admin(c)).json()["hecho"] > hechas)
                    detector.retirar()
                    hechas += 1
                time.sleep(0.03)
        hilo = threading.Thread(target=persona, daemon=True)
        hilo.start()
        esperar(lambda: c.get("/api/kinect/protocolo", headers=admin(c)).json().get("carpeta"), timeout=20)
        e = c.get("/api/kinect/protocolo", headers=admin(c)).json()
        assert e["informe"]["exactitud_pct"] == 75.0
        assert e["informe"]["por_letra"][1]["confusiones"] == {"d": 1}
        carpeta = next(tmp_path.iterdir())
        assert (carpeta / "matriz_confusion.png").exists() and (carpeta / "informe.md").exists()


def test_eco_desde_el_celular_con_turno(abrir_api, detector):
    with abrir_api(reconocedor="kinect", kinect_url=detector.url, kinect_intervalo=0.05) as (c, s):
        assert c.post("/api/kinect/eco", json={"activo": True, "cliente": "A"}).status_code == 403   # sin turno
        c.post("/api/kinect/turno", json={"cliente": "A"})
        assert c.post("/api/kinect/eco", json={"activo": True, "cliente": "A"}).json() == {"eco": True}
        assert c.post("/api/kinect/eco", json={"activo": False, "cliente": "B"}).status_code == 403  # espectador
        assert s.eco is True
```

## `tests/test_puertos.py`

```python
"""Pruebas de contrato: cada implementación cumple su puerto."""
import inspect
import time
import types

import pytest

from conftest import FabricaMano, ManoFalsa, TranscriptorFalso, TunelFalso, acceso, whisper

from pgc.puertos.acceso import AccesoPublico
from pgc.puertos.mano import PuertoMano
from pgc.puertos.transcriptor import Transcriptor


def miembros_del_puerto(puerto):
    return {n for n in dir(puerto) if not n.startswith("_")} | set(getattr(puerto, "__annotations__", {}))


@pytest.fixture(params=["real_simulada", "falsa"])
def mano(request):
    if request.param == "real_simulada":
        fabrica = FabricaMano()
        fabrica.time = types.SimpleNamespace(sleep=lambda s: None, time=time.time)
        return fabrica.Mano(simular=True, log=lambda m: None)
    return ManoFalsa()


def test_cumple_puerto_mano(mano):
    for nombre in miembros_del_puerto(PuertoMano):
        assert hasattr(mano, nombre), nombre
    for metodo in ("conectar", "cerrar", "hacer", "reset"):
        assert callable(getattr(mano, metodo)), metodo


def test_comportamiento_minimo_del_puerto(mano):
    assert mano.conectar() is False                  # sin hardware: queda simulada
    assert (mano.conectada, mano.modo) == (False, "simulada")
    assert mano.hacer("a") is True
    assert mano.reset() is True
    mano.cerrar()
    assert mano.modo == "simulada"


@pytest.mark.parametrize("puerto, implementaciones", [
    (Transcriptor, [lambda: whisper.Transcriptor(log=lambda m: None), lambda: TranscriptorFalso()]),
    (AccesoPublico, [lambda: acceso.Tunel(8000, log=lambda m: None), lambda: TunelFalso(8000)]),
], ids=["Transcriptor", "AccesoPublico"])
def test_voz_y_acceso_cumplen_su_puerto(puerto, implementaciones):
    for crear in implementaciones:
        obj = crear()
        for nombre in miembros_del_puerto(puerto):
            assert hasattr(obj, nombre), f"{type(obj).__name__} no tiene {nombre}"


def test_whisper_usa_el_modelo_configurado():
    assert whisper.Transcriptor(nombre_modelo="small").nombre_modelo == "small"
    assert whisper.Transcriptor().nombre_modelo == "medium"


def test_firma_de_hacer():
    assert list(inspect.signature(PuertoMano.hacer).parameters) == ["self", "orden"]
```

## `tests/test_seguridad.py`

```python
"""Medidas de seguridad de la etapa E7 (docs/ARQUITECTURA.md §B)."""
import io
import re
import tempfile
from pathlib import Path

import pytest
from starlette.websockets import WebSocketDisconnect

from conftest import AUDIO_WEBM, TunelFalso, admin, token_de_pantalla

PC = "127.0.0.1"
TUNEL = {"cf-connecting-ip": "203.0.113.7"}


# =============================================================================
#  M1 · Token de administrador
# =============================================================================
def test_token_solo_en_la_pantalla_del_pc(abrir_api):
    with abrir_api(desde=PC) as (c, s):
        token = token_de_pantalla(c)
        assert len(token) >= 40
        assert token_de_pantalla(c) == token                       # el mismo durante todo el arranque
        # Por el túnel (cloudflared conecta desde 127.0.0.1) la pantalla se sirve sin token
        r = c.get("/pantalla", headers=TUNEL)
        assert r.status_code == 200 and '<meta name="pgc-admin" content="">' in r.text
        # DNS rebinding: un dominio ajeno que apunta a 127.0.0.1
        r = c.get("/pantalla", headers={"Host": "atacante.example:8000"})
        assert '<meta name="pgc-admin" content="">' in r.text
    with abrir_api() as (c, _):                                    # celular
        assert token_de_pantalla(c) == ""


@pytest.mark.parametrize("encabezados, codigo", [
    ({}, 403),                                                     # sin token (CSRF desde otra página)
    ({"X-PGC-Admin": "falso"}, 403),
    (None, 404),                                                   # token correcto → llega a la ruta
])
def test_admin_exige_token(abrir_api, encabezados, codigo):
    with abrir_api(desde=PC) as (c, _):
        r = c.post("/api/mano/saltar", headers=admin(c) if encabezados is None else encabezados)
        assert r.status_code == codigo


def test_token_no_sirve_fuera_del_pc(abrir_api):
    with abrir_api(desde=PC) as (c, _):
        h = admin(c)
        assert c.post("/api/mano/saltar", headers={**h, **TUNEL}).status_code == 403
        assert c.post("/api/mano/saltar", headers={**h, "Host": "atacante.example"}).status_code == 403
        assert c.post("/api/mano/saltar", headers={**h, "X-Forwarded-For": "1.2.3.4"}).status_code == 403


def test_token_no_aparece_en_el_log(abrir_api, registro):
    with abrir_api(desde=PC) as (c, _):
        token = token_de_pantalla(c)
    assert token not in "\n".join(registro)


# =============================================================================
#  M8 · Documentación solo con --dev o con el token
# =============================================================================
def test_documentacion_en_modo_dev(abrir_api):
    with abrir_api(dev=True) as (c, _):
        assert c.get("/openapi.json").status_code == 200
        r = c.get("/docs")
        assert r.status_code == 200 and "swagger" in r.text.lower()


def test_documentacion_con_token(abrir_api):
    with abrir_api(desde=PC) as (c, _):
        token = token_de_pantalla(c)
        assert c.get("/openapi.json").status_code == 404
        assert c.get("/openapi.json", headers={"X-PGC-Admin": token}).status_code == 200
        r = c.get("/docs", params={"token": token})
        assert r.status_code == 200 and f"/openapi.json?token={token}" in r.text
        assert c.get("/docs", params={"token": token}, headers=TUNEL).status_code == 404


def test_404_amable(abrir_api):
    with abrir_api() as (c, _):
        assert c.get("/no-existe").json() == {"detail": "No encontramos esa página."}


# =============================================================================
#  M2 · Validación con mensajes amables
# =============================================================================
@pytest.mark.parametrize("cuerpo, detalle", [
    ({"texto": "a" * 201, "cliente": "A"}, "El mensaje es muy largo (máximo 60 caracteres)."),
    ({"texto": "hola\x00", "cliente": "A"}, "El mensaje tiene caracteres que no se pueden mostrar."),
    ({"texto": "hola", "cliente": "con espacios"}, "Recarga la página e intenta de nuevo."),
    ({"texto": "hola", "cliente": "<script>"}, "Recarga la página e intenta de nuevo."),
    ({"texto": 5, "cliente": "A"}, "Escribe tu mensaje de nuevo, por favor."),
    ({}, "Escribe tu mensaje de nuevo, por favor."),
])
def test_validacion_amable(abrir_api, cuerpo, detalle):
    with abrir_api() as (c, _):
        r = c.post("/api/mensaje", json=cuerpo)
    assert r.status_code == 422 and r.json() == {"detail": detalle}


def test_saltos_de_linea_si_se_permiten(abrir_api):
    with abrir_api() as (c, _):
        r = c.post("/api/mensaje", json={"texto": "hola\njurado", "cliente": "A"})
    assert r.status_code == 200 and r.json()["texto"] == "hola jurado"


def test_previa_tambien_limita_el_texto(abrir_api):
    with abrir_api() as (c, _):
        assert c.post("/api/previa", json={"texto": "a" * 201}).status_code == 422
        assert c.post("/api/previa", json={"texto": "a" * 200}).status_code == 200


def test_cancelar_valida_el_cliente(abrir_api):
    with abrir_api() as (c, _):
        assert c.delete("/api/mensaje/1", params={"cliente": "no valido!"}).status_code == 422


# =============================================================================
#  M4 · Tamaño del cuerpo
# =============================================================================
def test_cuerpo_json_demasiado_grande(abrir_api):
    with abrir_api() as (c, _):
        r = c.post("/api/mensaje", content=b'{"texto": "' + b"a" * 20000 + b'"}',
                   headers={"Content-Type": "application/json"})
    assert r.status_code == 413 and r.json() == {"detail": "El mensaje es muy largo."}


def test_cuerpo_sin_content_length_tambien_se_corta(abrir_api):
    def trozos():
        for _ in range(40):
            yield b"a" * 1024
    with abrir_api() as (c, _):
        r = c.post("/api/previa", content=trozos(), headers={"Content-Type": "application/json"})
    assert r.status_code == 413


def test_audio_demasiado_grande_antes_de_leerlo(abrir_api):
    with abrir_api() as (c, s):
        r = c.post("/api/transcribir", content=b"x", headers={"Content-Length": str(50 * 1024 * 1024),
                                                              "Content-Type": "multipart/form-data; boundary=x"})
        assert r.status_code == 413
        assert s.voz.recibidos == []


# =============================================================================
#  M3 · Audio
# =============================================================================
def subir(c, datos=AUDIO_WEBM, tipo="audio/webm", nombre="voz.webm", cliente=None):
    datos_form = {"cliente": cliente} if cliente else None
    return c.post("/api/transcribir", files={"audio": (nombre, io.BytesIO(datos), tipo)}, data=datos_form)


@pytest.mark.parametrize("cabecera", [
    b"\x1a\x45\xdf\xa3....",                  # webm (Android)
    b"\x00\x00\x00\x1cftypM4A ",               # m4a (iPhone)
    b"\x00\x00\x00\x18ftyp3gp4",               # 3gp (grabadora de Android)
    b"OggS\x00\x02",
    b"RIFF\x24\x00\x00\x00WAVEfmt ",
    b"ID3\x03\x00",
    b"\xff\xfb\x90\x00",                       # mp3 sin etiquetas
    b"\xff\xf1\x50\x80",                       # aac
    b"#!AMR\n",
])
def test_formatos_de_audio_aceptados(abrir_api, cabecera):
    with abrir_api() as (c, _):
        assert subir(c, datos=cabecera + b"\x00" * 32).status_code == 200


@pytest.mark.parametrize("datos, tipo", [
    (b"<html><script>alert(1)</script>", "audio/webm"),       # la firma no es de audio
    (b"MZ\x90\x00 ejecutable", "application/octet-stream"),
    (AUDIO_WEBM, "text/html"),                                 # el tipo declarado no es de audio
    (AUDIO_WEBM, "image/png"),
])
def test_rechaza_lo_que_no_es_audio(abrir_api, datos, tipo):
    with abrir_api() as (c, s):
        r = subir(c, datos=datos, tipo=tipo)
        assert r.status_code == 415
        assert r.json() == {"detail": "Ese archivo no parece un audio. Graba de nuevo con el botón."}
        assert s.voz.recibidos == []


def test_audio_demasiado_largo_en_segundos(abrir_api):
    with abrir_api() as (c, s):
        s.voz.segundos = 16.0
        r = subir(c)
        assert r.status_code == 413 and r.json() == {"detail": "El audio es muy largo. Graba máximo 10 segundos."}
        assert s.voz.recibidos == []                               # no llegó a Whisper
        s.voz.segundos = None                                      # duración desconocida: decide Whisper
        assert subir(c).status_code == 200


def test_temporales_en_carpeta_propia_y_limpieza_al_arrancar(abrir_api):
    carpeta = Path(tempfile.gettempdir()) / "pgc_voz"
    carpeta.mkdir(exist_ok=True)
    viejo = carpeta / "voz_de_una_caida.webm"
    viejo.write_bytes(b"x")
    with abrir_api() as (c, s):
        assert not viejo.exists()                                   # se limpió al arrancar
        subir(c)
        assert Path(s.voz.recibidos[0][0]).parent == carpeta
        assert not Path(s.voz.recibidos[0][0]).exists()


def test_nombre_de_archivo_raro_no_cambia_la_extension(abrir_api):
    with abrir_api() as (c, s):
        subir(c, nombre="..\\..\\evil.exe;rm -rf")
        assert s.voz.recibidos[0][0].endswith(".webm")


def test_demasiadas_transcripciones_a_la_vez(abrir_api):
    with abrir_api(voz_max_en_espera=3) as (c, _):
        c.app.state.voz_en_curso = 4                                # 1 transcribiendo + 3 esperando
        r = subir(c)
        assert r.status_code == 429
        assert r.json() == {"detail": "Hay varias personas usando la voz, intenta en unos segundos."}
        c.app.state.voz_en_curso = 0
        assert subir(c).status_code == 200


def test_error_de_whisper_no_filtra_detalles(abrir_api, registro):
    with abrir_api() as (c, s):
        s.voz.error = RuntimeError(r"C:\Users\secreto\ruta interna")
        subir(c)
    assert not any("secreto" in linea for linea in registro)


# =============================================================================
#  M5 · Límite de peticiones
# =============================================================================
def test_limite_por_ip(abrir_api):
    with abrir_api(lim_mensaje_ip=2, max_pendientes_cliente=10) as (c, _):
        for k in range(2):
            assert c.post("/api/mensaje", json={"texto": "a", "cliente": f"c{k}"}).status_code == 200
        r = c.post("/api/mensaje", json={"texto": "a", "cliente": "otro"})
    assert r.status_code == 429
    assert r.json() == {"detail": "Vas muy rápido, espera unos segundos."}
    assert int(r.headers["Retry-After"]) >= 1


def test_limite_por_cliente(abrir_api):
    with abrir_api(lim_mensaje_cliente=1, max_pendientes_cliente=10) as (c, _):
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "A"}).status_code == 200
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "A"}).status_code == 429
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "B"}).status_code == 200


def test_por_el_tunel_cuenta_la_ip_real(abrir_api):
    with abrir_api(desde=PC, lim_mensaje_ip=1, max_pendientes_cliente=10) as (c, _):
        def enviar(ip, cliente):
            return c.post("/api/mensaje", json={"texto": "a", "cliente": cliente},
                          headers={"cf-connecting-ip": ip}).status_code
        assert enviar("198.51.100.1", "a1") == 200
        assert enviar("198.51.100.1", "a2") == 429
        assert enviar("198.51.100.2", "b1") == 200               # otro celular por el túnel


def test_un_celular_no_puede_falsificar_su_ip(abrir_api):
    with abrir_api(lim_mensaje_ip=1, max_pendientes_cliente=10) as (c, _):
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "a1"},
                      headers={"cf-connecting-ip": "1.1.1.1"}).status_code == 200
        assert c.post("/api/mensaje", json={"texto": "a", "cliente": "a2"},
                      headers={"cf-connecting-ip": "2.2.2.2"}).status_code == 429


def test_el_pc_no_tiene_limite(abrir_api):
    with abrir_api(desde=PC, lim_previa_ip=1, lim_general_ip=1) as (c, _):
        for _ in range(5):
            assert c.post("/api/previa", json={"texto": "a"}).status_code == 200


def test_limite_general(abrir_api):
    with abrir_api(lim_general_ip=3) as (c, _):
        codigos = [c.get("/api/estado").status_code for _ in range(4)]
    assert codigos == [200, 200, 200, 429]


def test_limite_de_transcripcion_por_cliente(abrir_api):
    with abrir_api(lim_transcribir_cliente=1) as (c, _):
        assert subir(c, cliente="A").status_code == 200
        assert subir(c, cliente="A").status_code == 429
        assert subir(c, cliente="B").status_code == 200


# =============================================================================
#  M6 · WebSocket
# =============================================================================
def conectar(c, origen=None, **encabezados):
    if origen:
        encabezados["origin"] = origen
    return c.websocket_connect("/ws", headers=encabezados)


@pytest.mark.parametrize("origen", ["http://testserver", TunelFalso.URL, "http://192.168.0.10:8000"])
def test_websocket_acepta_las_paginas_propias(abrir_api, origen):
    with abrir_api() as (c, _):
        with conectar(c, origen) as ws:
            assert ws.receive_json()["tipo"] == "estado"


def test_websocket_rechaza_otros_sitios(abrir_api):
    with abrir_api() as (c, _):
        with pytest.raises(WebSocketDisconnect) as ex:
            with conectar(c, "https://sitio-ajeno.example") as ws:
                ws.receive_json()
    assert ex.value.code == 1008


def test_websocket_limite_por_ip(abrir_api):
    with abrir_api(ws_max_por_ip=1) as (c, _):
        with conectar(c) as w1:
            w1.receive_json()
            with pytest.raises(WebSocketDisconnect) as ex:
                with conectar(c) as w2:
                    w2.receive_json()
            assert ex.value.code == 1013
        with conectar(c) as w3:                                  # al cerrar el primero, vuelve a haber cupo
            assert w3.receive_json()["tipo"] == "estado"
        assert c.app.state.ws_total == 0 and c.app.state.ws_por_ip == {}


# =============================================================================
#  M7 · Encabezados y CSP
# =============================================================================
@pytest.mark.parametrize("ruta", ["/", "/pantalla", "/api/estado", "/qr.png", "/logo-udec.png", "/no-existe"])
def test_encabezados_de_seguridad(abrir_api, ruta):
    with abrir_api() as (c, _):
        r = c.get(ruta)
    assert r.headers["x-content-type-options"] == "nosniff"
    assert r.headers["referrer-policy"] == "no-referrer"
    assert r.headers["x-frame-options"] == "DENY"
    assert "microphone=(self)" in r.headers["permissions-policy"]
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]
    assert "access-control-allow-origin" not in r.headers


@pytest.mark.parametrize("ruta", ["/", "/pantalla"])
def test_csp_con_nonce_en_cada_script(abrir_api, ruta):
    with abrir_api() as (c, _):
        r = c.get(ruta)
        r2 = c.get(ruta)
    nonce = re.search(r"'nonce-([^']+)'", r.headers["content-security-policy"]).group(1)
    scripts = re.findall(r"<script[^>]*>", r.text)
    assert scripts and all(s == f'<script nonce="{nonce}">' for s in scripts)
    assert nonce not in r2.text                                     # cambia en cada respuesta
    assert "'unsafe-inline'" not in r.headers["content-security-policy"].split("script-src")[1].split(";")[0]
    assert "connect-src 'self' ws://testserver wss://testserver" in r.headers["content-security-policy"]


def test_csp_no_acepta_un_host_raro(abrir_api):
    with abrir_api() as (c, _):
        r = c.get("/", headers={"Host": "x; script-src *"})
    assert "script-src *" not in r.headers["content-security-policy"]


@pytest.mark.parametrize("pagina", ["movil.html", "pantalla.html"])
def test_innerhtml_solo_con_constantes(carpeta_web, pagina):
    permitidos = {"b.innerHTML = oscuro ? SOL : LUNA;", "pos.innerHTML = '<span class=\"vivo-punto\"></span>';"}
    for linea in (carpeta_web / pagina).read_text(encoding="utf-8").splitlines():
        if "innerHTML" in linea:
            assert linea.strip() in permitidos, linea.strip()


# =============================================================================
#  M9 · Filtro de palabras  ·  M10 · Registros
# =============================================================================
@pytest.mark.parametrize("texto", ["gonorrea", "h p", "hola malparido", "put4"])
def test_filtro_de_palabras(abrir_api, texto):
    with abrir_api() as (c, s):
        r = c.post("/api/mensaje", json={"texto": texto, "cliente": "A"})
        assert r.status_code == 400
        assert r.json() == {"detail": "Ese mensaje no se puede mostrar. Intenta con otras palabras."}
        assert s.cola == [] and s.actual is None


def test_el_log_no_guarda_textos_por_defecto(abrir_api, registro):
    with abrir_api() as (c, s):
        c.post("/api/mensaje", json={"texto": "secreto", "cliente": "cliente123"})
        c.post("/api/mensaje", json={"texto": "gonorrea", "cliente": "cliente123"})
    log = "\n".join(registro)
    assert "secreto" not in log and "SECRETO" not in log and "gonorrea" not in log
    assert "cliente123" not in log and "testclient" not in log
    assert "(7 letras" in log


def test_log_textos_para_depurar(abrir_api, registro):
    with abrir_api(log_textos=True) as (c, _):
        c.post("/api/mensaje", json={"texto": "hola", "cliente": "A"})
    assert "'hola'" in "\n".join(registro)
```

## `tests/test_senas.py`

```python
"""Señas → texto (E9): servicio de eventos, carga del reconocedor y aislamiento de errores."""
import threading
import time

import pytest

from conftest import configuracion, esperar

from pgc import arranque
from pgc.adaptadores.reconocedor_simulado import ReconocedorSimulado
from pgc.aplicacion.senas import ServicioSenas
from pgc.dominio.moderacion import cargar_moderador
from pgc.puertos.reconocedor import EventoSena


@pytest.fixture
def servicio():
    frases, log = [], []
    r = ReconocedorSimulado(pausa=0)
    s = ServicioSenas(r, al_frase=frases.append, log=log.append, moderador=cargar_moderador())
    s.iniciar()
    yield s, r, frases, log
    s.detener()


def test_arma_la_frase_y_la_entrega_al_terminar(servicio):
    s, r, frases, _ = servicio
    r.simular("Hola  mundo!", esperar=True)
    esperar(lambda: frases == ["hola mundo"])
    assert s.texto == ""


def test_borrar_y_espacios(servicio):
    s, _, frases, _ = servicio
    for e in [EventoSena("espacio"), EventoSena("letra", letra="a"), EventoSena("letra", letra="x"),
              EventoSena("borrar"), EventoSena("espacio"), EventoSena("espacio"), EventoSena("letra", letra="ñ"),
              EventoSena("fin")]:
        s._recibir(e)
    esperar(lambda: frases == ["a ñ"])


def test_eventos_invalidos_se_ignoran(servicio):
    s, _, frases, log = servicio
    s._recibir(EventoSena("letra", letra="A"))
    s._recibir("basura")
    s._recibir(EventoSena("letra", letra="b"))
    s._recibir(EventoSena("fin"))
    esperar(lambda: frases == ["b"])
    assert sum("Evento ignorado" in l for l in log) == 2


def test_frase_ofensiva_no_se_entrega(servicio):
    s, r, frases, log = servicio
    r.simular("gonorrea", esperar=True)
    esperar(lambda: any("filtro" in l for l in log))
    assert frases == []


def test_recibir_nunca_bloquea_al_reconocedor():
    lento = threading.Event()
    s = ServicioSenas(ReconocedorSimulado(), al_frase=lambda f: lento.wait(5))
    s.iniciar()
    t0 = time.monotonic()
    for _ in range(100):
        s._recibir(EventoSena("letra", letra="a"))
        s._recibir(EventoSena("fin"))
    assert time.monotonic() - t0 < 0.5
    lento.set()


class Roto:
    estado, detalle = "apagado", ""

    def iniciar(self, al_evento, al_cambiar_estado):
        raise RuntimeError("no hay Kinect")

    def detener(self):
        raise RuntimeError("tampoco")


def test_un_reconocedor_roto_no_tumba_nada():
    log = []
    s = ServicioSenas(Roto(), log=log.append)
    s.iniciar()
    s.detener()
    assert s.instantanea()["estado"] == "error"
    assert s.instantanea()["detalle"] == "Kinect: no disponible"


@pytest.mark.parametrize("ruta, detalle", [
    ("simulado", "Kinect simulado"),
    ("pgc.adaptadores.reconocedor_simulado:ReconocedorSimulado", "Kinect simulado"),
    ("pgc.adaptadores.kinect.no_existe:Clase", "Kinect: no disponible"),
    ("sin_dos_puntos", "Kinect: no disponible"),
])
def test_cargar_reconocedor(ruta, detalle):
    log = []
    r = arranque.cargar_reconocedor(configuracion(reconocedor=ruta), log.append)
    assert r.detalle == detalle
    assert ("No se pudo cargar" in "".join(log)) == (detalle == "Kinect: no disponible")


def test_el_sistema_inicia_y_detiene_el_reconocedor(abrir_api):
    with abrir_api() as (c, s):
        assert s.senas.reconocedor.estado == "sin_persona"
        s.senas.reconocedor.simular("ok", esperar=True)
        esperar(lambda: s.senas.frases == ["ok"])
        k = c.get("/api/estado").json()["kinect"]                                # ahora la pantalla lo ve
        assert k["estado"] == "sin_persona" and k["frases"] == ["ok"] and k["controles"] is False
    assert s.senas.reconocedor.estado == "apagado"
```

## `tests/test_texto.py`

```python
"""Texto libre → secuencia de pasos (caracterización de texto_util)."""
import pytest

from conftest import tipos


def test_letras_por_defecto_son_las_21_de_la_mano(texto):
    assert "".join(sorted(texto.LETRAS_POR_DEFECTO)) == "abcdefiklmnopqrtuvwxy"
    assert texto.MAX_CARACTERES == 60
    assert texto.APROXIMACIONES == {"ñ": "n"}


@pytest.mark.parametrize("entrada, esperado", [
    ("  HOLA   Mundo 12 ", "hola mundo uno dos"),
    ("a2b", "a dos b"),
    ("2026", "dos cero dos seis"),
    ("", ""),
    (None, ""),
    ("Señor José", "señor josé"),          # limpiar conserva tildes y ñ
])
def test_limpiar(texto, entrada, esperado):
    assert texto.limpiar(entrada) == esperado


def test_limpiar_recorta_a_60_despues_de_expandir_numeros(texto):
    r = texto.limpiar("1" * 30)
    assert len(r) == 60
    assert r.startswith("uno uno ")
    assert r.endswith("o uno ")             # el recorte puede dejar un espacio al final
    assert len(texto.limpiar("a" * 70)) == 60


def test_ejemplo_completo_senor_jose(texto):
    assert tipos(texto.a_secuencia("Señor José 2")) == [
        ("S", "nd"), ("E", "ok"), ("Ñ", "aprox"), ("O", "ok"), ("R", "ok"), (" ", "espacio"),
        ("J", "nd"), ("O", "ok"), ("S", "nd"), ("E", "ok"), (" ", "espacio"),
        ("D", "ok"), ("O", "ok"), ("S", "nd"),
    ]


def test_estructura_de_cada_paso(texto):
    pasos = texto.a_secuencia("ña h")
    assert pasos == [
        {"c": "Ñ", "l": "n", "tipo": "aprox"},
        {"c": "A", "l": "a", "tipo": "ok"},
        {"c": " ", "l": None, "tipo": "espacio"},
        {"c": "H", "l": None, "tipo": "nd"},
    ]


@pytest.mark.parametrize("entrada, esperado", [
    ("áéíóú", [("A", "ok"), ("E", "ok"), ("I", "ok"), ("O", "ok"), ("U", "ok")]),
    ("üÜ", [("U", "ok"), ("U", "ok")]),
    ("Ñandú", [("Ñ", "aprox"), ("A", "ok"), ("N", "ok"), ("D", "ok"), ("U", "ok")]),
    ("1", [("U", "ok"), ("N", "ok"), ("O", "ok")]),
    ("gh", [("G", "nd"), ("H", "nd")]),
    ("jsz", [("J", "nd"), ("S", "nd"), ("Z", "nd")]),
])
def test_tildes_enie_numeros_y_no_disponibles(texto, entrada, esperado):
    assert tipos(texto.a_secuencia(entrada)) == esperado


@pytest.mark.parametrize("entrada, esperado", [
    ("a , b", [("A", "ok"), (" ", "espacio"), ("B", "ok")]),       # espacios seguidos se juntan
    ("¡Hola, mundo!", [("H", "nd"), ("O", "ok"), ("L", "ok"), ("A", "ok"), (" ", "espacio"),
                       ("M", "ok"), ("U", "ok"), ("N", "ok"), ("D", "ok"), ("O", "ok")]),
    ("  a  ", [("A", "ok")]),
    ("a ¿?", [("A", "ok")]),                                        # sin espacio final
    ("¡¿?!", []),
    ("", []),
])
def test_espacios_y_puntuacion(texto, entrada, esperado):
    assert tipos(texto.a_secuencia(entrada)) == esperado


def test_letras_repetidas_se_conservan_en_la_secuencia(texto):
    # La regla de abrir la mano entre letras iguales está en el hilo de la mano, no aquí
    assert tipos(texto.a_secuencia("calle")) == [("C", "ok"), ("A", "ok"), ("L", "ok"), ("L", "ok"), ("E", "ok")]
    assert tipos(texto.a_secuencia("carro")) == [("C", "ok"), ("A", "ok"), ("R", "ok"), ("R", "ok"), ("O", "ok")]


def test_letras_que_reporta_la_mano(texto):
    assert tipos(texto.a_secuencia("gh", set("gh"))) == [("G", "ok"), ("H", "ok")]
    # Ñ sin N disponible: no se puede aproximar
    assert tipos(texto.a_secuencia("ñ", set("a"))) == [("Ñ", "nd")]
    # Conjunto vacío o None → letras por defecto
    assert tipos(texto.a_secuencia("gh", set())) == [("G", "nd"), ("H", "nd")]
    assert tipos(texto.a_secuencia("a", None)) == [("A", "ok")]
```

## `scripts/armar_main_placa.py`

```python
"""Arma firmware/esp32/main.py: el código original del autor + el bloque agregado (Bluetooth).

main.py = original/main_original.py copiado EXACTAMENTE hasta la línea
"# ---------------- BUCLE PRINCIPAL ----------------" (incluida)
        + original/bucle_ble.py (lo único agregado, marcado con INICIO/FIN).

Si cambias el original (pines, valores, letras), vuelve a correr:
    py -3.11 scripts/armar_main_placa.py
"""
from pathlib import Path

ESP = Path(__file__).resolve().parent.parent / "firmware" / "esp32"
MARCA = "# ---------------- BUCLE PRINCIPAL ----------------"


def armar():
    original = (ESP / "original" / "main_original.py").read_text(encoding="utf-8")
    fin_marca = original.index(MARCA) + len(MARCA)
    fin_linea = original.index("\n", fin_marca) + 1
    bloque = (ESP / "original" / "bucle_ble.py").read_text(encoding="utf-8")
    return original[:fin_linea] + bloque


def main():
    texto = armar()
    destino = ESP / "main.py"
    destino.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{destino.relative_to(ESP.parent.parent)}: {texto.count(chr(10))} líneas "
          f"(original hasta la línea {texto[:texto.index(MARCA)].count(chr(10)) + 1})")


if __name__ == "__main__":
    main()
```

## `scripts/diagnostico_kinect.py`

```python
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
            informar("AVISO", f"Llegan pocas imágenes: {fps:.1f} por segundo (lo normal es 12-18 con la app del 27/10)",
                     "Cierra programas pesados; revisa que el portátil esté conectado a la corriente")
        else:
            informar("OK", f"Llegan {fps:.1f} imágenes por segundo al detector (lo normal es 12-18 con la app del 27/10)")
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
```

## `scripts/generar_codigo_completo.py`

````python
"""Genera docs/CODIGO_COMPLETO.md: todo el código fuente del proyecto, tal cual, para el informe.

Uso:  py -3.11 scripts/generar_codigo_completo.py
"""
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETAS = ["pgc", "web", "firmware/esp32", "tests", "scripts"]
RAICES = ["servidor.py", "iniciar.bat", ".env.example", "requirements.txt", "requirements-dev.txt",
          "requirements-gpu.txt", "pytest.ini", ".gitignore", "datos/letras.json", "datos/palabras_bloqueadas.txt"]
EXCLUIR = {"referencia_doby"}                   # código de otro proyecto
LENGUAJE = {".py": "python", ".html": "html", ".json": "json", ".md": "markdown", ".bat": "bat", ".ini": "ini",
            ".txt": "text", ".example": "ini"}


def archivos():
    vistos = [RAIZ / r for r in RAICES]
    for carpeta in CARPETAS:
        for ruta in sorted((RAIZ / carpeta).rglob("*")):
            if ruta.is_file() and ruta.suffix in LENGUAJE and "__pycache__" not in ruta.parts \
                    and not EXCLUIR & set(ruta.parts) and ruta.name not in ("config_wifi.py", "config_ble.py"):
                vistos.append(ruta)
    return [r for r in vistos if r.exists()]


def main():
    lista = archivos()
    partes = [f"# Código completo del proyecto\n\nGenerado el {time.strftime('%d/%m/%Y %H:%M')} con "
              "`scripts/generar_codigo_completo.py`, a partir de los archivos actuales (no se edita a mano). "
              "No incluye el firmware de Doby (otro proyecto) ni secretos (`.env`, `config_ble.py`).\n\n## Índice\n"]
    partes += [f"- `{r.relative_to(RAIZ).as_posix()}`" for r in lista]
    total = 0
    for ruta in lista:
        texto = ruta.read_text(encoding="utf-8").rstrip("\n")
        total += texto.count("\n") + 1
        cerca = "````" if "```" in texto else "```"
        partes.append(f"\n## `{ruta.relative_to(RAIZ).as_posix()}`\n\n{cerca}{LENGUAJE.get(ruta.suffix, '')}\n{texto}\n{cerca}")
    destino = RAIZ / "docs" / "CODIGO_COMPLETO.md"
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")
    print(f"{destino.relative_to(RAIZ)}: {len(lista)} archivos, {total} líneas")


if __name__ == "__main__":
    main()
````

## `scripts/prueba_e2e.py`

```python
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
PUERTO = 8768                     # no el 8765: ese es el del detector del Kinect
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
    # Plataforma simulada: sin el detector real del Kinect ni la voz de salida (los prueba prueba_servicios_reales.py)
    entorno = {**os.environ, "PGC_RECONOCEDOR": "simulado", "PGC_VOZ_SALIDA": "false", "PGC_KINECT_LANZAR": "false"}
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
```

## `scripts/prueba_navegador.py`

```python
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


def cerrar_edge(proc, perfil=None):
    """Cierra Edge y todos sus procesos.

    terminate() no basta: el msedge.exe que se lanza le pasa el control a OTRO proceso principal y
    termina, y ese queda vivo con sus renderizadores. Por eso se cierran también, con su árbol, los
    procesos que usan el perfil temporal de esta prueba (es único por ejecución).
    """
    subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    if perfil:
        consulta = (f"Get-CimInstance Win32_Process -Filter \"Name='msedge.exe'\" | "
                    f"Where-Object {{ $_.CommandLine -like '*{Path(perfil).name}*' }} | "
                    "ForEach-Object { taskkill /PID $_.ProcessId /T /F | Out-Null }")
        subprocess.run(["powershell", "-NoProfile", "-Command", consulta], capture_output=True)


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
            cerrar_edge(edge, perfil)
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
```

## `scripts/prueba_servicios_reales.py`

```python
"""Prueba con servicios reales: Whisper (GPU o CPU), voz de salida (Coqui), detector del Kinect y túnel HTTPS.

Necesita internet. La mano va simulada. Genera un audio en español con la voz de
Windows (System.Speech) y lo transcribe en local y por el túnel. Comprueba que
Whisper, Coqui y el detector real (si está .venv-detector) conviven en el mismo
arranque, y que la cámara del Kinect nunca sale por el túnel.

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
            d = esperar_estado(lambda d: d["voz_salida"]["estado"] in ("listo", "error"), 240, "la voz de salida cargó")
            comprobar(bool(d) and d["voz_salida"]["estado"] == "listo", "voz de salida (Coqui VITS) lista")
            d = esperar_estado(lambda d: d["kinect"]["conectado"], 60, "el detector del Kinect arrancó")
            comprobar(bool(d), "detector del Kinect arrancado por la plataforma (necesita .venv-detector)")
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
                r = reintentar(lambda: httpx.get(url + "/api/kinect/imagen", timeout=20))
                comprobar(r.status_code == 403, "la cámara del Kinect por el túnel → 403")
        finally:
            proceso.terminate()
            try:
                proceso.wait(15)
            except subprocess.TimeoutExpired:
                proceso.kill()
            salida.seek(0)
            registro = salida.read().decode("utf-8", errors="replace")
            print("\n--- log del servidor (voz, túnel y Kinect) ---")
            print("\n".join(l for l in registro.splitlines() if "[voz]" in l or "[tunel]" in l or "[kinect]" in l))
    print("\nRESULTADO:", "TODO PASA" if not fallos else f"{len(fallos)} FALLA(N)")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
```

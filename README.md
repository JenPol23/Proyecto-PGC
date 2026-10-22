# Mano robótica bidireccional en Lengua de Señas Colombiana (LSC)

Proyecto de grado (PGC) · Ingeniería de Sistemas y Computación · Universidad de Cundinamarca, extensión Facatativá.
Autores: Jean Paul Miranda Díaz, Lina Tatiana Maldonado Rivera, Paula Camila Enríquez Galindo, Jean Harry Raigozo.

Sistema de comunicación en dos sentidos:

1. **Texto → señas con la mano.** Una persona escanea un QR, escribe o graba un mensaje en su celular, y una mano robótica (ESP32-S3 con 6 servos) lo deletrea con el alfabeto manual de la LSC.
2. **Kinect → texto y voz con IA.** La persona hace el alfabeto manual frente al Kinect. El PC lo reconoce con modelos de IA entrenados por el equipo, y lo muestra en pantalla y lo dice en voz alta.

También habrá un **modo eco**: lo que reconoce el Kinect, la mano lo repite.

> **Estado:** la plataforma (parte 1) está construida y probada sin hardware. La parte del Kinect está por integrarse. El detalle de lo probado y lo pendiente está en [ESTADO_FASE1.md](ESTADO_FASE1.md).

## Estructura de carpetas

| Carpeta | Qué contiene |
|---|---|
| `pgc/` | El servidor de la plataforma (FastAPI). Se ejecuta con `python -m pgc` |
| `pgc/dominio/` | Reglas puras, sin dependencias: texto → letras, letras disponibles, filtro de palabras, nombres |
| `pgc/aplicacion/` | Casos de uso: cola de mensajes, hilo que mueve la mano, estado en vivo, participantes, señas |
| `pgc/puertos/` | Interfaces que conectan la aplicación con el exterior: mano, transcriptor, sintetizador, reconocedor de señas, acceso público |
| `pgc/adaptadores/` | Implementaciones de esas interfaces: mano por Bluetooth, USB o simulada, Whisper, túnel HTTPS, reconocedor simulado |
| `pgc/adaptadores/kinect/` | **Aquí va el reconocimiento de señas con el Kinect** (ver [docs/CONTRATO_KINECT.md](docs/CONTRATO_KINECT.md)) |
| `pgc/api/` | Rutas web, WebSocket y seguridad |
| `web/` | Página del celular (`movil.html`), pantalla del proyector (`pantalla.html`) y logo |
| `firmware/esp32/` | Firmware MicroPython de la mano: `main.py` es el que va en la placa y `protocolo.md` explica las órdenes |
| `firmware/esp32/original/` | Código original de la mano, que sirve de referencia para las pruebas |
| `firmware/esp32/referencia_doby/` | Código de otro proyecto, solo como referencia |
| `datos/` | Letras que sabe hacer la mano (`letras.json`) y palabras bloqueadas |
| `docs/` | Arquitectura, contrato del Kinect, guía para modificar la mano y código completo generado |
| `tests/` | Pruebas automáticas con pytest. Funcionan sin hardware ni internet |
| `tests/contratos/` | Pruebas que comprueban que el reconocedor del Kinect cumpla el contrato |
| `scripts/` | Pruebas de punta a punta, con servicios reales y en el navegador |

Archivos que **no** están en el repositorio porque llevan secretos: `.env` (configuración del PC) y `firmware/esp32/config_ble.py` (configuración de la placa).

## Requisitos

### Hardware

- **Mano robótica:** ESP32-S3 N16R8 con MicroPython y 6 servos (índice, medio, anular, meñique y dos para el pulgar), en una PCB con regulador LM2596 y entrada de 12 V.
  - **Nunca conectes el USB y los 12 V a la vez.** El USB solo sirve para subir archivos con Thonny (sin 12 V los servos no se mueven). Con 12 V, la mano recibe las órdenes por Bluetooth.
- **Conexión con el PC:** Bluetooth BLE. La placa aparece como `Mano-LSC`. **No hay que emparejarla en Windows**, solo tener el Bluetooth del PC encendido. Alcance: unos 10 m.
- **Kinect v1 (Xbox 360)** con su adaptador, y Kinect for Windows SDK v1.8. Solo para la parte de reconocimiento de señas.
- **PC con Windows.** El PC de la demo tiene una GPU NVIDIA RTX 5050. Sin GPU NVIDIA, el reconocimiento de voz funciona en CPU (más lento; pendiente de confirmar cuánto).

No necesitas la mano para trabajar: la plataforma tiene un **modo simulado**.

### Software

- **Python 3.11.**
- **Dependencias** (versiones fijas):
  - [`requirements-dev.txt`](requirements-dev.txt): las de la plataforma ([`requirements.txt`](requirements.txt)) más `pytest`, `httpx` y `pip-audit`, para pruebas y auditoría.
  - [`requirements-gpu.txt`](requirements-gpu.txt): torch con CUDA 12.8, mediapipe, opencv y coqui-tts. Solo hacen falta para el Kinect, los modelos propios y la voz de salida.
- **cloudflared** (opcional): crea el enlace HTTPS público para el QR. Sin él, la plataforma funciona solo en la red local y el micrófono del celular no se puede usar; queda la opción de subir una nota de voz.

## Instalación paso a paso

Los comandos son para PowerShell en Windows.

1. **Clonar el repositorio:**
   ```powershell
   git clone https://github.com/JenPol23/Proyecto-PGC.git
   cd Proyecto-PGC
   ```

2. **Crear y activar el entorno virtual:**
   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python --version     # debe decir Python 3.11.x
   ```
   Si PowerShell no deja ejecutar `Activate.ps1`, ejecuta antes `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`. Ese permiso solo dura mientras esté abierta esa ventana.

   > **Importante:** con el entorno virtual activado, usa `python` y no `py -3.11`. Lo comprobamos: `py -3.11` ignora el entorno virtual y usa el Python del sistema. Por eso los comandos de este README usan `python`.

3. **Instalar las dependencias:**
   ```powershell
   python -m pip install -r requirements-dev.txt
   ```
   Para la parte del Kinect y la IA, instala además:
   ```powershell
   python -m pip install -r requirements-gpu.txt --extra-index-url https://download.pytorch.org/whl/cu128
   ```
   El autor trabaja con el Python 3.11 del sistema, no con un entorno virtual. Que la instalación funcione completa en un entorno virtual nuevo está **pendiente de confirmar**, igual que `requirements-gpu.txt` en un PC sin GPU NVIDIA. Si algo falla, avísale al dueño del proyecto con el mensaje de error.

4. **Crear tu `.env`:**
   ```powershell
   Copy-Item .env.example .env
   ```
   En `.env.example` todas las variables están comentadas, así que la plataforma arranca con valores por defecto. **Pide al dueño del proyecto (Jean Paul) los valores reales** que necesites, por ejemplo el token de la mano por Bluetooth (`PGC_MANO_BLE_TOKEN`). No pongas valores inventados. El `.env` es personal: no lo subas ni lo compartas.

5. **(Opcional) Instalar cloudflared** para el enlace HTTPS:
   ```powershell
   winget install Cloudflare.cloudflared
   ```

La primera vez que arranques con voz, el modelo de Whisper (`medium`) se descarga de Hugging Face, así que necesitas internet. Para arrancar sin voz, usa `--sin-voz`.

## Cómo ejecutar la aplicación

Con el entorno virtual activado:

```powershell
python -m pgc --simular
```

- Se abre sola la **pantalla del proyector**: `http://127.0.0.1:8000/pantalla`.
- La **página del celular** está en `http://127.0.0.1:8000/`. Desde un celular, escanea el QR de la pantalla.
- Para detener el servidor: **Ctrl+C**.

Opciones útiles:

| Opción | Qué hace |
|---|---|
| `--simular` | No busca la mano y la simula |
| `--sin-voz` | No carga Whisper (arranque rápido) |
| `--sin-tunel` | No lanza cloudflared (solo red local) |
| `--no-abrir` | No abre el navegador |
| `--puerto COM5` | Puerto USB fijo de la mano |
| `--puerto-web 8001` | Otro puerto web (por defecto 8000) |
| `--dev` | Publica la documentación automática de la API en `/docs` |

En el PC de la demo se usa `iniciar.bat` (doble clic). Ese archivo ejecuta `py -3.11 -m pgc`, es decir, el **Python del sistema** y no tu entorno virtual.

## Cómo correr las pruebas

```powershell
python -m pytest
```

Corre todas las pruebas de `tests/` sin hardware ni internet. En el PC del autor pasan las **431 pruebas en unos 20 segundos** (comprobado el 22/10/2026 con el Python del sistema).

**Pruebas de contrato del Kinect.** Córrelas antes de entregar tu parte. Comprueban que tu reconocedor cumpla [docs/CONTRATO_KINECT.md](docs/CONTRATO_KINECT.md), sin necesitar la mano ni el servidor:

```powershell
python -m pytest tests/contratos --reconocedor=pgc.adaptadores.kinect.reconocedor:ReconocedorKinect
```

Para ver tu reconocedor en vivo:
1. Pon `PGC_RECONOCEDOR=pgc.adaptadores.kinect.reconocedor:ReconocedorKinect` en tu `.env`.
2. Arranca con `python -m pgc --simular` y abre `http://127.0.0.1:8000/pantalla`.

Si tu clase falla al iniciar, la plataforma usa un reconocedor simulado y el proyector muestra "Kinect: no disponible", así que la demo no se cae.

Otras pruebas, en `scripts/`:
- `prueba_e2e.py`: de punta a punta en modo simulado.
- `prueba_servicios_reales.py`: Whisper y el túnel reales; necesita internet.
- `prueba_navegador.py`: usa Microsoft Edge.

## Reglas importantes

- **No modifiques `firmware/esp32/main.py`.** Es el código original de la mano, y las pruebas exigen que siga idéntico. Si hay que cambiar la mano, sigue [docs/GUIA_MODIFICAR_MANO.md](docs/GUIA_MODIFICAR_MANO.md).
- Tu código del Kinect va en `pgc/adaptadores/kinect/`. Si necesitas cambiar algo fuera de esa carpeta, pregunta antes.
- Nunca subas tokens, contraseñas ni el archivo `.env`.

## Trabajo en equipo

El flujo de ramas y Pull Requests, los responsables de cada parte y los pendientes están en **[HANDOFF.md](HANDOFF.md)**. En resumen: crea tu propia rama, súbela y abre un Pull Request hacia `main`. No hagas push directo a `main`.

Para entender cómo encaja todo: [docs/ARQUITECTURA.md](docs/ARQUITECTURA.md).

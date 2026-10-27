# Proyecto de grado: Mano robótica bidireccional en Lengua de Señas Colombiana (LSC)

PGC (Proyecto de Gestión del Conocimiento) · Ingeniería de Sistemas y Computación · Universidad de Cundinamarca, extensión Facatativá · 9.º semestre.
Autores: Jean Paul Miranda Díaz, Lina Tatiana Maldonado Rivera, Paula Camila Enríquez Galindo, Jean Harry Raigozo.
- **Parte de Jean Paul** (este repositorio): la mano robótica, su firmware y la plataforma web que integra todo.
- **Parte de los compañeros** (Camila: `integracion_kinect/`): el Kinect y el reconocimiento de señas. Se conectan por un contrato (`docs/CONTRATO_KINECT.md`, v1.1); desde el 26/10/2026 están integrados en la plataforma (ADR-9): un solo arranque, una sola página y una sola pantalla.

Es la **sustentación final de carrera** ante jurados: prioridad absoluta a que todo funcione de forma estable en vivo.

## Qué hace el sistema
1. **Texto/voz → mano**: un jurado escanea un QR, abre una página en su celular y escribe o graba audio. El PC transcribe (Whisper) y la mano deletrea el mensaje en el alfabeto de la **LSC**.
2. **Kinect → texto/voz** (integrado): el jurado hace el alfabeto manual frente al Kinect; el detector del equipo lo reconoce (MediaPipe + SVM), el texto se ve en vivo en el celular y en el proyector, y al tocar «Terminar» la frase se dice en voz alta (Coqui) por los parlantes del PC.
3. **Modo eco** (lo activa el presentador en el proyector): la frase que reconoce el Kinect va a la cola de la mano como un mensaje de "Kinect".

## Decisiones ya tomadas (no cambiar sin preguntar)
- **Arquitectura hexagonal** (puertos y adaptadores), documentada en `docs/ARQUITECTURA.md` con sus ADR.
- **Mano por Bluetooth BLE** (`PGC_MANO=ble` en el `.env`; antes era WiFi, se cambió el 22/10/2026). El ESP32-S3 solo tiene BLE: servicio UART de Nordic, nombre `Mano-LSC`, NO emparejar en Windows; en el PC, bleak **en un proceso aparte** (`ble_puente.py`), porque WinRT y faster-whisper en el mismo proceso tumban Python (access violation). En la PCB de la mano **no se pueden conectar USB y 12 V a la vez**: el USB es solo para subir archivos (sin 12 V, los servos no se mueven); con 12 V la mano funciona solo por Bluetooth. El código admite también `auto|usb|simulada` (USB sirve para pruebas sin fuerza). El PC es el servidor central.
- **Servidor**: Python 3.11 del sistema (`py -3.11`), con torch 2.11+cu128 y CUDA en la RTX 5050 (sm_120), mediapipe 0.10.9, coqui-tts 0.27.5 y faster-whisper. Las versiones están fijadas en `requirements*.txt`.
  - NO usar el venv viejo de la carpeta `kinect` (apunta a otro PC, está roto).
- **Web**: FastAPI + WebSocket. Páginas **sin dependencias de internet** (fuentes del sistema, CSS/JS inline), con tema claro y oscuro.
- **HTTPS**: Cloudflare quick tunnel (la URL `*.trycloudflare.com` va al QR). Sin internet, el QR usa `http://IP:8000` y el plan B es subir una nota de voz. cloudflared queda atado al proceso (no queda huérfano).
- **Cola**: la mano hace un mensaje a la vez. Máximo 60 caracteres por mensaje y 2 pendientes por celular. Cada celular ve su posición.
- **Participantes**: nombre opcional (máx. 20 caracteres, filtrado; en el celular vive en `sessionStorage`; en el servidor solo en memoria). El presentador puede **bloquear** a alguien durante la sesión: se cancelan sus pendientes y se salta su mensaje en curso. **Sin inicio de sesión** ni expulsión por inactividad (ADR-7, Ley 1581).
- **Seguridad** (`docs/ARQUITECTURA.md` §B):
  - token de administrador por arranque, que solo recibe `/pantalla` abierta en el PC;
  - CSP con nonce y encabezados de seguridad;
  - límites de peticiones (IP real tras el túnel y cliente);
  - validación amable en español;
  - audio validado (tipo, firma, ≤ 15 s);
  - filtro de palabras ofensivas (`datos/palabras_bloqueadas.txt`);
  - logs sin textos ni nombres;
  - `/docs` solo con `--dev`.
- **Kinect** (ADR-9): el detector y la app C# de `integracion_kinect/` se usan **tal cual**, en procesos aparte (el detector con el Python de `.venv-detector`: sus versiones no caben en el de la plataforma). `pgc/adaptadores/kinect/reconocedor.py` es el único que habla con el detector (`/spell/status` cada 0,3 s → eventos del contrato; con el proyector mirando la cámara, imagen cada 30 ms y estado con cada imagen nueva, para que coincidan; el proyector recibe cada cuadro con espera larga) y todo llega a las pantallas por el WebSocket (los celulares no consultan nada). **Un jurado a la vez** controla el Kinect con un **turno** (se libera solo tras 120 s sin usarlo; el presentador controla siempre y puede liberarlo; bloquear quita el turno); reemplazó al código de 8 dígitos. La imagen de la cámara **solo** se ve en el proyector del PC (token), nunca por el túnel. Sin detector o sin imágenes: "Kinect no conectado". Con el turno, el celular tiene todos los controles (Iniciar, Detener, Espacio, Borrar, Limpiar, Terminar y decirlo, Eco) y cualquiera Guardar TXT, Leer frase y Detener voz. Al arrancar, el lanzador cierra restos (detector, app C#, cámara del PC) de ejecuciones anteriores; si ya hay otra plataforma en el puerto, `iniciar.bat` no arranca otra (código 3). **Diagnóstico** (solo PC, `/diagnostico`, ADR-11): mano detectada, letra posible, 2.ª opción y margen del SVM (no es probabilidad), tiempo estable y por qué no se confirma; protocolo de prueba de letras que guarda CSV, gráficas e informe en `experimentos/<fecha_hora>/`.
- **Voz entrada**: faster-whisper `medium` (caché HF `Systran/faster-whisper-medium`), `language="es"`, `vad_filter=True`, CUDA float16 con calentamiento y CPU int8 de respaldo. El jurado revisa la transcripción antes de enviarla.
- **Voz salida**: Coqui VITS español `tts_models/es/css10/vits` (en caché en `%LOCALAPPDATA%\tts\…`), en CPU (carga ~10–50 s en segundo plano, ~0,1 s por frase), por sounddevice: `pgc/adaptadores/voz_salida.py`. Alternativa: XTTS v2.

## Estructura del código
```
pgc/            paquete de la plataforma (py -3.11 -m pgc)
  config.py     configuración: valores por defecto < .env < variables PGC_* < opciones de línea de comandos
  arranque.py   único lugar que conoce los adaptadores concretos
  dominio/      reglas puras: texto→secuencia, letras (datos/letras.json), regla de repetidas, moderación, nombres
  aplicacion/   cola, hilo de la mano (Deletreador), estado en vivo, participantes, señas (Kinect) y turno del Kinect
  puertos/      interfaces: mano, transcriptor, sintetizador, reconocedor (Kinect), acceso público
  adaptadores/  mano_usb, mano_ble (+ ble_puente), mano_simulada, mano_respaldo, whisper, voz_salida (Coqui), acceso (túnel), reconocedor_simulado,
                kinect/ (reconocedor.py = adaptador del detector, procesos.py = lanza detector y app C#, camara_pc.py = cámara del PC)
  api/          FastAPI: app, seguridad, esquemas, rutas (páginas, mensajes, voz, participantes, admin, kinect, ws)
web/            movil.html, pantalla.html, logo-udec.png
firmware/esp32/ main.py (el ÚNICO archivo de la mano en la placa, + config_ble.py), prueba_dedos.py, protocolo.md;
                original/ = main_original.py (código del autor) + bucle_ble.py (lo agregado); referencia_doby/ = otro proyecto
integracion_kinect/  parte de Camila, se usa TAL CUAL (no modificar): detector/ (server_web_svm.py :8765, modelo_estaticas.joblib) y capturador/ (app C#)
datos/          letras.json, palabras_bloqueadas.txt
tests/          pruebas (pytest); tests/contratos/ para el reconocedor; tests/detector_falso.py habla como el detector real
scripts/        prueba_e2e.py, prueba_servicios_reales.py, prueba_navegador.py, generar_codigo_completo.py
docs/           ARQUITECTURA.md, CONTRATO_KINECT.md, CODIGO_COMPLETO.md (generado)
servidor.py     atajo de arranque (= py -3.11 -m pgc)
iniciar.bat     arranque único: plataforma + detector + app del Kinect; instalar_detector.bat prepara .venv-detector una vez
iniciar_pgc_integrado.py, acceso_kinect.py   OBSOLETOS (de Camila): se conservan sin cambios
```
Regla de dependencias, comprobada por pruebas: `dominio` no importa nada del proyecto; `aplicacion` solo usa `dominio` y `puertos`; `api` no conoce los adaptadores.

## Hardware
- PC: portátil Windows 11 Pro, RTX 5050 8 GB. Sin CUDA toolkit (no se necesita). Git sí: repositorio https://github.com/JenPol23/Proyecto-PGC (ramas y Pull Requests, ver HANDOFF.md). Visual Studio Build Tools 2022 con el paquete de .NET 4.8 (instalado el 27/10/2026): la app C# se compila aquí con `MSBuild LSCKinectFramework.csproj /t:Rebuild /p:Configuration=Release`.
- Mano: ESP32-S3 N16R8 + MicroPython, 6 servos (índice GPIO8, meñique GPIO3, medio GPIO10, anular GPIO4 invertido, pulgar GPIO6 invertido, pulgar2 GPIO7), según `dedos_config` del código original (`firmware/esp32/original/main_original.py`). PCB casera con LM2596 y jack 12 V. **USB y 12 V nunca a la vez** (USB = subir archivos sin 12 V; 12 V = mano por Bluetooth).
  - GPIO3 es pin de arranque del S3: si la placa no arranca con los servos conectados, mover el meñique.
  - La placa es **exclusiva de la mano** (lo de Doby, otro proyecto del autor, está desmontado). Si se volviera a usar para Doby, hay conflicto en los GPIO 4, 6, 7 y 10.
- **Kinect v1 (Xbox 360)** con adaptador; Kinect for Windows SDK **v1.8**. Con SDK 1.8 el Kinect v1 NO aparece como webcam para OpenCV.
  - Hecho por Camila: app C# (SDK 1.8, .NET 4.8) que envía la imagen de color (640×480) en JPEG a `POST 127.0.0.1:8765/detect`. **Única modificación a su código (27/10/2026, autorizada por el autor y avisada a ella)**: la espera entre imágenes pasó de 100 a 50 ms (`AddMilliseconds(50)` en `MainWindow.xaml.cs`), ~17/s. Se compila aquí en Release con VS Build Tools 2022 (`bin\Release`, fuera de git); la versión vieja está en `respaldos\2026-10-27_app_kinect_debug_25oct`. El detector se sirve con `pgc/adaptadores/kinect/detector_paralelo.py`, que envuelve su `server_web_svm.py` sin cambiarlo (lecturas en paralelo; `PGC_KINECT_DETECTOR_PARALELO=false` vuelve al original); el detector aplica MediaPipe Hands sobre la imagen completa. Sin Kinect se prueba con la cámara del PC (`PGC_KINECT_CAPTURADOR=camara_pc`).

## Protocolo de la mano (`firmware/esp32/protocolo.md`)
**REGLA ABSOLUTA del autor**: `firmware/esp32/main.py` es SU CÓDIGO ORIGINAL copiado EXACTAMENTE (líneas 1–225 = `original/main_original.py`: mismos pines, valores, funciones, tiempos, textos y orden). NO reorganizarlo, NO separarlo en módulos, NO "mejorarlo", NO usar letras.json. Lo único agregado es el bloque que reemplaza el BUCLE PRINCIPAL (`original/bucle_ble.py`, marcado `>>> INICIO DE LO AGREGADO` / `<<< FIN DE LO AGREGADO`) para recibir las mismas órdenes también por Bluetooth. `main.py` se arma con `scripts/armar_main_placa.py`; las pruebas exigen que sea idéntico y que se comporte igual. Para modificar la mano: `docs/GUIA_MODIFICAR_MANO.md`.

Órdenes y respuestas (las del código original, iguales por USB y por Bluetooth, UART de Nordic: RX 6E400002, TX 6E400003, paquetes de 20 bytes):
- `<letra>` → `reset_all()` + la letra → `gesto_<letra>_ok`; letra que no está → `comando_no_reconocido`; `reset` o `1` → `reset_ok`; una palabra → `deletrear()`.
- **El firmware no tiene `ping` ni `letras`** (los deletrearía como palabras). El PC comprueba la conexión con `reset`, envía siempre letra por letra y toma las letras disponibles de `datos/letras.json`.
- Por Bluetooth, la primera línea es `auth <token>` (`ok:auth` / `error:auth`, 3 s; token compartido entre `config_ble.py` y `PGC_MANO_BLE_TOKEN`). Un solo PC a la vez (conectado, la placa deja de anunciarse). Alcance ~10 m.
- Sin vigilante: la mano no se suelta sin el PC.
- Letras (21), las de `acciones` del código original: `a b c d e f i k l m n o p q r t u v w x y`. Faltan g h j s z (j, z, ñ llevan movimiento; la mano no tiene muñeca → limitación documentada). ñ se aproxima con n.
- Cada letra tarda ~1–2,5 s (dedos uno por uno, a propósito). El PC SIEMPRE espera la confirmación antes de la siguiente letra.

## Parte de IA (aporte propio del equipo)
- Extractor: MediaPipe Hands (preentrenado, 21 puntos 3D); se declara como tal.
- **Modelo actual (el que se usa): SVM** (scikit-learn 1.5.2, kernel RBF, C=3, `class_weight="balanced"`, con `StandardScaler`) sobre **89 características de los 21 puntos de MediaPipe**, entrenado por el equipo con `integracion_kinect/detector/entrenar_estaticas.py` y **dataset propio** (`dataset_alfabeto/`, no está en el repositorio). 27 categorías: 26 letras + `sin_letra`. Una letra se confirma si la misma predicción dura ≥ 0,7 s y ≥ 4 imágenes; hay que retirar la mano 0,5 s entre letras. Archivo: `modelo_estaticas.joblib` (se carga solo con scikit-learn 1.5.2).
- Pendiente de Camila: dataset, métricas del SVM (exactitud, matriz de confusión, latencia) y confianza/latencia por letra en `/spell/status`.
- Plan original (no implementado; queda como trabajo futuro o comparación): A MLP sobre puntos, B LSTM/GRU sobre secuencias para letras con movimiento, C CNN sobre el recorte de profundidad, corrector LSTM por caracteres.
- `ASL-Alphabet-Detection-main` es de terceros y del alfabeto americano: solo referencia.
- Código heredado útil (en `C:\Users\miran\kinect`, comprado a Duvan, con permiso de modificarlo): `servidor_dashboard.py`, `dashboard.html`, `hablar_texto()` / `enviar_a_mano()` de `dibujar.py`.

## Plan por fases
1. ✅ Plataforma: servidor, página móvil, pantalla del proyector, túnel, seguridad, participantes, mano por USB y Bluetooth (falta probar con la mano y celulares reales: ver ESTADO_FASE1.md §6).
2. ✅ Lectura del Kinect v1 (app C# de Camila) y MediaPipe en el detector. Falta verificar a distancia real con el Kinect físico.
3. ✅ Grabación del dataset (scripts de Camila en `integracion_kinect/detector/`).
4. ✅ Modelo SVM + reconocimiento en tiempo real + TTS (Coqui). Falta: métricas del SVM.
5. ✅ Integración (26/10/2026, rama `integracion-unificada`): pestaña Kinect en la página, vista Kinect en el proyector, turno, modo eco, un solo arranque, prueba con 30 celulares. Falta: el `.exe` compilado y la prueba con el Kinect físico.

## Cómo se prueba
- `py -3.11 -m pytest`: unas 476 pruebas, sin hardware ni internet, en ~35 s. Ejecutan el `main.py` de la placa y el código original del autor en el PC y comparan texto (líneas 1–225), pulsos, pausas y respuestas, por USB y por Bluetooth (radio BLE falsa y un bleak falso), incluido un recorrido de punta a punta.
- `py -3.11 scripts/prueba_e2e.py`: de punta a punta en modo simulado.
- `py -3.11 scripts/prueba_servicios_reales.py`: Whisper en la GPU, Coqui, el detector real del Kinect (necesita `.venv-detector`) y el túnel real (necesita internet).
- `py -3.11 scripts/prueba_navegador.py [--tema light]`: Edge real, también por el túnel.

## Reglas de trabajo
- Responder y comentar el código en español.
- No borrar ni modificar nada en `C:\Users\miran\kinect` (solo leer de ahí).
- Probar cada pieza antes de pasar a la siguiente. Antes de un cambio grande, copia de respaldo en `respaldos\` (además de git; ahí solo se deja el último), **sin secretos**: `robocopy . respaldos\<fecha>_<motivo> /E /XD __pycache__ capturas respaldos .pytest_cache .git .venv .venv-detector registros /XF .env config_ble.py config_wifi.py`, y verificar que el respaldo quedó completo.
- No modificar nada dentro de `integracion_kinect/` (es de Camila): se usa tal cual; avisar al autor antes de cualquier cambio que la afecte.
- Las pruebas de caracterización (`tests/`) fijan el comportamiento: si una cambia, debe ser por una decisión aprobada.
- Nada de rutas absolutas de usuario en el código (rutas relativas o `%LOCALAPPDATA%`). Secretos solo en `.env` (PC) y `config_ble.py` (placa), nunca en el código.

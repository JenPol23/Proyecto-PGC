# Mano robótica bidireccional — guía de trabajo en equipo

Proyecto de grado (sustentación final). Dos partes que se integran en una sola página web con QR para la demo.

## Qué hace el sistema

1. **Texto → mano (modo señas):** la persona escribe texto o envía audio en la página web; la mano robótica (ESP32-S3, MicroPython, 6 servos) deletrea la palabra con el alfabeto de la Lengua de Señas Colombiana.
2. **Kinect → texto/voz (modo lectura):** la cámara (Kinect o cámara del PC mientras no esté disponible) reconoce señas con IA y el computador muestra o dice lo que se señó.

## Qué hay en el repositorio

| Carpeta / archivo | Qué es | Responsable |
|---|---|---|
| `firmware/esp32/` | Código MicroPython de la mano (`main.py` es el que va en la placa; `protocolo.md` explica las órdenes). **No modificar la lógica de movimiento** (ver `docs/GUIA_MODIFICAR_MANO.md`) | Jenpol |
| `pgc/` | Servidor de la plataforma (FastAPI): cola de mensajes, mano por Bluetooth/USB, voz con Whisper, túnel HTTPS | Jenpol |
| `web/` | Página del celular (`movil.html`, se abre con el QR) y pantalla del proyector (`pantalla.html`) | Jenpol |
| `integracion_kinect/` | Reconocimiento de señas: `capturador/` (app C# del Kinect, SDK 1.8) y `detector/` (MediaPipe Hands + **SVM** entrenado por el equipo, servidor en `127.0.0.1:8765`). La plataforma los usa tal cual | Camila |
| `pgc/adaptadores/kinect/` | Conexión del detector con la plataforma: `reconocedor.py` (adaptador del contrato `docs/CONTRATO_KINECT.md`; **pendiente de revisión de Camila**), `procesos.py` (arranca el detector y la app C#) y `camara_pc.py` (cámara del PC en lugar del Kinect) | Jenpol (revisa Camila) |
| `iniciar_pgc_integrado.py`, `acceso_kinect.py` | **Obsoletos** desde el 26/10/2026: `iniciar.bat` ya arranca todo y la pestaña Kinect es parte de la página. Se conservan sin cambios | Camila |
| `tests/` | Pruebas automáticas (`py -3.11 -m pytest`); `tests/contratos/` comprueba que el reconocedor cumpla el contrato | Ambos |
| `docs/` | Arquitectura, contrato del Kinect, guía para modificar la mano | Ambos |
| `datos/` | Letras que hace la mano (`letras.json`) y palabras bloqueadas | Jenpol |
| `scripts/` | Pruebas de punta a punta, con servicios reales y en el navegador | Jenpol |

## Cómo ejecutarlo

1. Instalar dependencias (Python 3.11): `py -3.11 -m pip install -r requirements.txt`
2. Copiar `.env.example` como `.env` (el `.env` **no** está en el repositorio porque lleva secretos).
3. Una sola vez: doble clic en `instalar_detector.bat` (crea `.venv-detector` con las versiones exactas del detector; unos 350 MB).
4. Doble clic en `iniciar.bat`: arranca la plataforma, el detector y la app del Kinect compilada, y los cierra al salir. Sin la mano: `iniciar.bat --simular`. Si falta el detector o el Kinect, la plataforma arranca igual y dice "Kinect no conectado".
5. Sin Kinect, con la cámara del PC: poner `PGC_KINECT_CAPTURADOR=camara_pc` en el `.env`.
6. Pruebas: `py -3.11 -m pytest`.

## Cambio en tu código: espera de 100 a 50 ms en la app del Kinect (27/10/2026)

Camila: la sustentación es en el PC de Jean Paul, así que hicimos aquí los cambios de velocidad (él te avisó). **Solo se cambió una línea de tu código**: en `integracion_kinect/capturador/LSCKinectFramework/MainWindow.xaml.cs`, `DateTime.UtcNow.AddMilliseconds(100)` pasó a `AddMilliseconds(50)`.

- **Por qué:** con 100 ms tu app mandaba como máximo 10 imágenes por segundo, y la vista previa del proyector no podía pasar de ahí. Con 50 ms llegan unas 17 por segundo (el resto lo limita el tiempo que tarda el detector en procesar cada imagen, ~50 ms).
- **Reconocimiento:** tu lógica confirma letras por tiempo (≥ 0,7 s estable y ≥ 4 imágenes; retirar la mano 0,5 s), así que con más imágenes por segundo reconoce las mismas letras. Lo comprobamos con 26 imágenes de prueba: misma secuencia de letras con 10 y con 20 imágenes por segundo.
- **Compilación:** Release, con Visual Studio Build Tools 2022, en `bin\Release` (fuera de git). Tu `.exe` del 25/10 (Debug) quedó guardado en `respaldos\2026-10-27_app_kinect_debug_25oct`.
- **Tu detector no se modificó:** `server_web_svm.py` se usa tal cual, envuelto por `pgc/adaptadores/kinect/detector_paralelo.py`, que lo sirve con `ThreadingHTTPServer` (la vista previa y el estado ya no esperan a que termine cada imagen; las peticiones POST siguen de a una y en orden, como en tu servidor). Para volver a tu servidor original: `PGC_KINECT_DETECTOR_PARALELO=false` en el `.env`.

## Pestaña Kinect de Camila: incorporada en `web/movil.html` (27/10/2026)

Camila, la pestaña Kinect que diseñaste para el celular (la que servía `iniciar_pgc_integrado.py`) ya es parte de la página normal (`web/movil.html`), **con todas sus funciones**, el diseño de la plataforma y el turno de un jurado a la vez en lugar del código de 8 dígitos:

| Tu pestaña | Ahora en `movil.html` |
|---|---|
| Texto deletreado y estado del detector ("Deletreo detenido.", "Posible letra…", "Letra añadida…") | Igual, en vivo por el WebSocket (los celulares no consultan el detector) |
| Activar control / Volver a espectador (con el código del PC) | **Activar control** / **Volver a espectador** con el turno: un solo celular a la vez, se libera solo tras 2 minutos sin usarlo; el presentador lo puede liberar desde el proyector |
| "Modo espectador." / "Control del teléfono activo (hasta 2 horas)." | "Modo espectador." / "Control del teléfono activo (se libera solo tras 2 minutos sin usarlo)." |
| Iniciar, Detener, Espacio, Borrar, Limpiar | Iguales, solo para quien tiene el turno (Limpiar borra todo el texto, sin decirlo) |
| Guardar TXT | Igual (`texto_lsc.txt`), **para todos**, también los espectadores: descarga el texto en curso o, si ya se terminó, la última frase |
| Leer frase / Detener voz (voz del navegador) | Iguales, **para todos**, con tus mensajes ("Leyendo...", "Lectura terminada.", "Lectura detenida.", "No hay una voz en español disponible…"); prefiere una voz de Colombia |
| Ver código / Revocar teléfonos y cambiar código | Reemplazados por **Liberar turno** en el proyector del PC |
| Imagen de la cámara en el celular | **No**: por privacidad (Ley 1581), la cámara solo se ve en el proyector del PC (ADR-9) |
| — | Nuevo: **Terminar y decirlo** (la frase se dice por los parlantes del PC con Coqui y, con el modo eco, la mano la deletrea) |

Tu lanzador `iniciar_pgc_integrado.py` no se modificó y sigue funcionando, pero ya no hace falta.

## Requisitos de hardware y red

- La mano se conecta al PC por **Bluetooth BLE** (nombre `Mano-LSC`; **no** emparejarla en Windows). La placa necesita su `config_ble.py` (copiar `firmware/esp32/config_ble.example.py`), con el mismo token que `PGC_MANO_BLE_TOKEN` del `.env`. Ese archivo tampoco está en el repositorio.
- ESP32-S3 N16R8 con PCB de expansión: **nunca conectar USB y la fuente de 12 V a la vez** (se quema el ESP32).
  - USB: solo para subir archivos con Thonny (sin 12 V los servos no se mueven).
  - 12 V: la mano recibe órdenes por Bluetooth.
- La mano no tiene antebrazo ni muñeca: solo mueve dedos. Las letras que requieren muñeca no se pueden hacer.

## Cómo trabajar con el repositorio

1. Clonar: `git clone https://github.com/JenPol23/Proyecto-PGC.git`
2. Crear una rama para tu parte: `git checkout -b nombre-tu-parte`
3. Trabajar y hacer commits pequeños con mensajes claros.
4. Subir la rama: `git push -u origin nombre-tu-parte`
5. Abrir un Pull Request hacia `main` para revisar antes de integrar.

Nunca hacer push directo a `main` durante el desarrollo.

## Pendientes

- [x] Integrar la página web con el reconocimiento del Kinect (Jenpol, 26/10/2026: rama `integracion-unificada`)
- [ ] Revisar `pgc/adaptadores/kinect/reconocedor.py` y la sección 9 de `docs/CONTRATO_KINECT.md` (Camila)
- [ ] Entregar el dataset, las métricas del SVM, `/spell/status` en JSON con confianza y latencia, y el `.exe` compilado (Camila)
- [ ] Probar el Kinect físico con la app C# lanzada por `iniciar.bat` (Ambos)
- [ ] Probar la página con la mano real por Bluetooth (ya implementado; falta la prueba física) (Jenpol)
- [ ] Validar que cada letra del abecedario se vea bien en la mano (Jenpol)
- [ ] Ajustar el reconocimiento del Kinect al proyecto (Camila)
- [ ] Probar la demo completa con QR en el hotspot del día de la presentación
- [ ] Documentar la metodología para el informe final

## Notas

- El código heredado de la carpeta kinect (dibujar.py, dashboard) fue adaptado con permiso del autor original; mantener la atribución en los archivos.
- El código original de movimiento de la mano funciona; cualquier cambio debe probarse antes de integrarse.

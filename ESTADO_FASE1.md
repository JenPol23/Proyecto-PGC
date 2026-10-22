# Estado de la Fase 1 — Plataforma: servidor, páginas y mano (USB y Bluetooth)

Proyecto: mano robótica bidireccional en LSC · PGC, Ingeniería de Sistemas y Computación, Universidad de Cundinamarca (Facatativá)
Autores: Jean Paul Miranda Díaz, Lina Tatiana Maldonado Rivera, Paula Camila Enríquez Galindo, Jean Harry Raigozo
Pruebas: 14/10/2026 (base) y 20/10/2026 (decisiones, rediseño, reorganización, seguridad, participantes, firmware y WiFi) y 22/10/2026 (mano por Bluetooth) · Documento actualizado: 22/10/2026

## 1. Resumen

La fase 1 está **construida y probada sin hardware**. Además:
- se probó **Whisper en la GPU** con audio real de Windows;
- se probó el **túnel HTTPS real** de Cloudflare;
- las páginas se probaron en un **navegador real** (Edge), en el PC y por el túnel;
- se probó la **mano por Bluetooth con un ESP32 falso** que corre el firmware real (radio BLE falsa), de punta a punta.

**Falta** probarla con la **mano física** (USB y Bluetooth), con **celulares reales** y en el **proyector de la sala** (lista en §6).

El 20/10/2026 el código se reorganizó en una **arquitectura hexagonal** sin cambiar el comportamiento; las pruebas de caracterización lo fijan (`docs/ARQUITECTURA.md`). Encima de eso se agregaron cuatro cosas:
- **Seguridad**: token del presentador, límites, CSP, filtro de palabras y validación amable.
- **Participantes**: nombre opcional y bloqueo por sesión.
- **Puertos para el Kinect** de los compañeros (`docs/CONTRATO_KINECT.md`).
- **Firmware con Bluetooth** (antes WiFi), que conserva el USB.

| Componente | Estado |
|---|---|
| Plataforma (`pgc/`) y pruebas automáticas | **423 pruebas** pasan en ~20 s, sin hardware ni internet |
| Servidor + cola + WebSocket | Probado (simulado, de punta a punta) |
| Whisper `medium` | Probado en **GPU, CUDA float16** (0,4–0,6 s por frase, en local y por el túnel) |
| Túnel Cloudflare (HTTPS + WSS) | Probado de verdad; cloudflared ya no queda huérfano |
| Páginas del celular y del proyector | Probadas en Edge real (PC y túnel, ambos temas, CSP sin violaciones); **no en un celular real** |
| Seguridad (token, límites, CSP, filtro, audio) | Probada (115 pruebas + navegador real) |
| Participantes (nombre y bloqueo) | Probado (pruebas + clics reales en el navegador) |
| Firmware de la mano (`main.py`) | **El código original del autor, idéntico en las líneas 1–225**, más el bloque Bluetooth. En el PC se probó texto, pulsos, pausas y respuestas contra el original, por USB y por Bluetooth. **Falta cargarlo en la placa** |
| Mano por Bluetooth | Probada con el `main.py` real corriendo en el PC (radio BLE y bleak falsos); **no con la placa**. Con el bleak real, el PC detecta y avisa si su Bluetooth está apagado |
| Mano por USB | Solo para subir archivos: la PCB no admite USB y 12 V a la vez |
| `iniciar.bat` | **Ejecutado** el 20/10: arranca `python -m pgc` y responde |
| Kinect, TTS de salida, modo eco | Puertos y contrato listos; la implementación es de las fases 2–5 |

## 2. Dependencias

Versiones fijas en `requirements.txt` (plataforma), `requirements-dev.txt` (pytest, httpx, pip-audit) y `requirements-gpu.txt` (torch cu128, mediapipe, coqui-tts…). Instalar: `py -3.11 -m pip install -r requirements-dev.txt`. `cloudflared` está instalado con winget.

**Auditoría con pip-audit (20/10/2026):**
- `requirements.txt` y `requirements-dev.txt`: **sin vulnerabilidades conocidas**.
- El entorno completo de Python 3.11 tiene avisos en paquetes que **no** usa la plataforma web, sino las fases siguientes y otras herramientas:

  | Paquete | Versión | Avisos | Corregido en |
  |---|---|---|---|
  | aiohttp | 3.14.3 | 5 | 3.14.4 |
  | certifi | 2026.7.22 | 1 | 2026.10.19 |
  | multidict | 6.7.1 | 1 | 6.9.1 |
  | protobuf | 3.20.3 | 4 | 4.25.8 o superior |
  | pypdf | 6.18.0 | 6 | 6.19.0 |
  | setuptools | 65.5.0 | 8 | 83.0.0 |
  | transformers | 4.57.6 | 9 | 5.x |
  | urllib3 | 2.7.0 | 3 | 2.8.0 |
  | werkzeug | 3.1.8 | 1 | 3.1.9 |

  No se actualizaron: `protobuf` lo fija mediapipe 0.10.9 y `transformers` lo usa coqui-tts, y cambiarlos puede romper la GPU o el TTS antes de la sustentación. **Decisión pendiente** (§6).

## 3. Estructura y qué hace cada parte

La arquitectura completa, con diagramas, ADR y el modelo de amenazas, está en `docs/ARQUITECTURA.md`. Resumen:

| Carpeta | Qué contiene |
|---|---|
| `pgc/dominio/` | Reglas puras: texto → secuencia (`texto.py`), letras como datos (`abecedario.py` + `datos/letras.json`), regla de letras repetidas y espacios (`ordenes.py`), filtro de palabras (`moderacion.py`), nombre del participante (`participante.py`) |
| `pgc/aplicacion/` | Cola de mensajes, hilo de la mano (`Deletreador`), estado en vivo (`Publicador`), participantes, señas (Kinect) y `Sistema`, que las reúne |
| `pgc/puertos/` | Interfaces: mano, transcriptor, sintetizador, reconocedor de señas, acceso público |
| `pgc/adaptadores/` | `mano_usb`, `mano_ble`, `mano_simulada`, `mano_respaldo` (Bluetooth → USB → simulada), `whisper`, `acceso` (túnel e IP local), `reconocedor_simulado`, `kinect/` (de los compañeros) |
| `pgc/api/` | FastAPI: `app.py`, `seguridad.py`, `esquemas.py`, rutas |
| `pgc/config.py`, `pgc/arranque.py` | Configuración (`.env`) y armado del sistema |
| `web/` | Página del celular, pantalla del proyector y logo |
| `firmware/esp32/` | Firmware de la mano (`protocolo.md`); `original/` = código original del autor (referencia de las pruebas); `referencia_doby/` = otro proyecto |

### Hilo de la mano (sin cambios de comportamiento)
- **Un mensaje a la vez**, letra por letra, esperando siempre la confirmación:
  - letra disponible: se forma y se mantiene 0,5 s para que se lea;
  - **letra igual a la forma actual** (ll, rr, ñn): primero `reset`;
  - espacio: `reset`;
  - letra que la mano no tiene: solo se muestra 0,9 s;
  - al terminar: `reset`.
- **Saltar**: la letra en curso termina, después ya no se envía nada más, y `reset`.
- **Entre mensajes, cada 3 s**: latido (sin enviar nada), respaldo y búsqueda de la mano. Un puerto USB que falló no se reintenta hasta desenchufarlo.

### Mano: Bluetooth con respaldo por USB (E10 y ADR-8)
- `PGC_MANO=auto` (por defecto): **Bluetooth** si hay `PGC_MANO_BLE_TOKEN` y la placa responde; si no, **USB**; si no, **simulada**.
- `ble` y `usb` usan solo ese medio; `simulada` nunca busca la mano. Para la sustentación: `PGC_MANO=ble`.
- La placa se busca por su nombre (`Mano-LSC`), sin emparejar. Hay que tener encendido el Bluetooth de Windows. Alcance: ~10 m.
- Si el medio activo se cae **durante una letra**, se pasa al otro y **la letra se repite por el respaldo**. Si se cae **entre mensajes**, lo detecta el latido.
- En modo `auto`, cuando el Bluetooth reaparece, se vuelve a él y se suelta el USB.
- La pantalla muestra **"Mano: Bluetooth · Mano-LSC"**, **"Mano: USB · COMx"** o **"Simulada"**.

### Rutas
| Ruta | Para qué | Quién |
|---|---|---|
| `GET /` | Página móvil | Todos |
| `GET /pantalla` | Pantalla del proyector (con el token del presentador solo si se abre en el PC) | Todos |
| `GET /logo-udec.png`, `GET /qr.png` | Logo; QR de la URL pública (túnel, o IP local) | Todos |
| `GET /api/estado` | Estado completo en JSON | Todos |
| `POST /api/previa` | Vista previa de letras (máx. 200 caracteres) | Todos (240/min por IP) |
| `POST /api/mensaje` | Encolar (60 caracteres; 2 pendientes por celular; filtro de palabras) | Todos (20/min por IP, 6/min por celular) |
| `DELETE /api/mensaje/{id}?cliente=` | Cancelar un mensaje propio pendiente | El celular que lo envió |
| `POST /api/transcribir` | Audio (máx. 10 MB y 15 s, formato de audio real) → texto | Todos (10/min por IP, 4/min por celular; 1 a la vez + 3 en espera) |
| `POST /api/participante` | Nombre opcional (máx. 20, filtrado) → alias `pid` | Todos |
| `POST /api/participantes/{pid}/bloquear` y `/desbloquear` | Bloqueo durante la sesión | **Solo el PC con token** |
| `POST /api/mano/reconectar`, `POST /api/mano/saltar` | Controles del presentador | **Solo el PC con token** |
| `GET /docs`, `GET /openapi.json` | Documentación automática | Solo con `--dev` o con el token |
| `WS /ws` | Estado en vivo (revisa Origin; máx. 100 conexiones, 8 por IP) | Todos |

Todas las respuestas llevan encabezados de seguridad (CSP con nonce, `nosniff`, `frame-ancestors 'none'`, etc.). Los errores para los jurados son amables y en español.

### Diseño común de las dos páginas (rediseño del 20/10/2026)
- **Sin dependencias externas**: CSS y JS inline, fuentes del sistema (Segoe UI Variable en Windows, SF Pro en iPhone, Roboto en Android). El logo se carga desde `/logo-udec.png`.
- **Identidad**: logo de la Universidad de Cundinamarca, etiqueta "PGC" y título corto **"Mano bidireccional LSC"**. El título completo del proyecto va en el pie del proyector.
- **Paleta**: el verde del logo (`#00482B`, medido sobre los píxeles de `web/logo-udec.png`) es el único acento. El amarillo del logo no se usa. Todos los colores son variables CSS.

  | Rol | Tema claro | Tema oscuro |
  |---|---|---|
  | Fondo / superficie | `#FFFFFF` / `#F4F6F5` | `#121615` / `#1A1F1D` |
  | Texto / secundario | `#141917` / `#4F5854` | `#EDF1EF` / `#A3ADA8` |
  | Terciario, letras pendientes y no disponibles | `#7A837F` (3,9:1) | `#7D8782` (≈ 4,9:1) |
  | Acento | `#00482B` | `#74BA9A` (botones `#4FA37F`) |
  | Aviso / error | `#A86A00` / `#C2362B` | `#E2B04A` / `#EE7A6E` |

  El texto terciario tiene al menos ~3:1 de contraste con el fondo para que se lea en un proyector a varios metros.
- **Tema claro y oscuro**: por defecto sigue el del sistema (`prefers-color-scheme`). El botón sol/luna lo cambia y lo guarda en `localStorage` (con try/catch). Un script en el `<head>` aplica el tema antes de pintar, así no hay parpadeo. El cambio de colores dura 250 ms y solo ocurre al pulsar el botón. Con la sala oscura se recomienda el tema oscuro en el proyector.
- **QR y logo**: el QR siempre va sobre una placa blanca, también en tema oscuro. En tema oscuro el logo va sobre una placa clara, porque su anillo verde oscuro casi desaparece sobre el fondo.
- **Letras que la mano no tiene**: van en gris con puntos debajo, sin tachar, y se explican con una nota corta. La Ñ va en color de aviso ("se forma como la N").
- **Palabras**: las letras de cada palabra van agrupadas, así una palabra solo se parte entre líneas si no cabe entera.
- Con `prefers-reduced-motion` se quitan las animaciones.

### `web/movil.html` — página del celular
- **Encabezado**: logo, "PGC", botón de tema, título y el estado de la mano con un punto de color ("Mano conectada", "Mano simulada" o "Reconectando…").
- **Pestañas** Escribir / Voz / Kinect como control segmentado de 46 px de alto.
- **Escribir**: caja de 60 caracteres con contador. La vista previa de letras se pide 250 ms después de dejar de escribir. La explicación de las marcas (letras no disponibles, Ñ) solo aparece cuando hacen falta. El botón "Enviar a la mano" mide 56 px de alto y al enviar cambia 1,4 s a "Enviado ✓".
- **Voz**: botón circular de 140 px con ícono de micrófono, grabación con `MediaRecorder` y corte automático a los 10 s. Prueba los formatos webm/opus, mp4 y ogg.
  - Mientras graba, el botón se pone del color de error y muestra los segundos que quedan. Alrededor, un anillo se va llenando durante los 10 s y un pulso suave sale cada 1,6 s.
  - Al transcribir, el texto pasa a la pestaña Escribir para que el jurado lo revise y lo envíe.
  - Sin HTTPS muestra `<input type="file" accept="audio/*" capture>` (plan B).
- **Kinect**: solo un aviso de "se habilitará en la siguiente fase".
- **Tus mensajes**: la posición se ve en grande ("**2** mensajes antes del tuyo", "**Sigue** el tuyo"). Un punto verde que late indica que la mano lo está deletreando ahora; "✓ Listo" que terminó; "– El presentador lo saltó" que se saltó. Los pendientes tienen un botón Cancelar, y los mensajes nuevos entran con un deslizamiento corto.
  - Se guardan en `localStorage` junto con una marca de sesión del servidor; si el servidor se reinicia, se descartan.
- **La mano ahora**: el mismo lenguaje del proyector. Las letras hechas en color normal, la actual en verde y subrayada, y las pendientes en gris.
- WebSocket con reconexión automática, evitando conexiones duplicadas. Mientras está caído consulta `/api/estado` cada 3 s.
- La barra del navegador (`theme-color`) cambia con el tema.

### `web/pantalla.html` — pantalla del proyector
- **Encabezado**: logo, "PGC", título corto, y a la derecha los botones de tema y de pantalla completa (o tecla **F**).
- **Izquierda**: QR sobre una placa blanca, la invitación "Escanea y escribe o habla a la mano" y la URL. Abajo, el estado de la mano ("WiFi · IP", "USB · COMx" o "Simulada"), de la voz (lista en GPU/CPU o cargando), del acceso HTTPS y del Kinect, cada uno con un punto de color.
- **Centro, deletreando**:
  - Arriba, "Deletreando" y la letra actual en verde, gigante.
  - La letra ocupa el alto que dejan libre la palabra y las notas: con unidades de contenedor (`cqh`/`cqw`), nunca empuja nada contra el pie.
  - Transición entre letras: la anterior sube y se desvanece en 160 ms. La nueva entra 120 ms después, subiendo desde abajo en 380 ms.
  - Notas debajo: "La mano aún no hace esta letra", "Se forma como la N", "Espacio / Mano abierta" o "Mensaje saltado / Abriendo la mano".
  - Más abajo, la palabra completa: las hechas en color normal, la actual en verde con una rayita que se desliza hasta ella, y las pendientes en gris.
- **Centro en reposo** (sin mensajes): el título "Mano bidireccional LSC", la invitación a escanear el código y la fila de **letras que la mano sabe hacer**, con un resalte verde que la recorre despacio (una letra cada 1,5 s).
  - Esa fila sale de las letras que reporta la mano. En modo simulado se piden a `/api/previa` con el abecedario, así que salen de `datos/letras.json`. Si se agregan letras (G, H, S), la fila y el texto "Las N letras que la mano sabe hacer" se actualizan solos.
- **Derecha**: la cola numerada (máximo 7 visibles y "y N más") y los 4 mensajes más recientes (los saltados llevan "saltado").
- **Pie**: el título completo del proyecto, los autores con nombre completo y "Ingeniería de Sistemas y Computación, Universidad de Cundinamarca, extensión Facatativá". A la derecha, **"Bloquear a …"**, **"Saltar mensaje"** (los dos, solo activos con un mensaje en curso) y **"Reconectar mano"**, legibles sin pasar el ratón. Solo aparecen si la pantalla se abrió en el PC, porque es la única que recibe el token.
- Si se pierde el servidor, una franja con el color de error del tema baja desde arriba: "Sin conexión con el servidor. Reconectando…".

### Participantes (E8)
- **Celular**: la primera vez aparece la hoja "¿Cómo te llamas?" con "Continuar" y "Prefiero no decirlo". El nombre es opcional (máx. 20 caracteres) y pasa por el filtro de palabras. Se guarda en el `sessionStorage` del celular, que se borra al cerrar la pestaña. Debajo del título queda "Participas como Ana · Cambiar".
- **Proyector**: "Mensaje de: Ana" sobre la letra grande y en la cola.
- **Bloquear** (solo el PC):
  - con el botón "Bloquear a Ana" del pie, o con "Bloquear", que aparece al pasar el ratón por la cola;
  - se cancelan sus pendientes y **se salta su mensaje en curso**;
  - durante 10 s hay "Deshacer", que no recupera lo cancelado;
  - su celular muestra "Gracias por participar. El presentador pausó tu participación en esta sesión." y ya no puede enviar ni grabar.
- En el servidor, los nombres y bloqueos viven solo en memoria y se pierden al cerrarlo (ADR-7). Nunca se escriben en el log.

### Firmware de la mano (versión final del 22/10/2026)
Detalles en `firmware/esp32/protocolo.md`; para modificarlo, `docs/GUIA_MODIFICAR_MANO.md`.
- **En la placa va un solo archivo, `main.py`, más `config_ble.py`.** Sus **líneas 1–225 son el código original del autor, idéntico**: pines, valores, funciones, tiempos, textos y orden.
- **Lo único agregado** es el bloque que reemplaza el BUCLE PRINCIPAL, marcado `>>> INICIO DE LO AGREGADO` / `<<< FIN DE LO AGREGADO`.
  - Atiende **las mismas órdenes** por USB y por Bluetooth (BLE, servicio UART de Nordic, nombre `Mano-LSC`, `auth <token>`, un solo PC) y **responde con los mismos textos**: `gesto_<l>_ok`, `reset_ok`, `comando_no_reconocido` y los de `deletrear()`.
  - Por USB llama a las funciones originales tal cual; también `deletrear()`.
- `main.py` se arma con `scripts/armar_main_placa.py` a partir de `original/main_original.py` y `original/bucle_ble.py`.
- Sin vigilante. Sin `letras.json`. Sin módulos aparte.
- **Hardware**: en la PCB no se pueden conectar USB y 12 V a la vez. El USB es solo para subir archivos, sin 12 V; con 12 V la mano funciona **solo por Bluetooth** (`PGC_MANO=ble`).
- `prueba_dedos.py`: mueve cada dedo por separado, sin PC, para revisar el cableado (`protocolo.md` §5).
- **El PC se adaptó a esas respuestas**:
  - comprueba la conexión con `reset` → `reset_ok`, porque el firmware no tiene `ping` ni `letras` y una palabra se deletrearía;
  - envía siempre letra por letra;
  - toma las letras disponibles de `datos/letras.json`;
  - por Bluetooth, un timeout da la conexión por perdida;
  - entre mensajes no envía nada.

**Historia.** Una primera versión reorganizó el firmware en módulos, con las letras en datos, vigilante y sin `reset_all()` antes de cada letra. La mano se movía distinto: con "hola" y el abecedario, 88 movimientos de dedo en 35 s contra 210 en 84 s del original. Por decisión del autor, el firmware volvió a ser su código exacto. El 22/10/2026 el WiFi se cambió por Bluetooth: con WiFi, el PC y la mano tenían que estar en la misma red y había que conocer la IP de la mano (ADR-8).

### `iniciar.bat`
Hace `cd` a la carpeta del proyecto y ejecuta `py -3.11 -m pgc` con las opciones que reciba. El resto se configura en `.env`. Termina en `pause`, para que la ventana no se cierre si hay un error. `py -3.11 servidor.py` sigue funcionando igual.

## 4. Qué se probó y con qué resultado

Las pruebas de modo simulado, Whisper, túnel y celular se hicieron el 14/10/2026 en el portátil, con `servidor.py --simular --no-abrir` y scripts de prueba propios (HTTP, WebSocket y túnel). Las de las decisiones de la fase 1 (§4.5) se hicieron el 20/10/2026 sobre la versión actual del código. Los cambios del 20/10 no tocan la cola básica, Whisper ni el túnel, así que esas pruebas del 14/10 no se repitieron, salvo el 403 de "Reconectar" por el túnel.

### Modo simulado (cola y mano)
| Prueba | Resultado |
|---|---|
| `GET /api/estado` | 200 · mano `simulada` |
| Vista previa de "Señor José 2" | S(nd) E Ñ(aprox) O R · J(nd) O S(nd) E · D O S(nd) → correcto |
| "Hola" y "uña" del celular A | Aceptados (id 1 y 2) |
| Tercer mensaje del celular A | **400** "Ya tienes 2 mensajes en espera…" → correcto |
| "ve mi" del celular B | Aceptado (id 3) |
| Celular B intenta cancelar el mensaje 2 (de A) | **404** → correcto |
| Mensaje de 61 caracteres | **400** "Máximo 60 caracteres." → correcto |
| Mensaje "¡¿?!" (sin letras) | **400** "Escribe al menos una letra." → correcto |
| Mensaje "gh" (ninguna letra disponible) | El 14/10 se aceptaba. **Desde el 20/10 se rechaza con 400** (ver §4.5) |
| Secuencia recibida por WebSocket | H O L A · U Ñ A · V E ␣ M I, en orden, en 20,1 s → correcto |
| `GET /qr.png` | 200, PNG válido |
| `GET /` y `GET /pantalla` | 200 (19 379 y 10 086 bytes) |
| `POST /api/mano/reconectar` desde el PC | 200 |

### Whisper
- Primer arranque: **"Whisper medium listo en cuda float16 (20.1 s)"**. El segundo arranque, con todo ya en caché, tardó 2,3 s. **No hizo falta el respaldo en CPU.**
- Transcripción: un audio WAV generado con la voz de Windows "Microsoft Helena" (es-ES) que decía "Hola jurado, bienvenidos a la sustentación". Resultado: `"Hola jurado, bienvenidos a la sustentación."` en **2,1 s**, perfecto.
- Ojo: era voz **sintética, en WAV y enviada desde el PC**. Todavía no se ha probado una voz humana grabada por el micrófono de un celular (webm/opus en Android, mp4 en iPhone).

### Túnel Cloudflare
- La URL pública salió unos 6–10 s después de arrancar, por ejemplo `https://ips-jews-saints-textbooks.trycloudflare.com`. Esa URL ya no sirve: **cambia en cada arranque**.
- Por el túnel, desde el PC: página móvil 200 en 1,4 s, `/api/estado` 200 en 0,6 s, **WebSocket seguro `wss://` funcionando**. `POST /api/mano/reconectar` responde **403**, como debe.

### Celular
- **No se probó en un celular real.** Todo lo de arriba se hizo desde el PC. Las páginas se entregan bien, pero falta verificar en el teléfono la interfaz, el permiso del micrófono, la grabación y la transcripción.

### 4.5 Decisiones de la fase 1 (pruebas del 20/10/2026)

Se hicieron dos pruebas: una directa del hilo de la mano, con una mano falsa que registra cada orden que recibiría el ESP32, y otra contra el servidor real (`--simular --no-abrir --sin-voz`) con el túnel activo.

**(1) Letras repetidas: órdenes que recibe la mano**

| Texto | Órdenes enviadas |
|---|---|
| `calle` | c a l **reset** l e reset |
| `carro` | c a r **reset** r o reset |
| `ll ll` | l **reset** l reset(espacio) l **reset** l reset |
| `ñn` | n **reset** n reset (la Ñ se hace con la forma de la N) |
| `lgl` | l **reset** l reset (la g no se envía; la mano seguía en l) |
| `hola` | o l a reset (la h no se envía; no hay repeticiones) |

La regla compara con **la forma que tiene la mano en ese momento**, no solo con la letra escrita justo antes. Por eso también se abre en `ñn` y en `lgl`: en ambos casos la mano se quedaría quieta.

**(2) Mensajes sin letras disponibles**

| Texto | Resultado |
|---|---|
| `gh` | 400 "La mano todavía no puede hacer esas letras" |
| `Jhs` | 400 "La mano todavía no puede hacer esas letras" |
| `zz gg` | 400 "La mano todavía no puede hacer esas letras" |
| `¡¿?!` | 400 "Escribe al menos una letra." (sin letras de ningún tipo) |
| `hola gh` | 200, aceptado (tiene letras posibles) |
| `Ñ` | 200, aceptado (se aproxima con la N) |

**(3) Saltar mensaje**

| Prueba | Resultado |
|---|---|
| Saltar sin mensaje en curso | 404 "No hay ningún mensaje en curso." |
| Saltar **por el túnel** | **403** "Solo desde el PC del proyector." |
| Reconectar por el túnel (comprobación de nuevo) | 403 |
| Saltar desde el PC durante la letra C de "abcdefiklmnop" | 200; la pantalla recibió `saltado: true` |
| Prueba directa: saltar durante la 3.ª letra | Órdenes: a b c **reset**, y nada más; los pasos restantes quedan sin ejecutar |
| Mensaje siguiente en la cola ("ok") | Se deletreó normal: O, K |
| Historial | `ok` (saltado: false), `abcdefiklmnop` (saltado: true) |

También se comprobó que `/` y `/pantalla` responden 200 y que el JavaScript de las dos páginas pasa `node --check` sin errores de sintaxis. **No se probó el clic en el botón dentro del navegador**: se llamó al endpoint directamente, que es lo mismo que hace el botón.

### 4.6 Rediseño visual (pruebas del 20/10/2026)

Servidor en `--simular --sin-voz --sin-tunel --no-abrir`, y Microsoft Edge sin ventana (headless) controlado con el protocolo de depuración (CDP) desde un script propio. El proyector se probó a 1920×1080. El celular se emuló a 390×844 (modo móvil, densidad 2). Cada tema se forzó emulando `prefers-color-scheme`. Mensajes de ejemplo: "Bienvenidos jurado" (de otro jurado), "Hola señor" y "Gracias" enviados desde la propia página del celular, y "calle".

| Prueba | Resultado |
|---|---|
| `GET /logo-udec.png`, `/` y `/pantalla` | 200 |
| Fila de letras del reposo en modo simulado | `ABCDEFIKLMNOPQRTUVWXY` (21, las de `texto_util.py`) |
| Enviar desde el celular | El botón cambia a "Enviado ✓". "Tus mensajes" muestra **1** y **2** "antes del tuyo", con Cancelar |
| "La mano ahora" y el proyector | Muestran la misma letra en curso; las palabras no se parten |
| QR en las capturas (decodificado con OpenCV) | Tema oscuro y claro, en reposo y deletreando: siempre `http://192.168.1.65:8000` (la URL de esa sesión) |
| Botón de tema | Cambia a oscuro, guarda `tema=dark` en `localStorage` y lo mantiene al recargar (fondo `rgb(18, 22, 21)`) |
| Transición entre letras | En 6 cuadros seguidos nunca hay dos letras superpuestas |
| Servidor apagado | Aparece la franja "Sin conexión con el servidor. Reconectando…" en los dos temas |
| Reposo, deletreo, celular y pestaña Voz | Capturas en ambos temas, guardadas en `capturas/` |

Capturas en `capturas/`:

| Vista | Tema claro | Tema oscuro |
|---|---|---|
| Proyector en reposo | `proyector_reposo_light.png` | `proyector_reposo_dark.png` |
| Proyector deletreando | `proyector_deletreo_light.png` | `proyector_deletreo_dark.png` |
| Proyector sin conexión | `proyector_sin_conexion_light.png` | `proyector_sin_conexion_dark.png` |
| Celular, página completa | `movil_light.png` | `movil_dark.png` |
| Celular, pestaña Voz grabando | `movil_voz_light.png` | `movil_voz_dark.png` |
| Celular, recién enviado | `movil_enviado_light.png` | — |

Ojo: en `movil_voz_*.png` el estado "grabando" se activó a mano, solo para la foto. Con `--sin-voz` y sin micrófono no hay grabación real.

### 4.7 Reorganización, seguridad y participantes (20/10/2026)
- **Pruebas de caracterización** (`tests/`) escritas **antes** de tocar el código. Las 109 originales pasaron sin editarse en cada etapa de la reorganización (E1–E6). En E7 y E8 cambiaron solo las aprobadas:
  - `/openapi.json` → 404;
  - `cliente` largo → 422;
  - audio con firma real;
  - token en las rutas del presentador;
  - instantánea con autor, `bloqueados` y `medio`.
- **De punta a punta** (`scripts/prueba_e2e.py`, con `servidor.py` y con `python -m pgc`), comprobado:
  - páginas y "gh" rechazado;
  - la pantalla ve C-A-L-L-E en orden;
  - token solo en `/pantalla` del PC;
  - 403 por el túnel aun con token;
  - filtro de palabras;
  - CSP con nonce;
  - `/openapi.json` cerrado.
- **Servicios reales** (`scripts/prueba_servicios_reales.py`): Whisper `medium` en CUDA float16 transcribió "Hola jurado, bienvenidos a la sustentación." en 0,4–0,6 s, en local y por el túnel. Por el túnel también funcionaron HTTPS, wss y el 403 del presentador.
- **Navegador real** (`scripts/prueba_navegador.py`, temas oscuro y claro, en el PC y por el túnel):
  - sin violaciones de CSP;
  - el WebSocket seguro pasa la revisión de Origin;
  - contexto seguro para el micrófono;
  - hoja del nombre, nombre ofensivo rechazado, "Mensaje de: Ana", saltar con el token;
  - bloquear y deshacer con clics reales;
  - por el túnel, la pantalla sin token ni controles.

  Capturas en `capturas/navegador_*.png`.
- **cloudflared** quedó atado al proceso con un Job Object de Windows: después de cerrar el servidor a la fuerza quedaron **0** procesos.

### 4.8 Firmware y mano por WiFi (20/10/2026; el WiFi se reemplazó por Bluetooth el 22/10, ver §4.9)
- **Igual al código original del autor** (`tests/test_firmware.py`, versión corregida). El código original se ejecuta en el PC tal cual, con `machine` y `time` falsos, recibiendo las órdenes por stdin como en la placa. Se comprueba que:
  - `mano_movimientos.py` es una **copia literal** de él;
  - el arranque produce la misma secuencia de pulsos (pin, µs) y pausas;
  - cada una de las 21 letras, enviada como orden, también;
  - una secuencia larga (con letras repetidas, `reset` y letras que no existen) también.
- **Protocolo**:
  - `salir`, `hola`, `1` y órdenes largas → `error:orden`, sin mover nada;
  - `G` → `na:g`;
  - cada letra empieza abriendo la mano;
  - vigilante (desactivado en `main.py`) con un reloj falso.
- **TCP real en el PC** con el código del firmware: token correcto; token incorrecto (rechazado y cerrado); sin token a tiempo; un intruso sin token no desconecta al PC; un PC con token reemplaza al anterior; líneas absurdas descartadas.
- **ESP32 falso por TCP** (`tests/esp32_falso.py`, el firmware real con servos falsos):
  - conexión, letras y latido;
  - el token nunca aparece en el log;
  - token incorrecto;
  - placa apagada, con un solo aviso en el log aunque se reintente;
  - timeout de una letra;
  - pérdida del WiFi;
  - **cambio a USB sin perder la letra**;
  - caída detectada por el latido;
  - **regreso al WiFi** cuando reaparece (el USB se suelta);
  - modos `usb` y `wifi`.
- **De punta a punta por WiFi** (`scripts/prueba_e2e.py --wifi`): el servidor con `PGC_MANO=wifi` se conectó a la placa falsa. La placa recibió **exactamente** `c a l reset l e reset`, la pantalla real mostró **"WiFi · 127.0.0.1"**, y al apagar el WiFi la mano pasó a simulada.

### 4.9 Mano por Bluetooth (22/10/2026)
- **Firmware** (`tests/test_firmware.py`, 50 pruebas):
  - las líneas 1–225 siguen idénticas al original;
  - por USB, mismos pulsos, pausas y textos que el original;
  - por Bluetooth (radio BLE falsa que ejecuta el `main.py` real):
    - se anuncia como `Mano-LSC`;
    - mismas respuestas y **mismos movimientos** que el original;
    - token incorrecto, sin token y sin presentarse en 3 s: desconecta sin mover nada y vuelve a anunciarse;
    - un solo PC a la vez;
    - reconexión;
    - respuestas largas en paquetes de 20 bytes;
    - el USB sigue funcionando a la vez;
    - sin `config_ble.py` o con un token corto, la placa funciona solo por USB.
- **PC** (`tests/test_mano_ble.py`, 20 pruebas, con un bleak falso que habla con esa placa):
  - conexión y letras;
  - movimientos idénticos al original;
  - el token nunca va al log;
  - token incorrecto;
  - placa fuera de alcance;
  - Bluetooth del PC apagado (mensaje claro en español);
  - un solo aviso aunque se reintente;
  - timeout de una letra;
  - pérdida y reconexión;
  - respaldo a USB y regreso al Bluetooth;
  - modos `ble` y `usb`;
  - configuración.
- **De punta a punta por Bluetooth** (`test_de_punta_a_punta_por_bluetooth`): celular → API → cola → `ManoBLE` → `main.py` real. La placa recibió **exactamente** `c a l reset l e reset` y `/api/estado` mostró `ble · Mano-LSC`.
- **Con el bleak real** en este PC: el Bluetooth de Windows estaba apagado, y el servidor lo informó y siguió en modo simulado sin fallar.

- **El servidor se cerraba solo** al arrancar con voz y Bluetooth (*access violation*).
  - Causa: WinRT (bleak) y ctranslate2 (Whisper) no conviven en el mismo proceso. Con solo importar WinRT antes de cargar Whisper, Python se cae.
  - Arreglo: bleak corre en un **proceso aparte** (`pgc/adaptadores/ble_puente.py`).
  - Comprobado con el servidor real: Whisper listo en GPU en 4,6 s y el servidor estable con el Bluetooth real. Al cerrarlo no quedan procesos.
  - `tests/test_ble_puente.py` (5 pruebas) usa un hijo de verdad que corre el `main.py` real: muerte y recuperación del hijo, y que el servidor nunca carga `bleak` ni `winrt`.
- **No emparejar la mano en Windows.** Si se empareja, Windows guarda claves que la placa no conoce. La conexión se corta ("Not connected") o Windows la ocupa y la placa deja de anunciarse.

## 5. Problemas encontrados y corregidos durante las pruebas
1. **Demora de unos 2 s por conexión**: `localhost` en Windows intenta IPv6 primero. Se cambió a `127.0.0.1` en el túnel y en la URL que se abre en el navegador.
2. **Líneas del log mezcladas entre hilos**: se agregó un lock a `log()`.
3. En modo `--simular` no se registraba nada sobre la mano: ahora se registra "Modo simulado (--simular)".
4. Página móvil: se evitaron WebSocket duplicados al volver a la pestaña. Un mensaje recién enviado ya no desaparece de "Tus mensajes" antes de que llegue el estado nuevo.
5. El primer script de prueba fallaba porque no ignoraba los mensajes `ping` del WebSocket. Era un error del script, no del servidor.
6. Rediseño, **palabras partidas** ("JURA / DO"): ahora las letras de cada palabra van agrupadas.
7. Rediseño, **centro del proyector desbordado**: la letra toma solo el alto libre (unidades de contenedor).
8. Rediseño, **letras superpuestas** durante la transición: la nueva entra 120 ms después.
9. Problema del script de capturas, no de las páginas: una pestaña en segundo plano congelaba las transiciones.
10. El servidor no tenía cómo entregar el logo: se agregó `GET /logo-udec.png`.
11. **cloudflared huérfano** al cerrar el servidor a la fuerza: corregido con un Job Object de Windows (E6).
12. **Las transcripciones y los textos quedaban en el log**: ya no, salvo con `PGC_LOG_TEXTOS=true` (E7).
13. **El audio se leía completo en memoria antes de revisar su tamaño**: ahora el tamaño se limita antes de leerlo (E7).
14. **Las rutas del presentador se podían llamar desde cualquier página web abierta en el PC (CSRF)**: ahora exigen el token (E7).
15. **Falso positivo del filtro**: "pera" se confundía con "perra". La reducción de letras repetidas solo se aplica con tres o más seguidas (E7).
16. **Al bloquear, la pantalla veía un instante el estado a medias** (bloqueado pero con sus mensajes en la cola): ahora se avisa una sola vez, al final (E8).
17. **La URL larga del túnel se partía a mitad de palabra** en el proyector ("trycloudflare.co / m"): ahora solo se corta después de los puntos (E8).
18. **Mover la carpeta del firmware**: el respaldo previo a E10 no copió `referencia_doby/main.py` y al mover la carpeta se perdió. Se restauró desde el respaldo previo a E9, con hash idéntico. Desde E11, cada respaldo se verifica archivo por archivo.

## 6. Qué falta (pruebas con hardware real y decisiones)
- **Mano física por USB** (sin 12 V, sin movimiento): conexión con `reset`, tiempos reales por letra, timeout y autodetección al enchufarla con el servidor encendido.
- **Firmware en la placa** (`firmware/esp32/protocolo.md` §4): subir `main.py`, crear `config_ble.py` (con el mismo token del `.env`), borrar `config_wifi.py` y los archivos de la versión anterior. Comprobar que las 21 letras se ven como con el código original y que la placa arranca con el meñique en GPIO3.
- **Prueba de dedos** (`prueba_dedos.py`): cada dedo se mueve solo y en su pin.
- **Mano por Bluetooth real**: "Mano: Bluetooth · Mano-LSC" en la pantalla; la reconexión al quitar y volver a poner los 12 V; el alcance en la sala, con el PC en su sitio.
- **Celulares reales** (iPhone y Android): interfaz, hoja del nombre con el teclado, permiso del micrófono, grabación (webm/opus y mp4) y transcripción de voz humana; varios celulares a la vez (límites por IP con datos móviles).
- **Proyector real de la sala**: contraste a 5 m, qué tema conviene y lectura del QR desde los celulares.
- **Acceso por red local** (`http://IP:8000`): Windows puede pedir permiso de firewall para Python la primera vez. Sin HTTPS no hay micrófono; queda el plan B de subir una nota de voz.
- **Tiempos con la mano real**: "Saltar" espera a que termine la letra en curso (hasta ~2,5 s) y luego abre la mano (~2,4 s). El `reset` entre letras repetidas suma ~2,4 s a "calle" o "carro".
- **En el celular, el error de "letras no disponibles" solo sale al tocar Enviar**: la vista previa ya marca esas letras, pero el botón no se desactiva por eso.
- **Decisión**: actualizar o no los paquetes del entorno con avisos de pip-audit (§2). Recomendación: hacerlo después de la sustentación, o probar antes la GPU, Whisper y el TTS.
- **Fuera del alcance de la fase 1**: Kinect, TTS de salida y modo eco (fases 2–5). Los puertos y el contrato ya están listos.

## 7. Pasos exactos para iniciarlo

**Primera vez:**
1. Copiar `.env.example` como `.env` en la carpeta del proyecto.
2. Para la mano por Bluetooth, poner ahí `PGC_MANO=ble` y `PGC_MANO_BLE_TOKEN=<el mismo TOKEN de config_ble.py>`. Sin token, la mano funciona solo por USB.

**En modo simulado (sin mano):**
1. Doble clic en `iniciar.bat`, o `py -3.11 -m pgc --simular` en PowerShell, en `C:\Users\miran\ProyectoPGC`.
2. Se abre sola `http://127.0.0.1:8000/pantalla`. Esperar a que aparezcan **Voz: Lista en GPU** y **HTTPS: Activo** (unos 20 s).
3. Escanear el QR con el celular.
4. Pulsar **F** para pantalla completa. Con la sala oscura, poner el tema oscuro.
5. Controles del pie: **Bloquear**, **Saltar mensaje** y **Reconectar mano**. Solo funcionan en la pantalla abierta en el PC.
6. Para apagar: **Ctrl+C** en la consola. Si se cierra con la X, cloudflared también se cierra.

**Con la mano real:**
1. Cargar `main.py` una vez, con USB y **sin 12 V** (`firmware/esp32/protocolo.md` §4), y **cerrar Thonny**.
2. **Desconectar el USB** y conectar los 12 V. La mano funciona solo por Bluetooth.
3. En el PC, **encender el Bluetooth** (Configuración › Bluetooth y dispositivos). No hace falta emparejar. En el `.env`: `PGC_MANO=ble` y `PGC_MANO_BLE_TOKEN`.
4. Doble clic en `iniciar.bat`. En la pantalla debe salir **"Mano: Bluetooth · Mano-LSC"**. Si dice "Simulada", leer el log (Bluetooth apagado, mano no encontrada o token distinto) y pulsar **"Reconectar mano"**.

**Opciones útiles:** `--sin-tunel` (solo red local), `--sin-voz` (arranque rápido sin Whisper), `--no-abrir`, `--puerto-web 8001` y `--dev` (documentación de la API en `/docs`). El resto, en `.env` (ver `.env.example`).

**Pruebas:** `py -3.11 -m pytest` (todas), `py -3.11 scripts/prueba_e2e.py`, `py -3.11 scripts/prueba_servicios_reales.py` (con internet) y `py -3.11 scripts/prueba_navegador.py`.

## 8. Código completo

Ya no se copia a mano en este documento, porque ahora está repartido en más de 30 archivos. Está en **`docs/CODIGO_COMPLETO.md`**, generado a partir de los archivos actuales con:
```
py -3.11 scripts/generar_codigo_completo.py
```
Hay que volver a generarlo después de cambiar el código. No incluye el firmware de Doby ni los secretos.

# Lista de verificación: prueba con el Kinect real

Para la primera prueba con el Kinect físico y la app C# compilada (`LSCKinectFramework.exe` del 25/10/2026).
Marca cada casilla; si algo falla, mira la tabla del final antes de seguir.

## A. Antes de salir (en el PC de la demo)

- [ ] Rama correcta: `git switch integracion-unificada` y `git status` sin cambios pendientes.
- [ ] `py -3.11 -m pytest` → todo pasa.
- [ ] `.venv-detector` existe (si no: doble clic en `instalar_detector.bat`, necesita internet).
- [ ] La app del Kinect está en `integracion_kinect\capturador\LSCKinectFramework\bin\Debug\` (`LSCKinectFramework.exe`, `.exe.config`, `Microsoft.Kinect.dll`).
- [ ] En el `.env`: `PGC_KINECT_CAPTURADOR=auto` (o sin esa línea). **No** `camara_pc`.
- [ ] Se lleva: Kinect, su adaptador de corriente/USB, la mano (12 V), cargador del portátil, parlantes (si los del portátil no bastan).

## B. Conectar el Kinect

1. [ ] Enchufar el adaptador del Kinect a la corriente **antes** que al USB.
2. [ ] USB a un puerto directo del portátil (sin hub). Esperar ~30 s.
3. [ ] Administrador de dispositivos → aparece **"Kinect for Windows"** (Camera, Audio, Device) sin signos de advertencia.
   - Si aparece "Xbox NUI ..." con advertencia: falta el controlador del SDK 1.8 (ver tabla).
4. [ ] La luz del Kinect queda verde.

## C. Diagnóstico (2 minutos)

1. [ ] Doble clic en `diagnostico_kinect.bat`. Durante la medición, pararse frente al Kinect a 1,5–3 m y mostrar una mano.
2. [ ] Resultado esperado: **0 fallas** y "Llegan 12–18 imágenes por segundo" (la app compilada el 27/10 espera 50 ms entre imágenes; la del 25/10, que esperaba 100 ms, está en `respaldos\2026-10-27_app_kinect_debug_25oct`).
3. [ ] Si hay fallas: seguir la indicación de cada línea (`-> ...`). El informe queda en `registros\diagnostico_kinect.txt`.

## D. Arranque completo

1. [ ] Doble clic en `iniciar.bat` (con la mano: sin opciones; sin la mano: `iniciar.bat --simular`).
2. [ ] Se abre el proyector. En la ventana negra aparece "Iniciando el detector" y "Abriendo la app del Kinect ..., minimizada".
3. [ ] **Verificar**: la ventana de la app C# quedó **minimizada** en la barra de tareas y no tapa el proyector. *(No se pudo probar sin Kinect; si se abre en grande, minimizarla a mano.)*
4. [ ] En el proyector, columna izquierda: **Kinect → "Listo"** (punto verde). Si dice "No conectado", ver tabla.
5. [ ] Voz: **"Lista en GPU"**. Esperar ~1 min a que cargue también la voz de salida (Coqui).

## E. Prueba de reconocimiento (desde el proyector)

1. [ ] Pie del proyector → **Kinect: Iniciar**. El centro cambia a la vista Kinect con la imagen de la cámara (grande) y los puntos de la mano.
   - [ ] La imagen se mueve con fluidez (unas 15–17 por segundo) y el texto y el estado bajo ella cambian **a la vez** que la imagen.
   - [ ] Si se desconecta el USB del Kinect, en ~1,5 s el proyector dice "No conectado" (no se queda con una imagen congelada).
2. [ ] Hacer una letra fácil (A, E, O, L, V) y mantenerla ~1 s: aparece en grande. Retirar la mano medio segundo entre letras.
3. [ ] Probar una palabra corta: **H O L A**.
4. [ ] **Borrar** quita la última letra; **Espacio** separa palabras.
5. [ ] **Terminar y decir**: la frase **se oye** por los parlantes (Coqui) y aparece "Dijo: «hola»". *(La voz no se ha escuchado nunca en una prueba: confirmar volumen y parlante.)*
6. [ ] **Eco: sí** → repetir una frase → la mano la deletrea; las letras que la mano no hace (G, H, J, S, Z) aparecen como no disponibles.
7. [ ] Anotar: distancia que mejor funciona, luz del salón, letras que fallan (para el informe y para Camila).

## E2. Diagnóstico y protocolo de letras (en el PC)

1. [ ] Pie del proyector → **Diagnóstico** (se abre `/diagnostico` en otra pestaña).
2. [ ] Con una letra frente al Kinect, la vista muestra: mano detectada, letra posible, 2.ª opción y margen, barra de «Estable» hasta 0,7 s, imágenes (x de 4) y el motivo en grande.
3. [ ] Protocolo: dejar «Letras» vacío (todas las del modelo), 5 repeticiones, 8 s → **Iniciar protocolo**. Hacer la letra que pide; cuando diga «Retira la mano», bajarla.
4. [ ] Al terminar, la vista muestra la tabla por letra y la carpeta `experimentos\<fecha_hora>\` con los CSV, la matriz de confusión, las gráficas e `informe.md`.
5. [ ] Anotar las condiciones de esa corrida (distancia, luz, quién hizo las letras) en `informe.md`: el análisis no las conoce.

## F. Desde los celulares

1. [ ] Escanear el QR con dos celulares (uno con datos, otro con el WiFi del salón).
2. [ ] Pestaña **Kinect**: dice "Kinect listo" (nunca "siguiente fase").
3. [ ] Celular 1: **Tomar el control del Kinect** → aparecen Iniciar/Detener/Espacio/Borrar/Terminar.
4. [ ] Celular 2 ve "Lo está usando ... Espera tu turno." y **no** ve botones.
5. [ ] El texto se ve en vivo en los dos celulares mientras alguien hace letras.
6. [ ] Por el túnel **no** se ve la imagen de la cámara (solo en el proyector del PC).
7. [ ] Celular 1: **Soltar el control** → el celular 2 puede tomarlo. (Si nadie lo suelta, se libera solo a los 2 minutos; el presentador puede usar **Liberar turno**.)

## G. Al terminar

1. [ ] Cerrar la ventana de `iniciar.bat` (o Ctrl+C).
2. [ ] Administrador de tareas: **no** quedan `python.exe` del detector ni `LSCKinectFramework.exe`.
3. [ ] Llevar de vuelta el informe `registros\diagnostico_kinect.txt` y las notas del paso E.7.

## No tocar en la ventana de la app C# (versión del 25/10)

Esa versión es anterior a la del repositorio y trae botones de cuando se grababa el dataset. Durante la demo, **no usar**:

| Botón de su ventana | Por qué |
|---|---|
| **Grabar letra** / **Grabar ejemplo** | Escriben grabaciones nuevas en `integracion_kinect\detector\dataset_alfabeto\` y `dataset\`: mezclarían datos de la demo con el dataset de entrenamiento |
| **Reconocer seña** | Usa `modelo_hola_adios.npz`, que no está en el repositorio: solo da error |
| **Leer texto** | Habla con la voz de Windows, además de Coqui: se oirían dos voces |
| **Iniciar/Detener deletreo**, **Espacio**, **Borrar**, **Limpiar** | Funcionan (actúan sobre el mismo detector y la plataforma lo refleja), pero se saltan el turno, y su botón puede decir "Iniciar" cuando el deletreo ya está iniciado desde el proyector (la app no se entera de lo que hace la plataforma). Usar los controles del proyector o del celular |

## Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| Diagnóstico: "Windows no ve ningún Kinect" | Sin corriente, USB flojo o hub | Revisar el adaptador (luz), otro puerto USB directo, esperar 30 s |
| Aparece "Xbox NUI Camera/Motor" con advertencia | Controlador genérico, sin el del SDK | Desconectar el Kinect, reinstalar Kinect SDK 1.8, reiniciar, conectar |
| App C# dice "No se detectó ningún Kinect conectado" | El Kinect no estaba listo cuando abrió la app | Cerrar `iniciar.bat`, esperar 30 s con el Kinect conectado y volver a abrir |
| Proyector: Kinect "No conectado" | No llegan imágenes al detector | Abrir la app C# desde la barra de tareas y leer su estado; mirar `registros\detector.log` y `registros\capturador.log` |
| "Falta el entorno del detector" en la ventana negra | No existe `.venv-detector` | `instalar_detector.bat` (necesita internet) |
| Las letras no salen o salen mal | Distancia, luz o mano fuera de cuadro | 1,5–2 m, luz de frente, una sola mano, fondo liso; mantener 1 s |
| No se oye la frase | Coqui aún cargando o parlante equivocado | Esperar 1 min tras arrancar; revisar el dispositivo de salida de Windows |
| Plan B: el Kinect no funciona | — | En el `.env`: `PGC_KINECT_CAPTURADOR=camara_pc` y reiniciar `iniciar.bat` (usa la cámara del portátil; puede reconocer peor porque el modelo se entrenó con imágenes del Kinect) |

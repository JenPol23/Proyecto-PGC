# Para Camila: cómo quedó integrada tu parte

Hola, Camila. Este documento resume cómo quedó tu parte (el Kinect y el reconocimiento de señas) dentro de la plataforma, qué se cambió de tu código y por qué, y los dos problemas que vimos en las pruebas. También están los pendientes y cómo trabajar en el repositorio sin que nos pisemos.

Gracias por todo el trabajo: el detector, el modelo y la app del Kinect funcionan, y el sistema completo ya arranca con un solo clic.

---

## 1. Cómo quedó integrada tu parte

Tu código se usa **tal cual**, en procesos aparte. La plataforma solo se comunica con él por HTTP, como lo describe `docs/CONTRATO_KINECT.md` (v1.1).

| Pieza tuya | Dónde está | Cómo se usa ahora |
|---|---|---|
| Detector (`server_web_svm.py`, puerto 8765) | `integracion_kinect/detector/` | Lo arranca `iniciar.bat` con el Python de `.venv-detector` (sus versiones no caben en el Python de la plataforma). Se sirve envuelto en `pgc/adaptadores/kinect/detector_paralelo.py`, que atiende varias peticiones a la vez **sin cambiar tu archivo**. Con `PGC_KINECT_DETECTOR_PARALELO=false` en el `.env` se usa tu servidor original. |
| Modelo (`modelo_estaticas.joblib`) | `integracion_kinect/detector/` | Lo carga tu detector, sin cambios (necesita scikit-learn 1.5.2). |
| App C# del Kinect (SDK 1.8, .NET 4.8) | `integracion_kinect/capturador/` | `iniciar.bat` la abre minimizada cuando el detector ya responde. Se compila en este PC en Release con VS Build Tools 2022 (`bin\Release`, fuera de git). |
| Pestaña del celular (la de `iniciar_pgc_integrado.py`) | ahora en `web/movil.html` | Ver el punto 1.2. |

Solo `pgc/adaptadores/kinect/reconocedor.py` habla con tu detector: consulta `/spell/status` cada 0,3 s y reparte el texto a todas las pantallas por WebSocket. Los celulares no consultan tu detector directamente, así que 30 celulares abiertos no lo cargan más que uno. La imagen de la cámara se ve **solo** en el proyector del PC, nunca por internet.

### 1.1. Lo único que se cambió de tu código

**Un solo valor, en un solo archivo:** en `MainWindow.xaml.cs` de la app C#, la espera entre imágenes pasó de **100 ms a 50 ms** (`AddMilliseconds(50)`).

- **Por qué:** con 100 ms llegaban unas 10 imágenes por segundo y las letras tardaban en confirmarse. Con 50 ms llegan unas **17 por segundo** (el límite real lo pone lo que tarda MediaPipe en cada imagen).
- Jean Paul lo autorizó el 27/10/2026 y quedó en su propio commit, con el mensaje "SE MODIFICÓ EL CÓDIGO DE CAMILA", para que sea fácil de ver o revertir.
- La versión anterior compilada está guardada en `respaldos\2026-10-27_app_kinect_debug_25oct`.

Nada más dentro de `integracion_kinect/` se modificó.

### 1.2. Tu lanzador ya no hace falta

`iniciar_pgc_integrado.py` y `acceso_kinect.py` quedan en el repositorio **sin cambios**, pero ya no se usan. Ahora todo arranca con `iniciar.bat`: la plataforma, tu detector y tu app del Kinect juntos. Si ya hay una plataforma corriendo, no se abre otra.

**Tu pestaña ahora vive en `web/movil.html`** y se ve como la diseñaste:

- arriba, el cuadro grande de texto "Tus letras aparecerán aquí" y, debajo, el estado del detector ("Deletreo detenido.", "Posible letra…");
- el campo **"Código del PC"** con los botones **"Activar control"** y **"Volver a espectador"**;
- los botones en cuadrícula: Iniciar, Detener, Espacio, Borrar, Limpiar, Guardar TXT, Leer frase y Detener voz, y además **"Terminar y decirlo"** (dice la frase en voz alta por los parlantes del PC con Coqui) y **Eco** (la mano robótica repite lo que reconoce el Kinect), los dos destacados.

**El código del PC ahora está unido al sistema de turno:**

- El proyector muestra un código de **6 dígitos** que cambia en cada arranque. El presentador puede generar otro con "Cambiar código", y quien tenía el control lo pierde.
- Para "Activar control", el celular escribe ese código. Solo **un celular a la vez** tiene el turno.
- El turno se libera solo tras 2 minutos sin usarlo. El presentador puede liberarlo, y si bloquea a alguien, esa persona también pierde el turno.
- Guardar TXT, Leer frase y Detener voz funcionan en cualquier celular, aunque no tenga el turno.
- El código nunca se envía a los celulares por el WebSocket: solo lo recibe el proyector.
- Se puede desactivar con `PGC_KINECT_CODIGO=false` en el `.env`. En ese caso basta con tocar "Activar control".

---

## 2. Problema 1: la O se reconoce como E

En las pruebas con el Kinect, al hacer la **O** el detector escribe **E**. Las dos letras tienen los dedos curvados y se parecen en los 21 puntos de MediaPipe, sobre todo de frente y con poca luz.

**Lo que te pedimos:**

1. **Grabar más ejemplos de O y E**, y también de las otras letras que se confundan (la matriz de confusión dirá cuáles). Tienen que ser:
   - grabados **con el Kinect** (no con la webcam), porque la imagen es distinta;
   - de **varias personas** (manos de distintos tamaños y tonos de piel);
   - a **1 a 1,5 m** del Kinect, la distancia de la sustentación;
   - con **distintas luces** (salón con luz natural, luz artificial, contraluz);
   - con **distintos ángulos** de la mano (de frente, un poco girada, un poco inclinada).
2. **Reentrenar el SVM** con `entrenar_estaticas.py`, separando a las personas entre entrenamiento y prueba (que nadie aparezca en los dos grupos). Así la exactitud no sale inflada.
3. **Evaluar por letra**: exactitud, precisión y exhaustividad (*recall*) de cada letra, y la **matriz de confusión**.
4. **Entrenar con `probability=True`** en el `SVC(...)`. Hoy el modelo da un margen de decisión, que no es una probabilidad. Con `probability=True`, `predict_proba` da una **confianza real** (0 a 1) para cada predicción, y con ella se puede, por ejemplo, no confirmar una letra si la confianza es baja.

**Números del protocolo de diagnóstico:** todavía **no hay resultados**. La carpeta `experimentos/` no existe porque el protocolo de prueba de letras aún no se ha corrido con el Kinect físico. Cuando se corra (vista `/diagnostico` en el PC, solo con el token), cada prueba guarda en `experimentos/<fecha_hora>/` un CSV, la matriz de confusión, gráficas y un `informe.md` con la exactitud por letra. Serán un buen punto de comparación antes y después de reentrenar.

---

## 3. Problema 2: tarda mucho en confirmar cada letra

Hoy una letra se confirma si la misma predicción se mantiene **al menos 0,7 s** (`TIEMPO_CONFIRMACION = 0.7` en `server_deletreo_svm.py`) **y en al menos 4 imágenes**. Además, hay que retirar la mano 0,5 s entre letras.

Con ~17 imágenes por segundo, las **4 imágenes se cumplen en unos 0,25 s**. El cuello de botella ya no es la cámara: es la **estabilidad de 0,7 s**.

**Propuesta:**

1. Probar `TIEMPO_CONFIRMACION = 0.5`.
2. Medir con el protocolo de diagnóstico, antes y después del cambio:
   - el tiempo hasta confirmar cada letra;
   - las **letras falsas**: letras que se confirman sin que nadie las haga, o la letra equivocada mientras la mano pasa de una seña a otra.
3. Si aparecen letras falsas, quedarse en un punto intermedio (0,6 s) o subir el mínimo de imágenes (por ejemplo, 6).

Como es tu código, el cambio lo haces tú (o nos avisas y lo acordamos), en tu rama.

---

## 4. Pendientes

- [ ] **Dataset**: subir `dataset_alfabeto/` o compartir un enlace (Drive, OneDrive), porque no está en el repositorio. Los jurados pueden pedirlo.
- [ ] **Métricas del SVM**: exactitud general, exactitud por letra, matriz de confusión y latencia (cuánto tarda en predecir cada imagen).
- [ ] **`/spell/status` en JSON**: hoy responde texto plano (`Texto: …` / `Estado: …`). Lo ideal es un JSON que, además del texto y el estado, traiga `confianza` (de `predict_proba`) y `latencia_ms`. El adaptador de la plataforma se ajusta después; está descrito en `docs/CONTRATO_KINECT.md`.
- [ ] **scikit-learn 1.5.2 fijo** en `requirements-detector.txt`, y **guardar la versión dentro del `.joblib`** (por ejemplo `"sklearn_version": sklearn.__version__` en el diccionario de `joblib.dump`). Así el detector puede avisar con un mensaje claro si alguien lo carga con otra versión.
- [ ] **El `.exe` recompilado** si cambias la app C#. Se compila en Release con `MSBuild LSCKinectFramework.csproj /t:Rebuild /p:Configuration=Release`. Los binarios no van a git: avísale a Jean Paul para recompilar en el PC de la sustentación.

---

## 5. Cómo trabajar en el repositorio

Repositorio: https://github.com/JenPol23/Proyecto-PGC

1. **Crea tu propia rama** a partir de `main`:
   ```
   git checkout main
   git pull
   git checkout -b camila/reentrenar-svm
   ```
2. Haz tus cambios dentro de `integracion_kinect/` y súbelos a tu rama.
3. **Antes de subir**, corre las pruebas del contrato con el Kinect:
   ```
   py -3.11 -m pytest tests/contratos
   ```
   Si alguna falla, el cambio rompe algo que la plataforma espera de tu detector. Avísanos y lo vemos juntos.
4. Abre un **Pull Request hacia `main`**. Jean Paul lo revisa y lo une.
5. **Avísanos antes de modificar `web/` o `pgc/`**: es la parte de la plataforma y tiene pruebas que fijan su comportamiento.
6. No subas secretos (`.env`, `config_ble.py`), binarios (`.exe`, `.dll`, `.pdb`), entornos virtuales (`.venv-detector`) ni el dataset completo. Para el dataset, mejor un enlace.

Cualquier duda, escríbenos. ¡Gracias!

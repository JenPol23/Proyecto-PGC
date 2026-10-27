# Contrato: cómo conectar el reconocimiento de señas al sistema

Para: Lina, Paula y Jean Harry · De: Jean Paul · Versión 1.1 (26/10/2026; la 1 es del 20/10/2026)

Este documento explica qué clase deben entregar para que su parte (Kinect + modelos de IA) se conecte a la plataforma **sin tocar el resto del código**, y qué hace la plataforma con lo que ustedes reconozcan.

> **Novedades de la versión 1.1 — para que Camila lo revise.** Su detector (`integracion_kinect/detector/server_web_svm.py`) ya está conectado con este contrato, **sin modificar nada de su carpeta**:
> - `pgc/adaptadores/kinect/reconocedor.py` (`ReconocedorKinect`) es la clase del contrato. La escribió Jean Paul con el visto bueno del equipo; está explicada en el §9. **Por favor revísenla**: si algo no coincide con cómo funciona su detector, díganmelo.
> - La plataforma arranca su detector (con el Python de `.venv-detector`) y su app C# compilada, y los cierra al salir. La pestaña Kinect del celular y la vista del proyector son ahora parte de la plataforma.
> - El §3.1 agrega **controles opcionales** (iniciar, detener, espacio, borrar, terminar). Una clase sin ellos sigue siendo válida.
> - `iniciar_pgc_integrado.py` y `acceso_kinect.py` quedan **obsoletos** (§10). No se borraron ni se modificaron.

---

## 1. La idea en una frase

Ustedes entregan **una clase de Python** que abre el Kinect, corre sus modelos y, cada vez que **confirma** una letra, llama a una función que yo les paso. Yo me encargo del resto: armar el texto, mostrarlo en el proyector y en el celular, decirlo en voz alta y, en modo eco, mandarlo a la mano.

```
Kinect ─► su puente C# ─► su clase Python ─► EventoSena ─► plataforma ─► pantalla · voz · mano
```

## 2. Dónde va su código

```
ProyectoPGC/pgc/adaptadores/kinect/     ← carpeta de ustedes; pueden organizarla como quieran
    __init__.py
    reconocedor.py                      ← aquí va la clase que cumple el contrato
    modelos/  puente/  ...              ← lo que necesiten (pesos, puente C#, utilidades)
```

No modifiquen nada fuera de esa carpeta. Si necesitan algo de la plataforma, me lo piden.

## 3. Lo que deben implementar

Copien estas definiciones tal cual. En la plataforma estarán en `pgc/puertos/reconocedor.py`; ustedes las importan de ahí:

```python
from dataclasses import dataclass
from typing import Callable, Literal, Protocol

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
                al_cambiar_estado: Callable[[], None]) -> None: ...
    def detener(self) -> None: ...
```

### Qué significa cada evento

| Evento | Cuándo lo envían | Qué hace la plataforma |
|---|---|---|
| `EventoSena("letra", letra="h", confianza=0.93, modelo="A-mlp", ...)` | Cuando **ustedes** deciden que una letra está confirmada | La agrega al texto y la muestra |
| `EventoSena("espacio")` | Pausa o gesto de separación entre palabras | Agrega un espacio |
| `EventoSena("borrar")` | Gesto de corregir, si lo implementan | Borra la última letra |
| `EventoSena("fin")` | La persona terminó (por ejemplo, baja la mano unos segundos) | Dice el texto en voz alta, lo envía al celular y, en modo eco, a la mano |

### Estados

| Estado | Significado |
|---|---|
| `"apagado"` | Antes de `iniciar()` o después de `detener()` |
| `"cargando"` | Abriendo el Kinect o cargando modelos |
| `"listo"` | Hay una persona frente al Kinect y se está reconociendo |
| `"sin_persona"` | Funciona, pero no hay nadie al frente |
| `"error"` | Algo falló; el motivo va en `detalle` |

Cada vez que cambien `estado` o `detalle`, llamen a `al_cambiar_estado()`.

### 3.1 Extensiones opcionales (versión 1.1)

Si la clase las tiene, la plataforma las usa; si no, todo sigue funcionando (sin botones en las pantallas).

| Extensión | Para qué |
|---|---|
| `controlar(accion)` con `"iniciar"`, `"detener"`, `"espacio"`, `"borrar"`, `"terminar"` | Los botones del celular (quien tiene el turno) y del proyector (el presentador). `"terminar"` debe terminar emitiendo `EventoSena("fin")`. Si falla, lanza una excepción con un mensaje corto para el jurado |
| `imagen()` → JPEG o `None` | La cámara con los puntos de la mano. **Solo** se muestra en el proyector del PC, nunca por el túnel |
| `diagnostico()` → dict o `None` | Por qué una letra se confirma o no (mano, predicción, 2.ª opción, margen, tiempo estable, motivo). Solo para la vista de diagnóstico del PC |
| `imagen_con_estado(despues=None, espera=0)` → `{jpeg, texto, detalle, cuadro, edad_ms, desfase_ms}` o `None` | La imagen con el texto y el estado leídos para ELLA (el proyector los muestra juntos); con `despues=N` espera hasta `espera` s un cuadro más nuevo que N |
| atributos `conectado`, `camara`, `activo` | Si el detector responde, si llegan imágenes y si el deletreo está iniciado |
| `desde_config(cfg)` (método de clase) | Recibir la configuración `PGC_KINECT_*` en lugar de leer el `.env` (regla 6) |

## 4. Reglas (las importantes)

1. **Ustedes confirman las letras.** La estabilización (por ejemplo, la misma letra en N cuadros seguidos, con una confianza mínima) y el corrector por caracteres son parte de su trabajo y de su evaluación. A mí solo me llegan letras ya decididas, nunca predicciones cuadro a cuadro.
2. **`iniciar()` retorna enseguida.** Abrir el Kinect y cargar modelos se hace en un hilo de ustedes. Mientras tanto, `estado = "cargando"`.
3. **Los callbacks se pueden llamar desde cualquier hilo**, y yo retorno enseguida: guardo el evento en una cola y lo proceso aparte. Ustedes nunca quedan bloqueados.
4. **Nunca dejen escapar excepciones desde sus hilos.** Si algo falla: `estado = "error"`, `detalle = "<motivo corto>"` y `al_cambiar_estado()`.
5. **`detener()` libera todo** (Kinect, hilos, sockets) y se puede llamar más de una vez sin error.
6. **El constructor no recibe argumentos.** Si necesitan configuración (puerto del puente, modelo a usar, umbral), léanla de variables `PGC_KINECT_*` en el archivo `.env`. Nunca usen rutas absolutas de un PC: usen rutas relativas a su carpeta (`Path(__file__).parent / "modelos"`).
7. **Letras válidas**: `a`–`z` y `ñ`, en minúscula. Las que llevan movimiento (j, z, ñ) las reconoce el modelo B. Si una letra no está en su modelo, simplemente no la emitan.

## 5. Esqueleto para empezar

```python
# pgc/adaptadores/kinect/reconocedor.py
import threading
import time
from pgc.puertos.reconocedor import EventoSena

class ReconocedorKinect:
    def __init__(self):
        self.estado = "apagado"
        self.detalle = ""
        self._parar = threading.Event()
        self._hilo = None

    def iniciar(self, al_evento, al_cambiar_estado):
        self._al_evento, self._avisar = al_evento, al_cambiar_estado
        self._cambiar("cargando", "Abriendo Kinect v1…")
        self._hilo = threading.Thread(target=self._bucle, daemon=True, name="kinect")
        self._hilo.start()

    def detener(self):
        self._parar.set()
        if self._hilo:
            self._hilo.join(timeout=3)
        self._cambiar("apagado", "")

    def _cambiar(self, estado, detalle):
        self.estado, self.detalle = estado, detalle
        self._avisar()

    def _bucle(self):
        try:
            # 1. abrir el puente / Kinect y cargar los modelos
            self._cambiar("listo", "Kinect v1 · modelo A")
            while not self._parar.is_set():
                t0 = time.monotonic()
                # 2. leer un cuadro, recortar la mano, MediaPipe, modelo...
                # 3. cuando una letra quede confirmada:
                #    self._al_evento(EventoSena("letra", letra="a", confianza=0.95,
                #                    modelo="A-mlp", instante=t0,
                #                    latencia_ms=(time.monotonic() - t0) * 1000))
                time.sleep(0.03)
        except Exception as ex:
            self._cambiar("error", f"Kinect: {ex}"[:80])
```

## 6. Cómo se conecta y cómo prueban

1. En el archivo `.env` de la carpeta del proyecto:
   ```
   PGC_RECONOCEDOR=pgc.adaptadores.kinect.reconocedor:ReconocedorKinect
   ```
   (Desde la versión 1.1 es el valor por defecto, con el nombre corto `PGC_RECONOCEDOR=kinect`.) Si la clase no se puede importar o falla al iniciar, la plataforma usa un reconocedor simulado y el proyector muestra "Kinect: no disponible". La demo no se cae.
2. Antes de entregarme su parte, corran las **pruebas de contrato**:
   ```
   py -3.11 -m pytest tests/contratos --reconocedor=pgc.adaptadores.kinect.reconocedor:ReconocedorKinect
   ```
   Comprueban que `iniciar()` no bloquea, que los eventos tienen el formato correcto y que `detener()` se puede llamar dos veces. No necesitan la mano ni el servidor.
3. Para probar en vivo: `iniciar.bat --simular` (o `py -3.11 -m pgc --simular`) y abran `http://127.0.0.1:8000/pantalla`. Lo que reconozcan debe aparecer en el proyector. Sin Kinect, con la cámara del PC: `PGC_KINECT_CAPTURADOR=camara_pc` en el `.env`.

## 7. Lo que yo les garantizo

- Las definiciones de la sección 3 no cambian sin avisarles y acordarlo. Si cambian, sube la versión de este documento.
- Recibo los eventos sin bloquearlos, y un error en su parte no tumba el servidor.
- Mientras su parte no esté lista, yo pruebo con un `ReconocedorSimulado` que emite los mismos eventos.

## 8. Lo que necesito que me digan

- Qué gesto usarán para `espacio` y para `fin`, para mostrarlo en la pantalla de ayuda. *(Por ahora son los botones Espacio y Terminar.)*
- Cuánto tarda en promedio entre que la persona forma la letra y el evento (`latencia_ms`), para ajustar las animaciones.
- ~~Si su puente C# usa un puerto local~~: el detector usa `127.0.0.1:8765` (respondido con el PR #2).
- **Pedido de la versión 1.1:** que `/spell/status` devuelva también JSON con la confianza y la latencia de cada letra (§9). El adaptador ya lo entiende; mientras tanto, los eventos llevan `confianza=1.0`.

Dudas: escríbanme antes de cambiar algo fuera de su carpeta.

## 9. Cómo se conectó el detector de Camila (`ReconocedorKinect`)

```
Kinect ─► app C# (capturador) ─JPEG POST /detect─► detector :8765 (MediaPipe + SVM) ◄─GET /spell/status cada 0,3 s─ ReconocedorKinect ─► EventoSena ─► plataforma
```

- **Su código se usa tal cual.** La plataforma arranca `server_web_svm.py` con el Python de `.venv-detector` (sus versiones exactas, con `instalar_detector.bat`) y su app C# compilada, minimizada. Los cierra al salir, aunque se cierre a la fuerza. No escribe nada en `integracion_kinect/` (ni `__pycache__`).
- **De su texto a eventos:** el adaptador compara el texto anterior con el nuevo: letra nueva → `letra` (en minúscula), espacio → `espacio`, texto más corto → `borrar`. Sus reglas de confirmación (0,7 s estable, 4 imágenes, retirar la mano 0,5 s) siguen siendo las que deciden las letras.
- **Terminar:** el adaptador recoge las letras pendientes, emite `fin` y deja en blanco su texto (`POST /spell/clear`). La frase se dice con la voz de la plataforma (Coqui, por los parlantes del PC) y, con el modo eco, la mano la deletrea.
- **Estados:** sin detector o sin imágenes → `"error"` con "Kinect no conectado"; reconociendo con la mano a la vista → `"listo"`; detenido o sin mano → `"sin_persona"`. El detalle es su propia línea de `Estado:` ("Posible letra: A | Estable: 0.4 s").
- **JSON (pedido):** si `/spell/status` devuelve `{"texto": "HOLA", "estado": "…", "activo": true, "confianza": 0.93, "latencia_ms": 120}`, el adaptador lo usa sin cambios. El texto plano actual sigue funcionando.
- **Control:** un jurado a la vez toma el turno desde su celular; el presentador controla siempre desde el proyector. Reemplaza al código de 8 dígitos (motivos en ARQUITECTURA.md, ADR-9).
- **Pruebas:** `tests/detector_falso.py` habla igual que su detector; `tests/test_kinect_adaptador.py` y `tests/test_kinect_plataforma.py` lo usan. La prueba de contrato pasa: `py -3.11 -m pytest tests/contratos --reconocedor=pgc.adaptadores.kinect.reconocedor:ReconocedorKinect`.

## 9.1 Cambio de velocidad (27/10/2026)

Con autorización del autor (la sustentación es en su PC): tu app se compila aquí con la espera entre imágenes en **50 ms** (antes 100; es la única línea cambiada de tu código) y tu `server_web_svm.py` se sirve sin cambios con `pgc/adaptadores/kinect/detector_paralelo.py` (lecturas en paralelo). Detalle y mediciones: HANDOFF.md y ARQUITECTURA.md (ADR-10).

## 10. Lo que queda obsoleto (sin borrar)

`iniciar_pgc_integrado.py` y `acceso_kinect.py` (en la raíz) ya no hacen falta: `iniciar.bat` arranca todo y la pestaña Kinect es parte de la página. **No se borraron ni se modificaron**, y siguen funcionando si alguien los ejecuta (la página del celular conserva las marcas que buscan). Cuando el equipo lo decida, se pueden quitar.

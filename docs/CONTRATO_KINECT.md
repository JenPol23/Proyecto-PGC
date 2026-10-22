# Contrato: cómo conectar el reconocimiento de señas al sistema

Para: Lina, Paula y Jean Harry · De: Jean Paul · Versión 1 (20/10/2026)

Este documento explica qué clase deben entregar para que su parte (Kinect + modelos de IA) se conecte a la plataforma **sin tocar el resto del código**, y qué hace la plataforma con lo que ustedes reconozcan.

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
   Si la clase no se puede importar o falla al iniciar, la plataforma usa un reconocedor simulado y el proyector muestra "Kinect: no disponible". La demo no se cae.
2. Antes de entregarme su parte, corran las **pruebas de contrato**:
   ```
   py -3.11 -m pytest tests/contratos --reconocedor=pgc.adaptadores.kinect.reconocedor:ReconocedorKinect
   ```
   Comprueban que `iniciar()` no bloquea, que los eventos tienen el formato correcto y que `detener()` se puede llamar dos veces. No necesitan la mano ni el servidor.
3. Para probar en vivo: `py -3.11 servidor.py --simular` y abran `http://127.0.0.1:8000/pantalla`. Lo que reconozcan debe aparecer en el proyector.

## 7. Lo que yo les garantizo

- Las definiciones de la sección 3 no cambian sin avisarles y acordarlo. Si cambian, sube la versión de este documento.
- Recibo los eventos sin bloquearlos, y un error en su parte no tumba el servidor.
- Mientras su parte no esté lista, yo pruebo con un `ReconocedorSimulado` que emite los mismos eventos.

## 8. Lo que necesito que me digan

- Qué gesto usarán para `espacio` y para `fin`, para mostrarlo en la pantalla de ayuda.
- Cuánto tarda en promedio entre que la persona forma la letra y el evento (`latencia_ms`), para ajustar las animaciones.
- Si su puente C# usa un puerto local, cuál, para no chocar con el 8000 del servidor.

Dudas: escríbanme antes de cambiar algo fuera de su carpeta.

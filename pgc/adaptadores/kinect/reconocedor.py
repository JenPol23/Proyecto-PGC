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
        self._t_pedida = -1e9         # alguien (el proyector) quiere ver la imagen
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

    def _bucle(self):
        siguiente_imagen = 0.0
        while not self._parar.is_set():
            try:
                with self._lock:
                    self._sincronizar()
                ahora = self._reloj()
                if ahora >= siguiente_imagen:
                    self._actualizar_imagen()
                    # 5 imágenes/s si el proyector la está mostrando; si no, 1/s (solo para saber si hay cámara)
                    siguiente_imagen = ahora + (0.2 if ahora - self._t_pedida < 3 else 1.0)
            except Exception as ex:                       # regla 4: nada se escapa del hilo
                self._cambiar("error", f"Kinect: {type(ex).__name__}")
            self._parar.wait(self.intervalo)

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

    def _actualizar_imagen(self):
        try:
            estado, tipo, cuerpo = self._pedir("/preview.jpg")
            if estado == 200 and tipo.startswith("image/jpeg"):
                self._imagen, self._t_imagen = cuerpo, self._reloj()
        except (urllib.error.URLError, OSError):
            pass                                       # 503 = no llegan imágenes; el detector puede no estar
        self._camara_al_dia()

    def _camara_al_dia(self):
        self.camara = self.conectado and self._reloj() - self._t_imagen < 3.0

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

    def imagen(self):
        """Última imagen JPEG con los puntos de la mano, o None. Pedirla sube el ritmo de actualización."""
        self._t_pedida = self._reloj()
        if self._imagen is None or self._reloj() - self._t_imagen > 3.0:
            return None
        return self._imagen

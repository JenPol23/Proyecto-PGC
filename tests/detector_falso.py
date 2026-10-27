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

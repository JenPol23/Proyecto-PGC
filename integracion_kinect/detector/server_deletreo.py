from collections import deque
from http.server import HTTPServer
from pathlib import Path
import json
import tempfile
import threading
import time

import mediapipe as mp
import numpy as np

from server_alfabeto import (
    HandlerAlfabeto,
    DetectorConGrabacion,
)

from probar_senas import extraer_secuencia
from probar_alfabeto import predecir


BASE = Path(__file__).resolve().parent
MODELO = BASE / "modelo_alfabeto.npz"


class Deletreador:
    def __init__(self):
        self.lock = threading.Lock()
        self.activo = False
        self.generacion = 0

        self.frames = deque()
        self.texto = ""
        self.estado = "Deletreo detenido."

        self.armado = True
        self.candidata = None
        self.repeticiones = 0

        self.sin_mano_desde = None
        self.ultimo_frame = 0.0

        self.referencias = None
        self.etiquetas = None

        threading.Thread(
            target=self.trabajar,
            daemon=True,
        ).start()

    def reiniciar_candidata(self):
        self.candidata = None
        self.repeticiones = 0

    def comando(self, accion):
        if accion == "start":
            with np.load(
                MODELO,
                allow_pickle=False,
            ) as modelo:
                referencias = modelo["secuencias"].copy()
                etiquetas = modelo["etiquetas"].copy()

            requeridas = {
            "a", "e", "i", "o", "u",
            "b", "c", "l",
            "d", "f", "v",
            "sin_letra",
            }

            if not requeridas.issubset(
                set(etiquetas.tolist())
            ):
                raise ValueError(
                    "El modelo no contiene todas las vocales "
                    "y Sin letra."
                )

            with self.lock:
                self.referencias = referencias
                self.etiquetas = etiquetas
                self.activo = True
                self.generacion += 1
                self.frames.clear()
                self.armado = True
                self.sin_mano_desde = None
                self.ultimo_frame = 0.0
                self.reiniciar_candidata()
                self.estado = "Mantén una vocal visible."

            return

        with self.lock:
            # Invalidar análisis que estuvieran en curso.
            self.generacion += 1
            self.reiniciar_candidata()

            if accion == "stop":
                self.activo = False
                self.frames.clear()
                self.estado = "Deletreo detenido."

            elif accion == "space":
                if self.texto and not self.texto.endswith(" "):
                    self.texto += " "

            elif accion == "backspace":
                self.texto = self.texto[:-1]

            elif accion == "clear":
                self.texto = ""

            else:
                raise ValueError("Comando no válido.")

    def agregar(self, resultado, ancho, alto):
        ahora = time.monotonic()

        manos = [
            [
                {
                    "x": float(p.x),
                    "y": float(p.y),
                    "z": float(p.z),
                }
                for p in mano.landmark
            ]
            for mano in (
                resultado.multi_hand_landmarks or []
            )
        ]

        with self.lock:
            if not self.activo:
                return

            # No mezclar imágenes separadas por una pausa.
            if (
                self.ultimo_frame
                and ahora - self.ultimo_frame > 1.0
            ):
                self.frames.clear()
                self.generacion += 1
                self.reiniciar_candidata()

            self.ultimo_frame = ahora

            if not manos:
                if self.sin_mano_desde is None:
                    self.sin_mano_desde = ahora

                if ahora - self.sin_mano_desde >= 0.5:
                    # Retirar la mano prepara la siguiente letra.
                    self.armado = True
                    self.frames.clear()
                    self.generacion += 1
                    self.reiniciar_candidata()
                    self.estado = "Lista para la siguiente letra."

                return

            self.sin_mano_desde = None

            if not self.armado:
                self.estado = (
                    "Letra añadida. Retira la mano "
                    "medio segundo para continuar."
                )
                return

            self.frames.append({
                "t": ahora,
                "width": ancho,
                "height": alto,
                "hands": manos,
            })

            # Ventana móvil de dos segundos.
            while (
                self.frames
                and ahora - self.frames[0]["t"] > 2.0
            ):
                self.frames.popleft()

    def trabajar(self):
        while True:
            time.sleep(0.6)

            with self.lock:
                if (
                    not self.activo
                    or not self.armado
                    or len(self.frames) < 10
                    or self.sin_mano_desde is not None
                ):
                    continue

                if time.monotonic() - self.ultimo_frame > 1.0:
                    continue

                frames = list(self.frames)

                if frames[-1]["t"] - frames[0]["t"] < 1.0:
                    continue

                generacion = self.generacion
                referencias = self.referencias
                etiquetas = self.etiquetas

            try:
                # Reutilizar la misma extracción que se
                # empleó al entrenar, sin guardar ejemplos.
                with tempfile.TemporaryDirectory(
                    prefix="lsc_deletreo_"
                ) as carpeta:
                    archivo = Path(carpeta) / "ventana.json"

                    archivo.write_text(
                        json.dumps({"frames": frames}),
                        encoding="utf-8",
                    )

                    consulta = extraer_secuencia(archivo)

                prediccion = predecir(
                    consulta,
                    referencias,
                    etiquetas,
                )

                with self.lock:
                    if (
                        not self.activo
                        or not self.armado
                        or generacion != self.generacion
                        or self.sin_mano_desde is not None
                        or time.monotonic() - self.ultimo_frame > 1.0
                    ):
                        continue

                    if prediccion == "sin_letra":
                        self.reiniciar_candidata()
                        self.estado = "Sin letra reconocida."
                        continue

                    if prediccion == self.candidata:
                        self.repeticiones += 1
                    else:
                        self.candidata = prediccion
                        self.repeticiones = 1

                    self.estado = (
                        f"Posible letra: {prediccion.upper()} | "
                        f"Confirmaciones: {self.repeticiones}/2"
                    )

                    # Confirmación inicial por dos resultados
                    # consecutivos. No es una confianza calibrada.
                    if self.repeticiones >= 1:
                        self.texto += prediccion.upper()
                        self.armado = False
                        self.frames.clear()
                        self.reiniciar_candidata()
                        self.estado = (
                            "Letra añadida. Retira la mano "
                            "medio segundo para continuar."
                        )

            except Exception as error:
                with self.lock:
                    if generacion == self.generacion:
                        self.estado = "Error: " + str(error)

    def obtener_estado(self):
        with self.lock:
            estado = self.estado

            if (
                self.activo
                and (
                    not self.ultimo_frame
                    or time.monotonic() - self.ultimo_frame > 2.0
                )
            ):
                estado = "Esperando imágenes del Kinect."

            return (
                "Texto: " + (self.texto or "—")
                + "\nEstado: " + estado
            )


deletreador = Deletreador()


class DetectorDeletreo(DetectorConGrabacion):
    def process(self, imagen_rgb):
        resultado = super().process(imagen_rgb)

        alto, ancho = imagen_rgb.shape[:2]

        deletreador.agregar(
            resultado,
            ancho,
            alto,
        )

        return resultado


class HandlerDeletreo(HandlerAlfabeto):
    def do_GET(self):
        if self.path == "/spell/status":
            self.send_data(
                200,
                deletreador.obtener_estado().encode("utf-8"),
                "text/plain; charset=utf-8",
            )
            return

        super().do_GET()

    def do_POST(self):
        if not self.path.startswith("/spell/"):
            super().do_POST()
            return

        accion = self.path.removeprefix("/spell/")

        if accion not in {
            "start", "stop", "space", "backspace", "clear"
        }:
            self.send_error(404)
            return

        try:
            cantidad = int(
                self.headers.get("Content-Length", "0")
            )

            if not 0 <= cantidad <= 100:
                self.send_error(413)
                return

            self.rfile.read(cantidad)
            deletreador.comando(accion)

        except Exception as error:
            self.send_data(
                400,
                str(error).encode("utf-8"),
                "text/plain; charset=utf-8",
            )
            return

        self.send_data(
            200,
            b"OK",
            "text/plain; charset=utf-8",
        )


def main():
    with mp.solutions.hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5,
    ) as detector:
        HandlerDeletreo.detector = DetectorDeletreo(detector)

        servidor = HTTPServer(
            ("127.0.0.1", 8765),
            HandlerDeletreo,
        )

        print(
            "Servidor de deletreo listo en 127.0.0.1:8765",
            flush=True,
        )

        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\nCerrando servidor...")
        finally:
            servidor.server_close()


if __name__ == "__main__":
    main()
from http.server import HTTPServer
from pathlib import Path
import time

import joblib
import mediapipe as mp

from entrenar_estaticas import (
    caracteristicas,
    VERSION_CARACTERISTICAS,
)

from server_alfabeto import (
    HandlerAlfabeto,
    DetectorConGrabacion,
)


BASE = Path(__file__).resolve().parent
MODELO = BASE / "modelo_estaticas.joblib"

# Tiempo mínimo de una predicción estable.
TIEMPO_CONFIRMACION = 0.7

# Ausencia de mano necesaria para preparar otra letra.
TIEMPO_LIBERACION = 0.5


class DeletreadorSVM:
    def __init__(self):
        self.modelo = None
        self.activo = False
        self.texto = ""
        self.estado = "Deletreo detenido."

        self.armado = True
        self.candidata = None
        self.candidata_desde = None
        self.confirmaciones = 0

        self.sin_mano_desde = None
        self.ultimo_frame = 0.0

    def reiniciar_candidata(self):
        self.candidata = None
        self.candidata_desde = None
        self.confirmaciones = 0

    def comando(self, accion):
        if accion == "start":
            if not MODELO.exists():
                raise ValueError(
                    "No existe modelo_estaticas.joblib."
                )

            # Cargar únicamente el modelo que generaste tú.
            contenido = joblib.load(MODELO)

            if (
                contenido["version_caracteristicas"]
                != VERSION_CARACTERISTICAS
            ):
                raise ValueError(
                    "La versión de características no coincide. "
                    "Vuelve a entrenar el modelo."
                )

            self.modelo = contenido["modelo"]
            self.activo = True
            self.armado = True
            self.sin_mano_desde = None
            self.ultimo_frame = 0.0
            self.reiniciar_candidata()

            self.estado = (
                "Mantén una letra estática visible."
            )
            return

        if accion == "stop":
            self.activo = False
            self.reiniciar_candidata()
            self.estado = "Deletreo detenido."
            return

        if accion == "space":
            if self.texto and not self.texto.endswith(" "):
                self.texto += " "
            return

        if accion == "backspace":
            self.texto = self.texto[:-1]
            return

        if accion == "clear":
            self.texto = ""
            return

        raise ValueError("Comando no válido.")

    def agregar(self, resultado):
        if not self.activo:
            return

        ahora = time.monotonic()

        # No considerar continuas imágenes separadas
        # por una pausa larga de la cámara.
        if (
            self.ultimo_frame
            and ahora - self.ultimo_frame > 1.0
        ):
            self.reiniciar_candidata()
            self.sin_mano_desde = None

        self.ultimo_frame = ahora

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

        if not manos:
            self.reiniciar_candidata()

            if self.sin_mano_desde is None:
                self.sin_mano_desde = ahora

            if (
                ahora - self.sin_mano_desde
                >= TIEMPO_LIBERACION
            ):
                self.armado = True
                self.estado = (
                    "Lista para la siguiente letra."
                )
            else:
                self.estado = "No se detecta la mano."

            return

        self.sin_mano_desde = None

        if len(manos) != 1:
            self.reiniciar_candidata()
            self.estado = (
                "Muestra solamente la mano dominante."
            )
            return

        if not self.armado:
            self.estado = (
                "Letra añadida. Retira la mano "
                "medio segundo para continuar."
            )
            return

        vector = caracteristicas(manos)

        if vector is None:
            self.reiniciar_candidata()
            self.estado = (
                "Puntos de mano no válidos. "
                "Comprueba la imagen."
            )
            return

        prediccion = str(
            self.modelo.predict(
                vector.reshape(1, -1)
            )[0]
        )

        if prediccion == "sin_letra":
            self.reiniciar_candidata()
            self.estado = "Sin letra reconocida."
            return

        if prediccion != self.candidata:
            self.candidata = prediccion
            self.candidata_desde = ahora
            self.confirmaciones = 1
        else:
            self.confirmaciones += 1

        duracion = ahora - self.candidata_desde

        self.estado = (
            f"Posible letra: {prediccion.upper()} | "
            f"Estable: {duracion:.1f} s"
        )

        # Combinar duración y cantidad de imágenes.
        if (
            duracion >= TIEMPO_CONFIRMACION
            and self.confirmaciones >= 4
        ):
            self.texto += prediccion.upper()
            self.armado = False
            self.reiniciar_candidata()

            self.estado = (
                "Letra añadida. Retira la mano "
                "medio segundo para continuar."
            )

    def obtener_estado(self):
        estado = self.estado

        if (
            self.activo
            and (
                not self.ultimo_frame
                or time.monotonic()
                - self.ultimo_frame > 2.0
            )
        ):
            estado = "Esperando imágenes del Kinect."

        return (
            "Texto: " + (self.texto or "—")
            + "\nEstado: " + estado
        )


deletreador = DeletreadorSVM()


class DetectorSVM(DetectorConGrabacion):
    def process(self, imagen_rgb):
        resultado = super().process(imagen_rgb)

        try:
            deletreador.agregar(resultado)
        except Exception as error:
            deletreador.reiniciar_candidata()
            deletreador.estado = (
                "Error de reconocimiento: " + str(error)
            )

        return resultado


class HandlerSVM(HandlerAlfabeto):
    def do_GET(self):
        if self.path == "/spell/status":
            self.send_data(
                200,
                deletreador.obtener_estado().encode(
                    "utf-8"
                ),
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
            "start",
            "stop",
            "space",
            "backspace",
            "clear",
        }:
            self.send_error(404)
            return

        try:
            cantidad = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
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
        HandlerSVM.detector = DetectorSVM(detector)

        servidor = HTTPServer(
            ("127.0.0.1", 8765),
            HandlerSVM,
        )

        print(
            "Servidor SVM listo en 127.0.0.1:8765",
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
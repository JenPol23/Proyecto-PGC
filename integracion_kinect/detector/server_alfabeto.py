from datetime import datetime, timezone
from http.server import HTTPServer
from pathlib import Path
import json
import time
import uuid

import mediapipe as mp

from server import DetectorHandler


BASE = Path(__file__).resolve().parent
DATASET = BASE / "dataset_alfabeto"

CATEGORIAS = {
    "a",
    "e",
    "i",
    "o",
    "u",
    "b",
    "c",
    "l",
    "d",
    "f",
    "v",
    "h",
    "m",
    "n",
    "p",
    "t",
    "r",
    "s",
    "w",
    "y",
    "x",
    "z",
    "g",
    "q",
    "j",
    "k",
    "sin_letra",
}


class GrabadorAlfabeto:
    def __init__(self):
        self.actual = None
        self.mensaje = "Selecciona una letra."

    def iniciar(self, categoria):
        self.finalizar_si_corresponde()

        if self.actual is not None:
            raise ValueError(
                "Ya hay una grabación de letras activa."
            )

        if categoria not in CATEGORIAS:
            raise ValueError("Categoría no válida.")

        self.actual = {
            "categoria": categoria,
            "inicio": time.monotonic(),
            "created_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "frames": [],
        }

        self.mensaje = "Grabando..."

    def agregar(self, resultado, ancho, alto):
        self.finalizar_si_corresponde()

        if self.actual is None:
            return

        manos = []

        for mano in (
            resultado.multi_hand_landmarks or []
        ):
            manos.append([
                {
                    "x": float(punto.x),
                    "y": float(punto.y),
                    "z": float(punto.z),
                }
                for punto in mano.landmark
            ])

        self.actual["frames"].append({
            "t": round(
                time.monotonic() -
                self.actual["inicio"],
                4,
            ),
            "width": ancho,
            "height": alto,
            "hands": manos,
        })

    def finalizar_si_corresponde(self):
        if self.actual is None:
            return

        transcurrido = (
            time.monotonic() -
            self.actual["inicio"]
        )

        if transcurrido < 3.0:
            return

        captura = self.actual
        self.actual = None

        frames = captura["frames"]
        categoria = captura["categoria"]

        if len(frames) < 10:
            self.mensaje = (
                "Descartado: llegaron menos de 10 imágenes. "
                "Comprueba la cámara y repite."
            )
            return

        con_manos = sum(
            bool(frame["hands"])
            for frame in frames
        )

        # Una vocal sostenida debe ser visible durante
        # buena parte de la grabación.
        if (
            categoria != "sin_letra"
            and con_manos < 0.7 * len(frames)
        ):
            self.mensaje = (
                "Descartado: faltó detección de manos "
                "en demasiadas imágenes. Repite."
            )
            return

        carpeta = DATASET / categoria
        carpeta.mkdir(parents=True, exist_ok=True)

        fecha = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%S"
        )

        nombre = (
            f"{fecha}_{uuid.uuid4().hex[:10]}.json"
        )

        destino = carpeta / nombre
        temporal = destino.with_suffix(".tmp")

        documento = {
            "schema_version": 1,
            "task": "lsc_fingerspelling",
            "label": categoria,
            "created_utc": captura["created_utc"],
            "duration_seconds": 3.0,
            "frame_count": len(frames),
            "frames_with_hands": con_manos,
            "coordinates": {
                "x_y": "normalized image coordinates",
                "z": "relative depth, not meters",
            },
            "frames": frames,
        }

        temporal.write_text(
            json.dumps(
                documento,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        temporal.replace(destino)

        cantidad = len(
            list(carpeta.glob("*.json"))
        )

        self.mensaje = (
            f"Guardado: {categoria.upper()} | "
            f"Ejemplos: {cantidad} | "
            f"Imágenes con manos: "
            f"{con_manos}/{len(frames)}"
        )

    def estado(self):
        self.finalizar_si_corresponde()

        if self.actual is not None:
            cantidad = len(
                self.actual["frames"]
            )

            return True, (
                "Grabando... "
                f"imágenes recibidas: {cantidad}"
            )

        return False, self.mensaje


grabador = GrabadorAlfabeto()


class DetectorConGrabacion:
    """
    Reutiliza MediaPipe y entrega el resultado al
    servidor existente y al grabador de letras.
    """

    def __init__(self, detector):
        self.detector = detector

    def process(self, imagen_rgb):
        resultado = self.detector.process(
            imagen_rgb
        )

        alto, ancho = imagen_rgb.shape[:2]

        grabador.agregar(
            resultado,
            ancho,
            alto,
        )

        return resultado


class HandlerAlfabeto(DetectorHandler):
    def do_GET(self):
        if self.path == "/alphabet/status":
            activo, mensaje = grabador.estado()

            self.send_data(
                200,
                mensaje.encode("utf-8"),
                "text/plain; charset=utf-8",
                {
                    "X-Alphabet-Recording":
                        "1" if activo else "0"
                },
            )
            return

        super().do_GET()

    def do_POST(self):
        if self.path != "/alphabet/start":
            super().do_POST()
            return

        try:
            cantidad = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

            if not 0 < cantidad <= 100:
                self.send_error(413)
                return

            categoria = self.rfile.read(
                cantidad
            ).decode("utf-8").strip()

            grabador.iniciar(categoria)

        except (ValueError, UnicodeError) as error:
            self.send_data(
                400,
                str(error).encode("utf-8"),
                "text/plain; charset=utf-8",
            )
            return

        self.send_data(
            200,
            b"Grabacion de letra iniciada",
            "text/plain; charset=utf-8",
        )


def main():
    DATASET.mkdir(
        parents=True,
        exist_ok=True,
    )

    with mp.solutions.hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5,
    ) as detector:
        HandlerAlfabeto.detector = (
            DetectorConGrabacion(detector)
        )

        servidor = HTTPServer(
            ("127.0.0.1", 8765),
            HandlerAlfabeto,
        )

        print(
            "Servidor de alfabeto listo "
            "en 127.0.0.1:8765",
            flush=True,
        )

        print(
            f"Ejemplos en: {DATASET}",
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
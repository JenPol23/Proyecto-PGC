from pathlib import Path
import json
import tempfile
import time

import numpy as np

from probar_senas import extraer_secuencia, distancia_dtw


BASE = Path(__file__).resolve().parent
MODELO = BASE / "modelo_hola_adios.npz"


class Reconocedor:
    def __init__(self):
        self.captura = None
        self.referencias = None
        self.etiquetas = None
        self.mensaje = "Listo para reconocer."

    def iniciar(self):
        if self.captura is not None:
            raise ValueError(
                "Ya hay un reconocimiento en curso."
            )

        if not MODELO.exists():
            raise ValueError(
                "No existe modelo_hola_adios.npz. "
                "Primero ejecuta el entrenamiento."
            )

        with np.load(MODELO, allow_pickle=False) as modelo:
            self.referencias = modelo["secuencias"].copy()
            self.etiquetas = modelo["etiquetas"].copy()

        self.captura = {
            "inicio": time.monotonic(),
            "frames": [],
        }

        self.mensaje = "Haz la seña ahora."

    def agregar_frame(self, hands, width, height):
        if self.captura is None:
            return

        elapsed = (
            time.monotonic() - self.captura["inicio"]
        )

        if elapsed >= 3.0:
            return

        self.captura["frames"].append({
            "t": round(elapsed, 4),
            "width": width,
            "height": height,
            "hands": hands,
        })

    def estado(self):
        if self.captura is None:
            return False, self.mensaje

        elapsed = (
            time.monotonic() - self.captura["inicio"]
        )

        if elapsed < 3.0:
            count = len(self.captura["frames"])
            return True, (
                f"Reconociendo... imágenes recibidas: {count}"
            )

        captura = self.captura
        self.captura = None

        frames = captura["frames"]

        if len(frames) < 10:
            self.mensaje = (
                "No llegaron suficientes imágenes. "
                "Vuelve a intentarlo."
            )
            return False, self.mensaje

        con_manos = sum(
            bool(frame["hands"]) for frame in frames
        )

        if con_manos < 5:
            self.mensaje = (
                "No se detectaron suficientes manos. "
                "Vuelve a intentarlo."
            )
            return False, self.mensaje

        try:
            # Archivo temporal para reutilizar exactamente
            # la extracción de características ya probada.
            # Se elimina al salir y no entra en dataset.
            with tempfile.TemporaryDirectory(
                prefix="lsc_reconocer_"
            ) as folder:
                archivo = Path(folder) / "captura.json"

                archivo.write_text(
                    json.dumps({"frames": frames}),
                    encoding="utf-8",
                )

                consulta = extraer_secuencia(archivo)

            distancias = np.array([
                distancia_dtw(consulta, referencia)
                for referencia in self.referencias
            ])

            puntuaciones = {}

            for etiqueta in ("hola", "adios"):
                valores = np.sort(
                    distancias[self.etiquetas == etiqueta]
                )

                if len(valores) == 0:
                    raise ValueError(
                        f"El modelo no contiene {etiqueta}."
                    )

                puntuaciones[etiqueta] = float(
                    np.mean(valores[:3])
                )

            prediccion = min(
                puntuaciones,
                key=puntuaciones.get,
            )

            palabras = {
                "hola": "Hola",
                "adios": "Adiós",
            }

            self.mensaje = (
                "Resultado: " + palabras[prediccion]
            )

        except Exception as error:
            self.mensaje = (
                "No se pudo reconocer: " + str(error)
            )

        return False, self.mensaje
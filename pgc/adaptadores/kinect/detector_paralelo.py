"""El detector de Camila (server_web_svm.py) TAL CUAL, atendiendo las lecturas en paralelo y con diagnóstico.

Su servidor (HTTPServer) atiende de a una petición: mientras procesa una imagen de /detect
(MediaPipe + SVM, ~25–45 ms), la vista previa y el estado esperan. Este envoltorio NO modifica
sus archivos: importa su módulo y lo sirve con ThreadingHTTPServer, con una regla para no
cambiar su lógica:

  - POST (/detect, /spell/*, /record/*, /alphabet/*, /recognize/*): de a uno, en orden, con un
    candado, igual que en su servidor (el deletreo y MediaPipe nunca corren en paralelo);
  - GET (/preview.jpg, /spell/status, ...): en paralelo; solo leen.

Además agrega GET /diagnostico (solo lectura): por qué una letra se confirma o no. Después de que
SU lógica procesa cada imagen, se leen los campos de su deletreador (candidata, desde cuándo,
confirmaciones, armado) y, con una copia propia de su modelo, la segunda letra más probable y el
margen entre ambas (su SVM no da probabilidades: probability=False). Nada de esto cambia su estado.

Lo lanza pgc/adaptadores/kinect/procesos.py con el Python de .venv-detector:
    python detector_paralelo.py <carpeta del detector>
"""
import json
import sys
import threading
import time
from collections import deque
from http.server import ThreadingHTTPServer
from pathlib import Path


class Diagnostico:
    """Último cuadro procesado: qué vio MediaPipe, qué dijo el SVM y por qué no (o sí) se confirma."""

    def __init__(self, svm_mod, entrenar_mod, modelo):
        self.svm = svm_mod                      # server_deletreo_svm (su módulo)
        self.caracteristicas = entrenar_mod.caracteristicas
        self.modelo = modelo                    # copia propia de su modelo_estaticas.joblib (o None)
        clases = list(modelo.classes_) if modelo is not None else list(entrenar_mod.CATEGORIAS)
        self.categorias = [str(c) for c in clases]
        self._lock = threading.Lock()
        self._ultimo = {"t": 0.0, "manos": None, "motivo": "Todavía no llegan imágenes"}
        self._recientes = deque(maxlen=60)      # (t, predicción) para ver si la letra está cambiando
        self._texto_antes = ""

    def registrar(self, resultado):
        ahora = time.monotonic()
        d = self.svm.deletreador
        manos = [[{"x": float(p.x), "y": float(p.y), "z": float(p.z)} for p in m.landmark]
                 for m in (resultado.multi_hand_landmarks or [])]
        pred = segunda = None
        margen = None
        if len(manos) == 1 and self.modelo is not None:
            vector = self.caracteristicas(manos)
            if vector is not None:
                fila = vector.reshape(1, -1)
                pred = str(self.modelo.predict(fila)[0])                  # la misma predicción que su lógica
                puntajes = self.modelo.decision_function(fila)[0]
                clases = [str(c) for c in self.modelo.classes_]
                orden = sorted(range(len(clases)), key=lambda i: puntajes[i], reverse=True)
                otras = [i for i in orden if clases[i] != pred]
                if otras:
                    segunda = clases[otras[0]]
                    margen = round(float(puntajes[clases.index(pred)] - puntajes[otras[0]]), 3)
        if pred is not None:
            self._recientes.append((ahora, pred))
        ventana = {p for t, p in self._recientes if ahora - t <= self.svm.TIEMPO_CONFIRMACION}
        estable = (ahora - d.candidata_desde) if (d.candidata and d.candidata_desde) else 0.0
        confirmada = d.texto[len(self._texto_antes):] if d.texto.startswith(self._texto_antes) else ""
        self._texto_antes = d.texto
        motivo = self._motivo(d, len(manos), pred, ventana, estable, confirmada)
        with self._lock:
            self._ultimo = {
                "t": ahora, "activo": bool(d.activo), "manos": len(manos),
                "prediccion": pred, "segunda": segunda, "margen": margen,
                "candidata": d.candidata, "estable_s": round(estable, 2), "confirmaciones": d.confirmaciones,
                "armado": bool(d.armado), "texto": d.texto, "estado": d.estado,
                "confirmada": confirmada.strip().lower() or None,
                "letras_recientes": sorted(ventana), "motivo": motivo,
                "tiempo_confirmacion": self.svm.TIEMPO_CONFIRMACION, "tiempo_liberacion": self.svm.TIEMPO_LIBERACION,
                "confirmaciones_necesarias": 4,
            }

    def _motivo(self, d, manos, pred, ventana, estable, confirmada):
        if confirmada.strip():
            return f"Letra confirmada: {confirmada.strip().upper()}"
        if not d.activo:
            return "Deletreo detenido"
        if manos == 0:
            return "Mano no detectada"
        if manos > 1:
            return "Más de una mano"
        if not d.armado:
            return f"Retira la mano {self.svm.TIEMPO_LIBERACION} s para la siguiente letra"
        if pred is None:
            return "Puntos de la mano no válidos"
        if pred == "sin_letra":
            return "El modelo dice «sin letra»"
        if len(ventana) > 1:
            return "Letra cambiando: " + " / ".join(sorted(x.upper() for x in ventana))
        if estable < self.svm.TIEMPO_CONFIRMACION:
            return f"Tiempo insuficiente: {estable:.1f} de {self.svm.TIEMPO_CONFIRMACION} s"
        if d.confirmaciones < 4:
            return f"Pocas imágenes: {d.confirmaciones} de 4"
        return "Confirmando…"

    def json(self):
        with self._lock:
            datos = dict(self._ultimo)
        datos["edad_ms"] = round((time.monotonic() - datos["t"]) * 1000) if datos["t"] else None
        datos["categorias"] = self.categorias
        return json.dumps(datos, ensure_ascii=False).encode("utf-8")


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    sys.path.insert(0, str(carpeta))
    import joblib
    import mediapipe as mp
    import entrenar_estaticas                           # sus módulos, sin cambios
    import server_deletreo_svm
    import server_web_svm

    try:                                                 # copia propia: su deletreador carga la suya al iniciar
        modelo = joblib.load(server_deletreo_svm.MODELO)["modelo"]
    except Exception as ex:                              # sin modelo, el diagnóstico sigue (sin predicción)
        print(f"Diagnóstico sin modelo: {ex}", flush=True)
        modelo = None
    diagnostico = Diagnostico(server_deletreo_svm, entrenar_estaticas, modelo)
    una_a_la_vez = threading.Lock()

    class DetectorConDiagnostico(server_web_svm.DetectorSVM):
        def process(self, imagen_rgb):
            resultado = super().process(imagen_rgb)      # SU procesamiento (MediaPipe + su deletreo)
            try:
                diagnostico.registrar(resultado)
            except Exception as ex:                      # el diagnóstico nunca afecta a su detector
                print(f"Diagnóstico: {type(ex).__name__}: {ex}", flush=True)
            return resultado

    class HandlerParalelo(server_web_svm.HandlerWeb):
        def do_GET(self):
            if self.path == "/diagnostico":
                self.send_data(200, diagnostico.json(), "application/json; charset=utf-8",
                               {"Cache-Control": "no-store"})
                return
            super().do_GET()

        def do_POST(self):
            with una_a_la_vez:
                super().do_POST()

    # Los mismos parámetros de MediaPipe que su main() en server_web_svm.py
    with mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5) as manos:
        HandlerParalelo.detector = DetectorConDiagnostico(manos)
        servidor = ThreadingHTTPServer(("127.0.0.1", 8765), HandlerParalelo)
        servidor.daemon_threads = True
        print("Detector para la página listo en 127.0.0.1:8765 (lecturas en paralelo, con diagnóstico)", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            servidor.server_close()


if __name__ == "__main__":
    main()

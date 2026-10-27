"""El detector de Camila (server_web_svm.py) TAL CUAL, pero atendiendo las lecturas en paralelo.

Su servidor (HTTPServer) atiende de a una petición: mientras procesa una imagen de /detect
(MediaPipe + SVM, ~25–45 ms), la vista previa y el estado esperan, y la plataforma no alcanza a
mostrar más de ~12 imágenes por segundo. Este envoltorio NO modifica sus archivos: importa su
módulo y lo sirve con ThreadingHTTPServer, con una regla para no cambiar su lógica:

  - POST (/detect, /spell/*, /record/*, /alphabet/*, /recognize/*): de a uno, en orden, con un
    candado, igual que en su servidor (el deletreo y MediaPipe nunca corren en paralelo);
  - GET (/preview.jpg, /spell/status, ...): en paralelo; solo leen.

Lo lanza pgc/adaptadores/kinect/procesos.py con el Python de .venv-detector:
    python detector_paralelo.py <carpeta del detector>
Medido el 27/10/2026: de ~12 a ~18 imágenes por segundo en el proyector con una fuente de 20/s.
"""
import sys
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path


def main():
    carpeta = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    sys.path.insert(0, str(carpeta))
    import mediapipe as mp
    import server_web_svm                               # su módulo, sin cambios

    una_a_la_vez = threading.Lock()

    class HandlerParalelo(server_web_svm.HandlerWeb):
        def do_POST(self):
            with una_a_la_vez:
                super().do_POST()

    # Los mismos parámetros de MediaPipe que su main() en server_web_svm.py
    with mp.solutions.hands.Hands(static_image_mode=True, max_num_hands=2, min_detection_confidence=0.5) as manos:
        HandlerParalelo.detector = server_web_svm.DetectorSVM(manos)
        servidor = ThreadingHTTPServer(("127.0.0.1", 8765), HandlerParalelo)
        servidor.daemon_threads = True
        print("Detector para la página listo en 127.0.0.1:8765 (lecturas en paralelo)", flush=True)
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            servidor.server_close()


if __name__ == "__main__":
    main()

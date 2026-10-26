from http.server import HTTPServer
import time

import mediapipe as mp

from server_deletreo_svm import HandlerSVM, DetectorSVM


class HandlerWeb(HandlerSVM):
    ultima_imagen = None
    instante_imagen = 0.0

    def send_data(
        self,
        status,
        body,
        content_type,
        headers=None,
    ):
        if (
            self.path == "/detect"
            and status == 200
            and content_type == "image/jpeg"
        ):
            HandlerWeb.ultima_imagen = body
            HandlerWeb.instante_imagen = time.monotonic()

        super().send_data(
            status,
            body,
            content_type,
            headers,
        )

    def do_GET(self):
        if self.path == "/preview.jpg":
            if (
                self.ultima_imagen is None
                or time.monotonic()
                - self.instante_imagen > 3
            ):
                self.send_data(
                    503,
                    b"Esperando imagen del Kinect",
                    "text/plain",
                )
            else:
                self.send_data(
                    200,
                    self.ultima_imagen,
                    "image/jpeg",
                    {"Cache-Control": "no-store"},
                )

            return

        super().do_GET()


def main():
    with mp.solutions.hands.Hands(
        static_image_mode=True,
        max_num_hands=2,
        min_detection_confidence=0.5,
    ) as detector:
        HandlerWeb.detector = DetectorSVM(detector)

        servidor = HTTPServer(
            ("127.0.0.1", 8765),
            HandlerWeb,
        )

        print(
            "Detector para la página listo "
            "en 127.0.0.1:8765",
            flush=True,
        )

        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            servidor.server_close()


if __name__ == "__main__":
    main()
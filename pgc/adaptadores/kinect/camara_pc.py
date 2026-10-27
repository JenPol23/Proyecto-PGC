"""Envía la cámara del PC al detector, igual que la app C# hace con el Kinect (para probar sin Kinect).

Toma la cámara con OpenCV, la lleva a 640×480 (la resolución del Kinect v1) y
envía unas 10 imágenes por segundo en JPEG a POST /detect del detector.
Corre con el Python del entorno del detector (ya trae OpenCV); no importa nada de pgc.

    .venv-detector\\Scripts\\python pgc\\adaptadores\\kinect\\camara_pc.py [--camara 0] [--probar]
"""
import argparse
import sys
import time
import urllib.error
import urllib.request

import cv2


def abrir(indice):
    # En Windows, DirectShow abre más rápido y más cámaras que el backend por defecto
    for backend in ((cv2.CAP_DSHOW,) if sys.platform == "win32" else ()) + (cv2.CAP_ANY,):
        cam = cv2.VideoCapture(indice, backend)
        if cam.isOpened():
            cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            return cam
        cam.release()
    return None


def main():
    try:                                     # su salida va a registros\camara_pc.log (cp1252 en Windows)
        sys.stdout.reconfigure(errors="replace")
    except AttributeError:
        pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--url", default="http://127.0.0.1:8765")
    ap.add_argument("--camara", type=int, default=0)
    ap.add_argument("--fps", type=float, default=10)
    ap.add_argument("--probar", action="store_true", help="envía una sola imagen y termina")
    args = ap.parse_args()

    cam = abrir(args.camara)
    if cam is None:
        print(f"No se pudo abrir la cámara {args.camara}", flush=True)
        return 1
    print(f"Cámara {args.camara} abierta; enviando a {args.url}/detect", flush=True)
    pausa = 1.0 / max(args.fps, 1)
    try:
        while True:
            t0 = time.monotonic()
            ok, cuadro = cam.read()
            if not ok:
                print("La cámara no entregó imagen; reintentando", flush=True)
                time.sleep(1)
                continue
            cuadro = cv2.resize(cuadro, (640, 480))
            ok, jpeg = cv2.imencode(".jpg", cuadro, [cv2.IMWRITE_JPEG_QUALITY, 85])
            req = urllib.request.Request(args.url + "/detect", data=jpeg.tobytes(), method="POST",
                                         headers={"Content-Type": "image/jpeg"})
            try:
                with urllib.request.urlopen(req, timeout=3) as r:
                    manos = r.headers.get("X-Hands-Count", "?")
                if args.probar:
                    print(f"Imagen enviada; manos detectadas: {manos}", flush=True)
                    return 0
            except (urllib.error.URLError, OSError):
                time.sleep(1)                       # el detector aún no está listo
                continue
            time.sleep(max(0.0, pausa - (time.monotonic() - t0)))
    except KeyboardInterrupt:
        return 0
    finally:
        cam.release()


if __name__ == "__main__":
    sys.exit(main())

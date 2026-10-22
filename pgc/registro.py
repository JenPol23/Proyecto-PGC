"""Registro en consola: una línea con hora por evento, segura entre hilos."""
import threading
import time

_lock_log = threading.Lock()


def log(msg):
    with _lock_log:
        print(time.strftime("%H:%M:%S"), msg, flush=True)

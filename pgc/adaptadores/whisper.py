"""Voz → texto con faster-whisper (español). Implementa el puerto Transcriptor.

El modelo se carga en segundo plano al iniciar el servidor. Primero intenta
CUDA float16 (con un calentamiento para detectar fallos de la RTX 5050 /
Blackwell sm_120 con ctranslate2); si algo falla, cae a CPU int8.
"""
import importlib.util
import os
import threading
import time

import numpy as np

MODELO = "medium"   # en la caché HF como Systran/faster-whisper-medium


def _agregar_dlls_cuda_de_torch():
    """ctranslate2 necesita cuBLAS/cuDNN; torch ya los trae en torch/lib."""
    spec = importlib.util.find_spec("torch")
    if not spec or not spec.submodule_search_locations:
        return
    lib = os.path.join(list(spec.submodule_search_locations)[0], "lib")
    if os.path.isdir(lib):
        try:
            os.add_dll_directory(lib)
        except (AttributeError, OSError):
            pass
        os.environ["PATH"] = lib + os.pathsep + os.environ.get("PATH", "")


class Transcriptor:
    def __init__(self, log=print, al_cambiar=None, nombre_modelo=MODELO, log_textos=False):
        self.log = log
        self.al_cambiar = al_cambiar or (lambda: None)
        self.nombre_modelo = nombre_modelo
        self.log_textos = log_textos   # False: la transcripción no queda en el log
        self.modelo = None
        self.estado = "sin cargar"     # sin cargar | cargando | listo | error | desactivado
        self.dispositivo = None        # "cuda float16" | "cpu int8"
        self._lock = threading.Lock()  # una transcripción a la vez

    @property
    def listo(self):
        return self.modelo is not None

    def _cambiar(self, estado):
        self.estado = estado
        self.al_cambiar()

    def cargar_en_segundo_plano(self):
        threading.Thread(target=self.cargar, daemon=True, name="whisper").start()

    def cargar(self):
        self._cambiar("cargando")
        try:
            from faster_whisper import WhisperModel
        except Exception as ex:
            self.log(f"[voz] faster-whisper no disponible: {ex}")
            self._cambiar("error")
            return
        _agregar_dlls_cuda_de_torch()
        for device, compute in (("cuda", "float16"), ("cpu", "int8")):
            t0 = time.time()
            try:
                modelo = self._crear(WhisperModel, device, compute)
                # Calentamiento: sin VAD para que el codificador corra de verdad
                ruido = (np.random.randn(16000) * 0.01).astype(np.float32)
                segs, _ = modelo.transcribe(ruido, language="es", vad_filter=False, beam_size=1)
                list(segs)
                self.modelo = modelo
                self.dispositivo = f"{device} {compute}"
                self.log(f"[voz] Whisper {self.nombre_modelo} listo en {self.dispositivo} ({time.time() - t0:.1f} s)")
                self._cambiar("listo")
                return
            except Exception as ex:
                self.log(f"[voz] Falló Whisper en {device} {compute}: {ex}")
        self._cambiar("error")

    def _crear(self, WhisperModel, device, compute):
        # Primero sin internet (el modelo ya está en la caché); si no, descarga
        try:
            return WhisperModel(self.nombre_modelo, device=device, compute_type=compute, local_files_only=True)
        except Exception:
            return WhisperModel(self.nombre_modelo, device=device, compute_type=compute)

    def transcribir(self, ruta_audio):
        """Devuelve el texto reconocido (puede ser cadena vacía)."""
        if not self.listo:
            raise RuntimeError("el modelo de voz aún no está listo")
        with self._lock:
            t0 = time.time()
            segs, _ = self.modelo.transcribe(
                ruta_audio, language="es", vad_filter=True, beam_size=5,
            )
            texto = " ".join(s.text.strip() for s in segs).strip()
            detalle = f"'{texto}'" if self.log_textos else f"{len(texto)} caracteres"
            self.log(f"[voz] Transcripción: {detalle} ({time.time() - t0:.1f} s)")
            return texto

    @staticmethod
    def duracion(ruta_audio):
        """Segundos de audio, o None si no se pudo leer (Whisper decidirá)."""
        try:
            import av
            with av.open(ruta_audio) as contenedor:
                if contenedor.duration:
                    return contenedor.duration / av.time_base
                pistas = [s for s in contenedor.streams if s.type == "audio" and s.duration and s.time_base]
                return float(pistas[0].duration * pistas[0].time_base) if pistas else None
        except Exception:
            return None

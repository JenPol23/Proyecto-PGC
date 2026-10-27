"""Texto → voz con Coqui VITS en español (tts_models/es/css10/vits), por los parlantes del PC.

El modelo ya está en la caché (%LOCALAPPDATA%\\tts) y se carga en segundo plano
al arrancar, en CPU: una frase corta tarda menos de un segundo y así no compite
con Whisper por la GPU. Implementa el puerto pgc.puertos.sintetizador.Sintetizador.
"""
import threading
import time


class SintetizadorCoqui:
    def __init__(self, modelo="tts_models/es/css10/vits", log=print, al_cambiar=None):
        self.modelo = modelo
        self.log = log
        self.al_cambiar = al_cambiar or (lambda: None)
        self.estado = "sin cargar"     # sin cargar | cargando | listo | error | desactivado
        self._tts = None
        self._lock = threading.Lock()  # una frase a la vez

    def _cambiar(self, estado):
        self.estado = estado
        self.al_cambiar()

    def cargar_en_segundo_plano(self):
        threading.Thread(target=self.cargar, daemon=True, name="voz-salida-carga").start()

    def cargar(self):
        self._cambiar("cargando")
        t0 = time.time()
        try:
            from TTS.api import TTS
            tts = TTS(model_name=self.modelo, progress_bar=False).to("cpu")
            tts.tts(text="hola")                       # calentamiento
            self._tts = tts
            self.log(f"[voz] Voz de salida lista ({time.time() - t0:.1f} s)")
            self._cambiar("listo")
        except Exception as ex:
            self.log(f"[voz] No se pudo cargar la voz de salida: {type(ex).__name__}: {ex}")
            self._cambiar("error")

    def sintetizar(self, texto):
        """(muestras float32, frecuencia). Separado de decir() para probarlo sin parlantes."""
        import numpy as np
        if self._tts is None:
            raise RuntimeError("la voz de salida no está lista")
        with self._lock:
            muestras = np.asarray(self._tts.tts(text=texto), dtype=np.float32)
        return muestras, self._tts.synthesizer.output_sample_rate

    def decir(self, texto):
        if self._tts is None:
            self.log("[voz] La voz de salida no está lista; no se dice la frase")
            return
        import sounddevice as sd
        muestras, frecuencia = self.sintetizar(texto)
        sd.play(muestras, frecuencia)
        sd.wait()

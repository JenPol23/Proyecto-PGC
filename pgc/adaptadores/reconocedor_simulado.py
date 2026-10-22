"""Reconocedor de señas simulado: emite los eventos de un texto, como lo haría el Kinect.

Sirve para construir y probar el modo Kinect, el modo eco y la pantalla antes de
que llegue el reconocedor real. No emite nada por sí solo: hay que llamar a
`simular("hola")`.
"""
import threading
import time

from pgc.puertos.reconocedor import EventoSena


class ReconocedorSimulado:
    def __init__(self, pausa=0.8, detalle="Kinect simulado"):
        self.estado = "apagado"
        self.detalle = detalle
        self.pausa = pausa
        self._al_evento = self._avisar = None
        self._parar = threading.Event()

    def iniciar(self, al_evento, al_cambiar_estado):
        self._al_evento, self._avisar = al_evento, al_cambiar_estado
        self._parar.clear()
        self._cambiar("sin_persona")

    def detener(self):
        self._parar.set()
        if self.estado != "apagado":
            self._cambiar("apagado")

    def _cambiar(self, estado):
        self.estado = estado
        if self._avisar:
            self._avisar()

    def simular(self, texto, esperar=False):
        """Emite letra por letra el texto (espacios incluidos) y al final 'fin'."""
        hilo = threading.Thread(target=self._emitir, args=(texto,), daemon=True, name="kinect-simulado")
        hilo.start()
        if esperar:
            hilo.join()

    def _emitir(self, texto):
        self._cambiar("listo")
        for c in texto.lower():
            if self._parar.is_set():
                return
            t0 = time.monotonic()
            if c == " ":
                evento = EventoSena("espacio")
            elif c.isalpha():
                evento = EventoSena("letra", letra=c, confianza=0.99, modelo="simulado", instante=t0)
            else:
                continue
            self._al_evento(evento)
            self._parar.wait(self.pausa)
        self._al_evento(EventoSena("fin"))
        self._cambiar("sin_persona")

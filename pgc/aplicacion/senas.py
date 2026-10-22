"""Señas → texto: recibe los eventos del reconocedor y arma la frase.

Los callbacks del reconocedor pueden llegar desde cualquier hilo: solo se copian
a una cola y un hilo propio los procesa, así el reconocedor nunca se bloquea
(regla 3 del contrato). Al llegar 'fin' se entrega la frase a `al_frase`
(fase 4–5: decirla en voz alta, mostrarla y, en modo eco, enviarla a la mano).
"""
import queue
import threading

from pgc.puertos.reconocedor import problemas_del_evento

MAX_TEXTO = 60


class ReconocedorNulo:
    """Sin Kinect configurado: cumple el puerto y no emite nada."""
    estado = "apagado"
    detalle = "Kinect: próxima fase"

    def iniciar(self, al_evento, al_cambiar_estado):
        pass

    def detener(self):
        pass


class ServicioSenas:
    def __init__(self, reconocedor, al_frase=None, al_cambiar=None, log=print, moderador=None):
        self.reconocedor = reconocedor
        self.moderador = moderador      # la frase pasa por el mismo filtro que los mensajes
        self.al_frase = al_frase or (lambda texto: None)
        self.al_cambiar = al_cambiar or (lambda: None)
        self.log = log
        self.texto = ""                 # frase en construcción
        self.frases = []                # frases terminadas en esta sesión (las últimas 10)
        self._eventos = queue.Queue(maxsize=500)
        self._iniciado = False

    # ---------------------------------------------------------------- ciclo de vida
    def iniciar(self):
        if self._iniciado:
            return
        self._iniciado = True
        threading.Thread(target=self._procesar, daemon=True, name="senas").start()
        try:
            self.reconocedor.iniciar(self._recibir, self.al_cambiar)
        except Exception as ex:          # un reconocedor roto no tumba el servidor
            self.log(f"[kinect] No se pudo iniciar el reconocedor: {type(ex).__name__}")
            self.reconocedor.estado, self.reconocedor.detalle = "error", "Kinect: no disponible"
            self.al_cambiar()

    def detener(self):
        try:
            self.reconocedor.detener()
        except Exception:
            pass

    # ---------------------------------------------------------------- eventos
    def _recibir(self, evento):
        """Lo llama el reconocedor desde su hilo: no bloquea nunca."""
        try:
            self._eventos.put_nowait(evento)
        except queue.Full:
            pass

    def _procesar(self):
        while True:
            evento = self._eventos.get()
            try:
                self._aplicar(evento)
            except Exception as ex:      # nunca dejar morir el hilo
                self.log(f"[kinect] Error procesando un evento: {type(ex).__name__}")

    def _aplicar(self, evento):
        problemas = problemas_del_evento(evento)
        if problemas:
            self.log(f"[kinect] Evento ignorado: {problemas[0]}")
            return
        if evento.tipo == "letra" and len(self.texto) < MAX_TEXTO:
            self.texto += evento.letra
        elif evento.tipo == "espacio" and self.texto and not self.texto.endswith(" "):
            self.texto += " "
        elif evento.tipo == "borrar":
            self.texto = self.texto[:-1]
        elif evento.tipo == "fin":
            frase, self.texto = self.texto.strip(), ""
            if frase and self.moderador and self.moderador.es_ofensivo(frase):
                self.log("[kinect] Frase descartada por el filtro de palabras")
            elif frase:
                self.frases = (self.frases + [frase])[-10:]
                self.al_frase(frase)
        self.al_cambiar()

    def instantanea(self):
        return {"estado": self.reconocedor.estado, "detalle": self.reconocedor.detalle, "texto": self.texto}

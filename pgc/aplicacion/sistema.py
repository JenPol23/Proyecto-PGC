"""Sistema: reúne la cola, el hilo de la mano y el estado en vivo.

Recibe los componentes ya armados (mano, voz, túnel); quien los crea es pgc/arranque.py.
"""
import queue
import threading
import time

from pgc.aplicacion.cola import ColaDeMensajes
from pgc.aplicacion.deletreo import Deletreador
from pgc.aplicacion.estado import instantanea_sistema
from pgc.aplicacion.participantes import Participantes
from pgc.aplicacion.protocolo import ServicioProtocolo
from pgc.aplicacion.senas import ReconocedorNulo, ServicioSenas
from pgc.dominio.participante import MSG_BLOQUEADO

CLIENTE_KINECT = "kinect"        # el "celular" del modo eco: sus mensajes van a la cola como los demás
AUTOR_KINECT = {"pid": None, "nombre": "Kinect"}


class SintetizadorNulo:
    """Sin voz de salida: cumple el puerto y no dice nada."""
    estado = "desactivado"

    def cargar_en_segundo_plano(self):
        pass

    def decir(self, texto):
        pass


class SinPermisoKinect(Exception):
    """Solo quien tiene el turno (o el presentador) controla el Kinect."""

    def __init__(self):
        super().__init__("Toma el control del Kinect para usar estos botones.")


class ParticipanteBloqueado(Exception):
    """El presentador pausó a este participante durante la sesión."""

    def __init__(self):
        super().__init__(MSG_BLOQUEADO)


class Sistema:
    def __init__(self, cfg, mano, voz, tunel, url_local, publicador, log=print, moderador=None, reconocedor=None,
                 sintetizador=None, reloj=time.monotonic, guardar_experimento=None):
        self.cfg = cfg
        self.log = log
        self.sesion = str(int(time.time()))   # cambia en cada arranque del servidor
        self.mano = mano                      # PuertoMano
        self.voz = voz                        # Transcriptor
        self.tunel = tunel                    # acceso público (cloudflared)
        self.url_local = url_local
        self.publicador = publicador
        publicador.fijar_instantanea(self.instantanea)
        self.moderador = moderador
        self.participantes = Participantes(moderador, al_cambiar=self.notificar, log=log)
        self._cola = ColaDeMensajes(cfg.max_pendientes_cliente, cfg.max_cola, cfg.historial, cfg.max_caracteres,
                                    al_cambiar=self.notificar, log=log, moderador=moderador,
                                    log_textos=cfg.log_textos)
        # Kinect → texto → voz (y, en modo eco, → mano)
        self.senas = ServicioSenas(reconocedor or ReconocedorNulo(), al_frase=self._frase_reconocida,
                                   al_cambiar=self.notificar, log=log, moderador=moderador,
                                   turno_segundos=cfg.kinect_turno_segundos, reloj=reloj)
        self.voz_salida = sintetizador or SintetizadorNulo()
        self.eco = cfg.kinect_eco
        self._por_decir = queue.Queue(maxsize=10)
        # Protocolo de prueba de letras (vista de diagnóstico del PC); guarda en experimentos/
        self.protocolo = ServicioProtocolo(self.senas, guardar=guardar_experimento, log=log)
        self._locutor = None
        self.deletreador = Deletreador(self._cola, mano, self.notificar, log,
                                       cfg.pausa_letra, cfg.pausa_no_disponible,
                                       simular=cfg.mano == "simulada", autodeteccion_cada=cfg.autodeteccion_cada)

    # ----------------------------------------------------------- estado
    cola = property(lambda self: self._cola.pendientes)
    actual = property(lambda self: self._cola.actual)
    historial = property(lambda self: self._cola.historial)
    cv = property(lambda self: self._cola.cv)

    @property
    def loop(self):
        return self.publicador.loop

    @loop.setter
    def loop(self, valor):
        self.publicador.loop = valor

    @property
    def pedir_reconexion(self):
        return self.deletreador.pedir_reconexion

    @pedir_reconexion.setter
    def pedir_reconexion(self, valor):
        self.deletreador.pedir_reconexion = valor

    @property
    def url_publica(self):
        return self.tunel.url or self.url_local

    def instantanea(self):
        kinect = {**self.senas.instantanea(), "eco": self.eco}
        return instantanea_sistema(self.sesion, self.mano, self.voz, self.tunel, self.url_local,
                                   self.url_publica, self.cfg.max_caracteres, self._cola,
                                   self.participantes.bloqueados(), kinect=kinect,
                                   voz_salida=self.voz_salida.estado)

    # ----------------------------------------------------------- operaciones
    def notificar(self):
        """Se puede llamar desde cualquier hilo."""
        self.publicador.notificar()

    def encolar(self, texto, cliente):
        autor = self.participantes.obtener(cliente)
        if autor["bloqueado"]:
            raise ParticipanteBloqueado()
        return self._cola.encolar(texto, cliente, self.mano.letras, autor)

    # ----------------------------------------------------------- participantes
    def registrar_participante(self, cliente, nombre):
        return self.participantes.registrar(cliente, nombre)

    def bloquear(self, pid):
        """Bloquea durante la sesión, cancela sus pendientes y salta el suyo si está en curso.

        Devuelve {"cancelados": n, "saltado": bool}, o None si el pid no existe.
        Desbloquear no recupera nada de esto.
        """
        # Primero se bloquea (ya no puede encolar), luego se limpia la cola y al final se avisa
        cliente = self.participantes.fijar_bloqueo(pid, True, avisar=False)
        if cliente is None:
            return None
        cancelados = self._cola.cancelar_de_cliente(cliente)
        actual = self._cola.actual
        saltado = bool(actual and actual["cliente"] == cliente and self._cola.saltar_actual())
        sin_turno = self.senas.turno.soltar(cliente)     # tampoco sigue controlando el Kinect
        self.log(f"[participantes] {pid}: {cancelados} pendiente(s) cancelado(s)"
                 + ("; se saltó el mensaje en curso" if saltado else "")
                 + ("; perdió el turno del Kinect" if sin_turno else ""))
        self.notificar()
        return {"cancelados": cancelados, "saltado": saltado}

    def desbloquear(self, pid):
        return self.participantes.fijar_bloqueo(pid, False) is not None

    def esta_bloqueado(self, cliente):
        return self.participantes.esta_bloqueado(cliente)

    def cancelar(self, id_msg, cliente):
        return self._cola.cancelar(id_msg, cliente)

    def saltar_actual(self):
        return self._cola.saltar_actual()

    def reconectar_mano(self):
        self.deletreador.reconectar()

    def iniciar_trabajador(self):
        self.deletreador.iniciar()

    # ----------------------------------------------------------- Kinect
    def tomar_turno_kinect(self, cliente):
        autor = self.participantes.obtener(cliente)
        if autor["bloqueado"]:
            raise ParticipanteBloqueado()
        self.senas.turno.tomar(cliente, autor["pid"], autor["nombre"])    # TurnoOcupado si lo tiene otro
        self.notificar()

    def soltar_turno_kinect(self, cliente):
        if self.senas.turno.soltar(cliente):
            self.notificar()

    def liberar_turno_kinect(self):
        if self.senas.turno.liberar():
            self.log("[kinect] El presentador liberó el turno")
            self.notificar()

    def controlar_kinect(self, accion, cliente=None, presentador=False):
        """El presentador siempre; un celular, solo si tiene el turno y no está bloqueado."""
        if not presentador:
            if cliente is None or not self.senas.turno.es_dueno(cliente):
                raise SinPermisoKinect()
            if self.participantes.esta_bloqueado(cliente):
                raise ParticipanteBloqueado()
            self.senas.turno.usar(cliente)
        self.senas.controlar(accion)

    def fijar_eco(self, activo, cliente=None, presentador=False):
        """El presentador siempre; un celular, solo si tiene el turno del Kinect (como los demás controles)."""
        if not presentador:
            if cliente is None or not self.senas.turno.es_dueno(cliente):
                raise SinPermisoKinect()
            if self.participantes.esta_bloqueado(cliente):
                raise ParticipanteBloqueado()
            self.senas.turno.usar(cliente)
        self.eco = bool(activo)
        self.log(f"[kinect] Modo eco {'activado' if self.eco else 'desactivado'}")
        self.notificar()

    def _frase_reconocida(self, frase):
        """'fin' del Kinect: la frase se dice en los parlantes y, en modo eco, la mano la deletrea."""
        self.log(f"[kinect] Frase reconocida ({len(frase)} caracteres)")
        self._decir(frase)
        if self.eco:
            try:
                self._cola.encolar(frase, CLIENTE_KINECT, self.mano.letras, AUTOR_KINECT)
            except ValueError as ex:          # p. ej. ninguna letra que la mano pueda hacer
                self.log(f"[kinect] Eco: la frase no va a la mano ({ex})")

    def _decir(self, frase):
        """La voz va en su propio hilo: decir() bloquea mientras habla y no debe frenar al Kinect."""
        if self._locutor is None:
            self._locutor = threading.Thread(target=self._hablar, daemon=True, name="voz-salida")
            self._locutor.start()
        try:
            self._por_decir.put_nowait(frase)
        except queue.Full:
            self.log("[voz] Demasiadas frases por decir; se omite una")

    def _hablar(self):
        while True:
            frase = self._por_decir.get()
            try:
                self.voz_salida.decir(frase)
            except Exception as ex:           # la voz nunca tumba el servidor
                self.log(f"[voz] No se pudo decir la frase: {type(ex).__name__}")

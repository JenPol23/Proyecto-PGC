"""Sistema: reúne la cola, el hilo de la mano y el estado en vivo.

Recibe los componentes ya armados (mano, voz, túnel); quien los crea es pgc/arranque.py.
"""
import time

from pgc.aplicacion.cola import ColaDeMensajes
from pgc.aplicacion.deletreo import Deletreador
from pgc.aplicacion.estado import instantanea_sistema
from pgc.aplicacion.participantes import Participantes
from pgc.aplicacion.senas import ReconocedorNulo, ServicioSenas
from pgc.dominio.participante import MSG_BLOQUEADO


class ParticipanteBloqueado(Exception):
    """El presentador pausó a este participante durante la sesión."""

    def __init__(self):
        super().__init__(MSG_BLOQUEADO)


class Sistema:
    def __init__(self, cfg, mano, voz, tunel, url_local, publicador, log=print, moderador=None, reconocedor=None):
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
        # Kinect (fase 2+): por ahora solo recibe frases; la pantalla y el eco llegan en las fases 4–5
        self.senas = ServicioSenas(reconocedor or ReconocedorNulo(), al_frase=self._frase_reconocida,
                                   al_cambiar=self.notificar, log=log, moderador=moderador)
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
        return instantanea_sistema(self.sesion, self.mano, self.voz, self.tunel, self.url_local,
                                   self.url_publica, self.cfg.max_caracteres, self._cola,
                                   self.participantes.bloqueados())

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
        self.log(f"[participantes] {pid}: {cancelados} pendiente(s) cancelado(s)"
                 + ("; se saltó el mensaje en curso" if saltado else ""))
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

    def _frase_reconocida(self, frase):
        self.log(f"[kinect] Frase reconocida ({len(frase)} caracteres)")

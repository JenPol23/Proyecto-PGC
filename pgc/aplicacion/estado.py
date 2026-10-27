"""Estado en vivo: instantánea del sistema y aviso a los WebSocket conectados."""
import asyncio


class Publicador:
    """Puente entre los hilos (mano, voz, túnel) y el bucle asyncio de la web.

    Cada suscriptor es una asyncio.Queue de tamaño 1: solo importa el estado más reciente.
    """

    def __init__(self, instantanea=None):
        self._instantanea = instantanea
        self.loop = None
        self.suscriptores = set()

    def fijar_instantanea(self, instantanea):
        """Se fija después porque los adaptadores necesitan `notificar` antes de que exista el Sistema."""
        self._instantanea = instantanea

    def notificar(self):
        """Se puede llamar desde cualquier hilo."""
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self._difundir)

    def _difundir(self):
        estado = self._instantanea()
        for q in list(self.suscriptores):
            if q.full():                      # solo importa el estado más reciente
                q.get_nowait()
            q.put_nowait(estado)

    def suscribir(self):
        q = asyncio.Queue(maxsize=1)
        self.suscriptores.add(q)
        return q

    def desuscribir(self, q):
        self.suscriptores.discard(q)


def instantanea_sistema(sesion, mano, voz, tunel, url_local, url_publica, max_caracteres, cola, bloqueados=(),
                        kinect=None, voz_salida="desactivado"):
    actual, pendientes, historial = cola.instantanea()
    return {
        "tipo": "estado",
        "sesion": sesion,
        "mano": {"modo": mano.modo, "medio": mano.medio, "puerto": mano.puerto,
                 "letras": "".join(sorted(mano.letras or [])) or None},
        "voz": {"estado": voz.estado, "dispositivo": voz.dispositivo},
        "tunel": {"estado": tunel.estado, "url": tunel.url},
        "url_local": url_local,
        "url_publica": url_publica,
        "voz_salida": {"estado": voz_salida},
        # estado, detalle, texto en curso, conectado/camara/activo, frases, turno (pid y nombre) y eco
        "kinect": kinect or {"estado": "apagado"},
        "max_caracteres": max_caracteres,
        "actual": actual,
        "cola": pendientes,
        "historial": historial,
        "bloqueados": list(bloqueados),      # alias (pid) bloqueados: cada celular sabe si es el suyo
    }

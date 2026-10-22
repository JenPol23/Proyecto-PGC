"""Participantes de la sesión: nombre opcional y bloqueo por el presentador (ADR-7).

Todo vive en memoria y desaparece al cerrar el servidor. Cada celular (`cliente`,
su id privado) recibe un alias opaco (`pid`) que sí se puede mostrar en el
WebSocket: con el pid no se pueden cancelar mensajes ajenos.
"""
import secrets
import threading

from pgc.dominio.participante import MSG_NOMBRE_OFENSIVO, normalizar_nombre


class Participantes:
    def __init__(self, moderador=None, al_cambiar=None, log=print):
        self.moderador = moderador
        self.al_cambiar = al_cambiar or (lambda: None)
        self.log = log
        self._lock = threading.Lock()
        self._por_cliente = {}          # cliente → {"pid", "nombre", "bloqueado"}
        self._por_pid = {}              # pid → cliente

    def _nuevo(self, cliente):
        pid = "p" + secrets.token_hex(4)
        while pid in self._por_pid:
            pid = "p" + secrets.token_hex(4)
        datos = {"pid": pid, "nombre": None, "bloqueado": False}
        self._por_cliente[cliente] = datos
        self._por_pid[pid] = cliente
        return datos

    def obtener(self, cliente):
        """Datos del participante (lo crea si es la primera vez que se le ve)."""
        with self._lock:
            return dict(self._por_cliente.get(cliente) or self._nuevo(cliente))

    def registrar(self, cliente, nombre):
        """Fija o cambia el nombre. Un participante bloqueado no puede cambiarlo."""
        nombre = normalizar_nombre(nombre)
        if nombre and self.moderador and self.moderador.es_ofensivo(nombre):
            raise ValueError(MSG_NOMBRE_OFENSIVO)
        with self._lock:
            datos = self._por_cliente.get(cliente) or self._nuevo(cliente)
            cambio = not datos["bloqueado"] and datos["nombre"] != nombre
            if cambio:
                datos["nombre"] = nombre
            resultado = dict(datos)
        if cambio:
            self.al_cambiar()
        return resultado

    def esta_bloqueado(self, cliente):
        with self._lock:
            datos = self._por_cliente.get(cliente)
            return bool(datos and datos["bloqueado"])

    def cliente_de(self, pid):
        with self._lock:
            return self._por_pid.get(pid)

    def fijar_bloqueo(self, pid, bloqueado, avisar=True):
        """Devuelve el cliente afectado, o None si el pid no existe.

        avisar=False: quien llama avisa después (p. ej. tras cancelar los pendientes),
        para que las pantallas nunca vean un estado a medias.
        """
        with self._lock:
            cliente = self._por_pid.get(pid)
            if cliente is None:
                return None
            self._por_cliente[cliente]["bloqueado"] = bloqueado
        self.log(f"[participantes] {pid} {'bloqueado' if bloqueado else 'desbloqueado'}")
        if avisar:
            self.al_cambiar()
        return cliente

    def bloqueados(self):
        with self._lock:
            return sorted(d["pid"] for d in self._por_cliente.values() if d["bloqueado"])

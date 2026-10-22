"""Cola de mensajes: varios jurados envían a la vez y la mano los hace uno por uno."""
import itertools
import threading
import time
from collections import deque

from pgc.dominio.texto import a_secuencia, limpiar


class ColaDeMensajes:
    def __init__(self, max_pendientes_cliente=2, max_cola=30, historial=6, max_caracteres=60,
                 al_cambiar=None, log=print, moderador=None, log_textos=True):
        self.max_pendientes_cliente = max_pendientes_cliente
        self.max_cola = max_cola
        self.max_caracteres = max_caracteres
        self.al_cambiar = al_cambiar or (lambda: None)
        self.log = log
        self.moderador = moderador           # filtro de palabras ofensivas (None = sin filtro)
        self.log_textos = log_textos         # False: el log no guarda lo que escribió el jurado
        self.cv = threading.Condition()      # protege pendientes/actual/historial
        self.pendientes = []                 # mensajes en espera (en orden)
        self.actual = None                   # mensaje que la mano está deletreando
        self.historial = deque(maxlen=historial)
        self._ids = itertools.count(1)
        self._saltar_id = None               # id del mensaje en curso que se pidió saltar

    # ------------------------------------------------------------ jurados
    def describir(self, msg):
        """Cómo aparece un mensaje en el log: sin su texto, salvo que se pida."""
        if self.log_textos:
            return f"#{msg['id']} '{msg['texto']}'"
        return f"#{msg['id']} ({sum(p['tipo'] != 'espacio' for p in msg['pasos'])} letras)"

    def encolar(self, texto, cliente, letras_mano=None, autor=None):
        """autor: {"pid", "nombre"} del participante (se muestra en el proyector)."""
        original = texto
        texto = limpiar(texto, self.max_caracteres)
        pasos = a_secuencia(texto, letras_mano, self.max_caracteres)
        if not any(p["tipo"] != "espacio" for p in pasos):
            raise ValueError("Escribe al menos una letra.")
        if self.moderador and (self.moderador.es_ofensivo(original) or self.moderador.es_ofensivo(texto)):
            self.log("[cola] Mensaje rechazado por el filtro de palabras")
            raise ValueError("Ese mensaje no se puede mostrar. Intenta con otras palabras.")
        if not any(p["tipo"] in ("ok", "aprox") for p in pasos):
            raise ValueError("La mano todavía no puede hacer esas letras")
        with self.cv:
            propios = [m for m in self.pendientes if m["cliente"] == cliente]
            if self.actual and self.actual["cliente"] == cliente:
                propios.append(self.actual)
            if len(propios) >= self.max_pendientes_cliente:
                raise ValueError(f"Ya tienes {self.max_pendientes_cliente} mensajes en espera. "
                                 "Espera a que la mano los haga.")
            if len(self.pendientes) >= self.max_cola:
                raise ValueError("La cola está llena, intenta en un momento.")
            autor = autor or {}
            msg = {"id": next(self._ids), "texto": texto, "cliente": cliente,
                   "pid": autor.get("pid"), "nombre": autor.get("nombre"),
                   "pasos": pasos, "i": -1, "creado": time.time()}
            self.pendientes.append(msg)
            self.cv.notify_all()
        self.log(f"[cola] +{self.describir(msg)} (en cola: {len(self.pendientes)})")
        self.al_cambiar()
        return msg

    def cancelar(self, id_msg, cliente):
        """Solo el celular que lo envió puede cancelarlo, y solo mientras espera."""
        with self.cv:
            for m in self.pendientes:
                if m["id"] == id_msg and m["cliente"] == cliente:
                    self.pendientes.remove(m)
                    break
            else:
                return False
        self.log(f"[cola] -#{id_msg} cancelado")
        self.al_cambiar()
        return True

    def cancelar_de_cliente(self, cliente):
        """Quita todos los pendientes de un celular (el que está en curso sigue). Devuelve cuántos."""
        with self.cv:
            antes = len(self.pendientes)
            self.pendientes[:] = [m for m in self.pendientes if m["cliente"] != cliente]
            quitados = antes - len(self.pendientes)
        if quitados:
            self.al_cambiar()
        return quitados

    # ------------------------------------------------------------ presentador
    def saltar_actual(self):
        """Corta el mensaje en curso (la letra que se está formando termina primero)."""
        with self.cv:
            if not self.actual:
                return False
            self._saltar_id = self.actual["id"]
        self.log(f"[mano] Saltar #{self._saltar_id} pedido desde el PC")
        return True

    def debe_saltar(self, msg):
        return self._saltar_id == msg["id"]

    # ------------------------------------------------------------ hilo de la mano
    def tomar_siguiente(self, espera):
        """Pasa el primer pendiente a 'actual'; si no hay, espera hasta `espera` s y devuelve None."""
        with self.cv:
            if self.pendientes:
                self.actual = self.pendientes.pop(0)
                return self.actual
            self.cv.wait(timeout=espera)
            return None

    def terminar(self, msg):
        with self.cv:
            self.actual = None
            self.historial.appendleft(msg)

    def despertar(self):
        with self.cv:
            self.cv.notify_all()

    # ------------------------------------------------------------ estado
    def instantanea(self):
        """(actual, cola, historial) listos para enviar; nunca incluye el id del cliente."""
        with self.cv:
            actual = None
            if self.actual:
                m = self.actual
                actual = {"id": m["id"], "texto": m["texto"], "i": m["i"], "saltado": m.get("saltado", False),
                          "pid": m.get("pid"), "nombre": m.get("nombre"),
                          "pasos": [{"c": p["c"], "tipo": p["tipo"], "r": p.get("r")} for p in m["pasos"]]}
            cola = [{"id": m["id"], "texto": m["texto"], "pid": m.get("pid"), "nombre": m.get("nombre")}
                    for m in self.pendientes]
            historial = [{"id": m["id"], "texto": m["texto"], "saltado": m.get("saltado", False)}
                         for m in self.historial]
        return actual, cola, historial

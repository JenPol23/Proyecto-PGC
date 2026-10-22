"""Hilo de la mano: saca mensajes de la cola y los deletrea esperando cada confirmación."""
import threading
import time

from pgc.dominio.ordenes import forma_despues, ordenes_para
from pgc.dominio.texto import a_secuencia


class Deletreador:
    def __init__(self, cola, mano, al_cambiar, log=print, pausa_letra=0.5, pausa_no_disponible=0.9,
                 simular=False, autodeteccion_cada=3.0):
        self.cola = cola
        self.mano = mano                      # PuertoMano
        self.al_cambiar = al_cambiar
        self.log = log
        self.pausa_letra = pausa_letra
        self.pausa_no_disponible = pausa_no_disponible
        self.simular = simular
        self.autodeteccion_cada = autodeteccion_cada
        self.pedir_reconexion = False

    def iniciar(self):
        threading.Thread(target=self._trabajar, daemon=True, name="mano").start()

    def reconectar(self):
        """Pide al hilo que vuelva a buscar la mano (lo hace entre mensajes)."""
        self.pedir_reconexion = True
        self.cola.despertar()

    # ------------------------------------------------------------ conexión
    def _conectar_mano(self):
        if self.simular:
            self.log("[mano] Modo simulado (--simular)")
        self.mano.conectar()
        self.al_cambiar()

    def _autodetectar(self):
        """Entre mensajes: latido, respaldo y búsqueda de la mano (si se conecta con el servidor
        ya corriendo, la toma sola)."""
        if self.simular:
            return
        if self.mano.revisar():
            self.al_cambiar()

    # ------------------------------------------------------------ bucle
    def _trabajar(self):
        self._conectar_mano()
        while True:
            if self.pedir_reconexion:
                self.pedir_reconexion = False
                if self.mano.conectada:
                    self.mano.cerrar()
                self._conectar_mano()
            msg = self.cola.tomar_siguiente(espera=self.autodeteccion_cada)
            if msg is None:
                self._autodetectar()
                continue
            try:
                self._deletrear(msg)
            except Exception as ex:          # nunca dejar morir el hilo
                self.log(f"[mano] Error deletreando #{msg['id']}: {ex}")
            self.cola.terminar(msg)
            self.al_cambiar()

    def _deletrear(self, msg):
        # Se recalcula por si la mano se conectó después y reportó otras letras
        msg["pasos"] = a_secuencia(msg["texto"], self.mano.letras, self.cola.max_caracteres)
        self.log(f"[mano] Deletreando {self.cola.describir(msg)} ({self.mano.modo})")
        forma = None                                  # letra que la mano tiene formada (None = abierta)
        for i, paso in enumerate(msg["pasos"]):
            if self.cola.debe_saltar(msg):
                break
            msg["i"] = i
            self.al_cambiar()
            ordenes = ordenes_para(paso, forma)       # regla de espacios y letras repetidas
            if ordenes:
                for orden in ordenes[:-1]:
                    self.mano.hacer(orden)
                ok = self.mano.hacer(ordenes[-1])
                if ok and paso["l"]:
                    time.sleep(self.pausa_letra)
            else:
                time.sleep(self.pausa_no_disponible)
                ok = None
            forma = forma_despues(paso, forma, ok)
            paso["r"] = "nd" if ok is None else ("ok" if ok else "error")
        if self.cola.debe_saltar(msg):
            msg["saltado"] = True
            self.log(f"[mano] #{msg['id']} saltado")
        else:
            msg["i"] = len(msg["pasos"])
        self.al_cambiar()
        self.mano.reset()

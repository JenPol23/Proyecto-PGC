"""Turno del Kinect: un solo jurado lo controla a la vez desde su celular.

Quien toma el turno puede iniciar, detener, poner espacio, borrar y terminar.
El turno se libera al soltarlo, al bloquear a esa persona, cuando el presentador
lo libera o, solo, tras `segundos` sin usar los controles. El presentador (PC con
token) controla siempre, tenga o no alguien el turno.
"""
import threading
import time


class TurnoOcupado(Exception):
    """Otro celular tiene el turno."""

    def __init__(self, nombre):
        quien = nombre or "otra persona"
        super().__init__(f"El Kinect lo está usando {quien}. Espera tu turno.")


class TurnoKinect:
    def __init__(self, segundos=120.0, reloj=time.monotonic):
        self.segundos = segundos
        self._reloj = reloj
        self._lock = threading.Lock()
        self._dueno = None          # {"cliente", "pid", "nombre", "ultimo"}

    def _vencido(self):
        return self._dueno and self._reloj() - self._dueno["ultimo"] >= self.segundos

    def tomar(self, cliente, pid, nombre):
        """Da el turno si está libre (o vencido). Lanza TurnoOcupado si lo tiene otro."""
        with self._lock:
            if self._vencido():
                self._dueno = None
            if self._dueno and self._dueno["cliente"] != cliente:
                raise TurnoOcupado(self._dueno["nombre"])
            self._dueno = {"cliente": cliente, "pid": pid, "nombre": nombre, "ultimo": self._reloj()}

    def es_dueno(self, cliente):
        with self._lock:
            return bool(self._dueno and not self._vencido() and self._dueno["cliente"] == cliente)

    def usar(self, cliente):
        """Cuenta como actividad (reinicia la espera para liberarlo)."""
        with self._lock:
            if self._dueno and self._dueno["cliente"] == cliente:
                self._dueno["ultimo"] = self._reloj()

    def soltar(self, cliente):
        with self._lock:
            if self._dueno and self._dueno["cliente"] == cliente:
                self._dueno = None
                return True
            return False

    def liberar(self):
        """El presentador libera el turno, sea de quien sea."""
        with self._lock:
            libre = self._dueno is None
            self._dueno = None
            return not libre

    def revisar(self):
        """Libera el turno vencido. Devuelve True si cambió (para avisar a las pantallas)."""
        with self._lock:
            if self._vencido():
                self._dueno = None
                return True
            return False

    def instantanea(self):
        """Lo que ven las pantallas: alias y nombre, nunca el id privado del celular."""
        with self._lock:
            if not self._dueno or self._vencido():
                return None
            restante = self.segundos - (self._reloj() - self._dueno["ultimo"])
            return {"pid": self._dueno["pid"], "nombre": self._dueno["nombre"], "libera_en": round(max(0, restante))}

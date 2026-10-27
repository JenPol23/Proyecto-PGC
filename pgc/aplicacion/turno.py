"""Turno del Kinect: un solo jurado lo controla a la vez desde su celular.

Quien toma el turno puede iniciar, detener, poner espacio, borrar y terminar.
El turno se libera al soltarlo, al bloquear a esa persona, cuando el presentador
lo libera o, solo, tras `segundos` sin usar los controles. El presentador (PC con
token) controla siempre, tenga o no alguien el turno.

Con `con_codigo`, para tomar el turno hay que escribir el código de 6 dígitos que
muestra el proyector (como el «Código del PC» del diseño de Camila): así solo
controla quien está en la sala. Cambia en cada arranque y el presentador puede
regenerarlo (eso también quita el turno a quien lo tenga).
"""
import secrets
import threading
import time


class TurnoOcupado(Exception):
    """Otro celular tiene el turno."""

    def __init__(self, nombre):
        quien = nombre or "otra persona"
        super().__init__(f"El Kinect lo está usando {quien}. Espera tu turno.")


class CodigoIncorrecto(Exception):
    """El código escrito no es el que muestra el proyector."""

    def __init__(self):
        super().__init__("Código incorrecto. Escribe el código de 6 dígitos que muestra el proyector.")


def nuevo_codigo():
    return f"{secrets.randbelow(10**6):06d}"


class TurnoKinect:
    def __init__(self, segundos=120.0, reloj=time.monotonic, con_codigo=False):
        self.segundos = segundos
        self.con_codigo = con_codigo
        self._reloj = reloj
        self._lock = threading.Lock()
        self._dueno = None          # {"cliente", "pid", "nombre", "ultimo"}
        self._codigo = nuevo_codigo() if con_codigo else None
        self.version_codigo = 0     # sube al regenerarlo: el proyector sabe que debe pedirlo otra vez

    @property
    def codigo(self):
        """Solo para el proyector (ruta con token): nunca va en el estado que reciben los celulares."""
        return self._codigo

    def regenerar_codigo(self):
        """Código nuevo; quien tenía el turno lo pierde (tendrá que escribir el nuevo)."""
        with self._lock:
            if not self.con_codigo:
                return None
            self._codigo = nuevo_codigo()
            self.version_codigo += 1
            self._dueno = None
            return self._codigo

    def _vencido(self):
        return self._dueno and self._reloj() - self._dueno["ultimo"] >= self.segundos

    def tomar(self, cliente, pid, nombre, codigo=None):
        """Da el turno si está libre (o vencido) y el código es el del proyector.

        Lanza TurnoOcupado si lo tiene otro y CodigoIncorrecto si el código no coincide.
        """
        with self._lock:
            if self._vencido():
                self._dueno = None
            if self._dueno and self._dueno["cliente"] != cliente:
                raise TurnoOcupado(self._dueno["nombre"])
            escrito = "".join(c for c in str(codigo or "") if c.isdigit())
            if self.con_codigo and not secrets.compare_digest(escrito, self._codigo):
                raise CodigoIncorrecto()
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

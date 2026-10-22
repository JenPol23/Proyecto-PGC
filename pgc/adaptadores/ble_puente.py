"""Puente Bluetooth: bleak en un PROCESO APARTE, manejado desde ManoBLE.

Por qué: el Bluetooth de Windows (WinRT, que usa bleak) y faster-whisper (ctranslate2
en la GPU) no pueden convivir en el mismo proceso: con solo importar WinRT antes de cargar
Whisper, Python se cae con "access violation" (probado el 22/10/2026). Aquí cada uno vive
en su proceso y una librería nunca puede tumbar a la otra.

Lado del servidor: `BleakRemoto` se usa igual que bleak (Escaner + Cliente), así ManoBLE
no cambia. Lado del hijo: `python -m pgc.adaptadores.ble_puente` atiende pedidos en JSON,
una línea por pedido, por stdin; responde y avisa (datos, desconexión) por stdout.
Si el servidor se cierra, el hijo ve stdin cerrado y termina (y el Job Object lo cierra igual).
"""
import asyncio
import importlib
import itertools
import json
import subprocess
import sys
import threading
import types
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent.parent
TIEMPO_ARRANQUE = 20.0             # s para que el hijo importe bleak y conteste


# =============================================================================
#  Lado del servidor
# =============================================================================
class BleakRemoto:
    """Escaner y Cliente con la misma forma que bleak; el trabajo lo hace el proceso hijo."""

    def __init__(self, comando=None, entorno=None):
        self.comando = comando or [sys.executable, "-m", "pgc.adaptadores.ble_puente"]
        self.entorno = entorno
        self._proc = None
        self._job = None
        self._ids = itertools.count(1)
        self._pendientes = {}              # id → (bucle, futuro)
        self._lock = threading.Lock()
        self._cliente = None               # el Cliente activo recibe datos y desconexión
        remoto = self

        class Escaner:
            @staticmethod
            async def find_device_by_name(nombre, timeout=5.0):
                res = await remoto._pedir({"op": "buscar", "nombre": nombre, "timeout": timeout}, timeout + 10)
                return types.SimpleNamespace(**res) if res else None

        class Cliente:
            def __init__(self, dispositivo, disconnected_callback=None):
                self.dispositivo = dispositivo
                self.al_desconectar = disconnected_callback
                self.al_notificar = None
                self.is_connected = False

            async def connect(self, timeout=10.0):
                remoto._cliente = self
                await remoto._pedir({"op": "conectar", "address": self.dispositivo.address, "timeout": timeout},
                                    timeout + 10)
                self.is_connected = True

            async def start_notify(self, caracteristica, callback):
                self.al_notificar = callback
                await remoto._pedir({"op": "notificar", "uuid": caracteristica}, 10)

            async def write_gatt_char(self, caracteristica, datos, response=False):
                await remoto._pedir({"op": "escribir", "uuid": caracteristica, "hex": bytes(datos).hex(),
                                     "response": response}, 10)

            async def disconnect(self):
                self.is_connected = False
                await remoto._pedir({"op": "desconectar"}, 10)

        self.Escaner, self.Cliente = Escaner, Cliente

    # ------------------------------------------------------------ proceso hijo
    def _arrancar(self):
        if self._proc is not None and self._proc.poll() is None:
            return
        self._proc = subprocess.Popen(
            self.comando, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            cwd=RAIZ, env=self.entorno,
            creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0))     # Ctrl+C solo al servidor
        try:
            from pgc.adaptadores.acceso import atar_al_proceso_actual
            self._job = atar_al_proceso_actual(self._proc)                        # sin hijos huérfanos
        except Exception:
            pass
        threading.Thread(target=self._leer, args=(self._proc,), daemon=True, name="ble-puente").start()

    def _leer(self, proc):
        for linea in proc.stdout:
            try:
                msg = json.loads(linea)
            except ValueError:
                continue
            if "id" in msg:
                with self._lock:
                    bucle, futuro = self._pendientes.pop(msg["id"], (None, None))
                if futuro is not None:
                    bucle.call_soon_threadsafe(_resolver, futuro, msg)
            elif msg.get("ev") == "datos" and self._cliente and self._cliente.al_notificar:
                self._cliente.al_notificar(None, bytearray.fromhex(msg["hex"]))
            elif msg.get("ev") == "desconectado":
                self._avisar_desconexion()
        # el hijo terminó: falla lo pendiente y se avisa la desconexión
        with self._lock:
            pendientes, self._pendientes = self._pendientes, {}
        for bucle, futuro in pendientes.values():
            bucle.call_soon_threadsafe(_resolver, futuro, {"ok": False, "tipo": "ConnectionError",
                                                           "motivo": "el puente Bluetooth se cerró"})
        self._avisar_desconexion()

    def _avisar_desconexion(self):
        cliente = self._cliente
        if cliente is not None and cliente.is_connected:
            cliente.is_connected = False
            if cliente.al_desconectar:
                cliente.al_desconectar(cliente)

    async def _pedir(self, pedido, timeout):
        bucle = asyncio.get_running_loop()
        futuro = bucle.create_future()
        with self._lock:
            self._arrancar()
            pedido["id"] = next(self._ids)
            self._pendientes[pedido["id"]] = (bucle, futuro)
            try:
                self._proc.stdin.write((json.dumps(pedido) + "\n").encode())
                self._proc.stdin.flush()
            except OSError:
                self._pendientes.pop(pedido["id"], None)
                raise ConnectionError("el puente Bluetooth no responde") from None
        try:
            return await asyncio.wait_for(futuro, TIEMPO_ARRANQUE + timeout)
        finally:
            with self._lock:
                self._pendientes.pop(pedido["id"], None)

    def cerrar(self):
        if self._proc is not None and self._proc.poll() is None:
            try:
                self._proc.stdin.close()
                self._proc.wait(3)
            except Exception:
                self._proc.kill()


def _resolver(futuro, msg):
    if futuro.done():
        return
    if msg.get("ok"):
        futuro.set_result(msg.get("res"))
    else:
        # misma clase (por nombre) que en el hijo, para que ManoBLE dé el mensaje adecuado
        futuro.set_exception(type(msg.get("tipo") or "Error", (RuntimeError,), {})(msg.get("motivo", "")))


# =============================================================================
#  Lado del proceso hijo
# =============================================================================
def _bleak_de(ruta):
    """'paquete.modulo:funcion' → objeto con Escaner y Cliente (solo para pruebas)."""
    if not ruta:
        import bleak
        return types.SimpleNamespace(Escaner=bleak.BleakScanner, Cliente=bleak.BleakClient)
    modulo, funcion = ruta.split(":")
    return getattr(importlib.import_module(modulo), funcion)()


async def _atender(bleak):
    bucle = asyncio.get_running_loop()
    salida = sys.stdout.buffer
    cola = asyncio.Queue()
    estado = {"cliente": None, "dispositivos": {}}
    candado = threading.Lock()                 # los avisos de bleak pueden llegar desde otro hilo

    def enviar(msg):
        with candado:
            salida.write((json.dumps(msg) + "\n").encode())
            salida.flush()

    def leer_stdin():
        for linea in sys.stdin.buffer:
            bucle.call_soon_threadsafe(cola.put_nowait, linea)
        bucle.call_soon_threadsafe(cola.put_nowait, None)          # el servidor se cerró

    threading.Thread(target=leer_stdin, daemon=True).start()

    def al_desconectar(_cliente):
        enviar({"ev": "desconectado"})

    def al_notificar(_caracteristica, datos):
        enviar({"ev": "datos", "hex": bytes(datos).hex()})

    async def hacer(p):
        op = p["op"]
        if op == "buscar":
            d = await bleak.Escaner.find_device_by_name(p["nombre"], timeout=p["timeout"])
            if d is None:
                return None
            estado["dispositivos"][d.address] = d
            return {"name": d.name, "address": d.address}
        if op == "conectar":
            if estado["cliente"] is not None:
                try:
                    await estado["cliente"].disconnect()
                except Exception:
                    pass
            dispositivo = estado["dispositivos"].get(p["address"], p["address"])
            cliente = bleak.Cliente(dispositivo, disconnected_callback=al_desconectar)
            await cliente.connect(timeout=p["timeout"])
            estado["cliente"] = cliente
            return None
        cliente = estado["cliente"]
        if op == "desconectar":
            estado["cliente"] = None
            if cliente is not None:
                await cliente.disconnect()
            return None
        if cliente is None:
            raise ConnectionError("Not connected")
        if op == "notificar":
            await cliente.start_notify(p["uuid"], al_notificar)
        elif op == "escribir":
            await cliente.write_gatt_char(p["uuid"], bytes.fromhex(p["hex"]), response=p["response"])
        return None

    async def responder(p):
        try:
            enviar({"id": p["id"], "ok": True, "res": await hacer(p)})
        except Exception as ex:
            motivo = ex.args[0] if ex.args and isinstance(ex.args[0], str) else str(ex)
            enviar({"id": p["id"], "ok": False, "tipo": type(ex).__name__, "motivo": motivo})

    while True:
        linea = await cola.get()
        if linea is None:
            break
        try:
            pedido = json.loads(linea)
        except ValueError:
            continue
        await responder(pedido)            # uno a la vez, en orden (como espera ManoBLE)
    if estado["cliente"] is not None:
        try:
            await estado["cliente"].disconnect()
        except Exception:
            pass


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ruta = argv[argv.index("--bleak") + 1] if "--bleak" in argv else None
    asyncio.run(_atender(_bleak_de(ruta)))


if __name__ == "__main__":
    main()

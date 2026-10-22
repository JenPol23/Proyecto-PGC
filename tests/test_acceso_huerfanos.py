"""cloudflared no queda huérfano si Python se cierra a la fuerza (Job Object de Windows)."""
import os
import subprocess
import sys
import time

import pytest

from conftest import RAIZ

PADRE = (
    "import subprocess, sys, time;"
    f"sys.path.insert(0, {str(RAIZ)!r});"
    "from pgc.adaptadores.acceso import atar_al_proceso_actual;"
    "h = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']);"
    "print(h.pid, atar_al_proceso_actual(h) is not None, flush=True);"
    "time.sleep(60)"
)


def vivo(pid):
    salida = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
    return str(pid) in salida


@pytest.mark.skipif(os.name != "nt", reason="solo aplica en Windows")
def test_el_hijo_muere_con_el_padre():
    padre = subprocess.Popen([sys.executable, "-c", PADRE], stdout=subprocess.PIPE, text=True)
    try:
        pid_hijo, atado = padre.stdout.readline().split()
        assert atado == "True"
        assert vivo(pid_hijo)
        padre.kill()                                   # como cerrar la ventana o taskkill /F
        padre.wait(5)
        limite = time.time() + 5
        while vivo(pid_hijo) and time.time() < limite:
            time.sleep(0.2)
        assert not vivo(pid_hijo), "el proceso hijo quedó huérfano"
    finally:
        if padre.poll() is None:
            padre.kill()

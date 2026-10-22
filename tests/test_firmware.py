"""El main.py de la placa = el código ORIGINAL del autor + solo el bloque agregado (Bluetooth).

Se ejecutan los dos programas TAL CUAL en el PC (machine/time/uselect/bluetooth falsos)
y se comparan los pulsos, las pausas y los textos que imprimen o envían.
"""
import ast
import importlib.util
import time

import pytest

from arnes_firmware import (ARRANQUE, FIRMWARE, MAIN, MARCA, ORIGINAL, CentralFalsa, PlacaEnHilo, correr)

LETRAS = "abcdefiklmnopqrtuvwxy"
TOKEN = "token-de-prueba-0123456789"


def armar_main():
    ruta = FIRMWARE.parent.parent / "scripts" / "armar_main_placa.py"
    spec = importlib.util.spec_from_file_location("armar_main_placa", ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo.armar()


# =============================================================================
#  Texto: todo lo de arriba del BUCLE PRINCIPAL es idéntico, línea por línea
# =============================================================================
def hasta_el_bucle(ruta):
    lineas = ruta.read_text(encoding="utf-8").splitlines()
    return lineas[:lineas.index(MARCA) + 1]


def test_arriba_del_bucle_principal_identico_linea_por_linea():
    original, placa = hasta_el_bucle(ORIGINAL), hasta_el_bucle(MAIN)
    assert len(placa) == len(original) == 225
    for numero, (a, b) in enumerate(zip(original, placa), start=1):
        assert a == b, f"línea {numero} distinta"


def test_main_es_el_original_mas_el_bloque_agregado():
    texto = MAIN.read_text(encoding="utf-8")
    assert texto == armar_main()                         # nada más se tocó
    bloque = texto[texto.index(MARCA) + len(MARCA):]
    assert ">>> INICIO DE LO AGREGADO" in bloque and "<<< FIN DE LO AGREGADO" in bloque
    assert "import bluetooth" in bloque
    assert "network" not in texto and "socket" not in texto            # sin WiFi
    assert "letras.json" not in texto


# =============================================================================
#  Por USB: mismos pulsos, pausas y textos que el original
# =============================================================================
@pytest.mark.parametrize("orden", list(LETRAS) + ["reset", "1", "g", "ñ", "hola", "calle"])
def test_por_usb_igual_que_el_original(orden):
    reg_o, txt_o = correr(ORIGINAL, [orden])
    reg_p, txt_p = correr(MAIN, [orden])
    assert reg_p == reg_o
    assert txt_p == txt_o


def test_secuencia_larga_por_usb():
    ordenes = list("hola") + ["reset", "jurado", "1"] + list(LETRAS) + ["xyz", "g", "", "   ", "a"]
    reg_o, txt_o = correr(ORIGINAL, ordenes)
    reg_p, txt_p = correr(MAIN, ordenes)
    assert reg_p == reg_o and txt_p == txt_o
    assert len(reg_p) > 400
    assert txt_p[0] == "Iniciando motores..." and txt_p[-1] == "Programa terminado."


def test_textos_de_respuesta():
    _, txt = correr(MAIN, ["a", "reset", "1", "g", "ab"])
    assert txt == ["Iniciando motores...", "Mano lista.", "Listo. Esperando comandos...",
                   "gesto_a_ok", "reset_ok", "reset_ok", "comando_no_reconocido",
                   "gesto_a_ok", "letra_actual:a", "gesto_b_ok", "letra_actual:b", "deletreo_completo",
                   "Programa terminado."]


# =============================================================================
#  Por Bluetooth: mismas órdenes, mismos textos y mismos movimientos
# =============================================================================
@pytest.fixture
def placa():
    p = PlacaEnHilo(TOKEN)
    assert p.error is None, p.error
    yield p
    p.detener()


def pc(placa, token=TOKEN):
    c = CentralFalsa(placa)
    if token is not None:
        c.enviar(f"auth {token}")
    return c


def test_se_anuncia_como_mano_lsc(placa):
    assert placa.radio.nombre == "Mano-LSC" and placa.radio.anunciando
    assert b"Mano-LSC" in placa.radio.anuncio
    assert "# Bluetooth listo: se anuncia como Mano-LSC" in placa.salida.lineas()


def test_ble_mismas_respuestas_que_el_original(placa):
    c = pc(placa)
    assert c.lineas(1) == ["ok:auth"]
    ordenes = ["a", "reset", "g", "hola", "1"]
    respuestas = []
    for o in ordenes:
        c.enviar(o)
        respuestas += c.lineas({"hola": 8}.get(o, 1))               # "hola" responde como deletrear()
    _, txt_o = correr(ORIGINAL, ordenes)
    assert respuestas == txt_o[3:-1]                                 # sin arranque ni "Programa terminado."


def test_ble_mueve_igual_que_el_original_por_usb(placa):
    c = pc(placa)
    c.lineas(1)
    ordenes = list("calle") + ["reset"] + list(LETRAS) + ["reset"]   # termina abierta, como el original al salir
    for o in ordenes:
        c.enviar(o)
        c.lineas(1)
    reg_o, _ = correr(ORIGINAL, ordenes)
    assert list(placa.registro) == list(reg_o)
    assert len(reg_o) > 300


def test_ble_token_incorrecto(placa):
    c = pc(placa, token="otro-token-cualquiera-xx")
    assert c.lineas(1) == ["error:auth"]
    assert c.desconectado.wait(2)                                    # la placa lo desconectó
    assert len(placa.registro) == ARRANQUE                           # no se movió nada
    time.sleep(0.05)
    assert placa.radio.anunciando                                    # y se anuncia de nuevo


def test_ble_sin_token_no_ejecuta(placa):
    c = pc(placa, token=None)
    c.enviar("a")
    assert c.lineas(1) == ["error:auth"]
    assert len(placa.registro) == ARRANQUE


def test_ble_sin_presentarse_a_tiempo(placa):
    c = pc(placa, token=None)
    assert c.desconectado.wait(5)                                    # a los 3 s
    assert placa.radio.anunciando


def test_ble_un_solo_pc_a_la_vez(placa):
    c = pc(placa)
    c.lineas(1)
    assert not placa.radio.anunciando                                # nadie más puede conectarse
    with pytest.raises(OSError):
        CentralFalsa(placa)
    c.enviar("a")
    assert c.lineas(1) == ["gesto_a_ok"]


def test_ble_desconexion_y_reconexion(placa):
    c = pc(placa)
    c.lineas(1)
    placa.radio.desconectar_central()
    time.sleep(0.05)
    assert placa.radio.anunciando
    c2 = pc(placa)                                                   # el PC vuelve a conectarse
    assert c2.lineas(1) == ["ok:auth"]
    c2.enviar("b")
    assert c2.lineas(1) == ["gesto_b_ok"]
    assert any("desconectado" in l for l in placa.salida.lineas())


def test_ble_paquetes_de_20_bytes(placa):
    c = pc(placa)
    c.lineas(1)
    c.enviar("hola")                                                 # respuestas largas: se parten en 20 bytes
    assert c.lineas(8)[-1] == "deletreo_completo"


def test_usb_sigue_funcionando_con_bluetooth(placa):
    placa.stdin.escribir("a\n")
    limite = time.time() + 5
    while time.time() < limite and "gesto_a_ok" not in placa.salida.lineas():
        time.sleep(0.01)
    assert "gesto_a_ok" in placa.salida.lineas()


def test_sin_config_ble_funciona_solo_por_usb():
    _, txt = correr(MAIN, ["a"])                                     # config_ble = None
    assert not any("Bluetooth" in l for l in txt)


def test_token_corto_desactiva_el_bluetooth():
    from arnes_firmware import config_ble_falso
    _, txt = correr(MAIN, ["a"], config_ble=config_ble_falso("corto"))
    assert any("Bluetooth desactivado" in l for l in txt) and "gesto_a_ok" in txt


# =============================================================================
#  prueba_dedos.py, MicroPython y secretos
# =============================================================================
def dedos_config_de(ruta):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in arbol.body:
        if isinstance(nodo, ast.Assign) and getattr(nodo.targets[0], "id", None) == "dedos_config":
            return ast.literal_eval(nodo.value)
    raise AssertionError("sin dedos_config")


def test_prueba_dedos_usa_la_misma_calibracion():
    assert dedos_config_de(FIRMWARE / "prueba_dedos.py") == dedos_config_de(MAIN) == dedos_config_de(ORIGINAL)


def test_prueba_dedos_mueve_un_dedo_a_la_vez():
    reg, txt = correr(FIRMWARE / "prueba_dedos.py", [])
    pulsos = [e for e in reg if e[0] == "pulso"][6:]
    assert len(pulsos) == 3 * 6 * 3                                  # 3 vueltas × 6 dedos × 3 posiciones
    for k in range(0, len(pulsos), 3):
        assert len({p[1] for p in pulsos[k:k + 3]}) == 1
    assert txt[-1] == "Prueba de dedos terminada: mano abierta."


def test_prueba_usa_la_misma_calibracion():
    assert dedos_config_de(FIRMWARE / "prueba.py") == dedos_config_de(ORIGINAL)


def test_prueba_cierra_y_abre_dedo_por_dedo_y_termina_cerrada():
    cfg = dedos_config_de(ORIGINAL)
    pines = {c["pin"]: n for n, c in cfg.items()}
    reg, txt = correr(FIRMWARE / "prueba.py", [])
    pulsos = [(pines[e[1]], e[2] // 1000) for e in reg if e[0] == "pulso"]      # duty_ns → µs
    abierto = {n: c["abierto"] for n, c in cfg.items()}
    cerrado = {n: c["cerrado"] for n, c in cfg.items()}
    abrir = ["pulgar2", "pulgar", "indice", "medio", "anular", "menique"]        # dedo gordo de primeras
    esperado = [(n, abierto[n]) for n in abrir]                                  # arranque: todos arriba
    for n in ["indice", "medio", "anular", "menique"]:                           # uno por uno, en ese orden
        esperado += [(n, cerrado[n]), (n, abierto[n])]
    esperado += [("pulgar", cerrado["pulgar"]), ("pulgar2", cerrado["pulgar2"]),  # gira y se recoge
                 ("pulgar2", abierto["pulgar2"]), ("pulgar", abierto["pulgar"])]  # se reinicia, como en l()
    cerrar = ["pulgar", "pulgar2", "indice", "medio", "anular", "menique"]       # dedo gordo de primeras
    esperado += [(n, cerrado[n]) for n in cerrar]
    abrir_final = ["indice", "medio", "anular", "menique", "pulgar2", "pulgar"]  # dedo gordo de últimas
    esperado += [(n, abierto[n]) for n in abrir_final]
    assert pulsos == esperado                                                    # termina abierta
    assert txt[-1] == "Prueba terminada: mano abierta."


PERMITIDOS = {"machine", "time", "sys", "uselect", "select", "bluetooth", "micropython", "config_ble"}


@pytest.mark.parametrize("archivo", ["main.py", "prueba_dedos.py", "prueba.py", "config_ble.example.py"])
def test_solo_modulos_de_micropython(archivo):
    arbol = ast.parse((FIRMWARE / archivo).read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres = [a.name for a in nodo.names]
        elif isinstance(nodo, ast.ImportFrom):
            nombres = [nodo.module]
        else:
            continue
        for n in nombres:
            assert n.split(".")[0] in PERMITIDOS, f"{archivo} importa {n}"


def test_en_la_placa_solo_va_main_py():
    sobrantes = {"mano_movimientos.py", "mano_protocolo.py", "mano_red.py", "mano_vigilante.py",
                 "mano_servos.py", "letras.json", "config_wifi.example.py"}
    assert not {p.name for p in FIRMWARE.iterdir()} & sobrantes


def test_config_ble_de_ejemplo_no_tiene_datos_reales():
    texto = (FIRMWARE / "config_ble.example.py").read_text(encoding="utf-8")
    assert 'NOMBRE = "Mano-LSC"' in texto and 'TOKEN = "cambia-este-token' in texto
    assert not (FIRMWARE / "config_ble.py").exists()

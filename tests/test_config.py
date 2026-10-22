"""Configuración centralizada (pgc.config)."""
import pytest

from conftest import RAIZ, mano_serial, modulo_texto, servidor

from pgc import config as cfgmod


def cargar(argv=(), entorno=None, archivo_env=None, tmp_path=None):
    if archivo_env is None:
        archivo_env = (tmp_path or RAIZ) / "no-existe.env"
    return cfgmod.cargar(list(argv), entorno or {}, archivo_env)


def test_valores_por_defecto_iguales_a_los_del_codigo_actual():
    c = cargar()
    assert c.puerto_web == 8000 and c.abrir_navegador and c.tunel and c.voz
    assert c.mano == "auto" and c.mano_puerto is None
    assert c.mano_baudios == 115200
    assert set(c.mano_vids) == mano_serial.VIDS_ESP32
    assert c.mano_timeout_letra == mano_serial.TIMEOUT_LETRA
    assert c.mano_tiempo_simulado == mano_serial.TIEMPO_SIMULADO
    assert c.pausa_letra == servidor.PAUSA_ENTRE_LETRAS
    assert c.pausa_no_disponible == servidor.PAUSA_NO_DISPONIBLE
    assert c.max_caracteres == modulo_texto.MAX_CARACTERES
    assert c.max_pendientes_cliente == servidor.MAX_PENDIENTES_CLIENTE
    assert c.max_cola == servidor.MAX_COLA
    assert c.audio_max_bytes == servidor.MAX_AUDIO_BYTES
    assert c.historial == 6 and c.ping_ws == 20.0 and c.autodeteccion_cada == 3.0
    assert c.voz_modelo == "medium"


@pytest.mark.parametrize("argv, esperado", [
    (["--simular"], {"mano": "simulada"}),
    (["--puerto", "COM5"], {"mano_puerto": "COM5", "mano": "auto"}),
    (["--puerto-web", "8001"], {"puerto_web": 8001}),
    (["--sin-tunel", "--sin-voz", "--no-abrir"], {"tunel": False, "voz": False, "abrir_navegador": False}),
])
def test_opciones_de_siempre(argv, esperado):
    c = cargar(argv)
    for k, v in esperado.items():
        assert getattr(c, k) == v


def test_prioridad_env_variables_opciones(tmp_path):
    env = tmp_path / ".env"
    env.write_text("PGC_PUERTO_WEB=8100\nPGC_MAX_COLA=10   # comentario\nPGC_MANO=simulada\n", encoding="utf-8")
    c = cargar(archivo_env=env)
    assert (c.puerto_web, c.max_cola, c.mano) == (8100, 10, "simulada")
    c = cargar(entorno={"PGC_PUERTO_WEB": "8200"}, archivo_env=env)
    assert (c.puerto_web, c.max_cola) == (8200, 10)                  # la variable gana al .env
    c = cargar(["--puerto-web", "8300"], entorno={"PGC_PUERTO_WEB": "8200"}, archivo_env=env)
    assert c.puerto_web == 8300                                      # la opción gana a todo


@pytest.mark.parametrize("variables, esperado", [
    ({"PGC_VOZ": "false"}, ("voz", False)),
    ({"PGC_TUNEL": "0"}, ("tunel", False)),
    ({"PGC_MANO_VIDS": "303a, 1A86"}, ("mano_vids", (0x303A, 0x1A86))),
    ({"PGC_MANO_PUERTO": ""}, ("mano_puerto", None)),
    ({"PGC_PAUSA_LETRA": "0.25"}, ("pausa_letra", 0.25)),
])
def test_conversion_de_tipos(variables, esperado):
    assert getattr(cargar(entorno=variables), esperado[0]) == esperado[1]


@pytest.mark.parametrize("variables, fragmento", [
    ({"PGC_PUERTO_WEB": "ocho mil"}, "PGC_PUERTO_WEB"),
    ({"PGC_VOZ": "quizas"}, "PGC_VOZ"),
    ({"PGC_MANO": "bluetooth"}, "PGC_MANO"),
    ({"PGC_MAX_COLA": "0"}, "PGC_MAX_COLA"),
    ({"PGC_PAUSA_LETRA": "-1"}, "PGC_PAUSA_LETRA"),
])
def test_valores_invalidos_dan_un_error_claro(variables, fragmento):
    with pytest.raises(cfgmod.ErrorConfig, match=fragmento):
        cargar(entorno=variables)


def test_variables_ajenas_se_ignoran():
    assert cargar(entorno={"PATH": "x", "PGC_DESCONOCIDA": "1"}) == cfgmod.Config()


def test_env_example_documenta_todas_las_variables():
    ejemplo = (RAIZ / ".env.example").read_text(encoding="utf-8")
    from dataclasses import fields
    for campo in fields(cfgmod.Config):
        assert f"PGC_{campo.name.upper()}=" in ejemplo, campo.name


def test_config_es_inmutable():
    with pytest.raises(Exception):
        cargar().puerto_web = 1

"""Regla de dependencias de la arquitectura hexagonal (las flechas apuntan hacia adentro)."""
import pytest

from conftest import RAIZ
from test_dominio import imports_de

EXTERNOS = {"serial", "fastapi", "starlette", "uvicorn", "qrcode", "faster_whisper", "ctranslate2",
            "subprocess", "socket", "servidor", "mano_serial", "texto_util", "tunel", "voz_entrada"}
PERMITIDO_EN_APLICACION = ("pgc.dominio", "pgc.puertos", "pgc.aplicacion")


@pytest.mark.parametrize("ruta", sorted((RAIZ / "pgc" / "aplicacion").glob("*.py")), ids=lambda r: r.name)
def test_la_aplicacion_solo_usa_dominio_y_puertos(ruta):
    for nombre in imports_de(ruta):
        raiz = nombre.split(".")[0]
        assert raiz not in EXTERNOS, f"{ruta.name} importa {nombre}"
        if raiz == "pgc":
            assert nombre.startswith(PERMITIDO_EN_APLICACION), f"{ruta.name} importa {nombre}"


@pytest.mark.parametrize("ruta", sorted((RAIZ / "pgc" / "api").rglob("*.py")), ids=lambda r: r.name)
def test_la_api_no_conoce_los_adaptadores(ruta):
    for nombre in imports_de(ruta):
        assert not nombre.startswith(("pgc.adaptadores", "pgc.arranque")), f"{ruta.name} importa {nombre}"
        assert nombre.split(".")[0] not in {"servidor", "mano_serial", "tunel", "voz_entrada", "serial"}, nombre


@pytest.mark.parametrize("ruta", sorted((RAIZ / "pgc" / "puertos").glob("*.py")), ids=lambda r: r.name)
def test_los_puertos_no_dependen_de_implementaciones(ruta):
    for nombre in imports_de(ruta):
        assert not nombre.startswith(("pgc.adaptadores", "pgc.aplicacion", "pgc.api")), f"{ruta.name} importa {nombre}"
        assert nombre.split(".")[0] not in EXTERNOS, f"{ruta.name} importa {nombre}"

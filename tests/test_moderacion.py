"""Filtro de palabras ofensivas (pgc.dominio.moderacion)."""
import pytest

from pgc.dominio.moderacion import Moderador, cargar_moderador


@pytest.fixture(scope="module")
def mod():
    return cargar_moderador()


@pytest.mark.parametrize("texto", [
    "gonorrea", "Gonorreaaa", "GONORREA!!", "hijueputa", "hijueputas", "malparido", "marica", "maricones",
    "h p", "H.P.", "p u t a", "put4", "puta", "mierda", "perrrra", "c0ño", "coño",
    "eres un hp", "hola gonorrea", "nazi", "venecos", "culos", "estúpido", "imbécil",
])
def test_bloquea(mod, texto):
    assert mod.es_ofensivo(texto), texto


@pytest.mark.parametrize("texto", [
    "hola jurado", "calle", "carro", "pera", "Maricarmen", "mondadientes", "computador", "disputa",
    "Puerto", "señor José", "bienvenidos a la sustentación", "a e i o u", "uña", "gracias", "chimenea",
    "perro", "zorro", "pendiente", "cultivo", "cono", "hipótesis",
])
def test_no_bloquea_palabras_normales(mod, texto):
    assert not mod.es_ofensivo(texto), texto


def test_lista_editable(tmp_path):
    ruta = tmp_path / "lista.txt"
    ruta.write_text("# comentario\nbrocoli\n\n", encoding="utf-8")
    m = cargar_moderador(ruta)
    assert m.es_ofensivo("odio el brócoli") and not m.es_ofensivo("gonorrea")


def test_moderador_vacio_no_bloquea_nada():
    assert not Moderador([]).es_ofensivo("lo que sea")

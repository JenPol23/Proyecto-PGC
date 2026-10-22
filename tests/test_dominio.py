"""Dominio puro: regla de órdenes, abecedario y aislamiento de la capa."""
import ast
import json

import pytest

from conftest import RAIZ, modulo_ordenes, modulo_texto

from pgc.dominio import abecedario


def plan(texto, letras=None):
    return " ".join(modulo_ordenes.planificar_ordenes(modulo_texto.a_secuencia(texto, letras)))


# ---------------------------------------------------------------- órdenes
@pytest.mark.parametrize("entrada, ordenes", [
    ("calle", "c a l reset l e reset"),
    ("carro", "c a r reset r o reset"),
    ("ll ll", "l reset l reset l reset l reset"),
    ("ñn", "n reset n reset"),
    ("lgl", "l reset l reset"),
    ("hola", "o l a reset"),
    ("ve mi", "v e reset m i reset"),
    ("a", "a reset"),
])
def test_planificar_ordenes_igual_que_el_hilo_de_la_mano(entrada, ordenes):
    assert plan(entrada) == ordenes


def test_ordenes_para_cada_tipo_de_paso():
    letra = {"c": "L", "l": "l", "tipo": "ok"}
    assert modulo_ordenes.ordenes_para(letra, None) == ["l"]
    assert modulo_ordenes.ordenes_para(letra, "a") == ["l"]
    assert modulo_ordenes.ordenes_para(letra, "l") == ["reset", "l"]
    assert modulo_ordenes.ordenes_para({"c": " ", "l": None, "tipo": "espacio"}, "l") == ["reset"]
    assert modulo_ordenes.ordenes_para({"c": "H", "l": None, "tipo": "nd"}, "l") == []
    assert modulo_ordenes.ordenes_para({"c": "Ñ", "l": "n", "tipo": "aprox"}, "n") == ["reset", "n"]


def test_forma_despues():
    letra = {"c": "L", "l": "l", "tipo": "ok"}
    assert modulo_ordenes.forma_despues(letra, None, True) == "l"
    assert modulo_ordenes.forma_despues(letra, None, False) is None          # sin confirmar: forma desconocida
    assert modulo_ordenes.forma_despues({"c": " ", "l": None, "tipo": "espacio"}, "l", True) is None
    assert modulo_ordenes.forma_despues({"c": "H", "l": None, "tipo": "nd"}, "l", None) == "l"


# ---------------------------------------------------------------- abecedario
def test_letras_json_da_las_21_letras_de_hoy():
    a = abecedario.cargar_abecedario()
    assert "".join(sorted(a.por_defecto)) == "abcdefiklmnopqrtuvwxy"
    assert a.aproximaciones == {"ñ": "n"}
    assert a.con_movimiento == frozenset("jzñ")
    assert modulo_texto.LETRAS_POR_DEFECTO == a.por_defecto


def test_agregar_letras_es_editar_datos(tmp_path):
    ruta = tmp_path / "letras.json"
    ruta.write_text(json.dumps({"por_defecto": "abcghs", "aproximaciones": {"ñ": "n"}}), encoding="utf-8")
    assert abecedario.cargar_abecedario(ruta).por_defecto == frozenset("abcghs")


@pytest.mark.parametrize("contenido, fragmento", [
    ("{no es json", "No se pudo leer"),
    (json.dumps({"por_defecto": ""}), "vacío"),
    (json.dumps({"por_defecto": "ab1"}), "no son letras"),
    (json.dumps({"por_defecto": "ab", "aproximaciones": {"ñ": "nn"}}), "aproximación inválida"),
])
def test_letras_json_invalido(tmp_path, contenido, fragmento):
    ruta = tmp_path / "letras.json"
    ruta.write_text(contenido, encoding="utf-8")
    with pytest.raises(abecedario.ErrorAbecedario, match=fragmento):
        abecedario.cargar_abecedario(ruta)


# ---------------------------------------------------------------- aislamiento
PROHIBIDOS = {"threading", "socket", "serial", "fastapi", "starlette", "uvicorn", "asyncio", "subprocess",
              "servidor", "mano_serial", "tunel", "voz_entrada"}


def imports_de(ruta):
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            yield from (a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            yield nodo.module


@pytest.mark.parametrize("ruta", sorted((RAIZ / "pgc" / "dominio").glob("*.py")), ids=lambda r: r.name)
def test_el_dominio_no_depende_de_nada_externo(ruta):
    for nombre in imports_de(ruta):
        raiz = nombre.split(".")[0]
        assert raiz not in PROHIBIDOS, f"{ruta.name} importa {nombre}"
        if raiz == "pgc":
            assert nombre.startswith("pgc.dominio"), f"{ruta.name} importa {nombre} (fuera del dominio)"

"""Texto libre → secuencia de pasos (caracterización de texto_util)."""
import pytest

from conftest import tipos


def test_letras_por_defecto_son_las_21_de_la_mano(texto):
    assert "".join(sorted(texto.LETRAS_POR_DEFECTO)) == "abcdefiklmnopqrtuvwxy"
    assert texto.MAX_CARACTERES == 60
    assert texto.APROXIMACIONES == {"ñ": "n"}


@pytest.mark.parametrize("entrada, esperado", [
    ("  HOLA   Mundo 12 ", "hola mundo uno dos"),
    ("a2b", "a dos b"),
    ("2026", "dos cero dos seis"),
    ("", ""),
    (None, ""),
    ("Señor José", "señor josé"),          # limpiar conserva tildes y ñ
])
def test_limpiar(texto, entrada, esperado):
    assert texto.limpiar(entrada) == esperado


def test_limpiar_recorta_a_60_despues_de_expandir_numeros(texto):
    r = texto.limpiar("1" * 30)
    assert len(r) == 60
    assert r.startswith("uno uno ")
    assert r.endswith("o uno ")             # el recorte puede dejar un espacio al final
    assert len(texto.limpiar("a" * 70)) == 60


def test_ejemplo_completo_senor_jose(texto):
    assert tipos(texto.a_secuencia("Señor José 2")) == [
        ("S", "nd"), ("E", "ok"), ("Ñ", "aprox"), ("O", "ok"), ("R", "ok"), (" ", "espacio"),
        ("J", "nd"), ("O", "ok"), ("S", "nd"), ("E", "ok"), (" ", "espacio"),
        ("D", "ok"), ("O", "ok"), ("S", "nd"),
    ]


def test_estructura_de_cada_paso(texto):
    pasos = texto.a_secuencia("ña h")
    assert pasos == [
        {"c": "Ñ", "l": "n", "tipo": "aprox"},
        {"c": "A", "l": "a", "tipo": "ok"},
        {"c": " ", "l": None, "tipo": "espacio"},
        {"c": "H", "l": None, "tipo": "nd"},
    ]


@pytest.mark.parametrize("entrada, esperado", [
    ("áéíóú", [("A", "ok"), ("E", "ok"), ("I", "ok"), ("O", "ok"), ("U", "ok")]),
    ("üÜ", [("U", "ok"), ("U", "ok")]),
    ("Ñandú", [("Ñ", "aprox"), ("A", "ok"), ("N", "ok"), ("D", "ok"), ("U", "ok")]),
    ("1", [("U", "ok"), ("N", "ok"), ("O", "ok")]),
    ("gh", [("G", "nd"), ("H", "nd")]),
    ("jsz", [("J", "nd"), ("S", "nd"), ("Z", "nd")]),
])
def test_tildes_enie_numeros_y_no_disponibles(texto, entrada, esperado):
    assert tipos(texto.a_secuencia(entrada)) == esperado


@pytest.mark.parametrize("entrada, esperado", [
    ("a , b", [("A", "ok"), (" ", "espacio"), ("B", "ok")]),       # espacios seguidos se juntan
    ("¡Hola, mundo!", [("H", "nd"), ("O", "ok"), ("L", "ok"), ("A", "ok"), (" ", "espacio"),
                       ("M", "ok"), ("U", "ok"), ("N", "ok"), ("D", "ok"), ("O", "ok")]),
    ("  a  ", [("A", "ok")]),
    ("a ¿?", [("A", "ok")]),                                        # sin espacio final
    ("¡¿?!", []),
    ("", []),
])
def test_espacios_y_puntuacion(texto, entrada, esperado):
    assert tipos(texto.a_secuencia(entrada)) == esperado


def test_letras_repetidas_se_conservan_en_la_secuencia(texto):
    # La regla de abrir la mano entre letras iguales está en el hilo de la mano, no aquí
    assert tipos(texto.a_secuencia("calle")) == [("C", "ok"), ("A", "ok"), ("L", "ok"), ("L", "ok"), ("E", "ok")]
    assert tipos(texto.a_secuencia("carro")) == [("C", "ok"), ("A", "ok"), ("R", "ok"), ("R", "ok"), ("O", "ok")]


def test_letras_que_reporta_la_mano(texto):
    assert tipos(texto.a_secuencia("gh", set("gh"))) == [("G", "ok"), ("H", "ok")]
    # Ñ sin N disponible: no se puede aproximar
    assert tipos(texto.a_secuencia("ñ", set("a"))) == [("Ñ", "nd")]
    # Conjunto vacío o None → letras por defecto
    assert tipos(texto.a_secuencia("gh", set())) == [("G", "nd"), ("H", "nd")]
    assert tipos(texto.a_secuencia("a", None)) == [("A", "ok")]

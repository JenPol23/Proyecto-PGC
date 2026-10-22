"""Letras que sabe hacer la mano, como datos (datos/letras.json) y no como código."""
import json
from dataclasses import dataclass, field
from pathlib import Path

RUTA_LETRAS = Path(__file__).resolve().parent.parent.parent / "datos" / "letras.json"
LETRAS_VALIDAS = set("abcdefghijklmnñopqrstuvwxyz")


class ErrorAbecedario(ValueError):
    """letras.json mal formado."""


@dataclass(frozen=True)
class Abecedario:
    por_defecto: frozenset           # letras que hace la mano si no informa las suyas
    aproximaciones: dict = field(default_factory=dict)   # letra → letra con la que se forma (ñ → n)
    con_movimiento: frozenset = frozenset()              # j, z, ñ: la mano no tiene muñeca


def _letras(valor, nombre):
    letras = set(valor)
    raras = letras - LETRAS_VALIDAS
    if raras:
        raise ErrorAbecedario(f"letras.json: '{nombre}' tiene caracteres que no son letras: {''.join(sorted(raras))}")
    return frozenset(letras)


def cargar_abecedario(ruta=RUTA_LETRAS):
    try:
        datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as ex:
        raise ErrorAbecedario(f"No se pudo leer {ruta}: {ex}") from None
    por_defecto = _letras(datos.get("por_defecto", ""), "por_defecto")
    if not por_defecto:
        raise ErrorAbecedario("letras.json: 'por_defecto' está vacío")
    aproximaciones = {}
    for letra, forma in datos.get("aproximaciones", {}).items():
        _letras(letra + forma, "aproximaciones")
        if len(letra) != 1 or len(forma) != 1:
            raise ErrorAbecedario(f"letras.json: aproximación inválida {letra!r} → {forma!r}")
        aproximaciones[letra] = forma
    con_movimiento = _letras("".join(datos.get("con_movimiento", [])), "con_movimiento")
    return Abecedario(por_defecto, aproximaciones, con_movimiento)

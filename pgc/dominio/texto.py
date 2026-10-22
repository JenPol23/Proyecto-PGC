"""Convierte un texto libre en la secuencia de letras que la mano puede hacer."""
import re
import unicodedata

from pgc.dominio.abecedario import cargar_abecedario

_ABECEDARIO = cargar_abecedario()

# Letras por defecto (se reemplazan por las que reporte el ESP32 con "letras")
LETRAS_POR_DEFECTO = _ABECEDARIO.por_defecto

# Letras que la mano no puede hacer exactas y se aproximan con otra forma
APROXIMACIONES = _ABECEDARIO.aproximaciones

DIGITOS = {
    "0": "cero", "1": "uno", "2": "dos", "3": "tres", "4": "cuatro",
    "5": "cinco", "6": "seis", "7": "siete", "8": "ocho", "9": "nueve",
}

MAX_CARACTERES = 60


def _quitar_tilde(c: str) -> str:
    if c == "ñ":
        return c
    base = unicodedata.normalize("NFD", c)
    return "".join(ch for ch in base if unicodedata.category(ch) != "Mn")


def limpiar(texto: str, maximo: int = MAX_CARACTERES) -> str:
    texto = (texto or "").strip().lower()
    texto = re.sub(r"\d", lambda m: " " + DIGITOS[m.group()] + " ", texto)
    texto = re.sub(r"\s+", " ", texto).strip()
    return texto[:maximo]


def a_secuencia(texto: str, letras_mano=None, maximo: int = MAX_CARACTERES):
    """Devuelve una lista de pasos: {"c": mostrar, "l": enviar|None, "tipo": ...}

    tipo: "ok" (la mano la hace), "aprox" (se aproxima con otra letra),
          "nd" (no disponible, se muestra pero no se envía), "espacio".
    """
    letras_mano = letras_mano or LETRAS_POR_DEFECTO
    pasos = []
    for c in limpiar(texto, maximo):
        if c == " ":
            if pasos and pasos[-1]["tipo"] != "espacio":
                pasos.append({"c": " ", "l": None, "tipo": "espacio"})
            continue
        c = _quitar_tilde(c)
        if c in APROXIMACIONES and APROXIMACIONES[c] in letras_mano:
            pasos.append({"c": c.upper(), "l": APROXIMACIONES[c], "tipo": "aprox"})
        elif c in letras_mano:
            pasos.append({"c": c.upper(), "l": c, "tipo": "ok"})
        elif c.isalpha():
            pasos.append({"c": c.upper(), "l": None, "tipo": "nd"})
        # signos de puntuación se ignoran
    while pasos and pasos[-1]["tipo"] == "espacio":
        pasos.pop()
    return pasos


if __name__ == "__main__":
    for t in ["Hola mundo", "Señor José 2026", "¡Gracias, jurado!"]:
        print(t, "->", [(p["c"], p["tipo"]) for p in a_secuencia(t)])

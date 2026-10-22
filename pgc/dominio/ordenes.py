"""Qué órdenes recibe la mano por cada paso de la secuencia.

Reglas:
  * espacio → "reset" (mano abierta = separación entre palabras);
  * letra igual a la forma que la mano ya tiene (ll, rr, ñn...) → "reset" y luego
    la letra; sin esto los servos ya estarían en su sitio y no se notaría;
  * letra no disponible → ninguna orden (solo se muestra en pantalla).
"""
RESET = "reset"


def ordenes_para(paso, forma):
    """Órdenes para `paso` si la mano tiene formada la letra `forma` (None = abierta).

    La última orden de la lista es la que decide si el paso salió bien.
    """
    if paso["tipo"] == "espacio":
        return [RESET]
    letra = paso["l"]
    if not letra:
        return []
    return [RESET, letra] if letra == forma else [letra]


def forma_despues(paso, forma, ok):
    """Letra que queda formada tras el paso (None = mano abierta o desconocida)."""
    if paso["tipo"] == "espacio":
        return None
    if paso["l"]:
        return paso["l"] if ok else None
    return forma                       # letra no disponible: la mano no se movió


def planificar_ordenes(pasos):
    """Todas las órdenes de un mensaje si la mano confirma cada una (incluye el reset final)."""
    ordenes, forma = [], None
    for paso in pasos:
        ordenes += ordenes_para(paso, forma)
        forma = forma_despues(paso, forma, True)
    return ordenes + [RESET]

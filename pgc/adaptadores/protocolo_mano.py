"""Respuestas del firmware de la mano (el código ORIGINAL del autor), iguales por USB y Bluetooth.

Órdenes que manda el PC        Respuesta del firmware
  "<letra>"  (a..y disponibles) "gesto_<letra>_ok"   (antes hace reset_all(): abre la mano)
  "<letra>"  (no disponible)    "comando_no_reconocido"
  "reset"                       "reset_ok"
El firmware NO tiene "ping" ni "letras": una palabra de más de una letra la
deletrearía (p. ej. "ping" movería la mano). Por eso el PC comprueba la conexión
con "reset" y nunca manda palabras: siempre letra por letra.
"""
ORDEN_COMPROBAR = "reset"
RESPUESTA_RESET = "reset_ok"
NO_RECONOCIDO = "comando_no_reconocido"


def resultado(orden, linea):
    """True si `linea` confirma la orden, False si la rechaza, None si es otra cosa."""
    if orden == "reset":
        return True if linea == RESPUESTA_RESET else None
    if linea == f"gesto_{orden}_ok":
        return True
    if linea == NO_RECONOCIDO:
        return False
    return None

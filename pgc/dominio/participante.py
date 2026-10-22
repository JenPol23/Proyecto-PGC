"""Nombre opcional del participante (ADR-7): corto, legible y sin datos de más."""
import re

MAX_NOMBRE = 20
ANONIMO = "Anónimo"          # autor de los mensajes de quien no puso nombre
_PATRON = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9 .'\-]+$")
MSG_NOMBRE_INVALIDO = f"Usa solo letras en tu nombre (máximo {MAX_NOMBRE})."
MSG_NOMBRE_OFENSIVO = "Ese nombre no se puede mostrar. Prueba con otro."
MSG_BLOQUEADO = "El presentador pausó tu participación en esta sesión. ¡Gracias por participar!"


def normalizar_nombre(texto):
    """'  ana   maría ' → 'ana maría'; vacío → None. ValueError si no es un nombre razonable."""
    if texto is None:
        return None
    nombre = re.sub(r"\s+", " ", texto).strip()
    if not nombre:
        return None
    if len(nombre) > MAX_NOMBRE or not _PATRON.match(nombre):
        raise ValueError(MSG_NOMBRE_INVALIDO)
    return nombre

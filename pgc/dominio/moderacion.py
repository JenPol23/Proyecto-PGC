"""Filtro básico de palabras ofensivas antes de mostrar un texto en el proyector.

Es una defensa razonable para una sala, no un sistema infalible: la lista vive
en datos/palabras_bloqueadas.txt y el presentador puede saltar un mensaje.
"""
import re
import unicodedata
from pathlib import Path

RUTA_PALABRAS = Path(__file__).resolve().parent.parent.parent / "datos" / "palabras_bloqueadas.txt"
LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
LARGO_PREFIJO = 7          # raíces de 7+ letras también bloquean palabras que empiezan por ellas


def _sin_tildes(texto):
    return "".join(c if c in "ñÑ" else
                   "".join(ch for ch in unicodedata.normalize("NFD", c) if unicodedata.category(ch) != "Mn")
                   for c in texto)


def _reducir(palabra):
    """Una sola letra por grupo de repetidas: 'gonorreaaa' → 'gonorea'."""
    return re.sub(r"(.)\1+", r"\1", palabra)


def _estirada(palabra):
    """Tres o más letras iguales seguidas ('perrrra'): señal de que se quiere esquivar el filtro."""
    return re.search(r"(.)\1\1", palabra) is not None


def palabras_normalizadas(texto):
    texto = _sin_tildes((texto or "").lower()).translate(LEET)
    return re.findall(r"[a-zñ]+", texto)


class Moderador:
    def __init__(self, bloqueadas):
        self.exactas = set(palabras_normalizadas(" ".join(bloqueadas)))
        self.reducidas = {_reducir(p) for p in self.exactas}

    @staticmethod
    def _coincide(palabra, conjunto):
        if palabra in conjunto or palabra.rstrip("s") in conjunto \
                or (palabra.endswith("es") and palabra[:-2] in conjunto):
            return True
        return any(palabra.startswith(r) for r in conjunto if len(r) >= LARGO_PREFIJO)

    def _bloqueada(self, palabra):
        if self._coincide(palabra, self.exactas):
            return True
        # "pera" no es "perra"; "perrrra" sí: solo se reduce lo que viene estirado
        return _estirada(palabra) and self._coincide(_reducir(palabra), self.reducidas)

    def es_ofensivo(self, texto):
        palabras = palabras_normalizadas(texto)
        # Letras sueltas seguidas se leen juntas: "h p" → "hp", "p u t a" → "puta"
        candidatas, sueltas = list(palabras), []
        for p in palabras + [""]:
            if len(p) == 1:
                sueltas.append(p)
                continue
            if len(sueltas) >= 2:
                candidatas.append("".join(sueltas))
            sueltas = []
        return any(self._bloqueada(p) for p in candidatas)


def cargar_moderador(ruta=RUTA_PALABRAS):
    lineas = Path(ruta).read_text(encoding="utf-8").splitlines()
    return Moderador([l.strip() for l in lineas if l.strip() and not l.lstrip().startswith("#")])

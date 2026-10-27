"""Modelos de entrada de la API (pydantic)."""
import unicodedata
from typing import Literal

from pydantic import BaseModel, Field, field_validator

PATRON_CLIENTE = r"^[A-Za-z0-9_-]{1,64}$"     # id aleatorio que genera la página del celular
PERMITIDOS = {"\n", "\r", "\t"}               # el cuadro de texto admite saltos de línea


def sin_caracteres_de_control(texto: str) -> str:
    if any(unicodedata.category(c) == "Cc" and c not in PERMITIDOS for c in texto):
        raise ValueError("caracteres de control")
    return texto


class Texto(BaseModel):
    texto: str
    cliente: str = Field(default="anonimo", pattern=PATRON_CLIENTE)

    _validar_texto = field_validator("texto")(sin_caracteres_de_control)


class Cliente(BaseModel):
    cliente: str = Field(pattern=PATRON_CLIENTE)


class ControlKinect(BaseModel):
    accion: Literal["iniciar", "detener", "espacio", "borrar", "limpiar", "terminar"]
    cliente: str | None = Field(default=None, pattern=PATRON_CLIENTE)    # None = el presentador (con token)


class Eco(BaseModel):
    activo: bool


class Participante(BaseModel):
    cliente: str = Field(pattern=PATRON_CLIENTE)
    nombre: str | None = Field(default=None, max_length=60)    # se normaliza a 20 caracteres

    @field_validator("nombre")
    @classmethod
    def _validar_nombre(cls, valor):
        return None if valor is None else sin_caracteres_de_control(valor)

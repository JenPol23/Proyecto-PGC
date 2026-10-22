"""Dependencias comunes de las rutas."""
from fastapi import Request

SIN_CACHE = {"Cache-Control": "no-store"}


def obtener_sistema(request: Request):
    return request.app.state.sistema

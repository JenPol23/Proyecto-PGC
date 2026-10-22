"""Controles del presentador: solo desde el PC del proyector y con el token de administrador."""
from fastapi import APIRouter, Depends, HTTPException

from pgc.api.dependencias import obtener_sistema
from pgc.api.seguridad import verificar_admin

router = APIRouter(dependencies=[Depends(verificar_admin)])


@router.post("/api/mano/reconectar")
def reconectar(sistema=Depends(obtener_sistema)):
    sistema.reconectar_mano()
    return {"ok": True}


@router.post("/api/mano/saltar")
def saltar(sistema=Depends(obtener_sistema)):
    if not sistema.saltar_actual():
        raise HTTPException(404, "No hay ningún mensaje en curso.")
    return {"ok": True}

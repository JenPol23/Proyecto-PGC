"""Participantes: nombre opcional (celular) y bloqueo por sesión (presentador)."""
from fastapi import APIRouter, Depends, HTTPException, Request

from pgc.api.dependencias import obtener_sistema
from pgc.api.esquemas import Participante
from pgc.api.seguridad import ip_real, limitar, verificar_admin

router = APIRouter()
NO_EXISTE = "No encontramos a ese participante."


@router.post("/api/participante")
def registrar(datos: Participante, request: Request, sistema=Depends(obtener_sistema)):
    """Lo llama el celular al abrir la página y al cambiar el nombre. Devuelve su alias (pid)."""
    limitar(request, "participante", ip_real(request), sistema.cfg.lim_mensaje_ip)
    try:
        return sistema.registrar_participante(datos.cliente, datos.nombre)
    except ValueError as ex:
        raise HTTPException(400, str(ex))


@router.post("/api/participantes/{pid}/bloquear", dependencies=[Depends(verificar_admin)])
def bloquear(pid: str, sistema=Depends(obtener_sistema)):
    resultado = sistema.bloquear(pid)
    if resultado is None:
        raise HTTPException(404, NO_EXISTE)
    return {"ok": True, **resultado}


@router.post("/api/participantes/{pid}/desbloquear", dependencies=[Depends(verificar_admin)])
def desbloquear(pid: str, sistema=Depends(obtener_sistema)):
    if not sistema.desbloquear(pid):
        raise HTTPException(404, NO_EXISTE)
    return {"ok": True}

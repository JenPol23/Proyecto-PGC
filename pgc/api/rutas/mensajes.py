"""Mensajes de los jurados: vista previa, enviar y cancelar."""
from fastapi import APIRouter, Depends, HTTPException, Query, Request

from pgc.api.dependencias import obtener_sistema
from pgc.api.esquemas import PATRON_CLIENTE, Texto
from pgc.api.seguridad import ip_real, limitar
from pgc.aplicacion.sistema import ParticipanteBloqueado
from pgc.dominio.texto import a_secuencia

router = APIRouter()


def revisar_largo(datos, cfg):
    """Más de texto_max_cuerpo: 422 (no es algo que la página envíe)."""
    if len(datos.texto) > cfg.texto_max_cuerpo:
        raise HTTPException(422, f"El mensaje es muy largo (máximo {cfg.max_caracteres} caracteres).")


@router.post("/api/previa")
def previa(datos: Texto, request: Request, sistema=Depends(obtener_sistema)):
    limitar(request, "previa", ip_real(request), sistema.cfg.lim_previa_ip)
    revisar_largo(datos, sistema.cfg)
    pasos = a_secuencia(datos.texto, sistema.mano.letras, sistema.cfg.max_caracteres)
    return {"pasos": [{"c": p["c"], "tipo": p["tipo"]} for p in pasos]}


@router.post("/api/mensaje")
def nuevo_mensaje(datos: Texto, request: Request, sistema=Depends(obtener_sistema)):
    cfg = sistema.cfg
    limitar(request, "mensaje", ip_real(request), cfg.lim_mensaje_ip)
    limitar(request, "mensaje-cliente", datos.cliente, cfg.lim_mensaje_cliente)
    revisar_largo(datos, cfg)
    if len(datos.texto.strip()) > cfg.max_caracteres:
        raise HTTPException(400, f"Máximo {cfg.max_caracteres} caracteres.")
    try:
        msg = sistema.encolar(datos.texto, datos.cliente)
    except ParticipanteBloqueado as ex:
        raise HTTPException(403, str(ex))
    except ValueError as ex:
        raise HTTPException(400, str(ex))
    return {"id": msg["id"], "texto": msg["texto"], "sesion": sistema.sesion}


@router.delete("/api/mensaje/{id_msg}")
def cancelar(id_msg: int, cliente: str = Query(pattern=PATRON_CLIENTE), sistema=Depends(obtener_sistema)):
    if not sistema.cancelar(id_msg, cliente):
        raise HTTPException(404, "Ese mensaje ya no se puede cancelar.")
    return {"ok": True}

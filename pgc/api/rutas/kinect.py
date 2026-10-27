"""Kinect: turno (un jurado a la vez), controles del deletreo, modo eco e imagen de la cámara.

El estado del Kinect (texto en vivo, detector, turno) NO tiene rutas para
consultar: llega a todos por el WebSocket. Aquí solo hay órdenes.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response

from pgc.api.dependencias import SIN_CACHE, obtener_sistema
from pgc.api.esquemas import Cliente, ControlKinect, Eco
from pgc.api.seguridad import es_admin, ip_real, limitar, verificar_admin
from pgc.aplicacion.senas import SinControles
from pgc.aplicacion.sistema import ParticipanteBloqueado, SinPermisoKinect
from pgc.aplicacion.turno import TurnoOcupado

router = APIRouter()


@router.post("/api/kinect/turno")
def tomar_turno(datos: Cliente, request: Request, sistema=Depends(obtener_sistema)):
    limitar(request, "kinect", datos.cliente, sistema.cfg.lim_kinect_cliente)
    try:
        sistema.tomar_turno_kinect(datos.cliente)
    except ParticipanteBloqueado as ex:
        raise HTTPException(403, str(ex))
    except TurnoOcupado as ex:
        raise HTTPException(409, str(ex))
    return {"ok": True}


@router.post("/api/kinect/turno/soltar")
def soltar_turno(datos: Cliente, sistema=Depends(obtener_sistema)):
    sistema.soltar_turno_kinect(datos.cliente)
    return {"ok": True}


@router.post("/api/kinect/control")
def controlar(datos: ControlKinect, request: Request, sistema=Depends(obtener_sistema)):
    presentador = es_admin(request, request.app.state.token_admin)
    if not presentador:
        limitar(request, "kinect-ip", ip_real(request), sistema.cfg.lim_kinect_cliente * 2)
        if datos.cliente:
            limitar(request, "kinect", datos.cliente, sistema.cfg.lim_kinect_cliente)
    try:
        sistema.controlar_kinect(datos.accion, datos.cliente, presentador=presentador)
    except (SinPermisoKinect, ParticipanteBloqueado) as ex:
        raise HTTPException(403, str(ex))
    except SinControles as ex:
        raise HTTPException(409, str(ex))
    except RuntimeError as ex:                 # el detector no responde o rechazó la orden
        raise HTTPException(503, str(ex))
    return {"ok": True}


# ----------------------------------------------------------------- solo el presentador
@router.post("/api/kinect/liberar", dependencies=[Depends(verificar_admin)])
def liberar_turno(sistema=Depends(obtener_sistema)):
    sistema.liberar_turno_kinect()
    return {"ok": True}


@router.post("/api/kinect/eco", dependencies=[Depends(verificar_admin)])
def eco(datos: Eco, sistema=Depends(obtener_sistema)):
    sistema.fijar_eco(datos.activo)
    return {"eco": sistema.eco}


@router.get("/api/kinect/imagen", dependencies=[Depends(verificar_admin)])
def imagen(sistema=Depends(obtener_sistema)):
    """La cámara con los puntos de la mano: solo en el PC del proyector, nunca por el túnel ni la red."""
    jpeg = sistema.senas.imagen()
    if jpeg is None:
        raise HTTPException(503, "No llegan imágenes del Kinect.")
    return Response(jpeg, media_type="image/jpeg", headers=SIN_CACHE)

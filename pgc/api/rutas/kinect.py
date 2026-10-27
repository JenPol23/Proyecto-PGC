"""Kinect: turno (un jurado a la vez), controles del deletreo, modo eco e imagen de la cámara.

El estado del Kinect (texto en vivo, detector, turno) NO tiene rutas para
consultar: llega a todos por el WebSocket. Aquí solo hay órdenes.
"""
import json
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response

from pgc.api.dependencias import SIN_CACHE, obtener_sistema
from pgc.api.esquemas import Cliente, ControlKinect, Eco, Protocolo, TomarTurno
from pgc.api.seguridad import es_admin, ip_real, limitar, verificar_admin
from pgc.aplicacion.senas import SinControles
from pgc.aplicacion.sistema import ParticipanteBloqueado, SinPermisoKinect
from pgc.aplicacion.turno import CodigoIncorrecto, TurnoOcupado

router = APIRouter()


@router.post("/api/kinect/turno")
def tomar_turno(datos: TomarTurno, request: Request, sistema=Depends(obtener_sistema)):
    limitar(request, "kinect", datos.cliente, sistema.cfg.lim_kinect_cliente)
    # Adivinar el código: 1 entre un millón y, por IP, unos 30 intentos por minuto
    limitar(request, "kinect-turno-ip", ip_real(request), 30)
    try:
        sistema.tomar_turno_kinect(datos.cliente, datos.codigo)
    except (ParticipanteBloqueado, CodigoIncorrecto) as ex:
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


@router.get("/api/kinect/codigo", dependencies=[Depends(verificar_admin)])
def ver_codigo(sistema=Depends(obtener_sistema)):
    """El código para tomar el turno: solo el proyector lo recibe (con el token), nunca por el WebSocket."""
    turno = sistema.senas.turno
    return Response(json.dumps({"activo": turno.con_codigo, "codigo": turno.codigo,
                                "version": turno.version_codigo}), media_type="application/json", headers=SIN_CACHE)


@router.post("/api/kinect/codigo", dependencies=[Depends(verificar_admin)])
def regenerar_codigo(sistema=Depends(obtener_sistema)):
    if not sistema.senas.turno.con_codigo:
        raise HTTPException(409, "El código está desactivado (PGC_KINECT_CODIGO=false).")
    codigo = sistema.regenerar_codigo_kinect()
    return Response(json.dumps({"activo": True, "codigo": codigo, "version": sistema.senas.turno.version_codigo}),
                    media_type="application/json", headers=SIN_CACHE)


@router.post("/api/kinect/eco")
def eco(datos: Eco, request: Request, sistema=Depends(obtener_sistema)):
    """El presentador (PC con token) o el celular que tiene el turno del Kinect."""
    presentador = es_admin(request, request.app.state.token_admin)
    if not presentador and datos.cliente:
        limitar(request, "kinect", datos.cliente, sistema.cfg.lim_kinect_cliente)
    try:
        sistema.fijar_eco(datos.activo, datos.cliente, presentador=presentador)
    except (SinPermisoKinect, ParticipanteBloqueado) as ex:
        raise HTTPException(403, str(ex))
    return {"eco": sistema.eco}


@router.get("/api/kinect/diagnostico", dependencies=[Depends(verificar_admin)])
def diagnostico(sistema=Depends(obtener_sistema)):
    """Por qué una letra se confirma o no, en vivo. Solo en el PC (como la cámara)."""
    datos = sistema.senas.diagnostico()
    if datos is None:
        raise HTTPException(503, "El detector no da diagnóstico (¿Kinect no conectado, o el detector original "
                                 "con PGC_KINECT_DETECTOR_PARALELO=false?).")
    return Response(json.dumps(datos, ensure_ascii=False), media_type="application/json", headers=SIN_CACHE)


@router.post("/api/kinect/protocolo/iniciar", dependencies=[Depends(verificar_admin)])
def iniciar_protocolo(datos: Protocolo, sistema=Depends(obtener_sistema)):
    diag = sistema.senas.diagnostico() or {}
    del_modelo = [c for c in diag.get("categorias", []) if c != "sin_letra"]
    letras = [l for l in (datos.letras or "").replace(",", " ").split() if l] or del_modelo
    fuera = [l for l in letras if del_modelo and l not in del_modelo]
    if not letras or fuera:
        raise HTTPException(400, f"Letras que el modelo no tiene: {', '.join(fuera)}" if fuera else
                                 "No hay letras para probar (¿Kinect no conectado?).")
    try:
        sistema.protocolo.iniciar(letras, datos.repeticiones, datos.tiempo_max)
    except RuntimeError as ex:
        raise HTTPException(409, str(ex))
    return sistema.protocolo.estado()


@router.post("/api/kinect/protocolo/detener", dependencies=[Depends(verificar_admin)])
def detener_protocolo(sistema=Depends(obtener_sistema)):
    sistema.protocolo.detener()
    return {"ok": True}


@router.get("/api/kinect/protocolo", dependencies=[Depends(verificar_admin)])
def estado_protocolo(sistema=Depends(obtener_sistema)):
    return Response(json.dumps(sistema.protocolo.estado(), ensure_ascii=False), media_type="application/json",
                    headers=SIN_CACHE)


@router.get("/api/kinect/imagen", dependencies=[Depends(verificar_admin)])
def imagen(despues: int | None = Query(default=None, ge=0), sistema=Depends(obtener_sistema)):
    """La cámara con los puntos de la mano: solo en el PC del proyector, nunca por el túnel ni la red.

    ?despues=N: responde apenas haya un cuadro más nuevo que N (o tras 1 s con el último).
    """
    foto = sistema.senas.imagen_con_estado(despues, 1.0 if despues is not None else 0.0)
    if not foto:
        raise HTTPException(503, "No llegan imágenes del Kinect.")
    # El estado del MISMO momento que la imagen, para que el proyector los muestre juntos
    cabeceras = {**SIN_CACHE, "X-Kinect-Texto": quote(foto.get("texto") or ""),
                 "X-Kinect-Detalle": quote(foto.get("detalle") or "")}
    for clave, nombre in (("cuadro", "X-Kinect-Cuadro"), ("edad_ms", "X-Kinect-Edad-Ms"),
                          ("desfase_ms", "X-Kinect-Desfase-Ms")):
        if foto.get(clave) is not None:
            cabeceras[nombre] = str(foto[clave])
    return Response(foto["jpeg"], media_type="image/jpeg", headers=cabeceras)

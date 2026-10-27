"""Páginas (celular y proyector), logo, QR y estado."""
import io
from pathlib import Path

import qrcode
from fastapi import APIRouter, Depends, Request
from fastapi.responses import FileResponse, HTMLResponse, Response

from pgc.api.dependencias import SIN_CACHE, obtener_sistema
from pgc.api.seguridad import es_local, preparar_pagina

CARPETA_WEB = Path(__file__).resolve().parent.parent.parent.parent / "web"

router = APIRouter()


def pagina(nombre, request, con_token=False):
    token = request.app.state.token_admin if con_token and es_local(request) else None
    html, csp = preparar_pagina(CARPETA_WEB / nombre, request, token)
    return HTMLResponse(html, headers={**SIN_CACHE, "Content-Security-Policy": csp})


@router.get("/")
def pagina_movil(request: Request):
    return pagina("movil.html", request)


@router.get("/pantalla")
def pagina_pantalla(request: Request):
    # Solo el navegador del PC recibe el token: por el túnel o la red local se ve sin controles
    return pagina("pantalla.html", request, con_token=True)


@router.get("/diagnostico")
def pagina_diagnostico(request: Request):
    # Vista de diagnóstico del Kinect: solo el navegador del PC recibe el token (por el túnel no funciona)
    return pagina("diagnostico.html", request, con_token=True)


@router.get("/logo-udec.png")
def logo():
    return FileResponse(CARPETA_WEB / "logo-udec.png")


@router.get("/qr.png")
def qr(sistema=Depends(obtener_sistema)):
    img = qrcode.make(sistema.url_publica, border=2, box_size=12)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(buf.getvalue(), media_type="image/png", headers=SIN_CACHE)


@router.get("/api/estado")
def estado(sistema=Depends(obtener_sistema)):
    return sistema.instantanea()

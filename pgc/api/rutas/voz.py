"""Voz → texto: el celular sube un audio y recibe la transcripción para revisarla."""
import os
import re
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool

from pgc.api.dependencias import obtener_sistema
from pgc.api.esquemas import PATRON_CLIENTE
from pgc.api.seguridad import MSG_AUDIO_LARGO, ip_real, limitar, parece_audio, tipo_permitido
from pgc.dominio.participante import MSG_BLOQUEADO

CARPETA_AUDIOS = Path(tempfile.gettempdir()) / "pgc_voz"     # temporales: se borran siempre

router = APIRouter()


def limpiar_audios_viejos():
    """Borra temporales que hayan quedado de una caída del servidor."""
    for ruta in CARPETA_AUDIOS.glob("voz_*"):
        try:
            ruta.unlink()
        except OSError:
            pass


@router.post("/api/transcribir")
async def transcribir(request: Request, audio: UploadFile = File(...), cliente: str | None = Form(None),
                      sistema=Depends(obtener_sistema)):
    cfg, estado = sistema.cfg, request.app.state
    limitar(request, "transcribir", ip_real(request), cfg.lim_transcribir_ip)
    if cliente and re.fullmatch(PATRON_CLIENTE, cliente):
        limitar(request, "transcribir-cliente", cliente, cfg.lim_transcribir_cliente)
        if sistema.esta_bloqueado(cliente):
            raise HTTPException(403, MSG_BLOQUEADO)
    if not sistema.voz.listo:
        raise HTTPException(503, "El reconocimiento de voz se está cargando, intenta en unos segundos.")
    if estado.voz_en_curso > cfg.voz_max_en_espera:                  # 1 transcribiendo + N esperando
        raise HTTPException(429, "Hay varias personas usando la voz, intenta en unos segundos.",
                            headers={"Retry-After": "5"})
    estado.voz_en_curso += 1
    try:
        return await _transcribir(audio, sistema)
    finally:
        estado.voz_en_curso -= 1


async def _transcribir(audio, sistema):
    cfg = sistema.cfg
    datos = await audio.read()                    # acotado: el middleware ya limitó el cuerpo
    if not datos:
        raise HTTPException(400, "No llegó audio.")
    if len(datos) > cfg.audio_max_bytes:
        raise HTTPException(413, MSG_AUDIO_LARGO)
    if not tipo_permitido(audio.content_type) or not parece_audio(datos[:16]):
        raise HTTPException(415, "Ese archivo no parece un audio. Graba de nuevo con el botón.")
    sufijo = Path(audio.filename or "").suffix.lower()
    sufijo = sufijo if re.fullmatch(r"\.[a-z0-9]{1,5}", sufijo) else ".webm"
    CARPETA_AUDIOS.mkdir(parents=True, exist_ok=True)
    fd, ruta = tempfile.mkstemp(suffix=sufijo, prefix="voz_", dir=CARPETA_AUDIOS)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(datos)
        segundos = await run_in_threadpool(sistema.voz.duracion, ruta)
        if segundos and segundos > cfg.audio_max_segundos:
            raise HTTPException(413, MSG_AUDIO_LARGO)
        texto = await run_in_threadpool(sistema.voz.transcribir, ruta)
    except HTTPException:
        raise
    except Exception as ex:
        sistema.log(f"[voz] Error transcribiendo: {type(ex).__name__}")
        raise HTTPException(500, "No se pudo entender el audio. Intenta de nuevo o escríbelo.")
    finally:
        try:
            os.remove(ruta)                       # el audio nunca se guarda
        except OSError:
            pass
    return {"texto": texto[:cfg.max_caracteres]}

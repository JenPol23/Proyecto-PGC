"""Seguridad de la capa web (ver docs/ARQUITECTURA.md §B).

- es_local / ip_real: distinguir el PC del proyector de los celulares y del túnel.
- Token de administrador por arranque (M1).
- Límite de peticiones por IP real y por cliente (M5).
- Páginas con nonce para la CSP y encabezados de seguridad (M7).
- Tamaño máximo del cuerpo antes de leerlo (M3, M4).
"""
import math
import re
import secrets
import threading
import time
from pathlib import Path

from fastapi import HTTPException
from starlette.requests import HTTPConnection
from starlette.responses import JSONResponse

ENCABEZADOS_PROXY = ("cf-connecting-ip", "cf-ray", "cf-visitor", "cdn-loop", "x-forwarded-for", "forwarded", "x-real-ip")
IPS_LOCALES = {"127.0.0.1", "::1"}
NOMBRES_LOCALES = {"127.0.0.1", "localhost", "[::1]"}
MSG_ADMIN = "Solo desde el PC del proyector."
MSG_RAPIDO = "Vas muy rápido, espera unos segundos."
MSG_AUDIO_LARGO = "El audio es muy largo. Graba máximo 10 segundos."
MSG_CUERPO_LARGO = "El mensaje es muy largo."
ENCABEZADOS = {
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "x-frame-options": "DENY",
    "permissions-policy": "microphone=(self), camera=(), geolocation=()",
    "cross-origin-opener-policy": "same-origin",
}
CSP_POR_DEFECTO = "default-src 'none'; frame-ancestors 'none'"


# ----------------------------------------------------------------- origen
def _nombre_host(host):
    host = (host or "").strip().lower()
    if host.startswith("["):
        return host.split("]")[0] + "]"
    return host.split(":")[0]


def es_local(conn: HTTPConnection):
    """Petición del propio PC: IP local, sin pasar por un proxy (cloudflared) y con Host local.

    cloudflared se conecta desde 127.0.0.1, por eso no basta con la IP. Exigir un
    Host local frena además el 'DNS rebinding' (un dominio ajeno que resuelve a 127.0.0.1).
    """
    if not conn.client or conn.client.host not in IPS_LOCALES:
        return False
    if any(h in conn.headers for h in ENCABEZADOS_PROXY):
        return False
    return _nombre_host(conn.headers.get("host")) in NOMBRES_LOCALES


def ip_real(conn: HTTPConnection):
    """IP del celular. CF-Connecting-IP solo se cree si la conexión viene de cloudflared (127.0.0.1)."""
    host = conn.client.host if conn.client else "desconocida"
    if host in IPS_LOCALES and "cf-connecting-ip" in conn.headers:
        return conn.headers["cf-connecting-ip"][:64]
    return host


# ----------------------------------------------------------------- administrador
def nuevo_token():
    return secrets.token_urlsafe(32)


def es_admin(conn: HTTPConnection, token, permitir_parametro=False):
    """PC del proyector + token correcto (encabezado X-PGC-Admin; ?token= solo si se permite)."""
    if not es_local(conn):
        return False
    recibido = conn.headers.get("x-pgc-admin", "")
    if not recibido and permitir_parametro:
        recibido = conn.query_params.get("token", "")
    return bool(recibido) and secrets.compare_digest(recibido, token)


def verificar_admin(conn: HTTPConnection):
    if not es_admin(conn, conn.app.state.token_admin):
        raise HTTPException(403, MSG_ADMIN)


# ----------------------------------------------------------------- límite de peticiones
class Limitador:
    """Cubeta de fichas en memoria: `por_minuto` peticiones, que se recargan de forma continua."""

    def __init__(self, reloj=time.monotonic):
        self._reloj = reloj
        self._cubetas = {}
        self._lock = threading.Lock()

    def esperar(self, clave, por_minuto):
        """0 si se permite (y consume una ficha); si no, segundos que faltan."""
        ahora = self._reloj()
        ritmo = por_minuto / 60.0
        with self._lock:
            fichas, antes = self._cubetas.get(clave, (float(por_minuto), ahora))
            fichas = min(float(por_minuto), fichas + (ahora - antes) * ritmo)
            if fichas >= 1:
                self._cubetas[clave] = (fichas - 1, ahora)
                return 0.0
            self._cubetas[clave] = (fichas, ahora)
            if len(self._cubetas) > 5000:          # no crecer sin límite con IPs de paso
                viejas = [k for k, (_, t) in self._cubetas.items() if ahora - t > 120]
                for k in viejas:
                    del self._cubetas[k]
            return (1 - fichas) / ritmo


def limitar(conn: HTTPConnection, nombre, clave, por_minuto):
    """Lanza 429 si `clave` superó `por_minuto`. El PC del proyector no tiene límite."""
    if es_local(conn):
        return
    espera = conn.app.state.limitador.esperar(f"{nombre}:{clave}", por_minuto)
    if espera:
        raise HTTPException(429, MSG_RAPIDO, headers={"Retry-After": str(max(1, math.ceil(espera)))})


# ----------------------------------------------------------------- páginas y CSP
_HOST_SEGURO = re.compile(r"^[A-Za-z0-9.\-:\[\]]{1,255}$")


def csp_pagina(nonce, host):
    host = host if _HOST_SEGURO.match(host or "") else ""
    conectar = f"'self' ws://{host} wss://{host}" if host else "'self'"
    return ("default-src 'none'; "
            f"script-src 'nonce-{nonce}'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            f"connect-src {conectar}; "
            "media-src 'self' blob:; "
            "base-uri 'none'; form-action 'self'; frame-ancestors 'none'")


def preparar_pagina(ruta: Path, conn: HTTPConnection, token=None):
    """HTML con nonce en cada <script> y, si corresponde, el token de administrador."""
    nonce = secrets.token_urlsafe(16)
    html = ruta.read_text(encoding="utf-8").replace("<script>", f'<script nonce="{nonce}">')
    if token:
        html = html.replace('<meta name="pgc-admin" content="">', f'<meta name="pgc-admin" content="{token}">')
    return html, csp_pagina(nonce, conn.headers.get("host", ""))


# ----------------------------------------------------------------- audio
TIPOS_AUDIO = ("audio/", "video/webm", "video/mp4", "video/3gpp", "application/octet-stream", "")


def tipo_permitido(content_type):
    tipo = (content_type or "").split(";")[0].strip().lower()
    return any(tipo.startswith(t) for t in TIPOS_AUDIO if t) or tipo == ""


def parece_audio(cabecera: bytes):
    """Firma de los formatos que graban los celulares (webm, mp4/m4a/3gp, ogg, wav, mp3, aac, amr, flac)."""
    c = cabecera
    return (c.startswith(b"\x1a\x45\xdf\xa3")                       # EBML: webm / mkv
            or c[4:8] == b"ftyp"                                    # mp4, m4a, 3gp
            or c.startswith(b"OggS")
            or (c.startswith(b"RIFF") and c[8:12] == b"WAVE")
            or c.startswith(b"ID3")                                 # mp3 con etiquetas
            or (len(c) > 1 and c[0] == 0xFF and (c[1] & 0xE0) == 0xE0)   # trama MPEG / AAC ADTS
            or c.startswith(b"#!AMR")
            or c.startswith(b"fLaC"))


# ----------------------------------------------------------------- middleware
class MiddlewareSeguridad:
    """ASGI: límite general por IP, tamaño máximo del cuerpo y encabezados de seguridad."""

    def __init__(self, app, cfg, limitador):
        self.app = app
        self.cfg = cfg
        self.limitador = limitador
        self.max_json = cfg.json_max_kb * 1024
        self.max_audio = cfg.audio_max_bytes + 64 * 1024      # margen del formulario multipart

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        async def enviar(evento):
            if evento["type"] == "http.response.start":
                encabezados = list(evento.get("headers", []))
                presentes = {k.decode().lower() for k, _ in encabezados}
                for k, v in ENCABEZADOS.items():
                    if k not in presentes:
                        encabezados.append((k.encode(), v.encode()))
                if "content-security-policy" not in presentes:
                    encabezados.append((b"content-security-policy", CSP_POR_DEFECTO.encode()))
                evento = {**evento, "headers": encabezados}
            await send(evento)

        conn = HTTPConnection(scope)
        if not es_local(conn):
            espera = self.limitador.esperar(f"general:{ip_real(conn)}", self.cfg.lim_general_ip)
            if espera:
                return await self._responder(scope, receive, enviar, 429, MSG_RAPIDO,
                                             {"Retry-After": str(max(1, math.ceil(espera)))})
        es_audio = scope["path"] == "/api/transcribir"
        limite = self.max_audio if es_audio else self.max_json
        mensaje = MSG_AUDIO_LARGO if es_audio else MSG_CUERPO_LARGO
        largo = conn.headers.get("content-length")
        if largo and largo.isdigit() and int(largo) > limite:
            return await self._responder(scope, receive, enviar, 413, mensaje)

        recibido = 0

        async def recibir():
            nonlocal recibido
            evento = await receive()
            if evento["type"] == "http.request":
                recibido += len(evento.get("body", b""))
                if recibido > limite:                              # sin Content-Length o mintiendo
                    # HTTPException: FastAPI la deja pasar aunque ocurra al leer el cuerpo
                    raise HTTPException(413, mensaje)
            return evento

        await self.app(scope, recibir, enviar)

    @staticmethod
    async def _responder(scope, receive, send, codigo, detalle, encabezados=None):
        respuesta = JSONResponse({"detail": detalle}, status_code=codigo, headers=encabezados)
        await respuesta(scope, receive, send)

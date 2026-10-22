"""Aplicación FastAPI: ciclo de vida, seguridad, errores amables y rutas."""
import asyncio
import webbrowser
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from pgc.api.rutas import admin, mensajes, paginas, participantes, voz, ws
from pgc.api.seguridad import Limitador, MiddlewareSeguridad, es_admin, nuevo_token

TRADUCCIONES = {
    "Not Found": "No encontramos esa página.",
    "Method Not Allowed": "Esa acción no está permitida.",
}
CSP_DOCS = ("default-src 'none'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' data: https://fastapi.tiangolo.com; "
            "connect-src 'self'; frame-ancestors 'none'")


def mensaje_validacion(errores, cfg):
    """422 amable y en español según el campo que falló."""
    for e in errores:
        campo = e.get("loc", ("",))[-1]
        if campo == "texto":
            if "caracteres de control" in str(e.get("msg", "")):
                return "El mensaje tiene caracteres que no se pueden mostrar."
            return "Escribe tu mensaje de nuevo, por favor."
        if campo == "cliente":
            return "Recarga la página e intenta de nuevo."
        if campo == "nombre":
            return "Usa solo letras en tu nombre (máximo 20)."
        if campo == "audio":
            return "No llegó audio."
    return "No pudimos leer lo que enviaste. Recarga la página e intenta de nuevo."


def crear_app(sistema, abrir_navegador=webbrowser.open):
    cfg, log = sistema.cfg, sistema.log

    @asynccontextmanager
    async def ciclo_de_vida(app):
        sistema.loop = asyncio.get_running_loop()
        voz.limpiar_audios_viejos()
        sistema.iniciar_trabajador()
        if cfg.voz:
            sistema.voz.cargar_en_segundo_plano()
        else:
            sistema.voz.estado = "desactivado"
        if cfg.tunel:
            sistema.tunel.iniciar()
        sistema.senas.iniciar()
        log(f"[web] Pantalla del proyector: http://127.0.0.1:{cfg.puerto_web}/pantalla")
        log(f"[web] Celulares en la misma red: {sistema.url_local}")
        if cfg.dev:
            log(f"[web] Modo desarrollo: documentación en http://127.0.0.1:{cfg.puerto_web}/docs")
        if cfg.abrir_navegador:
            abrir_navegador(f"http://127.0.0.1:{cfg.puerto_web}/pantalla")
        yield
        sistema.senas.detener()
        sistema.tunel.detener()

    # La documentación automática se sirve con rutas propias (solo --dev o con el token)
    app = FastAPI(lifespan=ciclo_de_vida, docs_url=None, redoc_url=None, openapi_url=None)
    app.state.sistema = sistema
    app.state.token_admin = nuevo_token()       # solo en memoria; lo recibe /pantalla en el PC
    app.state.limitador = Limitador()
    app.state.voz_en_curso = 0
    app.state.ws_total = 0
    app.state.ws_por_ip = {}
    app.add_middleware(MiddlewareSeguridad, cfg=cfg, limitador=app.state.limitador)

    @app.exception_handler(RequestValidationError)
    async def validacion(request, exc):
        return JSONResponse({"detail": mensaje_validacion(exc.errors(), cfg)}, status_code=422)

    @app.exception_handler(StarletteHTTPException)
    async def http(request, exc):
        detalle = TRADUCCIONES.get(exc.detail, exc.detail)
        return JSONResponse({"detail": detalle}, status_code=exc.status_code, headers=exc.headers)

    def documentacion_permitida(request):
        return cfg.dev or es_admin(request, app.state.token_admin, permitir_parametro=True)

    @app.get("/openapi.json", include_in_schema=False)
    def openapi(request: Request):
        if not documentacion_permitida(request):
            raise StarletteHTTPException(404)
        return JSONResponse(app.openapi())

    @app.get("/docs", include_in_schema=False)
    def docs(request: Request):
        if not documentacion_permitida(request):
            raise StarletteHTTPException(404)
        token = request.query_params.get("token")
        url = "/openapi.json" + (f"?token={token}" if token and not cfg.dev else "")
        respuesta = get_swagger_ui_html(openapi_url=url, title="Mano bidireccional LSC · API")
        respuesta.headers["Content-Security-Policy"] = CSP_DOCS
        return respuesta

    for modulo in (paginas, mensajes, voz, participantes, admin, ws):
        app.include_router(modulo.router)
    return app

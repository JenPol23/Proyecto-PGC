import hashlib
import secrets
import time
from urllib.parse import urlsplit

from fastapi import (
    Depends,
    HTTPException,
    Request,
    Response,
)
from pydantic import BaseModel, Field

from pgc.api.seguridad import (
    es_admin,
    verificar_admin,
    ip_real,
)


COOKIE = "pgc_control_kinect"
DURACION = 2 * 60 * 60


class CodigoAcceso(BaseModel):
    codigo: str = Field(
        min_length=8,
        max_length=8,
        pattern=r"^[0-9]{8}$",
    )


class AccesoControl:
    def __init__(self):
        self.codigo = str(
            secrets.randbelow(90000000) + 10000000
        )

        self.sesiones = {}
        self.intentos = {}
        self.globales = []
        self.reloj = time.monotonic

    def local(self, request):
        return es_admin(
            request,
            request.app.state.token_admin,
        )

    def permitido(self, request):
        if self.local(request):
            return True

        ahora = self.reloj()

        self.sesiones = {
            clave: vencimiento
            for clave, vencimiento
            in self.sesiones.items()
            if vencimiento > ahora
        }

        token = request.cookies.get(COOKIE, "")

        if not token or len(token) > 128:
            return False

        clave = hashlib.sha256(
            token.encode()
        ).hexdigest()

        return clave in self.sesiones

    def origen(self, request):
        origen = request.headers.get("origin")

        if origen:
            try:
                url = urlsplit(origen)

                valido = (
                    url.scheme in {"http", "https"}
                    and url.netloc.lower()
                    == request.headers.get(
                        "host", ""
                    ).lower()
                )
            except ValueError:
                valido = False

            if not valido:
                raise HTTPException(
                    403,
                    "Abre los controles desde "
                    "la página del proyecto.",
                )

    async def verificar(self, request: Request):
        self.origen(request)

        if not self.permitido(request):
            raise HTTPException(
                403,
                "Introduce el código del PC "
                "para controlar el deletreo.",
            )

    def limitar(self, request):
        ahora = self.reloj()

        self.intentos = {
            ip: [
                instante
                for instante in intentos
                if ahora - instante < 60
            ]
            for ip, intentos in self.intentos.items()
            if intentos
            and ahora - intentos[-1] < 60
        }

        self.globales = [
            instante
            for instante in self.globales
            if ahora - instante < 60
        ]

        ip = ip_real(request)
        intentos = self.intentos.get(ip, [])

        if (
            len(intentos) >= 5
            or len(self.globales) >= 60
        ):
            raise HTTPException(
                429,
                "Demasiados intentos. "
                "Espera un minuto.",
                headers={"Retry-After": "60"},
            )

        intentos.append(ahora)
        self.intentos[ip] = intentos
        self.globales.append(ahora)


def registrar_acceso(app):
    acceso = AccesoControl()
    app.state.acceso_deletreo = acceso

    @app.get("/api/deletreo/permiso")
    async def permiso(
        request: Request,
        response: Response,
    ):
        response.headers["Cache-Control"] = "no-store"

        return {
            "controlador": acceso.permitido(request),
            "local": acceso.local(request),
        }

    @app.get(
        "/api/deletreo/codigo",
        dependencies=[Depends(verificar_admin)],
    )
    async def codigo(response: Response):
        response.headers["Cache-Control"] = "no-store"

        return {"codigo": acceso.codigo}

    @app.post(
        "/api/deletreo/renovar",
        dependencies=[Depends(verificar_admin)],
    )
    async def renovar(
        request: Request,
        response: Response,
    ):
        acceso.origen(request)

        acceso.codigo = str(
            secrets.randbelow(90000000) + 10000000
        )

        acceso.sesiones.clear()

        response.headers["Cache-Control"] = "no-store"

        return {"codigo": acceso.codigo}

    @app.post("/api/deletreo/acceso")
    async def entrar(
        datos: CodigoAcceso,
        request: Request,
        response: Response,
    ):
        acceso.origen(request)
        acceso.limitar(request)

        if not secrets.compare_digest(
            datos.codigo,
            acceso.codigo,
        ):
            raise HTTPException(
                403,
                "Código incorrecto.",
            )

        ahora = acceso.reloj()

        acceso.sesiones = {
            clave: vencimiento
            for clave, vencimiento
            in acceso.sesiones.items()
            if vencimiento > ahora
        }

        if len(acceso.sesiones) >= 32:
            primera = next(iter(acceso.sesiones))
            del acceso.sesiones[primera]

        token = secrets.token_urlsafe(32)

        clave = hashlib.sha256(
            token.encode()
        ).hexdigest()

        acceso.sesiones[clave] = ahora + DURACION

        response.set_cookie(
            COOKIE,
            token,
            max_age=DURACION,
            httponly=True,
            secure=request.url.scheme == "https",
            samesite="strict",
            path="/api/deletreo",
        )

        response.headers["Cache-Control"] = "no-store"

        return {"controlador": True}

    @app.post("/api/deletreo/salir")
    async def salir(
        request: Request,
        response: Response,
    ):
        acceso.origen(request)

        token = request.cookies.get(COOKIE, "")

        clave = hashlib.sha256(
            token.encode()
        ).hexdigest()

        acceso.sesiones.pop(clave, None)

        response.delete_cookie(
            COOKIE,
            path="/api/deletreo",
            secure=request.url.scheme == "https",
            httponly=True,
            samesite="strict",
        )

        response.headers["Cache-Control"] = "no-store"

        return {"controlador": False}

    return acceso.verificar
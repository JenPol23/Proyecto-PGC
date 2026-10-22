"""Estado en vivo por WebSocket (pantalla del proyector y celulares)."""
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from pgc.api.seguridad import es_local, ip_real

router = APIRouter()


def origen_permitido(ws: WebSocket, sistema):
    """Solo páginas servidas por este mismo servidor (evita que otro sitio se conecte)."""
    origen = ws.headers.get("origin")
    if origen is None:                     # clientes que no son navegadores (scripts de prueba)
        return True
    host = ws.headers.get("host", "")
    puerto = sistema.cfg.puerto_web
    permitidos = {sistema.tunel.url, sistema.url_local, f"http://127.0.0.1:{puerto}", f"http://localhost:{puerto}",
                  f"http://{host}", f"https://{host}"}
    return origen.rstrip("/") in permitidos


@router.websocket("/ws")
async def ws_estado(ws: WebSocket):
    sistema, estado = ws.app.state.sistema, ws.app.state
    cfg = sistema.cfg
    if not origen_permitido(ws, sistema):
        await ws.close(code=1008)          # política: origen no permitido
        return
    ip = ip_real(ws)
    if not es_local(ws) and (estado.ws_total >= cfg.ws_max_conexiones
                             or estado.ws_por_ip.get(ip, 0) >= cfg.ws_max_por_ip):
        await ws.close(code=1013)          # vuelva a intentar más tarde
        return
    estado.ws_total += 1
    estado.ws_por_ip[ip] = estado.ws_por_ip.get(ip, 0) + 1
    try:
        await ws.accept()
        q = sistema.publicador.suscribir()
        try:
            await ws.send_json(sistema.instantanea())
            while True:
                try:
                    datos = await asyncio.wait_for(q.get(), timeout=cfg.ping_ws)
                except asyncio.TimeoutError:
                    datos = {"tipo": "ping"}     # mantiene vivo el túnel y detecta cierres
                await ws.send_json(datos)
        except (WebSocketDisconnect, RuntimeError, ConnectionError):
            pass
        finally:
            sistema.publicador.desuscribir(q)
    finally:
        estado.ws_total -= 1
        estado.ws_por_ip[ip] -= 1
        if not estado.ws_por_ip[ip]:
            del estado.ws_por_ip[ip]

"""
Deletreo y lectura de texto juntos en Kinect.
La pestaña Voz conserva su función original.
No modifica los archivos originales del proyecto.
"""

import asyncio
from pathlib import Path
import secrets
from typing import Literal

import httpx

from fastapi import Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from acceso_kinect import registrar_acceso
from pgc.api import app as modulo_app
from pgc.api.seguridad import (
    csp_pagina,
    es_local,
    verificar_admin,
)
from pgc.arranque import main


HTML_PANELES = '''
<section id="tab-kinect" class="panel oculto">
  <h2>De tus manos al texto</h2>

  <p class="nota">
    Mantén la letra hasta verla escrita.
    Retira la mano entre letras.
  </p>

  <img id="imagenKinect"
       alt="Imagen del Kinect con puntos de la mano"
       hidden
       style="width:100%;border-radius:16px;margin-top:12px">

  <p id="estadoCamara" class="nota">
    Esperando imagen del Kinect.
  </p>

  <textarea id="textoKinect"
            rows="4"
            readonly
            aria-label="Texto deletreado"
            placeholder="Tus letras aparecerán aquí"></textarea>

  <p id="estadoKinect"
     class="nota"
     role="status">
    Conectando...
  </p>
    <div id="panelAccesoKinect">
    <p id="modoControlKinect"
       class="nota"
       role="status">
      Modo espectador.
    </p>

    <form id="formAccesoKinect">
      <label for="codigoControlKinect">
        Código del PC
      </label>

      <input id="codigoControlKinect"
             type="password"
             inputmode="numeric"
             pattern="[0-9]{8}"
             minlength="8"
             maxlength="8"
             autocomplete="off"
             required>

      <button class="btn" type="submit">
        Activar control
      </button>
    </form>

    <div id="controlLocalKinect" hidden>
      <button class="btn"
              id="verCodigoKinect"
              type="button">
        Ver código para teléfono
      </button>

      <button class="btn"
              id="renovarCodigoKinect"
              type="button">
        Revocar teléfonos y cambiar código
      </button>

      <p id="codigoVisibleKinect"
         class="nota"></p>
    </div>

    <button class="btn"
            id="salirControlKinect"
            type="button"
            hidden>
      Volver a espectador
    </button>
  </div>
  <div class="acciones-deletreo">
    <button class="btn" data-deletreo="start">
      Iniciar
    </button>

    <button class="btn" data-deletreo="stop">
      Detener
    </button>

    <button class="btn" data-deletreo="space">
      Espacio
    </button>

    <button class="btn" data-deletreo="backspace">
      Borrar
    </button>

    <button class="btn" data-deletreo="clear">
      Limpiar
    </button>

    <button class="btn" id="guardarDeletreo">
      Guardar TXT
    </button>
  </div>

  <div class="acciones-deletreo">
    <button id="leerFrase"
            class="btn"
            disabled>
      Leer frase
    </button>

    <button id="detenerVoz" class="btn">
      Detener voz
    </button>
  </div>

  <p id="estadoVozKinect"
     class="nota"
     role="status"></p>

  <p class="nota">
    Usa los controles desde el PC del Kinect.
  </p>
</section>
'''


JS_DELETREO = '''
  // ---------- deletreo y lectura dentro de Kinect

  const tokenDeletreo = document.querySelector(
    'meta[name="pgc-admin"]'
  ).content;
  let puedeControlar = !!tokenDeletreo;
  let controlLocal = !!tokenDeletreo;
  let fraseActual = "";
  let ocupadoDeletreo = false;
  let consultandoDeletreo = false;
  let imagenPendiente = false;
  let imagenURL = null;

  const botonesDeletreo = [
    ...document.querySelectorAll("[data-deletreo]")
  ];

  const tieneVoz = "speechSynthesis" in window;

  if (tieneVoz) speechSynthesis.getVoices();

  function actualizarVozKinect() {
    $("#leerFrase").disabled =
      !tieneVoz || !fraseActual.trim();

    $("#detenerVoz").disabled = !tieneVoz;

    $("#guardarDeletreo").disabled =
      !fraseActual.trim();
  }

  function mostrarDeletreo(datos) {
    fraseActual = datos.texto;
    $("#textoKinect").value = fraseActual;
    $("#estadoKinect").textContent = datos.detalle;

    actualizarVozKinect();
  }

  async function peticionDeletreo(
    ruta,
    opciones = {}
  ) {
    const controlador = new AbortController();

    const limite = setTimeout(
      () => controlador.abort(),
      10000
    );

    try {
      const r = await fetch(
        "/api/deletreo/" + ruta,
        {
          ...opciones,
          signal: controlador.signal,
          headers: {
            "X-PGC-Admin": tokenDeletreo,
            ...(opciones.headers || {})
          }
        }
      );

      if (!r.ok) {
        const datos = await r.json().catch(
          () => ({})
        );

        throw new Error(
          typeof datos.detail === "string"
            ? datos.detail
            : "No se pudo completar la operación."
        );
      }

      return r;
    } finally {
      clearTimeout(limite);
    }
  }

  async function consultarDeletreo() {
    if (
      consultandoDeletreo ||
      ocupadoDeletreo ||
      document.hidden
    ) return;

    consultandoDeletreo = true;

    try {
      const r = await peticionDeletreo("estado");
      mostrarDeletreo(await r.json());
    } catch (e) {
      $("#estadoKinect").textContent = e.message;
    } finally {
      consultandoDeletreo = false;
    }
  }

  botonesDeletreo.forEach((b) => {
    b.disabled = !puedeControlar;

    b.addEventListener("click", async () => {
      if (ocupadoDeletreo || !puedeControlar) return;

      ocupadoDeletreo = true;

      botonesDeletreo.forEach(
        (boton) => boton.disabled = true
      );

      try {
        const r = await peticionDeletreo(
          "control",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              accion: b.dataset.deletreo
            })
          }
        );

        mostrarDeletreo(await r.json());
      } catch (e) {
        $("#estadoKinect").textContent = e.message;
      } finally {
        ocupadoDeletreo = false;

        botonesDeletreo.forEach(
          (boton) => boton.disabled = !puedeControlar
        );
      }
    });
  });

  if (!tokenDeletreo) {
    $("#estadoKinect").textContent =
      "Abre http://127.0.0.1:8000/ " +
      "en el PC conectado al Kinect.";
  }

  async function actualizarImagen() {
    if (
      imagenPendiente ||
      document.hidden ||
      $("#tab-kinect").classList.contains("oculto")
    ) return;

    imagenPendiente = true;

    try {
      const r = await peticionDeletreo("imagen");
      const blob = await r.blob();

      const anterior = imagenURL;
      imagenURL = URL.createObjectURL(blob);

      $("#imagenKinect").src = imagenURL;
      $("#imagenKinect").hidden = false;

      if (anterior) {
        URL.revokeObjectURL(anterior);
      }

      $("#estadoCamara").textContent =
        "Cámara conectada.";
    } catch (e) {
      $("#imagenKinect").hidden = true;
      $("#estadoCamara").textContent = e.message;
    } finally {
      imagenPendiente = false;
    }
  }

  $("#leerFrase").addEventListener("click", () => {
    if (!tieneVoz || !fraseActual.trim()) return;

    const voz = speechSynthesis.getVoices().find(
      v => v.lang.toLowerCase().startsWith("es")
    );

    if (!voz) {
      $("#estadoVozKinect").textContent =
        "No hay una voz en español disponible. " +
        "Revisa las voces de Windows o vuelve a " +
        "intentarlo cuando carguen.";
      return;
    }

    speechSynthesis.cancel();

    const lectura =
      new SpeechSynthesisUtterance(fraseActual);

    lectura.voice = voz;
    lectura.lang = voz.lang;

    lectura.onstart = () => {
      $("#estadoVozKinect").textContent =
        "Leyendo...";
    };

    lectura.onend = () => {
      $("#estadoVozKinect").textContent =
        "Lectura terminada.";
    };

    lectura.onerror = () => {
      $("#estadoVozKinect").textContent =
        "Lectura detenida o audio no disponible.";
    };

    speechSynthesis.speak(lectura);
  });

  $("#detenerVoz").addEventListener("click", () => {
    if (tieneVoz) speechSynthesis.cancel();

    $("#estadoVozKinect").textContent =
      "Lectura detenida.";
  });

  $("#guardarDeletreo").addEventListener(
    "click",
    () => {
      const url = URL.createObjectURL(
        new Blob(
          [fraseActual],
          {type: "text/plain;charset=utf-8"}
        )
      );

      const enlace = document.createElement("a");

      enlace.href = url;
      enlace.download = "texto_lsc.txt";

      document.body.appendChild(enlace);
      enlace.click();
      enlace.remove();

      setTimeout(
        () => URL.revokeObjectURL(url),
        1000
      );
    }
  );

  window.addEventListener("pagehide", () => {
    if (tieneVoz) speechSynthesis.cancel();

    if (imagenURL) {
      URL.revokeObjectURL(imagenURL);
    }
  });
    function pintarAccesoKinect() {
    botonesDeletreo.forEach(
      b => b.disabled =
        ocupadoDeletreo || !puedeControlar
    );

    $("#formAccesoKinect").hidden =
      controlLocal || puedeControlar;

    $("#controlLocalKinect").hidden =
      !controlLocal;

    $("#salirControlKinect").hidden =
      controlLocal || !puedeControlar;

    $("#modoControlKinect").textContent =
      controlLocal
        ? "Control del PC activo."
        : puedeControlar
          ? "Control del teléfono activo (hasta 2 horas)."
          : "Modo espectador. Introduce el código del PC para controlar.";
  }

  async function consultarPermisoKinect() {
    if (document.hidden) return;

    try {
      const respuesta = await peticionDeletreo(
        "permiso"
      );

      const datos = await respuesta.json();

      puedeControlar = datos.controlador;
      controlLocal = datos.local;
    } catch (e) {
      puedeControlar = false;
      controlLocal = false;
    }

    pintarAccesoKinect();
  }

  $("#formAccesoKinect").addEventListener(
    "submit",
    async e => {
      e.preventDefault();

      const boton = e.currentTarget.querySelector(
        "button"
      );

      boton.disabled = true;

      try {
        await peticionDeletreo(
          "acceso",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({
              codigo: $("#codigoControlKinect")
                .value.trim()
            })
          }
        );

        $("#codigoControlKinect").value = "";

        await consultarPermisoKinect();
      } catch (error) {
        $("#modoControlKinect").textContent =
          error.message;
      } finally {
        boton.disabled = false;
      }
    }
  );

  $("#verCodigoKinect").addEventListener(
    "click",
    async () => {
      try {
        const respuesta = await peticionDeletreo(
          "codigo"
        );

        const datos = await respuesta.json();

        $("#codigoVisibleKinect").textContent =
          "Código para autorizar el teléfono: " +
          datos.codigo;
      } catch (e) {
        $("#codigoVisibleKinect").textContent =
          e.message;
      }
    }
  );

  $("#renovarCodigoKinect").addEventListener(
    "click",
    async () => {
      try {
        const respuesta = await peticionDeletreo(
          "renovar",
          {method: "POST"}
        );

        const datos = await respuesta.json();

        $("#codigoVisibleKinect").textContent =
          "Accesos anteriores revocados. Nuevo código: " +
          datos.codigo;
      } catch (e) {
        $("#codigoVisibleKinect").textContent =
          e.message;
      }
    }
  );

  $("#salirControlKinect").addEventListener(
    "click",
    async () => {
      try {
        await peticionDeletreo(
          "salir",
          {method: "POST"}
        );

        await consultarPermisoKinect();
      } catch (e) {
        $("#modoControlKinect").textContent =
          e.message;
      }
    }
  );

  pintarAccesoKinect();
  consultarPermisoKinect();

  setInterval(consultarPermisoKinect, 10000);

  actualizarVozKinect();
  consultarDeletreo();

  setInterval(
    consultarDeletreo,
    tokenDeletreo ? 700 : 1000
  );

  setInterval(
    actualizarImagen,
    tokenDeletreo ? 200 : 400
  );

'''


def construir_html():
    ruta = (
        Path(__file__).resolve().parent
        / "web"
        / "movil.html"
    )

    html = ruta.read_text(encoding="utf-8")

    # Reemplazar únicamente el apartado Kinect.
    # La sección original de Voz permanece intacta.
    inicio = html.index(
        "<!-- ======================= KINECT"
    )

    fin = html.index(
        "<!-- ===================== MIS MENSAJES",
        inicio,
    )

    html = (
        html[:inicio]
        + HTML_PANELES
        + html[fin:]
    )

    # Conservar el JavaScript original de Voz.
    # Insertar el código de Kinect antes de Mis mensajes.
    posicion = html.index(
        "  // ---------- mis mensajes"
    )

    html = (
        html[:posicion]
        + JS_DELETREO
        + html[posicion:]
    )

    if '<meta name="pgc-admin"' not in html:
        html = html.replace(
            "</head>",
            '<meta name="pgc-admin" content="">\n'
            "</head>",
        )

    return html.replace(
        "</style>",
        """
        .acciones-deletreo {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
          margin-top: 12px;
        }

        .acciones-deletreo .btn {
          width: auto;
          flex: 1;
          min-width: 100px;
          margin: 0;
        }

        #textoKinect {
          width: 100%;
          font-size: 24px;
          margin-top: 12px;
        }
        </style>
        """,
        1,
    )


class Control(BaseModel):
    accion: Literal[
        "start",
        "stop",
        "space",
        "backspace",
        "clear",
    ]


crear_original = modulo_app.crear_app


def crear_integrada(sistema, *args, **kwargs):
    app = crear_original(
        sistema,
        *args,
        **kwargs,
    )

    verificar_control = registrar_acceso(app)

    html_base = construir_html()
    lock = asyncio.Lock()

    async def solicitar(ruta, metodo="GET"):
        try:
            async with httpx.AsyncClient(
                trust_env=False,
                timeout=2.5,
            ) as cliente:
                respuesta = await cliente.request(
                    metodo,
                    "http://127.0.0.1:8765" + ruta,
                )

        except httpx.RequestError:
            raise HTTPException(
                503,
                "Sin detector. Inicia server_web_svm.py "
                "y abre la aplicación C#.",
            ) from None

        if respuesta.status_code != 200:
            raise HTTPException(
                503,
                "El detector respondió: "
                + respuesta.text[:400],
            )

        return respuesta

    async def leer_estado():
        respuesta = await solicitar(
            "/spell/status"
        )

        mensaje = respuesta.text.replace(
            "\r\n",
            "\n",
        )

        texto, separador, detalle = (
            mensaje.partition("\nEstado:")
        )

        if (
            not texto.startswith("Texto: ")
            or not separador
        ):
            raise HTTPException(
                502,
                "Estado del detector no válido.",
            )

        texto = texto[len("Texto: "):]

        return {
            "texto": "" if texto == "—" else texto,
            "detalle": detalle.strip(),
        }

    @app.get("/", response_class=HTMLResponse)
    async def pagina(request: Request):
        nonce = secrets.token_urlsafe(16)

        token = (
            app.state.token_admin
            if es_local(request)
            else ""
        )

        html = html_base.replace(
            '<meta name="pgc-admin" content="">',
            f'<meta name="pgc-admin" content="{token}">',
        )

        html = html.replace(
            "<script>",
            f'<script nonce="{nonce}">',
        )

        return HTMLResponse(
            html,
            headers={
                "Cache-Control": "no-store",
                "Content-Security-Policy": csp_pagina(
                    nonce,
                    request.headers.get("host", ""),
                ),
            },
        )

    # Priorizar esta página frente a la original.
    app.router.routes.insert(
        0,
        app.router.routes.pop(),
    )

    @app.get("/api/deletreo/estado")
    async def estado(response: Response):
        response.headers["Cache-Control"] = "no-store"

        async with lock:
            return await leer_estado()

    @app.post(
        "/api/deletreo/control",
        dependencies=[Depends(verificar_control)],
    )
    async def control(datos: Control):
        async with lock:
            await solicitar(
                "/spell/" + datos.accion,
                "POST",
            )

            return await leer_estado()

    @app.get("/api/deletreo/imagen")

    async def imagen():
        respuesta = await solicitar(
            "/preview.jpg"
        )

        tipo = respuesta.headers.get(
            "content-type",
            "",
        )

        if not tipo.startswith("image/jpeg"):
            raise HTTPException(
                502,
                "Imagen no válida.",
            )

        return Response(
            respuesta.content,
            media_type="image/jpeg",
            headers={
                "Cache-Control": "no-store"
            },
        )

    return app


if __name__ == "__main__":
    modulo_app.crear_app = crear_integrada
    raise SystemExit(main())
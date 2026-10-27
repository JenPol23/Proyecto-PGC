"""Protocolo de prueba de letras: pide cada letra N veces y registra qué reconoce el detector y en cuánto tiempo.

Flujo de cada intento:
  pedir    "Haz la letra A (intento 2 de 5)". Termina cuando el texto del detector crece (letra confirmada:
           acierto o confusión) o cuando pasan `tiempo_max` s (no detectada). El tiempo se cuenta desde
           la primera imagen con mano, para no medir lo que tarda la persona en reaccionar.
  retirar  "Retira la mano". Hasta que no haya mano y su lógica esté lista para otra letra (o 3 s);
           entonces se limpia el texto del detector y empieza el siguiente intento.
Cada muestra del diagnóstico (~10/s) se guarda para el análisis (pgc/dominio/experimento.py).

ProtocoloLetras es pura (recibe muestras y la hora): se prueba con una línea de tiempo inventada.
ServicioProtocolo la alimenta desde un hilo y guarda los resultados al terminar.
"""
import threading
import time
from collections import Counter


class ProtocoloLetras:
    def __init__(self, letras, repeticiones=5, tiempo_max=8.0, espera_retirar=3.0):
        self.plan = [(letra, k) for letra in letras for k in range(1, repeticiones + 1)]
        self.repeticiones = repeticiones
        self.tiempo_max = tiempo_max
        self.espera_retirar = espera_retirar
        self.i = 0
        self.fase = "listo"                 # listo | pedir | retirar | terminado | detenido
        self.intentos = []                  # resultados (ver pgc/dominio/experimento.py)
        self.muestras = []                  # todas las muestras del diagnóstico, con el intento al que pertenecen
        self._actual = []                   # muestras del intento en curso
        self._t_diag = None                 # hora (del detector) de la última imagen vista
        self._t_corte = None                # imágenes procesadas hasta aquí son de antes de limpiar

    @property
    def total(self):
        return len(self.plan)

    @property
    def pedida(self):
        return self.plan[self.i] if self.i < len(self.plan) else (None, None)

    def iniciar(self, ahora):
        self._abrir(ahora, texto="")
        return ["iniciar", "limpiar"]

    def detener(self):
        if self.fase not in ("terminado",):
            self.fase = "detenido"

    def _abrir(self, ahora, texto):
        # El diagnóstico se actualiza con cada IMAGEN: hasta que llegue una nueva, puede seguir mostrando
        # el texto de antes de limpiar. Esas muestras no cuentan para decidir si se confirmó una letra.
        self._t_corte = self._t_diag
        self.fase = "pedir"
        self._t0 = ahora
        self._t_mano = None
        self._texto0 = texto
        self._actual = []

    def muestra(self, d, ahora):
        """Procesa una muestra del diagnóstico. Devuelve las órdenes para el detector (p. ej. ["limpiar"])."""
        if self.fase not in ("pedir", "retirar") or d is None:
            return []
        letra, k = self.pedida
        fila = {"t": round(ahora, 3), "fase": self.fase, "letra": letra, "intento": k,
                "manos": d.get("manos"), "prediccion": d.get("prediccion"), "segunda": d.get("segunda"),
                "margen": d.get("margen"), "estable_s": d.get("estable_s"), "confirmaciones": d.get("confirmaciones"),
                "motivo": d.get("motivo"), "texto": d.get("texto")}
        self.muestras.append(fila)
        texto = (d.get("texto") or "")
        vieja = self._t_corte is not None and (d.get("t") or 0) <= self._t_corte
        self._t_diag = d.get("t", self._t_diag)
        if self.fase == "pedir":
            self._actual.append(fila)
            if (d.get("manos") or 0) >= 1 and self._t_mano is None:
                self._t_mano = ahora
            nuevo = "" if vieja else (texto[len(self._texto0):].strip() if texto.startswith(self._texto0)
                                      else texto.strip())
            if nuevo:                                            # su lógica confirmó una letra
                self._cerrar(nuevo[-1].lower(), ahora)
            elif ahora - self._t0 >= self.tiempo_max:
                self._cerrar(None, ahora)
            return []
        # retirar: sin mano y su lógica lista para otra letra (armado), o tiempo agotado
        if ((d.get("manos") == 0 and d.get("armado")) or ahora - self._t_retirar >= self.espera_retirar):
            self.i += 1
            if self.i >= len(self.plan):
                self.fase = "terminado"
                return ["limpiar"]
            self._abrir(ahora, texto="")
            return ["limpiar"]
        return []

    def _cerrar(self, reconocida, ahora):
        letra, k = self.pedida
        con_mano = [m for m in self._actual if (m["manos"] or 0) == 1]
        preds = [m["prediccion"] for m in con_mano if m["prediccion"]]
        cambios = sum(1 for a, b in zip(preds, preds[1:]) if a != b)
        margenes = [m["margen"] for m in con_mano if m["margen"] is not None]
        motivos = Counter(m["motivo"] for m in self._actual if m["motivo"])
        n = len(self._actual) or 1
        self.intentos.append({
            "letra": letra, "intento": k, "reconocida": reconocida,
            "tiempo_s": round(ahora - (self._t_mano if self._t_mano is not None else self._t0), 2)
            if reconocida else None,
            "mano_pct": round(100 * len(con_mano) / n, 1),
            "prediccion_frecuente": Counter(preds).most_common(1)[0][0] if preds else None,
            "margen_medio": round(sum(margenes) / len(margenes), 3) if margenes else None,
            "estable_max_s": max((m["estable_s"] or 0 for m in self._actual), default=0.0),
            "cambios": cambios,
            "sin_letra_pct": round(100 * preds.count("sin_letra") / len(preds), 1) if preds else 0.0,
            "motivo_frecuente": motivos.most_common(1)[0][0] if motivos else None,
        })
        self.fase = "retirar"
        self._t_retirar = ahora

    def estado(self):
        letra, k = self.pedida
        return {"fase": self.fase, "letra": letra, "intento": k, "repeticiones": self.repeticiones,
                "hecho": len(self.intentos), "total": self.total, "ultimos": self.intentos[-8:][::-1]}


class ServicioProtocolo:
    """Corre el protocolo en un hilo (~10 muestras/s) y guarda los resultados al terminar."""

    def __init__(self, senas, guardar=None, log=print, al_cambiar=None, reloj=time.monotonic, periodo=0.1):
        self.senas = senas
        self.guardar = guardar               # (protocolo, info) -> carpeta; lo pone arranque.py
        self.log = log
        self.al_cambiar = al_cambiar or (lambda: None)
        self._reloj = reloj
        self.periodo = periodo
        self.protocolo = None
        self.carpeta = None
        self.error = None
        self.informe = None
        self._hilo = None

    @property
    def corriendo(self):
        return bool(self.protocolo and self.protocolo.fase in ("pedir", "retirar"))

    def iniciar(self, letras, repeticiones=5, tiempo_max=8.0):
        if self.corriendo:
            raise RuntimeError("Ya hay un protocolo en curso.")
        if self.senas.diagnostico() is None:
            raise RuntimeError("El detector no da diagnóstico (¿Kinect no conectado o detector original?).")
        self.protocolo = ProtocoloLetras(letras, repeticiones, tiempo_max)
        self.carpeta = self.error = self.informe = None
        for orden in self.protocolo.iniciar(self._reloj()):
            self.senas.controlar(orden)
        self.log(f"[kinect] Protocolo de letras: {len(letras)} letras × {repeticiones}")
        self._hilo = threading.Thread(target=self._bucle, daemon=True, name="protocolo")
        self._hilo.start()
        self.al_cambiar()

    def detener(self):
        if self.protocolo:
            self.protocolo.detener()

    def _bucle(self):
        p = self.protocolo
        while p.fase in ("pedir", "retirar"):
            try:
                for orden in p.muestra(self.senas.diagnostico(), self._reloj()):
                    self.senas.controlar(orden)
            except Exception as ex:                         # nunca dejar morir el hilo sin avisar
                self.error = f"{type(ex).__name__}: {ex}"
                p.detener()
                break
            time.sleep(self.periodo)
        if p.intentos and self.guardar:
            try:
                self.carpeta, self.informe = self.guardar(p, {"detenido": p.fase == "detenido"})
                self.log(f"[kinect] Protocolo guardado en {self.carpeta}")
            except Exception as ex:
                self.error = f"No se pudieron guardar los resultados: {type(ex).__name__}: {ex}"
        self.al_cambiar()

    def estado(self):
        if not self.protocolo:
            return {"fase": "sin_iniciar"}
        return {**self.protocolo.estado(), "carpeta": self.carpeta, "error": self.error, "informe": self.informe}

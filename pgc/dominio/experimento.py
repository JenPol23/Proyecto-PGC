"""Análisis del protocolo de letras: tabla por letra, matriz de confusión y causa probable de cada fallo.

Funciones puras (sin archivos ni gráficas): las usan el guardado de experimentos y las pruebas.

Un intento es un dict con: letra (pedida), intento (1..n), reconocida (letra o None), tiempo_s (o None),
mano_pct (0–100: imágenes con una mano), prediccion_frecuente, margen_medio, estable_max_s,
cambios (veces que cambió la predicción), sin_letra_pct, motivo_frecuente.
"""
from collections import Counter

NINGUNA = "(ninguna)"
TIEMPO_CONFIRMACION = 0.7            # el de su detector (server_deletreo_svm.py); solo para explicar causas


def resultado_de(intento):
    if intento["reconocida"] is None:
        return "no_detectada"
    return "acierto" if intento["reconocida"] == intento["letra"] else "confusion"


def resumen_por_letra(intentos):
    """[{letra, intentos, aciertos, confusiones {letra: n}, no_detectadas, exactitud_pct, tiempo_medio_s}]"""
    por_letra = {}
    for it in intentos:
        por_letra.setdefault(it["letra"], []).append(it)
    filas = []
    for letra, lista in por_letra.items():
        aciertos = [it for it in lista if resultado_de(it) == "acierto"]
        confusiones = Counter(it["reconocida"] for it in lista if resultado_de(it) == "confusion")
        tiempos = [it["tiempo_s"] for it in aciertos if it["tiempo_s"] is not None]
        filas.append({
            "letra": letra, "intentos": len(lista), "aciertos": len(aciertos),
            "confusiones": dict(confusiones.most_common()),
            "no_detectadas": sum(1 for it in lista if resultado_de(it) == "no_detectada"),
            "exactitud_pct": round(100 * len(aciertos) / len(lista), 1),
            "tiempo_medio_s": round(sum(tiempos) / len(tiempos), 2) if tiempos else None,
        })
    return filas


def matriz_confusion(intentos, letras=None):
    """(filas = letra pedida, columnas = letras reconocidas + "(ninguna)", matriz de conteos)."""
    pedidas = letras or sorted({it["letra"] for it in intentos})
    columnas = sorted(set(pedidas) | {it["reconocida"] for it in intentos if it["reconocida"]}) + [NINGUNA]
    matriz = [[0] * len(columnas) for _ in pedidas]
    for it in intentos:
        if it["letra"] in pedidas:
            matriz[pedidas.index(it["letra"])][columnas.index(it["reconocida"] or NINGUNA)] += 1
    return pedidas, columnas, matriz


def causa_probable(letra, intentos):
    """La explicación más probable de por qué la letra falla (o None si no falla), con lo que lo sugiere."""
    lista = [it for it in intentos if it["letra"] == letra]
    fallos = [it for it in lista if resultado_de(it) != "acierto"]
    if not fallos:
        return None
    media = lambda clave: sum(it.get(clave) or 0 for it in fallos) / len(fallos)
    confundida = Counter(it["reconocida"] for it in fallos if it["reconocida"])
    predicha = Counter(it["prediccion_frecuente"] for it in fallos if it.get("prediccion_frecuente"))
    if media("mano_pct") < 50:
        return ("mano", f"La mano casi no se detecta ({media('mano_pct'):.0f}% de las imágenes): "
                        "distancia, luz o la mano fuera de cuadro")
    if predicha and predicha.most_common(1)[0][0] == "sin_letra" or media("sin_letra_pct") >= 50:
        return ("sin_letra", "El modelo la ve como «sin letra»: el ángulo o la forma difieren de los ejemplos "
                             "con que se entrenó (faltan ejemplos de esa letra en esas condiciones)")
    if confundida:
        otra, n = confundida.most_common(1)[0]
        return ("parecida", f"Se confunde con {otra.upper()} ({n} de {len(lista)}): letras parecidas en los "
                            "puntos de la mano, o el ángulo hace que se vean iguales")
    if predicha and predicha.most_common(1)[0][0] not in (letra, "sin_letra"):
        otra = predicha.most_common(1)[0][0]
        return ("parecida", f"El modelo la ve casi siempre como {otra.upper()} pero sin llegar a confirmarla")
    if media("cambios") >= 3:
        return ("inestable", f"La predicción cambia mucho ({media('cambios'):.0f} veces por intento): "
                             "la mano se mueve, o está justo entre dos letras")
    if media("estable_max_s") < TIEMPO_CONFIRMACION:
        return ("tiempo", f"Se reconoce pero no se mantiene {TIEMPO_CONFIRMACION} s seguidos "
                          f"(máximo {media('estable_max_s'):.2f} s): tiempo de confirmación")
    if media("margen_medio") < 0.3:
        return ("margen", "El modelo duda (margen bajo entre la primera y la segunda letra)")
    return ("otra", "Sin una causa clara en los datos: repetirla con más cuidado y mirar la vista de diagnóstico")


def informe(intentos, letras=None):
    """Resumen para mostrar y guardar: exactitud total, por letra y causas de los fallos."""
    filas = resumen_por_letra(intentos)
    total = len(intentos)
    aciertos = sum(f["aciertos"] for f in filas)
    tiempos = [it["tiempo_s"] for it in intentos if resultado_de(it) == "acierto" and it["tiempo_s"] is not None]
    causas = {}
    for f in filas:
        c = causa_probable(f["letra"], intentos)
        if c:
            causas[f["letra"]] = {"tipo": c[0], "texto": c[1]}
    return {
        "intentos": total, "aciertos": aciertos,
        "exactitud_pct": round(100 * aciertos / total, 1) if total else 0.0,
        "tiempo_medio_s": round(sum(tiempos) / len(tiempos), 2) if tiempos else None,
        "por_letra": filas, "causas": causas,
        "fallan": [f["letra"] for f in sorted(filas, key=lambda f: f["exactitud_pct"]) if f["aciertos"] < f["intentos"]],
    }

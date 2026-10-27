"""Guarda un protocolo de letras en experimentos/<fecha_hora>/: CSV, gráficas e informe (para el informe final).

    intentos.csv            un renglón por intento (letra pedida, reconocida, tiempo, % con mano, ...)
    muestras.csv            todas las muestras del diagnóstico (~10/s)
    resumen_por_letra.csv   aciertos, confusiones, no detectadas y tiempo medio por letra
    matriz_confusion.csv / .png
    aciertos_por_letra.png  aciertos, confusiones y no detectadas por letra
    tiempos_por_letra.png   tiempo hasta confirmar (solo aciertos)
    informe.md              exactitud, letras que fallan y causa probable de cada una

Los CSV usan ";" y coma decimal (Excel en español los abre bien) y UTF-8 con BOM.
"""
import csv
import time
from pathlib import Path

from pgc.dominio import experimento as ex

RAIZ = Path(__file__).resolve().parents[2]
CARPETA = RAIZ / "experimentos"


def _num(v):
    return str(v).replace(".", ",") if isinstance(v, float) else ("" if v is None else v)


def _csv(ruta, filas, columnas):
    with open(ruta, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(columnas)
        for fila in filas:
            w.writerow([_num(fila.get(c)) for c in columnas])


def guardar(protocolo, info=None, carpeta_base=None):
    """Devuelve (carpeta relativa al proyecto, informe)."""
    carpeta = Path(carpeta_base or CARPETA) / time.strftime("%Y-%m-%d_%H%M%S")
    carpeta.mkdir(parents=True, exist_ok=True)
    intentos = protocolo.intentos
    letras = list(dict.fromkeys(letra for letra, _ in protocolo.plan))
    resumen = ex.informe(intentos, letras)

    _csv(carpeta / "intentos.csv", [{**it, "resultado": ex.resultado_de(it)} for it in intentos],
         ["letra", "intento", "resultado", "reconocida", "tiempo_s", "mano_pct", "prediccion_frecuente",
          "margen_medio", "estable_max_s", "cambios", "sin_letra_pct", "motivo_frecuente"])
    _csv(carpeta / "muestras.csv", protocolo.muestras,
         ["t", "fase", "letra", "intento", "manos", "prediccion", "segunda", "margen", "estable_s",
          "confirmaciones", "motivo", "texto"])
    _csv(carpeta / "resumen_por_letra.csv",
         [{**f, "confusiones": ", ".join(f"{k.upper()}×{v}" for k, v in f["confusiones"].items()),
           "causa_probable": resumen["causas"].get(f["letra"], {}).get("texto", "")} for f in resumen["por_letra"]],
         ["letra", "intentos", "aciertos", "exactitud_pct", "confusiones", "no_detectadas", "tiempo_medio_s",
          "causa_probable"])
    filas, columnas, matriz = ex.matriz_confusion(intentos, [l for l in letras if any(i["letra"] == l for i in intentos)])
    with open(carpeta / "matriz_confusion.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["pedida \\ reconocida"] + [c.upper() for c in columnas])
        for letra, fila in zip(filas, matriz):
            w.writerow([letra.upper()] + fila)
    _graficas(carpeta, resumen, filas, columnas, matriz, intentos)
    _informe(carpeta, resumen, protocolo, info or {})
    return str(carpeta.relative_to(RAIZ)) if RAIZ in carpeta.parents else str(carpeta), resumen


def _graficas(carpeta, resumen, filas, columnas, matriz, intentos):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Matriz de confusión
    fig, eje = plt.subplots(figsize=(max(6, len(columnas) * 0.45), max(5, len(filas) * 0.4)))
    imagen = eje.imshow(matriz, cmap="Greens")
    eje.set_xticks(range(len(columnas)), [c.upper() if c != ex.NINGUNA else "ninguna" for c in columnas], rotation=90)
    eje.set_yticks(range(len(filas)), [f.upper() for f in filas])
    eje.set_xlabel("Reconocida")
    eje.set_ylabel("Pedida")
    eje.set_title("Matriz de confusión del protocolo de letras")
    for i, fila in enumerate(matriz):
        for j, v in enumerate(fila):
            if v:
                eje.text(j, i, v, ha="center", va="center", fontsize=8,
                         color="white" if v > max(map(max, matriz)) / 2 else "black")
    fig.colorbar(imagen, ax=eje, fraction=0.03)
    fig.tight_layout()
    fig.savefig(carpeta / "matriz_confusion.png", dpi=150)
    plt.close(fig)

    # Aciertos, confusiones y no detectadas por letra
    por = resumen["por_letra"]
    nombres = [f["letra"].upper() for f in por]
    aciertos = [f["aciertos"] for f in por]
    confus = [sum(f["confusiones"].values()) for f in por]
    nodet = [f["no_detectadas"] for f in por]
    fig, eje = plt.subplots(figsize=(max(6, len(por) * 0.4), 4))
    eje.bar(nombres, aciertos, color="#1A7A55", label="Acierto")
    eje.bar(nombres, confus, bottom=aciertos, color="#A86A00", label="Confundida")
    eje.bar(nombres, nodet, bottom=[a + c for a, c in zip(aciertos, confus)], color="#9AA3A0", label="No detectada")
    eje.set_ylabel("Intentos")
    eje.set_title(f"Resultado por letra (exactitud total {resumen['exactitud_pct']} %)")
    eje.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    fig.savefig(carpeta / "aciertos_por_letra.png", dpi=150)
    plt.close(fig)

    # Tiempo hasta confirmar (aciertos)
    datos = {f["letra"]: [it["tiempo_s"] for it in intentos if it["letra"] == f["letra"]
                          and ex.resultado_de(it) == "acierto" and it["tiempo_s"] is not None] for f in por}
    con_datos = [(l.upper(), v) for l, v in datos.items() if v]
    if con_datos:
        fig, eje = plt.subplots(figsize=(max(6, len(con_datos) * 0.4), 4))
        eje.boxplot([v for _, v in con_datos], tick_labels=[l for l, _ in con_datos])
        eje.axhline(ex.TIEMPO_CONFIRMACION, color="#C2362B", linestyle="--", linewidth=1,
                    label=f"Mínimo de su lógica ({ex.TIEMPO_CONFIRMACION} s)")
        eje.set_ylabel("Segundos desde que aparece la mano")
        eje.set_title("Tiempo hasta confirmar la letra")
        eje.legend(fontsize=8)
        fig.tight_layout()
        fig.savefig(carpeta / "tiempos_por_letra.png", dpi=150)
        plt.close(fig)


def _informe(carpeta, resumen, protocolo, info):
    lineas = [
        "# Protocolo de letras: resultados",
        "",
        f"- Fecha: {time.strftime('%d/%m/%Y %H:%M')}",
        f"- Letras: {len({l for l, _ in protocolo.plan})} · repeticiones: {protocolo.repeticiones} · "
        f"tiempo máximo por intento: {protocolo.tiempo_max} s" + (" · **detenido antes de terminar**" if info.get("detenido") else ""),
        f"- Intentos: {resumen['intentos']} · aciertos: {resumen['aciertos']} · **exactitud {resumen['exactitud_pct']} %**"
        + (f" · tiempo medio hasta confirmar: {resumen['tiempo_medio_s']} s" if resumen["tiempo_medio_s"] else ""),
        "",
        "## Por letra",
        "",
        "| Letra | Aciertos | Confusiones | No detectadas | Tiempo medio (s) | Causa probable de los fallos |",
        "|---|---|---|---|---|---|",
    ]
    for f in resumen["por_letra"]:
        conf = ", ".join(f"{k.upper()}×{v}" for k, v in f["confusiones"].items()) or "—"
        causa = resumen["causas"].get(f["letra"], {}).get("texto", "—")
        tiempo = f["tiempo_medio_s"] if f["tiempo_medio_s"] is not None else "—"
        lineas.append(f"| {f['letra'].upper()} | {f['aciertos']}/{f['intentos']} | {conf} | {f['no_detectadas']} | "
                      f"{tiempo} | {causa} |")
    lineas += ["", "Archivos: intentos.csv, muestras.csv, resumen_por_letra.csv, matriz_confusion.csv/.png, "
               "aciertos_por_letra.png, tiempos_por_letra.png.", ""]
    (carpeta / "informe.md").write_text("\n".join(lineas), encoding="utf-8")

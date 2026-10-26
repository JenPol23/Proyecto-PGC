from collections import Counter
from pathlib import Path
import csv
import json

import joblib
import numpy as np

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt

from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


BASE = Path(__file__).resolve().parent
DATASET = BASE / "dataset_alfabeto"
MODELO = BASE / "modelo_estaticas.joblib"

CATEGORIAS = (
    "a", "e", "i", "o", "u",
    "b", "c", "l","r","s",
    "d", "f", "v", "h","y",
    "m", "n", "p","t","w",
    "sin_letra","g","q",
    "j","k","x","z"
)

VERSION_CARACTERISTICAS = 1

# 63 coordenadas + 15 ángulos + 10 distancias
# + 1 indicador de presencia.
DIMENSION = 89


def caracteristicas(manos):
    if not manos:
        return np.zeros(DIMENSION, dtype=np.float64)

    if len(manos) != 1:
        return None

    puntos = np.array([
        [p["x"], p["y"], p["z"]]
        for p in manos[0]
    ], dtype=np.float64)

    if puntos.shape != (21, 3):
        return None

    if not np.isfinite(puntos).all():
        return None

    # Trasladar la muñeca al origen.
    puntos = puntos - puntos[0]

    # Normalizar respecto al tamaño de la palma.
    escala = np.linalg.norm(puntos[9])

    if escala < 0.01:
        return None

    puntos = puntos / escala

    # Menor peso a la profundidad relativa.
    puntos[:, 2] *= 0.5

    valores = puntos.reshape(-1).tolist()

    dedos = (
        (0, 1, 2, 3, 4),
        (0, 5, 6, 7, 8),
        (0, 9, 10, 11, 12),
        (0, 13, 14, 15, 16),
        (0, 17, 18, 19, 20),
    )

    for dedo in dedos:
        for posicion in (1, 2, 3):
            anterior = puntos[dedo[posicion - 1]]
            centro = puntos[dedo[posicion]]
            siguiente = puntos[dedo[posicion + 1]]

            vector_a = anterior - centro
            vector_b = siguiente - centro

            denominador = (
                np.linalg.norm(vector_a)
                * np.linalg.norm(vector_b)
            )

            coseno = (
                np.dot(vector_a, vector_b) / denominador
                if denominador > 1e-8
                else 0.0
            )

            valores.append(
                float(np.clip(coseno, -1.0, 1.0))
            )

    puntas = (4, 8, 12, 16, 20)

    for i in range(len(puntas)):
        for j in range(i + 1, len(puntas)):
            valores.append(float(np.linalg.norm(
                puntos[puntas[i]] - puntos[puntas[j]]
            )))

    valores.append(1.0)

    return np.asarray(valores, dtype=np.float64)


def leer_ejemplo(archivo, categoria):
    documento = json.loads(
        archivo.read_text(encoding="utf-8")
    )

    vectores = []

    for frame in documento.get("frames", []):
        manos = frame.get("hands", [])

        if categoria != "sin_letra" and not manos:
            continue

        vector = caracteristicas(manos)

        if vector is not None:
            vectores.append(vector)

    if len(vectores) < 5:
        raise ValueError(
            f"{archivo}: menos de 5 fotogramas utilizables. "
            "Revisa esa grabación."
        )

    # Cada grabación aporta 12 muestras.
    indices = np.linspace(
        0, len(vectores) - 1, 12
    ).round().astype(int)

    return np.stack([
        vectores[indice]
        for indice in indices
    ])


def generar_graficas(matriz):
    carpeta = BASE / "graficas"
    carpeta.mkdir(parents=True, exist_ok=True)

    nombres = [
        "Sin letra" if c == "sin_letra" else c.upper()
        for c in CATEGORIAS
    ]

    # Gráfica 1: matriz de confusión.
    tamano = max(9, len(nombres) * 0.55)

    figura, eje = plt.subplots(
        figsize=(tamano, tamano)
    )

    visualizacion = ConfusionMatrixDisplay(
        confusion_matrix=matriz,
        display_labels=nombres,
    )

    visualizacion.plot(
        ax=eje,
        cmap="Blues",
        values_format="d",
        xticks_rotation=45,
        colorbar=False,
    )

    eje.set_title(
        "SVM: evaluación en grabaciones reservadas"
    )
    eje.set_xlabel("Categoría predicha")
    eje.set_ylabel("Categoría real")

    figura.tight_layout()

    figura.savefig(
        carpeta / "matriz_confusion.png",
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(figura)

    # Gráfica 2: aciertos por categoría.
    totales = matriz.sum(axis=1)
    correctos = np.diag(matriz)

    porcentajes = np.divide(
        correctos,
        totales,
        out=np.zeros(len(totales), dtype=float),
        where=totales != 0,
    ) * 100

    figura, eje = plt.subplots(
        figsize=(max(10, len(nombres) * 0.6), 6)
    )

    barras = eje.bar(
        nombres,
        porcentajes,
        color="#2878B5",
    )

    eje.set_ylim(0, 115)
    eje.set_ylabel("Aciertos (%)")
    eje.set_xlabel("Categoría")
    eje.set_title(
        "Aciertos por categoría: grabaciones reservadas"
    )

    eje.tick_params(
        axis="x",
        labelrotation=45,
    )

    for barra, porcentaje, aciertos, total in zip(
        barras,
        porcentajes,
        correctos,
        totales,
    ):
        eje.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 1,
            f"{porcentaje:.0f}%\n{aciertos}/{total}",
            ha="center",
            va="bottom",
            fontsize=8,
        )

    figura.tight_layout()

    figura.savefig(
        carpeta / "aciertos_por_letra.png",
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(figura)

    # Exportar conteos con etiquetas de filas y columnas.
    with (carpeta / "matriz_confusion.csv").open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as archivo:
        escritor = csv.writer(archivo)

        escritor.writerow([
            "Real / Predicha",
            *nombres,
        ])

        for nombre, fila in zip(nombres, matriz):
            escritor.writerow([
                nombre,
                *fila.tolist(),
            ])

    print(
        f"\nGráficas guardadas en: {carpeta}"
    )


def entrenar():
    x_entrenamiento = []
    y_entrenamiento = []

    pruebas = []
    archivos_entrenamiento = []
    archivos_prueba = []

    for categoria in CATEGORIAS:
        archivos = sorted(
            (DATASET / categoria).glob("*.json")
        )

        if len(archivos) < 5:
            raise ValueError(
                f"{categoria}: necesitas al menos "
                "5 grabaciones; recomendado: 30."
            )

        cantidad_prueba = max(
            1,
            round(len(archivos) * 0.20),
        )

        entrenamiento = archivos[:-cantidad_prueba]
        evaluacion = archivos[-cantidad_prueba:]

        print(
            f"{categoria.upper()}: "
            f"{len(entrenamiento)} para entrenar, "
            f"{len(evaluacion)} para evaluar."
        )

        for archivo in entrenamiento:
            vectores = leer_ejemplo(
                archivo,
                categoria,
            )

            x_entrenamiento.extend(vectores)

            y_entrenamiento.extend(
                [categoria] * len(vectores)
            )

            archivos_entrenamiento.append(
                archivo.relative_to(DATASET).as_posix()
            )

        for archivo in evaluacion:
            pruebas.append((
                archivo,
                categoria,
                leer_ejemplo(archivo, categoria),
            ))

            archivos_prueba.append(
                archivo.relative_to(DATASET).as_posix()
            )

    modelo = make_pipeline(
        StandardScaler(),
        SVC(
            kernel="rbf",
            C=3.0,
            gamma="scale",
            class_weight="balanced",
        ),
    )

    print("\nEntrenando SVM...")

    modelo.fit(
        np.stack(x_entrenamiento),
        np.asarray(y_entrenamiento),
    )

    reales = []
    predichas = []

    print("\nRESULTADOS POR GRABACIÓN")

    for archivo, real, vectores in pruebas:
        resultados = modelo.predict(vectores)

        prediccion = Counter(
            resultados.tolist()
        ).most_common(1)[0][0]

        reales.append(real)
        predichas.append(prediccion)

        resultado = (
            "ACIERTO"
            if prediccion == real
            else "FALLO"
        )

        print(
            f"{archivo.name} | "
            f"Real: {real.upper()} | "
            f"Predicción: {prediccion.upper()} | "
            f"{resultado}"
        )

    # Este bloque va fuera del bucle anterior.
    print("\nREPORTE")

    print(classification_report(
        reales,
        predichas,
        labels=list(CATEGORIAS),
        target_names=[
            c.upper() for c in CATEGORIAS
        ],
        zero_division=0,
        digits=3,
    ))

    matriz = confusion_matrix(
        reales,
        predichas,
        labels=list(CATEGORIAS),
    )

    generar_graficas(matriz)

    print("\nCONFUSIONES")

    hubo_confusiones = False

    for i, real in enumerate(CATEGORIAS):
        for j, predicha in enumerate(CATEGORIAS):
            if i != j and matriz[i, j]:
                hubo_confusiones = True

                print(
                    f"{real.upper()} → "
                    f"{predicha.upper()}: "
                    f"{matriz[i, j]}"
                )

    if not hubo_confusiones:
        print("Ninguna en esta evaluación.")

    correctos = sum(
        real == predicha
        for real, predicha in zip(
            reales,
            predichas,
        )
    )

    print(
        f"\nTOTAL: {correctos}/{len(reales)} "
        "grabaciones reservadas."
    )

    joblib.dump(
        {
            "modelo": modelo,
            "categorias": list(CATEGORIAS),
            "version_caracteristicas":
                VERSION_CARACTERISTICAS,
            "archivos_entrenamiento":
                archivos_entrenamiento,
            "archivos_prueba": archivos_prueba,
        },
        MODELO,
    )

    print(f"\nModelo guardado en: {MODELO}")

    print(
        "Reinicia el deletreo SVM para cargar "
        "el modelo actualizado."
    )


if __name__ == "__main__":
    try:
        entrenar()
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit(f"Error: {error}")
from pathlib import Path
import argparse

import numpy as np

from probar_senas import (
    extraer_secuencia,
    distancia_dtw,
)


BASE = Path(__file__).resolve().parent

DATASET = BASE / "dataset_alfabeto"
MODELO = BASE / "modelo_alfabeto.npz"

CATEGORIAS = (
    "a", "e", "i", "o", "u",
    "b", "c", "l",
    "d", "f", "v","h",
    "sin_letra",
)

def nombre_visible(etiqueta):
    if etiqueta == "sin_letra":
        return "Sin letra"

    return etiqueta.upper()


def entrenar():
    secuencias = []
    etiquetas = []
    archivos_entrenamiento = []
    archivos_prueba = []

    for categoria in CATEGORIAS:
        carpeta = DATASET / categoria
        archivos = sorted(carpeta.glob("*.json"))

        if len(archivos) < 5:
            raise ValueError(
                f"La categoría '{categoria}' tiene "
                f"{len(archivos)} ejemplos. "
                "Necesita al menos 5; "
                "recomendado: 30."
            )

        # Reservar aproximadamente el 20% de los
        # archivos completos, no imágenes sueltas.
        cantidad_prueba = max(
            1,
            int(round(len(archivos) * 0.20)),
        )

        entrenamiento = archivos[:-cantidad_prueba]
        prueba = archivos[-cantidad_prueba:]

        print(
            f"{nombre_visible(categoria)}: "
            f"{len(entrenamiento)} para entrenar, "
            f"{len(prueba)} para probar."
        )

        for archivo in entrenamiento:
            secuencia = extraer_secuencia(archivo)

            secuencias.append(secuencia)
            etiquetas.append(categoria)

            archivos_entrenamiento.append(
                archivo.relative_to(
                    DATASET
                ).as_posix()
            )

        for archivo in prueba:
            # Validar también los archivos reservados.
            extraer_secuencia(archivo)

            archivos_prueba.append(
                archivo.relative_to(
                    DATASET
                ).as_posix()
            )

    np.savez_compressed(
        MODELO,
        secuencias=np.stack(secuencias),
        etiquetas=np.asarray(etiquetas),
        archivos=np.asarray(
            archivos_entrenamiento
        ),
        pruebas=np.asarray(
            archivos_prueba
        ),
    )

    print(f"\nModelo guardado en: {MODELO}")
    print(
        "Ahora ejecuta la acción 'probar'."
    )


def predecir(consulta, referencias, etiquetas):
    distancias = np.array([
        distancia_dtw(consulta, referencia)
        for referencia in referencias
    ])

    puntuaciones = {}

    for categoria in CATEGORIAS:
        valores = np.sort(
            distancias[etiquetas == categoria]
        )

        if len(valores) == 0:
            raise ValueError(
                f"El modelo no contiene {categoria}."
            )

        # Promedio de los tres ejemplos más cercanos.
        puntuaciones[categoria] = float(
            np.mean(valores[:3])
        )

    prediccion = min(
        puntuaciones,
        key=puntuaciones.get,
    )

    return prediccion


def probar():
    if not MODELO.exists():
        raise ValueError(
            "Primero ejecuta el entrenamiento."
        )

    with np.load(
        MODELO,
        allow_pickle=False,
    ) as modelo:
        referencias = modelo["secuencias"].copy()
        etiquetas = modelo["etiquetas"].copy()
        usados = set(
            modelo["archivos"].tolist()
        )
        reservados = set(
            modelo["pruebas"].tolist()
        )

    pruebas = []

    for categoria in CATEGORIAS:
        carpeta = DATASET / categoria

        for archivo in sorted(
            carpeta.glob("*.json")
        ):
            ruta = archivo.relative_to(
                DATASET
            ).as_posix()

            if ruta not in usados:
                pruebas.append(archivo)

    presentes = {
        archivo.relative_to(DATASET).as_posix()
        for archivo in pruebas
    }

    faltantes = reservados - presentes

    if faltantes:
        raise ValueError(
            "Faltan archivos reservados para la prueba. "
            "No borres ni muevas las grabaciones."
        )

    if not pruebas:
        raise ValueError(
            "No hay ejemplos disponibles para probar."
        )

    totales = {
        categoria: 0
        for categoria in CATEGORIAS
    }

    aciertos = {
        categoria: 0
        for categoria in CATEGORIAS
    }

    confusiones = {}

    for numero, archivo in enumerate(pruebas, 1):
        print(
            f"\nAnalizando {numero}/{len(pruebas)}: "
            f"{archivo.name}",
            flush=True,
        )

        consulta = extraer_secuencia(archivo)

        prediccion = predecir(
            consulta,
            referencias,
            etiquetas,
        )

        real = archivo.parent.name

        totales[real] += 1

        if prediccion == real:
            aciertos[real] += 1
            resultado = "ACIERTO"
        else:
            resultado = "FALLO"
            clave = (real, prediccion)

            confusiones[clave] = (
                confusiones.get(clave, 0) + 1
            )

        print(
            f"Real: {nombre_visible(real)} | "
            f"Predicción: "
            f"{nombre_visible(prediccion)} | "
            f"{resultado}",
            flush=True,
        )

    print("\nRESULTADOS POR CATEGORÍA")

    for categoria in CATEGORIAS:
        total = totales[categoria]
        correctos = aciertos[categoria]

        print(
            f"{nombre_visible(categoria)}: "
            f"{correctos}/{total}"
        )

    total = sum(totales.values())
    correctos = sum(aciertos.values())

    print(
        f"\nTOTAL: {correctos}/{total} "
        "en grabaciones no usadas para entrenar."
    )

    if confusiones:
        print("\nCONFUSIONES")

        for (real, predicha), cantidad in sorted(
            confusiones.items()
        ):
            print(
                f"{nombre_visible(real)} → "
                f"{nombre_visible(predicha)}: "
                f"{cantidad}"
            )

    print(
        "\nEl modelo siempre elige una categoría. "
        "'Sin letra' todavía no garantiza rechazar "
        "cualquier gesto desconocido."
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "accion",
        choices=["entrenar", "probar"],
    )

    argumentos = parser.parse_args()

    try:
        if argumentos.accion == "entrenar":
            entrenar()
        else:
            probar()
    except (ValueError, OSError, KeyError) as error:
        raise SystemExit(f"Error: {error}")


if __name__ == "__main__":
    main()
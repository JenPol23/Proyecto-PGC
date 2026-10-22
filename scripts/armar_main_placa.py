"""Arma firmware/esp32/main.py: el código original del autor + el bloque agregado (Bluetooth).

main.py = original/main_original.py copiado EXACTAMENTE hasta la línea
"# ---------------- BUCLE PRINCIPAL ----------------" (incluida)
        + original/bucle_ble.py (lo único agregado, marcado con INICIO/FIN).

Si cambias el original (pines, valores, letras), vuelve a correr:
    py -3.11 scripts/armar_main_placa.py
"""
from pathlib import Path

ESP = Path(__file__).resolve().parent.parent / "firmware" / "esp32"
MARCA = "# ---------------- BUCLE PRINCIPAL ----------------"


def armar():
    original = (ESP / "original" / "main_original.py").read_text(encoding="utf-8")
    fin_marca = original.index(MARCA) + len(MARCA)
    fin_linea = original.index("\n", fin_marca) + 1
    bloque = (ESP / "original" / "bucle_ble.py").read_text(encoding="utf-8")
    return original[:fin_linea] + bloque


def main():
    texto = armar()
    destino = ESP / "main.py"
    destino.write_text(texto, encoding="utf-8", newline="\n")
    print(f"{destino.relative_to(ESP.parent.parent)}: {texto.count(chr(10))} líneas "
          f"(original hasta la línea {texto[:texto.index(MARCA)].count(chr(10)) + 1})")


if __name__ == "__main__":
    main()

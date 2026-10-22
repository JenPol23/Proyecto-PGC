"""Genera docs/CODIGO_COMPLETO.md: todo el código fuente del proyecto, tal cual, para el informe.

Uso:  py -3.11 scripts/generar_codigo_completo.py
"""
import time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
CARPETAS = ["pgc", "web", "firmware/esp32", "tests", "scripts"]
RAICES = ["servidor.py", "iniciar.bat", ".env.example", "requirements.txt", "requirements-dev.txt",
          "requirements-gpu.txt", "pytest.ini", ".gitignore", "datos/letras.json", "datos/palabras_bloqueadas.txt"]
EXCLUIR = {"referencia_doby"}                   # código de otro proyecto
LENGUAJE = {".py": "python", ".html": "html", ".json": "json", ".md": "markdown", ".bat": "bat", ".ini": "ini",
            ".txt": "text", ".example": "ini"}


def archivos():
    vistos = [RAIZ / r for r in RAICES]
    for carpeta in CARPETAS:
        for ruta in sorted((RAIZ / carpeta).rglob("*")):
            if ruta.is_file() and ruta.suffix in LENGUAJE and "__pycache__" not in ruta.parts \
                    and not EXCLUIR & set(ruta.parts) and ruta.name not in ("config_wifi.py", "config_ble.py"):
                vistos.append(ruta)
    return [r for r in vistos if r.exists()]


def main():
    lista = archivos()
    partes = [f"# Código completo del proyecto\n\nGenerado el {time.strftime('%d/%m/%Y %H:%M')} con "
              "`scripts/generar_codigo_completo.py`, a partir de los archivos actuales (no se edita a mano). "
              "No incluye el firmware de Doby (otro proyecto) ni secretos (`.env`, `config_ble.py`).\n\n## Índice\n"]
    partes += [f"- `{r.relative_to(RAIZ).as_posix()}`" for r in lista]
    total = 0
    for ruta in lista:
        texto = ruta.read_text(encoding="utf-8").rstrip("\n")
        total += texto.count("\n") + 1
        cerca = "````" if "```" in texto else "```"
        partes.append(f"\n## `{ruta.relative_to(RAIZ).as_posix()}`\n\n{cerca}{LENGUAJE.get(ruta.suffix, '')}\n{texto}\n{cerca}")
    destino = RAIZ / "docs" / "CODIGO_COMPLETO.md"
    destino.write_text("\n".join(partes) + "\n", encoding="utf-8")
    print(f"{destino.relative_to(RAIZ)}: {len(lista)} archivos, {total} líneas")


if __name__ == "__main__":
    main()

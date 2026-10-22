# Mano robótica bidireccional — guía de trabajo en equipo

Proyecto de grado (sustentación final). Dos partes que se integran en una sola página web con QR para la demo.

## Qué hace el sistema

1. **Texto → mano (modo señas):** la persona escribe texto o envía audio en la página web; la mano robótica (ESP32-S3, MicroPython, 6 servos) deletrea la palabra con el alfabeto de la Lengua de Señas Colombiana.
2. **Kinect → texto/voz (modo lectura):** la cámara (Kinect o cámara del PC mientras no esté disponible) reconoce señas con IA y el computador muestra o dice lo que se señó.

## Qué hay en el repositorio

| Carpeta / archivo | Qué es | Responsable |
|---|---|---|
| `firmware/esp32/` | Código MicroPython de la mano (`main.py` es el que va en la placa; `protocolo.md` explica las órdenes). **No modificar la lógica de movimiento** (ver `docs/GUIA_MODIFICAR_MANO.md`) | Jenpol |
| `pgc/` | Servidor de la plataforma (FastAPI): cola de mensajes, mano por Bluetooth/USB, voz con Whisper, túnel HTTPS | Jenpol |
| `web/` | Página del celular (`movil.html`, se abre con el QR) y pantalla del proyector (`pantalla.html`) | Jenpol |
| `pgc/adaptadores/kinect/` | Aquí va el reconocimiento de señas con el Kinect, siguiendo el contrato de `docs/CONTRATO_KINECT.md` | Camila |
| `tests/` | Pruebas automáticas (`py -3.11 -m pytest`); `tests/contratos/` comprueba que el reconocedor cumpla el contrato | Ambos |
| `docs/` | Arquitectura, contrato del Kinect, guía para modificar la mano | Ambos |
| `datos/` | Letras que hace la mano (`letras.json`) y palabras bloqueadas | Jenpol |
| `scripts/` | Pruebas de punta a punta, con servicios reales y en el navegador | Jenpol |

## Cómo ejecutarlo

1. Instalar dependencias (Python 3.11): `py -3.11 -m pip install -r requirements.txt`
2. Copiar `.env.example` como `.env` (el `.env` **no** está en el repositorio porque lleva secretos).
3. Sin la mano: `py -3.11 -m pgc --simular`. Con la mano: doble clic en `iniciar.bat`.
4. Pruebas: `py -3.11 -m pytest`.

## Requisitos de hardware y red

- La mano se conecta al PC por **Bluetooth BLE** (nombre `Mano-LSC`; **no** emparejarla en Windows). La placa necesita su `config_ble.py` (copiar `firmware/esp32/config_ble.example.py`), con el mismo token que `PGC_MANO_BLE_TOKEN` del `.env`. Ese archivo tampoco está en el repositorio.
- ESP32-S3 N16R8 con PCB de expansión: **nunca conectar USB y la fuente de 12 V a la vez** (se quema el ESP32).
  - USB: solo para subir archivos con Thonny (sin 12 V los servos no se mueven).
  - 12 V: la mano recibe órdenes por Bluetooth.
- La mano no tiene antebrazo ni muñeca: solo mueve dedos. Las letras que requieren muñeca no se pueden hacer.

## Cómo trabajar con el repositorio

1. Clonar: `git clone https://github.com/JenPol23/Proyecto-PGC.git`
2. Crear una rama para tu parte: `git checkout -b nombre-tu-parte`
3. Trabajar y hacer commits pequeños con mensajes claros.
4. Subir la rama: `git push -u origin nombre-tu-parte`
5. Abrir un Pull Request hacia `main` para revisar antes de integrar.

Nunca hacer push directo a `main` durante el desarrollo.

## Pendientes

- [ ] Integrar la página web con el reconocimiento del Kinect (Jenpol)
- [ ] Probar la página con la mano real por Bluetooth (ya implementado; falta la prueba física) (Jenpol)
- [ ] Validar que cada letra del abecedario se vea bien en la mano (Jenpol)
- [ ] Ajustar el reconocimiento del Kinect al proyecto (Camila)
- [ ] Probar la demo completa con QR en el hotspot del día de la presentación
- [ ] Documentar la metodología para el informe final

## Notas

- El código heredado de la carpeta kinect (dibujar.py, dashboard) fue adaptado con permiso del autor original; mantener la atribución en los archivos.
- El código original de movimiento de la mano funciona; cualquier cambio debe probarse antes de integrarse.

# Guía para modificar la mano (pines, valores y letras)

El firmware de la placa es **un solo archivo**, `firmware/esp32/main.py`:

- **Líneas 1–225**: tu código original, **idéntico** a `firmware/esp32/original/main_original.py`, línea por línea. Los números de línea de esta guía valen para los dos archivos.
- **Líneas 226 al final**: lo único agregado, que atiende las mismas órdenes también por Bluetooth. Va marcado con `>>> INICIO DE LO AGREGADO` y `<<< FIN DE LO AGREGADO`. **No hace falta tocarlo** para cambiar pines, valores o letras.

## Cómo hacer un cambio (siempre igual)

1. Edita **`firmware/esp32/original/main_original.py`** en la línea que indica la tabla.
2. Vuelve a armar el `main.py` de la placa:
   ```
   py -3.11 scripts\armar_main_placa.py
   ```
   Copia tu código hasta el BUCLE PRINCIPAL y le pega el bloque del Bluetooth.
3. Comprueba que todo sigue bien:
   ```
   py -3.11 -m pytest tests\test_firmware.py
   ```
4. Sube **`firmware/esp32/main.py`** a la placa con Thonny. Recuerda que en tu PCB no se pueden conectar USB y 12 V a la vez:
   1. quita los 12 V y conecta el USB;
   2. sube el archivo y pulsa Detener/Reiniciar;
   3. cierra Thonny, desconecta el USB y conecta los 12 V.

Si prefieres editar directamente `main.py` (líneas 1–225), copia después el mismo cambio en `original/main_original.py`. La prueba exige que esas líneas sean idénticas en los dos archivos.

## Dónde está cada cosa

### Tiempos y límites
| Línea | Qué es | Valor actual |
|---|---|---|
| 6 | `PAUSA_DEDO`: espera tras mover cada dedo | `0.4` s |
| 7 | `PAUSA_LETRA`: pausa entre letras al deletrear una palabra (`deletrear`) | `1.0` s |
| 8 | `US_MIN`: pulso mínimo permitido | `500` µs |
| 9 | `US_MAX`: pulso máximo permitido | `2500` µs |
| 27 | Espera entre servos al arrancar (`time.sleep(0.5)`) | `0.5` s |

El PC sostiene cada letra `PGC_PAUSA_LETRA` segundos (en `.env`; ahora `1.0`). Lo de la línea 7 solo se usa cuando la placa recibe una palabra entera, y el PC nunca la manda.

### Pines y calibración de cada dedo (`dedos_config`, líneas 11–18)
| Línea | Dedo | `pin` | `abierto` | `cerrado` | `mitad` |
|---|---|---|---|---|---|
| 12 | índice | 8 | 500 | 2000 | 1000 |
| 13 | meñique | 3 | 500 | 2000 | 1200 |
| 14 | medio | 10 | 500 | 2000 | 1000 |
| 15 | anular | 4 | 2200 | 500 | 1700 |
| 16 | pulgar | 6 | 1500 | 500 | 1000 |
| 17 | pulgar 2 | 7 | 500 | 2500 | 1600 |

- **Cambiar un pin** (por ejemplo, el pulgar 2 al GPIO 5): en la línea 17, `"pin": 7` → `"pin": 5`.
- **Calibrar**: cambia `abierto`, `cerrado` o `mitad` del dedo, en µs entre 500 y 2500. En el anular y el pulgar, `abierto` es el número mayor, porque esos servos están invertidos.
- `cuarto` y `cuarto_mas` no se configuran: se calculan con `abierto` y `mitad` (líneas 58–69).
- **Si cambias un pin o un valor**, cámbialo igual en `prueba_dedos.py` (líneas 24–31): la prueba exige que coincidan.

### Funciones de movimiento (normalmente no se tocan)
| Líneas | Función |
|---|---|
| 31–44 | `mover_a(nombre, us)`: límites de pulso, no mueve si ya está ahí, pausa `PAUSA_DEDO` |
| 46–50 | `mover_dedo(nombre, estado)`: 1 = cerrado, 0 = abierto |
| 52–56 | `mover_mitad(nombre)` |
| 58–62 | `mover_cuarto(nombre)`: entre abierto y mitad |
| 64–69 | `mover_cuarto_mas(nombre)`: entre cuarto y mitad |
| 71–73 | `reset_all()`: abre todos los dedos (se llama antes de cada letra) |

### Letras (líneas 75–209)
Cada letra es una función que mueve los dedos **en el orden en que están escritas sus líneas**:

| Letra | Líneas | Letra | Líneas | Letra | Líneas |
|---|---|---|---|---|---|
| a | 76–78 | k | 112–118 | r | 162–166 |
| b | 80–84 | l | 120–125 | t | 168–171 |
| c | 86–89 | m | 127–133 | u | 173–177 |
| d | 91–94 | n | 135–141 | v | 179–183 |
| e | 96–100 | o | 143–146 | w | 185–189 |
| f | 102–105 | p | 148–154 | x | 191–194 |
| i | 107–110 | q | 156–160 | y | 196–201 |

`acciones` (líneas 203–209) es la lista de letras que la mano sabe hacer.

- **Cambiar una letra**: edita su función. Para cambiar el orden de los dedos, cambia el orden de las líneas o de la lista `for d in [...]`.
- **Agregar una letra** (por ejemplo, la G):
  1. Después de `def y()` (línea 201) y antes de `acciones` (línea 203), agrega su función:
     ```python
     def g():
         mover_dedo("indice", 0)
         mover_dedo("medio", 1)
         ...
     ```
     Al agregar líneas, los números de línea de lo que viene después aumentan.
  2. Agrega `"g": g,` dentro de `acciones`.
  3. **En el PC**, agrega la letra en `datos/letras.json`, en `"por_defecto"` (ahora `"abcdefiklmnopqrtuvwxy"`). El firmware original no le dice al PC qué letras sabe hacer, así que el PC solo envía las que están en esa lista.
- Las letras que la mano no tiene (g, h, j, s, z) responden `comando_no_reconocido` y no mueven nada. El PC solo las muestra en pantalla.

### Deletreo y bucle
| Líneas | Qué es |
|---|---|
| 212–223 | `deletrear(palabra)`: no se usa desde el PC (manda letra por letra) |
| 225 | `# ---------------- BUCLE PRINCIPAL ----------------`: desde aquí empieza lo agregado |

## Bluetooth (`config_ble.py`, solo en la placa)
Nombre y token. Se copia desde `firmware/esp32/config_ble.example.py` y **nunca se guarda en el proyecto con datos reales**. El token debe ser el mismo que `PGC_MANO_BLE_TOKEN` en el `.env` del PC, y el nombre el mismo que `PGC_MANO_BLE_NOMBRE` (por defecto `Mano-LSC`).

## Respuestas de la placa (no cambiarlas: el PC las espera así)
| Orden | Respuesta |
|---|---|
| una letra de `acciones` | `gesto_<letra>_ok` |
| `reset` o `1` | `reset_ok` |
| una letra que no está | `comando_no_reconocido` |
| una palabra | `gesto_…_ok` / `letra_actual:…` / `letra_…_no_disponible` … `deletreo_completo` |
| por Bluetooth, primera línea `auth <token>` | `ok:auth` o `error:auth` |

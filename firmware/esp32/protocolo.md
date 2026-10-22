# Firmware de la mano: archivos, órdenes, Bluetooth y carga con Thonny

ESP32-S3 N16R8 con MicroPython y 6 servos.

## 0. Regla del hardware: USB **o** 12 V, nunca los dos

En la PCB de la mano **no se pueden conectar el USB y los 12 V a la vez**.

| Conectado | Para qué |
|---|---|
| **Solo USB** (sin 12 V) | Subir archivos con Thonny y probar las respuestas. Los servos **no** se mueven |
| **Solo 12 V** (sin USB) | La mano funcionando. El PC la maneja **solo por Bluetooth** |

Por eso, en el PC el `.env` lleva `PGC_MANO=ble`. Con la mano encendida no hay respaldo por USB.

## 1. Archivos

| Archivo | Va a la placa | Qué es |
|---|---|---|
| `main.py` | **Sí** | **Tu código original, idéntico en las líneas 1–225**. Desde la línea 226 va el bloque agregado, marcado `>>> INICIO DE LO AGREGADO` … `<<< FIN DE LO AGREGADO`, que atiende las mismas órdenes también por Bluetooth |
| `config_ble.py` | **Sí** | Nombre y token. Solo existe en la placa. En el proyecto está `config_ble.example.py`, con datos ficticios |
| `prueba_dedos.py` | Solo para probar | Mueve cada dedo por separado, sin PC (sección 5) |
| `prueba.py` | Solo para probar | Cierra y abre cada dedo, uno por uno, y al final cierra toda la mano. Se usa igual que `prueba_dedos.py` |
| `original/main_original.py` | No | Tu código tal cual. Es la referencia de las pruebas |
| `original/bucle_ble.py` | No | El bloque agregado. `scripts/armar_main_placa.py` arma `main.py` con los dos |
| `referencia_doby/` | No | Otro proyecto |

Para cambiar pines, valores o letras, sigue `docs/GUIA_MODIFICAR_MANO.md`: ahí están los números de línea y el procedimiento.

## 2. Órdenes y respuestas (las de tu código, iguales por USB y por Bluetooth)

| Orden | Qué hace | Respuesta |
|---|---|---|
| una letra de `acciones` (a b c d e f i k l m n o p q r t u v w x y) | `reset_all()` y la función de la letra | `gesto_<letra>_ok` |
| `reset` o `1` | `reset_all()` | `reset_ok` |
| una palabra (más de una letra) | `deletrear()` | `gesto_…_ok`, `letra_actual:…`, `letra_…_no_disponible`, …, `deletreo_completo` |
| `salir` | Termina el programa (`reset_all()` y "Programa terminado.") | — |
| otra cosa de una letra | Nada | `comando_no_reconocido` |

- Al arrancar imprime "Iniciando motores...", "Mano lista." y "Listo. Esperando comandos...".
- Si hay `config_ble.py`, también imprime avisos que empiezan por `# `, por ejemplo `# Bluetooth listo: se anuncia como Mano-LSC` o `# PC conectado por Bluetooth`.
- **El PC envía siempre letra por letra** y `reset`, nunca palabras. Tu firmware no tiene `ping` ni `letras` (una palabra se deletrearía), así que el PC comprueba la conexión con `reset` → `reset_ok`.

### Solo por Bluetooth (BLE)
El ESP32-S3 solo tiene **Bluetooth de bajo consumo (BLE)**. No crea un puerto COM, así que **no hace falta emparejarlo en Windows**. La placa usa el servicio "UART" de Nordic, el estándar para enviar texto por BLE:

| Característica | UUID | Uso |
|---|---|---|
| Servicio | `6E400001-B5A3-F393-E0A9-E50E24DCCA9E` | |
| RX | `6E400002-…` | el PC escribe las órdenes (una por línea) |
| TX | `6E400003-…` | la placa notifica las respuestas (una por línea) |

1. El PC busca el dispositivo por su nombre (`NOMBRE` de `config_ble.py`, que debe coincidir con `PGC_MANO_BLE_NOMBRE`; por defecto `Mano-LSC`) y se conecta.
2. **Primera línea**: `auth <TOKEN>`. La placa responde `ok:auth`. Si el token es incorrecto, responde `error:auth` y desconecta. Si el token no llega en 3 s, también desconecta.
3. Desde ahí se usan las órdenes de la tabla, con las mismas respuestas.

- **Un solo PC a la vez**: mientras hay uno conectado, la placa deja de anunciarse. Al desconectarse, vuelve a anunciarse sola.
- Los datos viajan en paquetes de 20 bytes (sirve con cualquier adaptador).
- El Bluetooth nunca bloquea el bucle, y el USB sigue funcionando igual que en el original.
- **Alcance**: unos 10 m sin paredes. En la sustentación, deja el PC cerca de la mano.

## 3. Pines (los de `dedos_config`, líneas 12–17 de `main.py`)

| Dedo | GPIO | Nota |
|---|---|---|
| Índice | 8 | |
| Meñique | 3 | **Pin de arranque (strapping) del S3**: si la placa no arranca con los servos conectados, mueve el meñique a otro GPIO |
| Medio | 10 | |
| Anular | 4 | Invertido (abierto 2200, cerrado 500) |
| Pulgar | 6 | Invertido (abierto 1500, cerrado 500) |
| Pulgar 2 | 7 | |

La placa es **exclusiva de la mano**. Si algún día se vuelve a usar para Doby, hay conflicto en los GPIO 4, 6, 7 y 10.

## 4. Cargar el firmware con Thonny

**Antes de empezar:**
1. Cierra el servidor del PC.
2. **Quita los 12 V.**
3. Conecta el USB.

**Pasos:**
1. Abre Thonny. En **Herramientas › Opciones › Intérprete**, elige **MicroPython (ESP32)** y el puerto COM. Pulsa **Detener/Reiniciar** (el octágono rojo).
2. Abre **Ver › Archivos**. Abajo aparece **"Dispositivo MicroPython"**.
3. **Respaldo** (opcional): selecciona los archivos de la placa, clic derecho › **Descargar a …** una carpeta de tu PC.
4. **Borra de la placa** lo que ya no se usa (clic derecho › **Eliminar**): `config_wifi.py`, `mano_movimientos.py`, `mano_protocolo.py`, `mano_red.py`, `mano_vigilante.py`, `mano_servos.py`, `letras.json` y `secretos.py`, si existen.
5. Arriba, ve a `ProyectoPGC\firmware\esp32`, clic derecho sobre **`main.py`** › **Subir a /**, y acepta reemplazarlo.
6. **Crea `config_ble.py` en la placa**:
   1. En Thonny, **Archivo › Nuevo**, y pega:
      ```python
      NOMBRE = "Mano-LSC"
      TOKEN = "<el mismo valor de PGC_MANO_BLE_TOKEN del .env del PC>"
      ```
   2. **Archivo › Guardar como… › Dispositivo MicroPython**, con el nombre `config_ble.py`.
   3. No lo guardes en la carpeta del proyecto.
7. Pulsa **Detener/Reiniciar**. Deben aparecer "Iniciando motores...", "Mano lista.", `# Bluetooth listo: se anuncia como Mano-LSC` y "Listo. Esperando comandos...".
8. Prueba en la consola de Thonny: `a` → `gesto_a_ok`; `reset` → `reset_ok`. Sin 12 V, los servos no se mueven.
9. **Cierra Thonny**, desconecta el USB y conecta los 12 V. La mano arranca sola y queda esperando por Bluetooth.

**En el PC:**
1. **Enciende el Bluetooth**: Configuración › Bluetooth y dispositivos › Bluetooth **Activado**. **No emparejes la mano** ("Agregar dispositivo"): Windows guardaría claves que la placa no conoce y la conexión se cortaría. Si ya la emparejaste, quítala en Dispositivos (menú **⋯** › **Quitar dispositivo**) y reinicia la mano.
2. El `.env` debe tener:
   ```
   PGC_MANO=ble
   PGC_MANO_BLE_TOKEN=<el mismo TOKEN de config_ble.py>
   ```
3. Ejecuta `iniciar.bat`. En la pantalla debe salir **"Mano: Bluetooth · Mano-LSC"**.

Si sale "Simulada", revisa el log del servidor:
- `el Bluetooth del PC está apagado` → enciéndelo en Windows.
- `no se encontró` → revisa que la mano tenga 12 V, que esté cerca y que ningún otro PC o celular esté conectado a ella.
- `rechazó el token` → el TOKEN de `config_ble.py` y el del `.env` no coinciden.

Después usa **«Reconectar mano»** en la pantalla, o espera: el PC lo reintenta solo cada 10 s.

## 5. Probar cada dedo por separado (`prueba_dedos.py`)

Mueve un dedo a la vez (cerrado → mitad → abierto), 3 vueltas, sin PC. Sirve para revisar el cableado y la calibración.

1. **Sin 12 V y con USB**, en Thonny: clic derecho sobre `prueba_dedos.py` › **Subir a /**.
2. Luego, abajo, renombra en la placa `main.py` a `main_mano.py` y `prueba_dedos.py` a `main.py`. La placa solo ejecuta sola el archivo que se llama `main.py`.
3. Cierra Thonny, desconecta el USB y conecta los 12 V: la placa mueve los dedos uno por uno y termina con la mano abierta.
4. Para volver a la mano:
   1. Quita los 12 V y conecta el USB.
   2. En Thonny, borra el `main.py` (la prueba).
   3. Renombra `main_mano.py` a `main.py`, o vuelve a subir `firmware\esp32\main.py`.

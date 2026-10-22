# config_ble.example.py  —  EJEMPLO con datos ficticios
# -----------------------------------------------------------------------------
# Copia este archivo en la placa con el nombre config_ble.py y pon tu token.
# NO guardes config_ble.py con el token real en el proyecto ni lo compartas.
# Sin config_ble.py en la placa, la mano funciona solo por USB.
# -----------------------------------------------------------------------------

NOMBRE = "Mano-LSC"                 # nombre con el que la placa aparece por Bluetooth

# Mismo valor que PGC_MANO_BLE_TOKEN en el .env del PC (mínimo 16 caracteres).
# Para generar uno:  py -3.11 -c "import secrets; print(secrets.token_urlsafe(24))"
TOKEN = "cambia-este-token-por-uno-aleatorio"

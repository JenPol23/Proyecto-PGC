@echo off
rem Inicia el servidor de la mano LSC (abre la pantalla del proyector sola).
rem Opciones: --simular  --puerto COM5  --sin-tunel  --sin-voz  --no-abrir  --dev
rem Lo demas (mano por Bluetooth, token, limites...) se configura en el archivo .env
rem (copia .env.example como .env la primera vez).
cd /d "%~dp0"
py -3.11 -m pgc %*
pause

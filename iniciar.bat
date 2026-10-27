@echo off
rem Inicia TODO el sistema (abre la pantalla del proyector sola):
rem   - la plataforma (pagina del celular, proyector, mano, voz, tunel HTTPS)
rem   - el detector de senas de integracion_kinect (con el Python de .venv-detector)
rem   - la app del Kinect ya compilada (LSCKinectFramework.exe), minimizada
rem Al cerrar esta ventana (o con Ctrl+C) se cierran el detector y la app del Kinect.
rem Si falta el detector o el Kinect, la plataforma arranca igual ("Kinect no conectado").
rem Opciones: --simular  --puerto COM5  --sin-tunel  --sin-voz  --no-abrir  --dev
rem Lo demas (mano por Bluetooth, token, Kinect, camara del PC...) se configura en el archivo .env
rem (copia .env.example como .env la primera vez). Primera vez del detector: instalar_detector.bat
cd /d "%~dp0"
py -3.11 -m pgc %*
pause

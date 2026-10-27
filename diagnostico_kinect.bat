@echo off
rem Diagnostico del Kinect paso a paso (Windows, archivos, puertos y prueba en vivo).
rem Conecta el Kinect (corriente + USB) y espera unos 30 s antes de ejecutarlo.
rem No cambia nada: abre el detector y la app del Kinect, mide y los cierra.
rem El informe queda en registros\diagnostico_kinect.txt
rem Opciones: --sin-capturador (no abre la app del Kinect)  --segundos 20
cd /d "%~dp0"
py -3.11 scripts\diagnostico_kinect.py %*
pause

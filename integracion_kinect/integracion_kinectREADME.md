# Integración Kinect y deletreo LSC

Requiere Windows, Kinect Xbox 360, Kinect SDK 1.8,
.NET Framework 4.8 y Python 3.11.

## Detector

Desde integracion_kinect/detector:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-detector.txt
.\.venv\Scripts\python.exe server_web_svm.py
```

## Captura

Abrir y compilar el proyecto de integracion_kinect/capturador
en Visual Studio. Ejecutarlo y dejarlo abierto para capturar
las imágenes. Controlar el deletreo desde la página.

## Plataforma web

Desde la raíz del repositorio:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe iniciar_pgc_integrado.py --simular --sin-tunel --no-abrir
```

Abrir http://127.0.0.1:8000/ y seleccionar Kinect.

El teléfono puede consultar imagen y texto mediante el QR.
Para controlar, introducir el código mostrado en el PC.
La lectura de texto utiliza las voces disponibles del navegador.

Mantener separados los entornos virtuales del detector y la web.
@echo off
rem Prepara UNA VEZ el entorno del detector de senas (integracion_kinect\detector).
rem Usa sus versiones exactas (mediapipe 0.10.21, numpy 1.26.4, scikit-learn 1.5.2...), que no
rem caben en el Python de la plataforma; por eso va en su propia carpeta .venv-detector.
rem Necesita internet (unos 350 MB). Despues, iniciar.bat lo usa solo.
cd /d "%~dp0"
if exist .venv-detector\Scripts\python.exe (
  echo El entorno del detector ya existe: .venv-detector
) else (
  py -3.11 -m venv .venv-detector || goto error
)
.venv-detector\Scripts\python.exe -m pip install --disable-pip-version-check -r integracion_kinect\detector\requirements-detector.txt || goto error
.venv-detector\Scripts\python.exe -c "import mediapipe, sklearn, cv2; print('Detector listo: mediapipe', mediapipe.__version__, '- scikit-learn', sklearn.__version__)" || goto error
pause
exit /b 0
:error
echo No se pudo preparar el entorno del detector. Revisa la conexion a internet y vuelve a intentar.
pause
exit /b 1

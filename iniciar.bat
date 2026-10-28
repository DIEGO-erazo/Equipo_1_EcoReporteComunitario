@echo off
REM Prepara y ejecuta EcoReporte Comunitario en Windows (doble clic o desde la terminal).
cd /d "%~dp0"

if not exist .venv (
    echo Creando entorno virtual...
    python -m venv .venv || (echo No se encontro Python. Instalalo desde https://www.python.org & pause & exit /b 1)
)
call .venv\Scripts\activate.bat

echo Instalando dependencias...
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q || (pause & exit /b 1)

if not exist .env copy .env.example .env >nul

python manage.py migrate || (pause & exit /b 1)
python manage.py cargar_datos_iniciales --demo

echo.
echo Abre http://127.0.0.1:8000 en tu navegador. Presiona Ctrl+C para detener.
python manage.py runserver

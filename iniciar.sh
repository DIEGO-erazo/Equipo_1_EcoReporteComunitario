#!/bin/sh
# Prepara y ejecuta EcoReporte Comunitario en macOS o Linux.
set -e
cd "$(dirname "$0")"

[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate

pip install --upgrade pip -q
pip install -r requirements.txt -q

[ -f .env ] || cp .env.example .env

python manage.py migrate
python manage.py cargar_datos_iniciales --demo

echo
echo "Abre http://127.0.0.1:8000 en tu navegador. Presiona Ctrl+C para detener."
python manage.py runserver

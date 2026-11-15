#!/usr/bin/env bash
# Preparación de EcoReporte Comunitario en Render (se ejecuta en cada despliegue).
# Render lo llama desde "Build Command": ./build.sh
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

# Reúne el CSS, JavaScript e imágenes en staticfiles/ para que WhiteNoise los sirva.
python manage.py collectstatic --no-input

# Crea o actualiza las tablas en la base de datos PostgreSQL de Render.
python manage.py migrate --no-input

# Roles, estados y categorías. Con --demo añade dos cuentas y tres reportes de ejemplo
# (solo la primera vez: si ya existen no los duplica).
python manage.py cargar_datos_iniciales --demo

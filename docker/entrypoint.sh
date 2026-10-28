#!/bin/sh
set -e

if [ "$DB_ENGINE" = "mssql" ]; then
    python docker/crear_base_de_datos.py
fi

python manage.py migrate --noinput
python manage.py cargar_datos_iniciales ${CARGAR_DEMO:+--demo}

exec "$@"

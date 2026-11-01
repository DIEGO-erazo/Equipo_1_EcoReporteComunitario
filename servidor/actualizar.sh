#!/bin/bash
# Aplica cambios después de copiar una versión nueva del código a la laptop.
# Uso:  bash servidor/actualizar.sh
set -e
cd "$(dirname "$0")/.."

.venv/bin/pip install -r requirements.txt gunicorn==23.0.0 -q
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py collectstatic --noinput -v 0
sudo systemctl restart ecoreporte
echo "Actualizado. La dirección pública no cambia."

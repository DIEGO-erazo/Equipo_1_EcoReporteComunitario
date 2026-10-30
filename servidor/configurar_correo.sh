#!/bin/bash
# Configura la cuenta de Gmail con la que la página envía los enlaces para
# recuperar la contraseña. Pide el correo y la contraseña de aplicación, prueba
# que Gmail los acepte, los guarda en .env y reinicia la página.
#
# Requisito: haber ejecutado antes  bash servidor/instalar_servidor.sh
# Uso:       bash servidor/configurar_correo.sh
# Cómo obtener la contraseña de aplicación: documentacion/recuperar_contrasena.md
set -e
cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
    echo "Primero ejecuta:  bash servidor/instalar_servidor.sh"
    exit 1
fi

read -rp "Correo de Gmail que enviará los mensajes: " CORREO
read -rsp "Contraseña de aplicación de Google (16 letras; no se ve al escribir): " CLAVE
echo
CORREO="${CORREO// /}"
CLAVE="${CLAVE// /}"
if [ -z "$CORREO" ] || [ "${#CLAVE}" -ne 16 ]; then
    echo "Falta el correo o la contraseña no tiene 16 letras. No se cambió nada."
    exit 1
fi

echo "Probando la conexión con Gmail..."
# Las variables puestas aquí tienen prioridad sobre el .env, así se prueba sin guardar nada.
if ! CORREO_USUARIO="$CORREO" CORREO_CONTRASENA="$CLAVE" .venv/bin/python manage.py shell -v 0 \
        -c "from django.core.mail import mailers; c = mailers.default; c.open(); c.close()" 2> /tmp/ecoreporte-correo.log; then
    echo "Gmail no aceptó esos datos. No se cambió nada."
    echo "Revisa que la verificación en 2 pasos esté activa y copia de nuevo la contraseña de aplicación."
    echo "Detalle del error: $(tail -n 1 /tmp/ecoreporte-correo.log)"
    rm -f /tmp/ecoreporte-correo.log
    exit 1
fi
rm -f /tmp/ecoreporte-correo.log

# Reemplaza la configuración anterior, si la había.
sed -i '/^CORREO_USUARIO=/d; /^CORREO_CONTRASENA=/d' .env
[ -n "$(tail -c 1 .env)" ] && echo >> .env
printf 'CORREO_USUARIO=%s\nCORREO_CONTRASENA=%s\n' "$CORREO" "$CLAVE" >> .env
chmod 600 .env

sudo systemctl daemon-reload
sudo systemctl restart ecoreporte
echo "Listo: la página ya puede enviar correos desde $CORREO."
echo "Pruébalo en Ingresar -> ¿Olvidaste tu contraseña?"

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
# Un solo intento de ingreso: smtplib.login() prueba un segundo método cuando Gmail
# rechaza el primero, Gmail cierra la conexión y el error real (535) queda oculto.
if ! RESPUESTA="$(CORREO_USUARIO="$CORREO" CORREO_CONTRASENA="$CLAVE" .venv/bin/python - 2>&1 <<'EOF'
import os, smtplib, sys
try:
    s = smtplib.SMTP(os.getenv('CORREO_SERVIDOR', 'smtp.gmail.com'), int(os.getenv('CORREO_PUERTO', '587')), timeout=20)
    s.starttls()
    s.ehlo()
    s.user, s.password = os.environ['CORREO_USUARIO'], os.environ['CORREO_CONTRASENA']
    s.auth('PLAIN', s.auth_plain)
    s.quit()
except smtplib.SMTPAuthenticationError as e:
    print('Gmail respondió: ' + e.smtp_error.decode(errors='replace').splitlines()[0])
    sys.exit(1)
except Exception as e:
    print('No se pudo conectar con Gmail: ' + type(e).__name__ + ': ' + str(e))
    sys.exit(1)
EOF
)"; then
    echo "$RESPUESTA"
    echo "No se cambió nada."
    echo "Revisa que la contraseña de aplicación sea de ESA MISMA cuenta ($CORREO),"
    echo "que la verificación en 2 pasos esté activa y que copiaste las 16 letras completas."
    exit 1
fi

# Reemplaza la configuración anterior, si la había.
sed -i '/^CORREO_USUARIO=/d; /^CORREO_CONTRASENA=/d' .env
[ -n "$(tail -c 1 .env)" ] && echo >> .env
printf 'CORREO_USUARIO=%s\nCORREO_CONTRASENA=%s\n' "$CORREO" "$CLAVE" >> .env
chmod 600 .env

sudo systemctl daemon-reload
sudo systemctl restart ecoreporte
echo "Listo: la página ya puede enviar correos desde $CORREO."
echo "Pruébalo en Ingresar -> ¿Olvidaste tu contraseña?"

#!/bin/bash
# Convierte una computadora con Ubuntu en el servidor de EcoReporte Comunitario.
#
# Qué hace:
#   1. Instala Python y prepara el entorno virtual con las dependencias.
#   2. Crea un .env de producción (DEBUG apagado y clave secreta nueva).
#   3. Prepara la base de datos SQLite y los archivos estáticos.
#   4. Deja la app corriendo con gunicorn como servicio (arranca sola al prender).
#   5. Instala Cloudflare Tunnel para que la página se abra desde internet.
#   6. Evita que la laptop se suspenda al cerrar la tapa.
#   7. Programa un respaldo diario de la base de datos y las fotos.
#   8. Revisa GitHub cada 2 minutos e instala solo los cambios que pasaron las pruebas
#      (de la rama que se clonó: main, o la que se indicó con  git clone -b <rama>).
#
# Uso: clona el repositorio y, desde su carpeta, ejecuta  bash servidor/instalar_servidor.sh
set -e

PROYECTO="$(cd "$(dirname "$0")/.." && pwd)"
USUARIO="$(whoami)"
cd "$PROYECTO"

if [ "$USUARIO" = "root" ]; then
    echo "Ejecuta este script con tu usuario normal (sin sudo); él pedirá la contraseña cuando la necesite."
    exit 1
fi

if [ ! -d .git ]; then
    echo "Esta carpeta no es un clon de GitHub, así que no podrá actualizarse sola. Descárgala con:"
    echo "  git clone https://github.com/DIEGO-erazo/Equipo_1_EcoReporteComunitario.git"
    exit 1
fi

echo "== 1/8 Instalando Python y herramientas =="
sudo apt-get -o DPkg::Lock::Timeout=600 update -q
sudo apt-get -o DPkg::Lock::Timeout=600 install -y -q python3 python3-venv python3-pip sqlite3 curl git

# Django 6 necesita Python 3.12 o más nuevo.
PYTHON=python3
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)'; then
    echo "Tu Ubuntu trae $(python3 --version); se instalará Python 3.12 aparte."
    sudo apt-get -o DPkg::Lock::Timeout=600 install -y -q software-properties-common
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt-get -o DPkg::Lock::Timeout=600 update -q
    sudo apt-get -o DPkg::Lock::Timeout=600 install -y -q python3.12 python3.12-venv
    PYTHON=python3.12
fi

echo "== 2/8 Preparando entorno virtual y dependencias =="
[ -d .venv ] || "$PYTHON" -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt gunicorn==23.0.0 -q

echo "== 3/8 Configuración de producción (.env) =="
if [ -f .env ] && grep -q '^DEBUG=False' .env; then
    echo ".env de producción ya existe; se conserva."
else
    [ -f .env ] && mv .env .env.desarrollo
    CLAVE="$(.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(50))')"
    cat > .env <<EOF
DEBUG=False
SECRET_KEY=$CLAVE
DB_ENGINE=sqlite
DETRAS_DE_PROXY=True
# Direcciones desde las que se puede abrir la página.
# Si luego compras un dominio, agrégalo aquí (ej. ecoreporte.com y https://ecoreporte.com).
ALLOWED_HOSTS=localhost,127.0.0.1,.trycloudflare.com
CSRF_TRUSTED_ORIGINS=https://*.trycloudflare.com
EOF
    chmod 600 .env
fi

echo "== 4/8 Base de datos y archivos estáticos =="
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py cargar_datos_iniciales
.venv/bin/python manage.py collectstatic --noinput -v 0
mkdir -p media

if ! .venv/bin/python manage.py shell -c 'from django.contrib.auth.models import User; import sys; sys.exit(0 if User.objects.filter(is_superuser=True).exists() else 1)'; then
    echo
    echo "Crea la cuenta de administrador de la página."
    echo "Como 'Username' escribe el mismo correo con el que vas a iniciar sesión."
    .venv/bin/python manage.py createsuperuser
fi

echo "== 5/8 Servicio de la aplicación (gunicorn) =="
sudo tee /etc/systemd/system/ecoreporte.service > /dev/null <<EOF
[Unit]
Description=EcoReporte Comunitario (Django + gunicorn)
After=network.target

[Service]
User=$USUARIO
WorkingDirectory=$PROYECTO
ExecStart=$PROYECTO/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 60
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

echo "== 6/8 Cloudflare Tunnel (acceso desde internet) =="
if ! command -v cloudflared > /dev/null; then
    curl -fsSL -o /tmp/cloudflared.deb \
        https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    sudo dpkg -i /tmp/cloudflared.deb
    rm /tmp/cloudflared.deb
fi

sudo tee /etc/systemd/system/ecoreporte-tunel.service > /dev/null <<EOF
[Unit]
Description=Cloudflare Tunnel para EcoReporte Comunitario
After=network-online.target ecoreporte.service
Wants=network-online.target

[Service]
User=$USUARIO
ExecStart=/usr/bin/cloudflared tunnel --no-autoupdate --url http://localhost:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now ecoreporte.service ecoreporte-tunel.service
sudo systemctl restart ecoreporte.service ecoreporte-tunel.service

echo "== 7/8 Tapa cerrada y respaldos =="
# Que la laptop siga encendida con la tapa cerrada (aplica después de reiniciar).
sudo mkdir -p /etc/systemd/logind.conf.d
sudo tee /etc/systemd/logind.conf.d/ecoreporte.conf > /dev/null <<EOF
[Login]
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
EOF
sudo systemctl mask -q sleep.target suspend.target hibernate.target hybrid-sleep.target

# Respaldo diario en ~/respaldos_ecoreporte; se guardan los últimos 14 días.
sudo tee /etc/cron.daily/ecoreporte-respaldo > /dev/null <<EOF
#!/bin/sh
DESTINO=/home/$USUARIO/respaldos_ecoreporte
FECHA=\$(date +%Y-%m-%d)
mkdir -p "\$DESTINO"
sqlite3 "$PROYECTO/db.sqlite3" ".backup '\$DESTINO/db-\$FECHA.sqlite3'"
tar -czf "\$DESTINO/media-\$FECHA.tar.gz" -C "$PROYECTO" media
find "\$DESTINO" -type f -mtime +14 -delete
chown -R $USUARIO:$USUARIO "\$DESTINO"
EOF
sudo chmod +x /etc/cron.daily/ecoreporte-respaldo

echo "== 8/8 Actualización automática desde GitHub =="
sudo tee /etc/systemd/system/ecoreporte-actualizar.service > /dev/null <<EOF
[Unit]
Description=Instala los cambios nuevos de GitHub en EcoReporte
After=network-online.target ecoreporte.service

[Service]
Type=oneshot
User=$USUARIO
ExecStart=/bin/bash $PROYECTO/servidor/autoactualizar.sh
EOF

sudo tee /etc/systemd/system/ecoreporte-actualizar.timer > /dev/null <<EOF
[Unit]
Description=Revisa GitHub cada 2 minutos

[Timer]
OnBootSec=1min
OnUnitActiveSec=2min

[Install]
WantedBy=timers.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now ecoreporte-actualizar.timer

echo
echo "Esperando la dirección pública..."
for _ in $(seq 1 30); do
    URL="$(journalctl -u ecoreporte-tunel --since '-2 min' --no-pager 2>/dev/null | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | tail -1)"
    [ -n "$URL" ] && break
    sleep 2
done

echo
echo "============================================================"
echo " ¡Listo! EcoReporte está corriendo."
if [ -n "$URL" ]; then
    echo " Dirección pública: $URL"
else
    echo " Para ver la dirección pública ejecuta:  bash servidor/ver_direccion.sh"
fi
echo " Esta dirección cambia cada vez que se reinicia la laptop;"
echo " consúltala de nuevo con:  bash servidor/ver_direccion.sh"
echo "============================================================"

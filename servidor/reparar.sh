#!/bin/bash
# Revisa el servidor de EcoReporte, arregla lo que encuentre y lo deja listo para
# que arranque solo al encender la laptop. Se puede ejecutar las veces que haga falta.
#
# Uso (con tu usuario normal, sin sudo):  bash servidor/reparar.sh
cd "$(dirname "$0")/.."
PROYECTO="$(pwd)"
USUARIO="$(whoami)"
PROBLEMAS=0

ok()   { echo "  [OK]    $*"; }
mal()  { echo "  [FALLA] $*"; PROBLEMAS=$((PROBLEMAS + 1)); }
hecho() { echo "  [ARREGLADO] $*"; }

if [ "$USUARIO" = "root" ]; then
    echo "Ejecuta este script con tu usuario normal (sin sudo); él pedirá la contraseña cuando la necesite."
    exit 1
fi
if [ ! -f .env ]; then
    echo "No hay .env: este servidor nunca se instaló. Ejecuta primero:  bash servidor/instalar_servidor.sh"
    exit 1
fi
sudo -v || exit 1

echo "== 1/6 Internet =="
if curl -fsS -o /dev/null --max-time 15 https://github.com; then
    ok "Hay conexión a internet."
else
    mal "No hay internet. Conecta la laptop y vuelve a ejecutar este script."
fi

# Si el Wi-Fi está guardado "solo para este usuario", Ubuntu no se conecta hasta que
# alguien inicia sesión, y el servidor queda sin internet al encender.
if command -v nmcli > /dev/null; then
    CONEXION="$(nmcli -t -f NAME,TYPE connection show --active | grep -v ':loopback$' | head -1 | cut -d: -f1)"
    if [ -n "$CONEXION" ]; then
        sudo nmcli connection modify "$CONEXION" connection.autoconnect yes
        if [ -n "$(nmcli -g connection.permissions connection show "$CONEXION")" ]; then
            sudo nmcli connection modify "$CONEXION" connection.permissions ""
            hecho "La red «$CONEXION» ahora se conecta al encender, sin iniciar sesión."
        fi
        if [ "$(nmcli -g 802-11-wireless-security.psk-flags connection show "$CONEXION" 2>/dev/null)" = "1" ]; then
            CLAVE_WIFI="$(nmcli -s -g 802-11-wireless-security.psk connection show "$CONEXION" 2>/dev/null)"
            if [ -n "$CLAVE_WIFI" ]; then
                sudo nmcli connection modify "$CONEXION" \
                    802-11-wireless-security.psk-flags 0 802-11-wireless-security.psk "$CLAVE_WIFI"
                hecho "La contraseña del Wi-Fi «$CONEXION» quedó guardada para todos los usuarios."
            else
                mal "La contraseña del Wi-Fi «$CONEXION» solo la conoce tu usuario. En Configuración > Wi-Fi > «$CONEXION», marca «Disponible para todos los usuarios»."
            fi
        fi
        ok "Red activa: $CONEXION"
    fi
fi

echo "== 2/6 Código y dependencias =="
RAMA="$(git rev-parse --abbrev-ref HEAD)"
if git fetch -q origin "$RAMA" && git merge -q --ff-only "origin/$RAMA"; then
    ok "Código al día con GitHub (rama $RAMA, commit $(git rev-parse --short HEAD))."
else
    mal "No se pudo traer el código de GitHub. Revisa  git status  en $PROYECTO"
fi

if ! .venv/bin/python -c 'import django' 2> /dev/null; then
    echo "  El entorno de Python está dañado; se vuelve a crear."
    PYTHON=python3
    python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' || PYTHON=python3.12
    rm -rf .venv
    "$PYTHON" -m venv .venv && .venv/bin/pip install --upgrade pip -q
fi
if .venv/bin/pip install -r requirements.txt gunicorn==23.0.0 -q &&
   .venv/bin/python manage.py migrate --noinput &&
   .venv/bin/python manage.py collectstatic --noinput -v 0; then
    ok "Dependencias, base de datos y archivos estáticos listos."
else
    mal "Falló la instalación de dependencias o la base de datos (mira el error de arriba)."
fi

echo "== 3/6 Aplicación (gunicorn) =="
sudo tee /etc/systemd/system/ecoreporte.service > /dev/null <<EOF
[Unit]
Description=EcoReporte Comunitario (Django + gunicorn)
After=network.target
# Nunca deja de reintentar, aunque falle varias veces seguidas.
StartLimitIntervalSec=0

[Service]
User=$USUARIO
WorkingDirectory=$PROYECTO
ExecStart=$PROYECTO/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 60
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable -q ecoreporte.service
sudo systemctl restart ecoreporte.service

RESPONDE=""
for _ in $(seq 1 15); do
    curl -s -o /dev/null --max-time 5 http://127.0.0.1:8000/ && RESPONDE=1 && break
    sleep 2
done
if [ -n "$RESPONDE" ]; then
    ok "La página responde en la laptop (http://127.0.0.1:8000)."
else
    mal "La página no arranca. Últimas líneas del registro:"
    sudo journalctl -u ecoreporte -n 25 --no-pager
fi

echo "== 4/6 Tailscale y dirección fija =="
DIRECCION_FIJA="$(grep -oP '^DIRECCION_FIJA=\K.+' .env || true)"
if [ -z "$DIRECCION_FIJA" ]; then
    echo "  Este servidor usa el túnel temporal de Cloudflare."
    sudo systemctl enable -q --now ecoreporte-tunel.service 2> /dev/null && sudo systemctl restart ecoreporte-tunel.service
    ok "Túnel reiniciado. Su dirección:  bash servidor/ver_direccion.sh"
elif ! command -v tailscale > /dev/null; then
    mal "Tailscale no está instalado. Ejecuta:  bash servidor/usar_direccion_fija.sh"
else
    sudo systemctl enable -q --now tailscaled
    if ! tailscale status > /dev/null 2>&1; then
        echo "  Tailscale está desconectado. Si aparece un enlace, ábrelo en el navegador e inicia sesión."
        sudo tailscale up --hostname=ecoreporte
    fi
    if tailscale status > /dev/null 2>&1; then
        ok "Tailscale conectado."
        sudo timeout 120 tailscale funnel --bg 8000 > /dev/null
        if sudo tailscale funnel status 2> /dev/null | grep -q 'Funnel on'; then
            ok "Funnel encendido."
        else
            mal "El Funnel no se pudo encender. Ejecuta  sudo tailscale funnel 8000  y abre el enlace que muestre."
        fi

        # La app solo acepta visitas a las direcciones anotadas en el .env.
        DOMINIO="$(tailscale status --json | .venv/bin/python -c 'import json, sys; print(json.load(sys.stdin)["Self"]["DNSName"].rstrip("."))')"
        if [ -n "$DOMINIO" ] && [ "$DIRECCION_FIJA" != "https://$DOMINIO" ]; then
            .venv/bin/python - "$DOMINIO" <<'EOF'
import sys
from pathlib import Path

dominio = sys.argv[1]
env = Path(".env")
valores = {
    "ALLOWED_HOSTS": f"localhost,127.0.0.1,{dominio}",
    "CSRF_TRUSTED_ORIGINS": f"https://{dominio}",
    "DIRECCION_FIJA": f"https://{dominio}",
}
lineas = []
for linea in env.read_text().splitlines():
    clave = linea.split("=", 1)[0]
    if clave in valores:
        linea = f"{clave}={valores.pop(clave)}"
    lineas.append(linea)
lineas += [f"{clave}={valor}" for clave, valor in valores.items()]
env.write_text("\n".join(lineas) + "\n")
EOF
            DIRECCION_FIJA="https://$DOMINIO"
            sudo systemctl restart ecoreporte.service
            hecho "La dirección cambió; el .env ahora usa $DIRECCION_FIJA"
        fi
    else
        mal "Tailscale sigue desconectado. Ejecuta  sudo tailscale up  e inicia sesión con el enlace."
    fi
fi

echo "== 5/6 Arranque automático =="
sudo tee /etc/systemd/system/ecoreporte-vigilar.service > /dev/null <<EOF
[Unit]
Description=Revisa que EcoReporte y su dirección pública sigan funcionando
After=network-online.target ecoreporte.service

[Service]
Type=oneshot
ExecStart=/bin/bash $PROYECTO/servidor/vigilar.sh
EOF
sudo tee /etc/systemd/system/ecoreporte-vigilar.timer > /dev/null <<EOF
[Unit]
Description=Revisa EcoReporte cada 3 minutos

[Timer]
OnBootSec=1min
OnUnitActiveSec=3min

[Install]
WantedBy=timers.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable -q --now ecoreporte-vigilar.timer
sudo systemctl enable -q --now ecoreporte-actualizar.timer 2> /dev/null
# Que la laptop no se suspenda, ni con la tapa cerrada.
sudo mkdir -p /etc/systemd/logind.conf.d
printf '[Login]\nHandleLidSwitch=ignore\nHandleLidSwitchExternalPower=ignore\nHandleLidSwitchDocked=ignore\n' |
    sudo tee /etc/systemd/logind.conf.d/ecoreporte.conf > /dev/null
sudo systemctl mask -q sleep.target suspend.target hibernate.target hybrid-sleep.target
for servicio in ecoreporte.service ecoreporte-vigilar.timer ecoreporte-actualizar.timer; do
    if systemctl is-enabled -q "$servicio"; then
        ok "$servicio arranca al encender."
    else
        mal "$servicio no quedó activado."
    fi
done

echo "== 6/6 Prueba desde internet =="
if [ -n "$DIRECCION_FIJA" ]; then
    PUBLICA=""
    for _ in $(seq 1 10); do
        curl -fsS -o /dev/null --max-time 10 "$DIRECCION_FIJA/" && PUBLICA=1 && break
        sleep 3
    done
    if [ -n "$PUBLICA" ]; then
        ok "La página abre desde internet: $DIRECCION_FIJA"
    else
        mal "Todavía no abre desde internet. Espera 2 minutos y prueba $DIRECCION_FIJA en el celular."
    fi
fi

echo
echo "============================================================"
if [ "$PROBLEMAS" -eq 0 ]; then
    echo " ¡Todo bien! EcoReporte está en línea y arranca solo al encender."
else
    echo " Quedaron $PROBLEMAS problema(s) marcados con [FALLA] arriba."
    echo " Toma una foto de esta pantalla y compártela para revisarlo."
fi
echo "============================================================"

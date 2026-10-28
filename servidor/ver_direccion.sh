#!/bin/bash
# Muestra la dirección pública actual de EcoReporte y el estado de los servicios.
cd "$(dirname "$0")/.."

DIRECCION_FIJA="$(grep -oP '^DIRECCION_FIJA=\K.+' .env 2>/dev/null)"

echo "Aplicación: $(systemctl is-active ecoreporte)"
if [ -n "$DIRECCION_FIJA" ]; then
    echo "Funnel:     $(tailscale funnel status 2>/dev/null | grep -q 'Funnel on' && echo activo || echo 'revisar con: tailscale funnel status')"
    echo
    echo "Dirección pública (fija): $DIRECCION_FIJA"
    exit 0
fi

URL="$(journalctl -u ecoreporte-tunel -b --no-pager 2>/dev/null | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | tail -1)"
echo "Túnel:      $(systemctl is-active ecoreporte-tunel)"
echo
if [ -n "$URL" ]; then
    echo "Dirección pública: $URL"
    echo "(cambia al reiniciar; para una fija:  bash servidor/usar_direccion_fija.sh)"
else
    echo "Todavía no hay dirección. Espera unos segundos y vuelve a intentar."
    echo "Si sigue sin aparecer:  sudo systemctl restart ecoreporte-tunel"
fi

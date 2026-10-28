#!/bin/bash
# Muestra la dirección pública actual de EcoReporte y el estado de los servicios.

URL="$(journalctl -u ecoreporte-tunel -b --no-pager 2>/dev/null | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' | tail -1)"

echo "Aplicación: $(systemctl is-active ecoreporte)"
echo "Túnel:      $(systemctl is-active ecoreporte-tunel)"
echo
if [ -n "$URL" ]; then
    echo "Dirección pública: $URL"
else
    echo "Todavía no hay dirección. Espera unos segundos y vuelve a intentar."
    echo "Si sigue sin aparecer:  sudo systemctl restart ecoreporte-tunel"
fi

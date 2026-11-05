#!/bin/bash
# Mantiene EcoReporte en línea. Lo ejecuta cada 3 minutos el temporizador
# ecoreporte-vigilar.timer (también un minuto después de encender la laptop):
#   - si la página no responde, reinicia el servicio;
#   - si Tailscale está conectado pero el Funnel se apagó, lo vuelve a encender.
# Para ver qué ha hecho:  journalctl -u ecoreporte-vigilar -n 50

if ! curl -s -o /dev/null --max-time 15 http://127.0.0.1:8000/; then
    echo "La página no respondía; se reinicia el servicio."
    systemctl restart ecoreporte
fi

if command -v tailscale > /dev/null && tailscale status > /dev/null 2>&1; then
    if ! tailscale funnel status 2>/dev/null | grep -q 'Funnel on'; then
        echo "El Funnel estaba apagado; se vuelve a encender."
        timeout 60 tailscale funnel --bg 8000
    fi
fi

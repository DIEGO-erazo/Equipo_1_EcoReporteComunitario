#!/bin/bash
# Publica EcoReporte en una dirección https fija y gratuita con Tailscale Funnel
# (https://<nombre>.<tu-red>.ts.net), que no cambia al reiniciar la laptop.
# Reemplaza al túnel temporal de Cloudflare (*.trycloudflare.com).
#
# Requisito: haber ejecutado antes  bash servidor/instalar_servidor.sh
# Uso:       bash servidor/usar_direccion_fija.sh
set -e
cd "$(dirname "$0")/.."

NOMBRE="${NOMBRE:-ecoreporte}"

if [ ! -f .env ] || ! systemctl is-enabled -q ecoreporte 2>/dev/null; then
    echo "Primero ejecuta:  bash servidor/instalar_servidor.sh"
    exit 1
fi

echo "== 1/4 Instalando Tailscale =="
if ! command -v tailscale > /dev/null; then
    curl -fsSL https://tailscale.com/install.sh | sh
fi

echo "== 2/4 Conectando la laptop a tu cuenta de Tailscale =="
if ! tailscale status > /dev/null 2>&1; then
    echo "Se mostrará un enlace: ábrelo en el navegador e inicia sesión (puedes usar tu cuenta de GitHub o Google)."
    sudo tailscale up --hostname="$NOMBRE"
fi

echo "== 3/4 Publicando la página en internet (Funnel) =="
echo "Si aparece un enlace para activar Funnel o HTTPS, ábrelo, actívalo y espera aquí."
sudo tailscale funnel --bg 8000

DOMINIO="$(tailscale status --json | python3 -c 'import json, sys; print(json.load(sys.stdin)["Self"]["DNSName"].rstrip("."))')"
URL="https://$DOMINIO"

echo "== 4/4 Configurando la app para $URL =="
python3 - "$DOMINIO" <<'EOF'
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

# El túnel temporal de Cloudflare ya no hace falta.
sudo systemctl disable --now ecoreporte-tunel.service 2>/dev/null || true
sudo systemctl restart ecoreporte.service

echo
echo "Comprobando..."
for _ in $(seq 1 20); do
    curl -fsS -o /dev/null --max-time 10 "$URL/" && OK=1 && break
    sleep 3
done

echo
echo "============================================================"
if [ -n "$OK" ]; then
    echo " ¡Listo! Dirección fija de EcoReporte:"
else
    echo " Configurado. La primera vez el certificado https puede tardar"
    echo " un par de minutos; luego abre:"
fi
echo "   $URL"
echo " Esta dirección no cambia aunque se reinicie la laptop."
echo "============================================================"

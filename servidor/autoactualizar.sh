#!/bin/bash
# Revisa si hay commits nuevos en GitHub y, si pasaron las pruebas, los instala.
# Lo ejecuta cada 2 minutos el temporizador ecoreporte-actualizar.timer.
# Para ver qué ha hecho:  journalctl -u ecoreporte-actualizar -n 50
#
# Todo está dentro de main(): git puede reemplazar este mismo archivo durante
# la actualización, y así bash ya lo leyó completo antes de que cambie.

main() {
    set -e
    cd "$(dirname "$0")/.."

    # Sigue la rama con la que se clonó el proyecto (por ejemplo, main o una rama de pruebas).
    RAMA="${RAMA:-$(git rev-parse --abbrev-ref HEAD)}"
    git fetch -q origin "$RAMA"
    ACTUAL="$(git rev-parse HEAD)"
    NUEVO="$(git rev-parse "origin/$RAMA")"
    [ "$ACTUAL" = "$NUEVO" ] && exit 0

    # Repositorio en GitHub, a partir de la URL de origin (https o ssh).
    REPO="$(git remote get-url origin | sed -E 's#(\.git)?$##; s#.*github\.com[:/]##')"

    # Estado de las pruebas de GitHub Actions para ese commit: listo, esperar o fallo.
    ESTADO="$(curl -fsS "https://api.github.com/repos/$REPO/commits/$NUEVO/check-runs" \
        | .venv/bin/python -c '
import json, sys, time, subprocess
corridas = json.load(sys.stdin)["check_runs"]
if not corridas:
    # Sin pruebas registradas: se espera 10 minutos por si GitHub aún no las inicia.
    fecha = int(subprocess.check_output(["git", "show", "-s", "--format=%ct", sys.argv[1]]))
    print("listo" if time.time() - fecha > 600 else "esperar")
elif any(c["status"] != "completed" for c in corridas):
    print("esperar")
elif all(c["conclusion"] in ("success", "skipped", "neutral") for c in corridas):
    print("listo")
else:
    print("fallo")
' "$NUEVO")" || { echo "No se pudo consultar GitHub; se intentará más tarde."; exit 0; }

    case "$ESTADO" in
        esperar) echo "Commit ${NUEVO:0:7}: las pruebas aún no terminan."; exit 0 ;;
        fallo)   echo "Commit ${NUEVO:0:7}: las pruebas fallaron en GitHub; NO se instala."; exit 0 ;;
    esac

    echo "Instalando ${ACTUAL:0:7} -> ${NUEVO:0:7}: $(git log -1 --format=%s "$NUEVO")"
    git merge -q --ff-only "origin/$RAMA"

    if ! { .venv/bin/pip install -r requirements.txt gunicorn==23.0.0 -q &&
           .venv/bin/python manage.py migrate --noinput &&
           .venv/bin/python manage.py collectstatic --noinput -v 0; }; then
        echo "Falló la actualización; se regresa a ${ACTUAL:0:7}."
        git reset -q --hard "$ACTUAL"
        exit 1
    fi

    # HUP hace que gunicorn cargue el código nuevo sin cortar las visitas en curso.
    PID="$(systemctl show -p MainPID --value ecoreporte)"
    [ "$PID" != "0" ] && kill -HUP "$PID"
    echo "Actualizado a ${NUEVO:0:7}."
}

main "$@"
exit

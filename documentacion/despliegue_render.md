# Despliegue en Render

EcoReporte Comunitario se publica en [Render](https://render.com) con el plan gratuito: un servicio web con Django y gunicorn, y una base de datos PostgreSQL. El repositorio ya trae todo lo necesario, así que el despliegue se hace con un *Blueprint* y no hace falta escribir ninguna configuración a mano.

## Archivos que usa Render

| Archivo | Para qué sirve |
|---|---|
| `render.yaml` | Describe el servicio web y la base de datos (*Blueprint*). Render lo lee y crea los dos |
| `build.sh` | Se ejecuta en cada despliegue: instala dependencias, reúne los archivos estáticos, aplica las migraciones y carga roles, estados, categorías y datos de ejemplo |
| `requirements.txt` | Incluye `gunicorn` (servidor web) y `psycopg` (conexión a PostgreSQL) |
| `config/settings.py` | Si existe `DATABASE_URL`, usa PostgreSQL. Acepta sola la dirección que Render publica en `RENDER_EXTERNAL_HOSTNAME` |

### Variables de entorno

Render las crea solas a partir de `render.yaml`:

| Variable | Valor | Por qué |
|---|---|---|
| `DATABASE_URL` | La conexión a la base `ecoreporte-db` | Django se conecta a PostgreSQL |
| `SECRET_KEY` | Generada por Render | Clave secreta única, fuera del repositorio |
| `DEBUG` | `False` | No muestra errores internos al público |
| `DEMO_ADMIN_CONTRASENA` y `DEMO_VECINA_CONTRASENA` | Generadas por Render | Las cuentas de ejemplo no usan las contraseñas públicas del README |
| `PYTHON_VERSION` | `3.13.5` | La misma versión que en desarrollo |

## Pasos para publicar

1. Entra a [dashboard.render.com](https://dashboard.render.com) e inicia sesión con **GitHub**.
2. Pulsa **New ▸ Blueprint**.
3. Si Render lo pide, autoriza el acceso al repositorio `DIEGO-erazo/Equipo_1_EcoReporteComunitario` y elígelo.
4. Render muestra lo que va a crear: `ecoreporte-db` (PostgreSQL) y `ecoreporte-comunitario` (servicio web). Escribe un nombre para el Blueprint y pulsa **Deploy Blueprint**.
5. Espera a que el servicio pase a **Live**. El primer despliegue tarda de 3 a 6 minutos y se puede seguir en la pestaña **Logs**.
6. Abre la dirección que aparece arriba del servicio, por ejemplo `https://ecoreporte-comunitario.onrender.com`.
7. Para entrar como administrador, abre el servicio, ve a **Environment** y copia el valor de `DEMO_ADMIN_CONTRASENA`. El usuario es `admin@ecoreporte.local`.

Cada `git push` a la rama `main` vuelve a desplegar la aplicación automáticamente.

### Correo (opcional)

Sin configurar el correo, los mensajes (recuperar contraseña, aviso de cambio de estado) solo quedan escritos en los **Logs** de Render. Para enviarlos de verdad, añade en **Environment** las variables `CORREO_USUARIO` y `CORREO_CONTRASENA` con una contraseña de aplicación de Gmail. Los pasos están en [recuperar_contrasena.md](recuperar_contrasena.md).

## Cómo se probó antes de publicar

Se reprodujo el despliegue en un contenedor Linux con Python 3.13 y PostgreSQL 17, con las mismas variables que usa Render:

| Prueba | Resultado |
|---|---|
| `build.sh` completo | 145 archivos estáticos, migraciones aplicadas, 3 reportes y 2 cuentas de ejemplo |
| `build.sh` por segunda vez | No duplica datos |
| 63 pruebas automáticas sobre PostgreSQL | Todas correctas |
| Páginas con gunicorn y `DEBUG=False` | Inicio, reportes, mapa, detalle e ingreso responden 200; CSS y JavaScript se sirven; una página inexistente da 404 |
| Ingreso con la contraseña pública del README | Rechazado |
| Ingreso con la contraseña generada | Correcto: panel de gestión, nuevo reporte y descargas en Excel y PDF |

GitHub Actions también ejecuta las pruebas sobre PostgreSQL en cada cambio (`.github/workflows/pruebas.yml`).

## Limitaciones del plan gratuito

| Limitación | Efecto | Qué hacer |
|---|---|---|
| El servicio se duerme tras 15 minutos sin visitas | La primera visita tarda unos 50 segundos | Abrir la página un minuto antes de la demostración |
| La base de datos gratuita vence a los 30 días | Render avisa por correo y después la borra | Para la evaluación alcanza; luego se puede crear otra o pasar a un plan de pago |
| El disco del servicio no es permanente | Las fotos de evidencia subidas se pierden al volver a desplegar o reiniciar | Para uso real, guardar las fotos en un almacenamiento externo o en un disco de Render de pago. Los reportes y su historial sí quedan en PostgreSQL |
| Sin correo configurado | Los avisos solo aparecen en los Logs | Ver «Correo (opcional)» |

El servidor propio del equipo (Ubuntu con Tailscale Funnel, ver el README) sigue funcionando en paralelo y no tiene estas limitaciones.

## Problemas posibles

| Síntoma | Causa | Solución |
|---|---|---|
| `DisallowedHost` | Se abrió con otra dirección (dominio propio) | Añadirla a `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` en **Environment** |
| Error 403 CSRF al ingresar | Se abrió por `http://` | Usar siempre `https://` |
| El despliegue falla en `build.sh: Permission denied` | El archivo perdió el permiso de ejecución | En *Settings*, cambiar *Build Command* por `bash build.sh` |
| `Error loading psycopg` en Windows | Una política de Windows bloquea la librería de PostgreSQL | Solo afecta a la computadora local: en Render (Linux) funciona. En local usar SQLite o SQL Server |

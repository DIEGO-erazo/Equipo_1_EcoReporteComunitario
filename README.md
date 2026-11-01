# 🍃 EcoReporte Comunitario

**Universidad Dr. Andrés Bello**  
**Carrera:** Ingeniería en Sistemas y Computación  
**Asignatura:** Programación Orientada a Objetos (POO)  
**Proyecto de Proyección Social — Ciclo 02-2026**  
**Ubicación:** Comunidad de San Rafael e Instituto Nacional de San Rafael, distrito de San Rafael, Chalatenango, El Salvador.

## 1. Descripción del proyecto

EcoReporte Comunitario es una aplicación web desarrollada con Python, Django y Microsoft SQL Server, orientada al registro y seguimiento de problemáticas ambientales en la comunidad de San Rafael.

El proyecto busca facilitar la comunicación entre habitantes, instituciones educativas y responsables comunitarios mediante una plataforma para organizar información sobre botaderos clandestinos, acumulación de basura y problemas en la recolección de residuos.

## 2. Objetivos

### Objetivo general

Desarrollar una aplicación web que facilite el registro, consulta y seguimiento de problemas ambientales de la comunidad.

### Objetivos específicos

- Organizar la información de los reportes ambientales.
- Establecer una estructura modular mediante Django.
- Utilizar una base de datos relacional con SQL Server.
- Aplicar conceptos de programación orientada a objetos.
- Gestionar el código fuente mediante Git y GitHub.

## 3. Integrantes y responsabilidades

| Integrante | Carnet | Rol |
|---|---|---|
| Patrick Alejandro Alvarenga Cardoza | ac0473032026 | Líder de proyecto |
| Jefersson Javier Galdámez Mejía | gm1366032026 | Analista de requerimientos |
| Diego Fabricio Erazo Deras | ed0921032026 | Líder técnico y administrador de Git |
| Victor Angel Rivas Torres | rt0234032026 | Diseñador UX/UI y frontend |
| Geovany Enmanuel Alas Orellana | ao0922032026 | Desarrollador backend y QA |

## 4. Tecnologías utilizadas

- Python 3.12 o superior
- Django 6.1
- Microsoft SQL Server (también funciona con SQLite para pruebas rápidas)
- `mssql-django` y `mssql-python` (este último ya incluye el ODBC Driver 18)
- Docker y Docker Compose (opcional, para levantar todos los servicios con un solo comando)
- Git y GitHub (con pruebas automáticas en GitHub Actions)

## 5. Estructura del repositorio

```text
Equipo_1_EcoReporteComunitario/
├── config/                  # Configuración de Django (settings, urls, wsgi)
├── usuarios/                # Registro, inicio de sesión, perfil y roles
├── reportes/                # Reportes, categorías, estados, evidencias y seguimiento
│   ├── management/commands/cargar_datos_iniciales.py
│   └── templatetags/interfaz.py  # Filtro que aplica las clases de Bootstrap a los formularios
├── gestion/                 # Panel para administradores: categorías, estados y usuarios
├── templates/               # Páginas HTML (base.html, parciales/ y una carpeta por app)
├── static/                  # Estilos (CSS), imágenes y Bootstrap 5.3 (static/vendor/)
├── docker/                  # Scripts usados por el contenedor
├── documentacion/           # Documentos de las tareas del curso
├── Dockerfile
├── docker-compose.yml       # SQL Server + aplicación web
├── iniciar.bat / iniciar.sh # Instalación y arranque en un solo paso
├── .env.example             # Plantilla de configuración
├── manage.py
└── requirements.txt
```

## 6. Funcionalidades

- **Cuentas de usuario:** registro con correo, inicio y cierre de sesión, edición del perfil y cambio de contraseña.
- **Recuperar la contraseña por correo:** enlace "¿Olvidaste tu contraseña?" en la página de ingreso. Para que el servidor envíe los correos, ver [documentacion/recuperar_contrasena.md](documentacion/recuperar_contrasena.md).
- **Reportes ambientales:** crear, ver, editar y eliminar reportes con título, categoría, descripción, ubicación y coordenadas opcionales (con enlace al mapa).
- **Evidencias fotográficas:** se pueden subir varias fotos por reporte (máximo 5 MB cada una).
- **Búsqueda y filtros:** por texto, categoría y estado, con paginación.
- **Seguimiento:** los administradores cambian el estado (Pendiente, En proceso, Resuelto, Rechazado) con un comentario; cada cambio queda en el historial del reporte.
- **Roles y permisos:** cada ciudadano solo puede editar sus propios reportes; los administradores pueden gestionar todos.
- **Gestión (solo administradores):** panel con estadísticas y CRUD de categorías, estados y usuarios
  (cambiar rol, desactivar o eliminar cuentas) sin entrar al panel de Django. No se puede eliminar una
  categoría o estado que tenga reportes, ni renombrar los cuatro estados que usa el sistema.
- **Inicio con estadísticas** y panel de administración de Django en `/admin/`.
- **Interfaz con Bootstrap 5.3**, adaptable a teléfonos (menú desplegable, tablas y tarjetas responsivas).
  Bootstrap va incluido en el proyecto, así que el sitio se ve bien aunque no haya internet.

### Rutas principales

| URL | Nombre | Qué hace | Quién |
|---|---|---|---|
| `/` | `inicio` | Portada con estadísticas y reportes recientes | Todos |
| `/reportes/` | `reportes:lista` | Lista con búsqueda, filtros y paginación | Todos |
| `/reportes/<id>/` | `reportes:detalle` | Detalle, fotos e historial de seguimiento | Todos |
| `/reportes/nuevo/` | `reportes:crear` | Registrar un reporte con fotos | Con sesión |
| `/reportes/<id>/editar/` | `reportes:editar` | Modificar un reporte | Autor o administrador |
| `/reportes/<id>/eliminar/` | `reportes:eliminar` | Eliminar un reporte (pide confirmación) | Autor o administrador |
| `/reportes/<id>/estado/` | `reportes:cambiar_estado` | Cambiar el estado con un comentario | Administrador |
| `/reportes/mios/` | `reportes:mis_reportes` | Reportes de la persona conectada | Con sesión |
| `/ingresar/`, `/salir/` | `login`, `logout` | Iniciar y cerrar sesión | Todos |
| `/usuarios/registro/` | `usuarios:registro` | Crear cuenta | Todos |
| `/usuarios/perfil/` | `usuarios:perfil` | Ver y editar el perfil | Con sesión |
| `/usuarios/recuperar/` | `usuarios:recuperar` (+ `_enviado`, `_confirmar`, `_listo`) | Recuperar la contraseña por correo | Todos |
| `/gestion/` | `gestion:panel` | Panel con estadísticas | Administrador |
| `/gestion/categorias/` | `gestion:categorias` (+ `_crear`, `_editar`, `_eliminar`) | CRUD de categorías | Administrador |
| `/gestion/estados/` | `gestion:estados` (+ `_crear`, `_editar`, `_eliminar`) | CRUD de estados | Administrador |
| `/gestion/usuarios/` | `gestion:usuarios` (+ `_editar`, `_eliminar`) | Buscar, editar y eliminar usuarios | Administrador |

## 7. Cómo ejecutar el proyecto

Hay tres formas. La más sencilla es la **opción A**.

### Opción A: un solo paso (Windows, macOS o Linux)

Requisitos: [Python](https://www.python.org/downloads/) 3.12 o superior (en Windows, marca "Add Python to PATH" al instalarlo).

```powershell
git clone https://github.com/DIEGO-erazo/Equipo_1_EcoReporteComunitario.git
cd Equipo_1_EcoReporteComunitario
```

- **Windows:** doble clic en `iniciar.bat` (o ejecuta `.\iniciar.bat` en la terminal).
- **macOS / Linux:** `./iniciar.sh`

El script crea el entorno virtual, instala las dependencias, prepara la base de datos (SQLite por defecto), carga datos de ejemplo e inicia el servidor. Luego abre http://127.0.0.1:8000.

### Opción B: con Docker (todos los servicios: SQL Server + aplicación)

Requisitos: [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```powershell
docker compose up --build
```

Esto levanta **SQL Server 2022**, crea la base de datos `EcoReporteDB`, aplica las migraciones, carga los datos iniciales y de ejemplo, e inicia la aplicación en http://localhost:8000. Para detenerlo: `Ctrl+C` o `docker compose down`. Los datos se conservan entre ejecuciones; para borrarlos usa `docker compose down -v`.

SQL Server queda disponible en `localhost,1433` (usuario `sa`, contraseña `EcoReporte#2026`) para consultarlo con SQL Server Management Studio o Azure Data Studio.

### Opción C: paso a paso con SQL Server local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Edita `.env`: cambia a `DB_ENGINE=mssql` y descomenta las líneas de SQL Server. Si dejas `DB_USER` vacío se usa la autenticación integrada de Windows, igual que en la configuración anterior del proyecto. La base `EcoReporteDB` debe existir en el servidor.

```powershell
python manage.py migrate
python manage.py cargar_datos_iniciales          # roles, estados y categorías
python manage.py cargar_datos_iniciales --demo   # (opcional) usuarios y reportes de ejemplo
python manage.py createsuperuser                 # (opcional) tu propia cuenta de administrador
python manage.py runserver
```

### Cuentas de ejemplo

Se crean con `--demo` (y automáticamente con las opciones A y B):

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@ecoreporte.local | admin12345 |
| Ciudadana | vecina@ecoreporte.local | vecina12345 |

> Cambia o elimina estas cuentas antes de usar la aplicación con datos reales.

### Iniciar sesión con Google, GitHub o Microsoft

Es opcional. Cada botón aparece al poner las credenciales de su proveedor en el `.env`.
Los pasos para obtenerlas están en [documentacion/inicio_sesion_social.md](documentacion/inicio_sesion_social.md).

### Opción D: publicarla en internet desde una computadora con Ubuntu

Convierte una laptop (por ejemplo, una de las entregadas por el gobierno) en el servidor de la página.
Usa SQLite, gunicorn y **Cloudflare Tunnel**, que da una dirección `https://` pública gratis sin
configurar el router. En la laptop:

```bash
git clone https://github.com/DIEGO-erazo/Equipo_1_EcoReporteComunitario.git
cd Equipo_1_EcoReporteComunitario
bash servidor/instalar_servidor.sh   # instala todo; pide crear la cuenta de administrador
bash servidor/ver_direccion.sh       # muestra la dirección pública actual
journalctl -u ecoreporte-actualizar -n 50   # historial de actualizaciones automáticas
```

Cada 2 minutos la laptop revisa en GitHub la rama que se clonó (`main`, o la que se indique con
`git clone -b <rama> ...` para probar una rama sin tocar `main`). Cuando hay un commit nuevo **y pasó
las pruebas de GitHub Actions**, lo descarga, aplica las migraciones y recarga la app sin cortar las
visitas; si las pruebas fallan, no se instala. Si algo falla durante la actualización, regresa sola
a la versión anterior. `bash servidor/actualizar.sh` hace una actualización manual inmediata.

La app y el túnel arrancan solos al encender la laptop, que sigue funcionando con la tapa cerrada.
Cada día se guarda un respaldo de la base de datos y las fotos en `~/respaldos_ecoreporte`.
La dirección gratuita (`*.trycloudflare.com`) cambia cada vez que se reinicia la laptop. Para una
**dirección fija y gratuita** (`https://ecoreporte.<tu-red>.ts.net`) con Tailscale Funnel:

```bash
bash servidor/usar_direccion_fija.sh   # pide iniciar sesión en Tailscale y activar Funnel
```

### Ejecutar las pruebas

```powershell
python manage.py test
```

Las pruebas se ejecutan automáticamente en GitHub Actions con SQLite y con SQL Server en cada `push`.

## 8. Programación orientada a objetos

Los modelos de Django son clases de Python que representan las tablas de la base de datos. La clase `ReporteAmbiental` (`reportes/models.py`) incluye, además de sus atributos, los métodos:

- `mostrar_informacion()`: devuelve un resumen legible del reporte.
- `cambiar_estado(nuevo_estado, responsable, comentario)`: cambia el estado y registra el cambio en la tabla de seguimiento, todo en una sola transacción.
- `puede_editar(perfil)`: indica si un usuario puede modificar el reporte.

Otros ejemplos de POO en el proyecto: la clase `Usuario` con las propiedades `nombre_completo` y `es_administrador`, el método de clase `Estado.inicial()`, la herencia en los formularios (`RegistroForm` hereda de `UserCreationForm`) y en el comando `cargar_datos_iniciales` (hereda de `BaseCommand`).

## 9. Base de datos

Tablas principales (los nombres coinciden con el diseño del proyecto):

| Tabla | Contenido |
|---|---|
| `roles` | Ciudadano, Administrador |
| `usuarios` | Perfil de cada persona; se enlaza con la cuenta de acceso de Django (`auth_user`) |
| `categorias` | Botadero clandestino, Acumulación de basura, Recolección de residuos, etc. |
| `estados` | Pendiente, En proceso, Resuelto, Rechazado |
| `reportes` | Reportes ambientales |
| `evidencias` | Fotos de cada reporte (la imagen se guarda en la carpeta `media/`) |
| `seguimiento_reporte` | Historial de cambios de estado |

Las contraseñas las cifra el sistema de autenticación de Django en `auth_user`. La columna `contrasena_hash` de `usuarios` se conserva por compatibilidad, pero ya no se usa.

**Si ya tenían la base de datos creada:** basta con ejecutar `python manage.py migrate`; las nuevas migraciones agregan la columna `cuenta_id` sin borrar datos. Los usuarios creados antes no tienen contraseña de Django: se pueden enlazar a una cuenta desde `/admin/` o registrarse de nuevo.

## 10. Control de versiones

El código fuente se almacena en GitHub y se administra mediante Git para registrar los cambios realizados durante el desarrollo.

**Repositorio oficial:**  
https://github.com/DIEGO-erazo/Equipo_1_EcoReporteComunitario

Comandos básicos para registrar y enviar cambios:

```powershell
git status
git add .
git commit -m "Descripción de los cambios"
git push
```

## 11. Seguridad

La configuración se lee del archivo `.env` (excluido de Git) o de variables de entorno, por lo que las claves y contraseñas no se guardan en el repositorio. Antes de publicar la aplicación se debe definir un `SECRET_KEY` propio, usar `DEBUG=False` y cambiar la contraseña de SQL Server y de las cuentas de ejemplo.

El archivo `.gitignore` debe excluir el entorno virtual, archivos temporales, bases de datos locales y archivos que contengan información sensible.

## 12. Estado del proyecto

La aplicación es funcional: registro e inicio de sesión, gestión completa de reportes con fotos, búsqueda y filtros, seguimiento de estados por parte de los administradores y panel de administración, con pruebas automáticas.

Posibles mejoras futuras: mapa interactivo de reportes, notificaciones por correo al cambiar el estado y exportación de reportes a Excel o PDF.

## 13. Información académica

**Institución:** Universidad Dr. Andrés Bello  
**Carrera:** Ingeniería en Sistemas y Computación  
**Asignatura:** Programación Orientada a Objetos  
**Proyecto:** EcoReporte Comunitario  
**Ciclo:** 02-2026  
**Equipo:** N.º 1

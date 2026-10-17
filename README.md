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

- Python
- Django
- Microsoft SQL Server
- `mssql-django`
- ODBC Driver 18 for SQL Server
- Git y GitHub
- Visual Studio Code

## 5. Estructura del repositorio

El repositorio contiene la configuración principal de Django, la aplicación de reportes y archivos de documentación del proyecto.

```text
Equipo_1_EcoReporteComunitario/
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── reportes/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── migrations/
├── ecoreporte_app/
├── ecoreporte_project/
├── docs/
├── documentacion/
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Archivos principales

- `manage.py`: punto de entrada para ejecutar comandos de Django.
- `config/settings.py`: configuración general del proyecto y de la base de datos.
- `config/urls.py`: configuración de rutas.
- `reportes/`: aplicación destinada a las funcionalidades relacionadas con los reportes ambientales.
- `reportes/models.py`: contiene la clase Python `ReporteAmbiental`.
- `requirements.txt`: lista de dependencias de Python.
- `.gitignore`: define archivos y carpetas excluidos del control de versiones.
- `README.md`: documentación general del proyecto.

## 6. Requisitos de instalación

Para ejecutar el proyecto se requiere:

- Python instalado.
- Git instalado.
- Microsoft SQL Server disponible.
- ODBC Driver 18 for SQL Server.
- Acceso a la base de datos `EcoReporteDB`.

## 7. Instalación y ejecución

### 7.1. Clonar el repositorio

```powershell
git clone https://github.com/DIEGO-erazo/Equipo_1_EcoReporteComunitario.git
cd Equipo_1_EcoReporteComunitario
```

### 7.2. Crear y activar el entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 7.3. Instalar las dependencias

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 7.4. Configurar la base de datos

En `config/settings.py`, Django utiliza el motor `mssql` y la base de datos `EcoReporteDB`. La configuración local emplea autenticación integrada de Windows y el controlador ODBC Driver 18 for SQL Server.

El servidor y las credenciales de conexión deben corresponder al entorno donde se ejecuta la aplicación. No se deben incluir contraseñas ni claves secretas en el repositorio.

### 7.5. Verificar la configuración de Django

```powershell
python manage.py check
```

### 7.6. Comprobar la conexión con SQL Server

```powershell
python manage.py shell -c "from django.db import connection; connection.ensure_connection(); print('CONEXION EXITOSA'); print(connection.vendor); print(connection.settings_dict['NAME'])"
```

### 7.7. Ejecutar las migraciones

```powershell
python manage.py migrate
```

### 7.8. Iniciar el servidor de desarrollo

```powershell
python manage.py runserver
```

La aplicación se puede consultar localmente en:

http://127.0.0.1:8000/

## 8. Programación orientada a objetos

El proyecto incorpora una clase Python denominada `ReporteAmbiental`, ubicada en `reportes/models.py`.

La clase define los siguientes atributos:

- `titulo`: título del reporte.
- `descripcion`: descripción del problema.
- `ubicacion`: lugar donde se presenta.
- `tipo`: categoría o tipo de problema.
- `estado`: estado inicial del reporte, establecido como `Pendiente`.

También contiene los métodos:

- `mostrar_informacion()`: devuelve una descripción del reporte.
- `cambiar_estado(nuevo_estado)`: actualiza el estado del objeto.

Esta clase representa la estructura inicial de un reporte ambiental mediante atributos y métodos de Python.

## 9. Base de datos

La base de datos utilizada por la configuración local se denomina `EcoReporteDB` y corresponde a Microsoft SQL Server.

Django se conecta mediante `mssql-django` y ODBC Driver 18 for SQL Server. La conexión fue comprobada desde la consola de Django.

La definición de modelos persistentes, sus relaciones y las migraciones correspondientes forman parte de la evolución de la estructura de datos de la aplicación.

## 10. Funcionalidades contempladas

De acuerdo con los requerimientos definidos para el proyecto, la plataforma está orientada a incorporar:

- Registro y autenticación de usuarios.
- Creación y consulta de reportes ambientales.
- Clasificación de reportes por categoría.
- Incorporación de evidencias fotográficas.
- Búsqueda y filtrado de reportes.
- Actualización del estado y seguimiento de los casos.
- Gestión de usuarios, roles y permisos.

Estas funcionalidades corresponden al alcance definido en los requisitos del proyecto; su disponibilidad depende de la implementación de cada componente.

## 11. Control de versiones

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

## 12. Seguridad

La configuración de desarrollo no debe utilizarse directamente en producción. Las claves secretas y credenciales deben mantenerse fuera del repositorio y gestionarse mediante variables de entorno o mecanismos de configuración seguros.

El archivo `.gitignore` debe excluir el entorno virtual, archivos temporales, bases de datos locales y archivos que contengan información sensible.

## 13. Estado del proyecto

El proyecto cuenta con una estructura inicial de Django, una aplicación destinada a los reportes ambientales, una página de inicio funcional y una configuración de conexión con SQL Server.

El desarrollo continuará con la definición de modelos de datos, migraciones, formularios, operaciones CRUD y las funcionalidades descritas en los requerimientos.

## 14. Información académica

**Institución:** Universidad Dr. Andrés Bello  
**Carrera:** Ingeniería en Sistemas y Computación  
**Asignatura:** Programación Orientada a Objetos  
**Proyecto:** EcoReporte Comunitario  
**Ciclo:** 02-2026  
**Equipo:** N.º 1

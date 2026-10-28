"""
Configuración de Django para EcoReporte Comunitario.

Los valores sensibles y los que cambian entre computadoras (clave secreta,
modo debug, base de datos) se leen de variables de entorno o de un archivo
.env en la raíz del proyecto. Ver .env.example.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


def env_bool(nombre, por_defecto=False):
    valor = os.getenv(nombre)
    if valor is None:
        return por_defecto
    return valor.strip().lower() in ("1", "true", "yes", "si", "sí", "on")


def env_list(nombre, por_defecto=""):
    return [v.strip() for v in os.getenv(nombre, por_defecto).split(",") if v.strip()]


# SECURITY WARNING: en producción define SECRET_KEY en el entorno.
SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-solo-para-desarrollo-cambiar-en-produccion",
)

DEBUG = env_bool("DEBUG", True)

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    # Inicio de sesión con Google, GitHub y Microsoft:
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.microsoft',
    # Aplicaciones del proyecto EcoReporte Comunitario:
    'usuarios',
    'reportes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'usuarios.context_processors.perfil',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Base de datos
# DB_ENGINE=sqlite (por defecto, no requiere instalar nada) o DB_ENGINE=mssql.

DB_ENGINE = os.getenv("DB_ENGINE", "sqlite").strip().lower()

if DB_ENGINE == "mssql":
    DB_USER = os.getenv("DB_USER", "")
    opciones_mssql = {
        'driver': os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server"),
        'extra_params': 'TrustServerCertificate=yes;',
    }
    if os.getenv("DB_PYTHON_DRIVER"):
        # Driver "mssql_python": no requiere instalar el ODBC Driver por separado.
        opciones_mssql['python_driver'] = os.getenv("DB_PYTHON_DRIVER")
    if not DB_USER:
        # Sin usuario: autenticación integrada de Windows.
        opciones_mssql['trusted_connection'] = 'yes'

    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': os.getenv("DB_NAME", "EcoReporteDB"),
            'HOST': os.getenv("DB_HOST", "localhost"),
            'PORT': os.getenv("DB_PORT", ""),
            'USER': DB_USER,
            'PASSWORD': os.getenv("DB_PASSWORD", ""),
            'OPTIONS': opciones_mssql,
        },
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / os.getenv("DB_NAME_SQLITE", "db.sqlite3"),
        }
    }

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'inicio'
LOGOUT_REDIRECT_URL = 'inicio'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]


# Inicio de sesión con Google, GitHub y Microsoft (django-allauth).
# Cada proveedor se activa al poner su ID y clave en el .env; si faltan, su
# botón no aparece. Cómo obtenerlas: documentacion/inicio_sesion_social.md

SOCIALACCOUNT_PROVIDERS = {}
for proveedor, ajustes in {
    'google': {'SCOPE': ['profile', 'email']},
    'github': {'SCOPE': ['user:email']},
    'microsoft': {'TENANT': 'common'},  # cuentas personales (Outlook/Hotmail) y de trabajo o escuela
}.items():
    client_id = os.getenv(f"{proveedor.upper()}_CLIENT_ID", "").strip()
    secreto = os.getenv(f"{proveedor.upper()}_CLIENT_SECRET", "").strip()
    if client_id and secreto:
        SOCIALACCOUNT_PROVIDERS[proveedor] = {**ajustes, 'APPS': [{'client_id': client_id, 'secret': secreto}]}

ACCOUNT_ADAPTER = 'usuarios.adaptadores.AdaptadorCuenta'
SOCIALACCOUNT_ADAPTER = 'usuarios.adaptadores.AdaptadorCuentaSocial'
ACCOUNT_LOGIN_METHODS = {'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*']
# No hay servidor de correo configurado; el proveedor ya confirmó el correo.
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_QUERY_EMAIL = True
# Si el correo ya tiene cuenta en EcoReporte, se entra a esa cuenta en vez de crear otra.
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'http' if DEBUG else 'https'


# Internacionalización

LANGUAGE_CODE = 'es'

TIME_ZONE = 'America/El_Salvador'

USE_I18N = True

USE_TZ = True


# Archivos estáticos y fotos subidas

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Permite servir los estáticos sin ejecutar collectstatic (útil en desarrollo).
WHITENOISE_USE_FINDERS = True

MEDIA_URL = 'media/'
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", BASE_DIR / 'media'))

# Tamaño máximo de cada foto de evidencia (5 MB).
MAX_TAMANO_EVIDENCIA = 5 * 1024 * 1024


# Email

MAILERS = {
    'default': {
        'BACKEND': 'django.core.mail.backends.console.EmailBackend',
    },
}


if not DEBUG:
    SESSION_COOKIE_SECURE = env_bool("SECURE_COOKIES", True)
    CSRF_COOKIE_SECURE = env_bool("SECURE_COOKIES", True)

if env_bool("DETRAS_DE_PROXY"):
    # Cloudflare Tunnel (u otro proxy) recibe la conexión HTTPS y la reenvía
    # a gunicorn por HTTP; este encabezado le avisa a Django que era segura.
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

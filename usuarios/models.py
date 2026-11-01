from django.conf import settings
from django.db import models


class Rol(models.Model):
    CIUDADANO = 'Ciudadano'
    ADMINISTRADOR = 'Administrador'

    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre_rol

    class Meta:
        db_table = 'roles'
        verbose_name = 'rol'
        verbose_name_plural = 'roles'
        ordering = ['nombre_rol']


class Usuario(models.Model):
    """Perfil de una persona de la comunidad.

    El inicio de sesión y la contraseña los maneja el sistema de autenticación
    de Django (tabla auth_user); este perfil se enlaza con esa cuenta mediante
    el campo ``cuenta``.
    """

    id_usuario = models.AutoField(primary_key=True)
    cuenta = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='perfil',
        null=True,
        blank=True,
    )
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(max_length=150, unique=True)
    # Se conserva por compatibilidad con el diseño de la base de datos;
    # la contraseña real se guarda cifrada en auth_user.
    contrasena_hash = models.CharField(max_length=256, blank=True, default='')
    telefono = models.CharField(max_length=15, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    id_rol = models.ForeignKey(Rol, on_delete=models.PROTECT, db_column='id_rol', verbose_name='rol')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def es_administrador(self):
        if self.cuenta_id and (self.cuenta.is_staff or self.cuenta.is_superuser):
            return True
        return self.id_rol.nombre_rol == Rol.ADMINISTRADOR

    @classmethod
    def para_cuenta(cls, cuenta):
        """Devuelve el perfil de una cuenta de Django, creándolo si no existe
        (por ejemplo, para un superusuario creado con createsuperuser)."""
        try:
            return cuenta.perfil
        except cls.DoesNotExist:
            pass
        nombre_rol = Rol.ADMINISTRADOR if cuenta.is_staff else Rol.CIUDADANO
        rol, _ = Rol.objects.get_or_create(nombre_rol=nombre_rol)
        correo = cuenta.email or f"{cuenta.username}@ecoreporte.local"
        perfil, _ = cls.objects.update_or_create(
            correo=correo,
            defaults={
                'cuenta': cuenta,
                'nombre': cuenta.first_name or cuenta.username,
                'apellido': cuenta.last_name,
                'id_rol': rol,
            },
        )
        return perfil

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'usuario'
        verbose_name_plural = 'usuarios'
        ordering = ['nombre', 'apellido']

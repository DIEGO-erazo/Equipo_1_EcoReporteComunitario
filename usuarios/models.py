from django.db import models

class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre_rol

    class Meta:
        db_table = 'roles'


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(max_length=150, unique=True)
    contrasena_hash = models.CharField(max_length=256)
    telefono = models.CharField(max_length=15, null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE, db_column='id_rol')

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        db_table = 'usuarios'
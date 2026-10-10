from django.db import models

class Usuario(models.Model):
    ROLES = [
        ('Ciudadano', 'Ciudadano'),
        ('Administrador', 'Administrador'),
    ]
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    contrasena_hash = models.CharField(max_length=256)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    rol = models.CharField(max_length=50, choices=ROLES, default='Ciudadano')

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol})"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre


class ReporteAmbiental(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('En Proceso', 'En Proceso'),
        ('Resuelto', 'Resuelto'),
        ('Rechazado', 'Rechazado'),
    ]

    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    ubicacion = models.CharField(max_length=200)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Relaciones definidas en el análisis de clases y base de datos
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='reportes', null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='reportes')
    estado = models.CharField(max_length=50, choices=ESTADOS, default='Pendiente')

    def __str__(self):
        return self.titulo


class Seguimiento(models.Model):
    reporte = models.ForeignKey(ReporteAmbiental, on_delete=models.CASCADE, related_name='seguimientos')
    responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='seguimientos_realizados', null=True, blank=True)
    estado_anterior = models.CharField(max_length=50)
    estado_nuevo = models.CharField(max_length=50)
    comentario = models.TextField(blank=True, null=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Seguimiento para {self.reporte.titulo} - {self.estado_nuevo}"
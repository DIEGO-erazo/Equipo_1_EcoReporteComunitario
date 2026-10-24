from django.db import models
from usuarios.models import Usuario

class CategoriaProblema(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre_categoria

    class Meta:
        db_table = 'categorias'


class Estado(models.Model):
    id_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre_estado

    class Meta:
        db_table = 'estados'


class ReporteAmbiental(models.Model):
    id_reporte = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField()
    ubicacion_direccion = models.CharField(max_length=255)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)
    
    # Relaciones ForeignKey con otras tablas:
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    id_categoria = models.ForeignKey(CategoriaProblema, on_delete=models.CASCADE, db_column='id_categoria')
    id_estado = models.ForeignKey(Estado, on_delete=models.CASCADE, db_column='id_estado')

    def __str__(self):
        return self.titulo

    class Meta:
        db_table = 'reportes'


class Evidencia(models.Model):
    id_evidencia = models.AutoField(primary_key=True)
    id_reporte = models.ForeignKey(ReporteAmbiental, on_delete=models.CASCADE, db_column='id_reporte')
    url_imagen = models.CharField(max_length=500)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia #{self.id_evidencia}"

    class Meta:
        db_table = 'evidencias'


class Seguimiento(models.Model):
    id_seguimiento = models.AutoField(primary_key=True)
    id_reporte = models.ForeignKey(ReporteAmbiental, on_delete=models.CASCADE, db_column='id_reporte')
    id_usuario_responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario_responsable')
    id_estado_anterior = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='seguimientos_anterior', db_column='id_estado_anterior')
    id_estado_nuevo = models.ForeignKey(Estado, on_delete=models.CASCADE, related_name='seguimientos_nuevo', db_column='id_estado_nuevo')
    comentario = models.TextField(null=True, blank=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Seguimiento #{self.id_seguimiento}"

    class Meta:
        db_table = 'seguimiento_reporte'
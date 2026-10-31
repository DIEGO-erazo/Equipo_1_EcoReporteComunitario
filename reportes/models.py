from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse

from usuarios.models import Usuario


class CategoriaProblema(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(max_length=100, unique=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre_categoria

    class Meta:
        db_table = 'categorias'
        verbose_name = 'categoría'
        verbose_name_plural = 'categorías'
        ordering = ['nombre_categoria']


class Estado(models.Model):
    PENDIENTE = 'Pendiente'
    EN_PROCESO = 'En proceso'
    RESUELTO = 'Resuelto'
    RECHAZADO = 'Rechazado'
    # Estados que el código usa por nombre; no se pueden renombrar ni eliminar.
    DEL_SISTEMA = (PENDIENTE, EN_PROCESO, RESUELTO, RECHAZADO)

    id_estado = models.AutoField(primary_key=True)
    nombre_estado = models.CharField(max_length=50, unique=True)
    descripcion = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.nombre_estado

    @classmethod
    def inicial(cls):
        estado, _ = cls.objects.get_or_create(
            nombre_estado__iexact=cls.PENDIENTE,
            defaults={'nombre_estado': cls.PENDIENTE},
        )
        return estado

    @property
    def es_del_sistema(self):
        return self.nombre_estado.lower() in {nombre.lower() for nombre in self.DEL_SISTEMA}

    @property
    def clase_css(self):
        """Nombre corto usado por las plantillas para dar color a la etiqueta."""
        return {
            self.PENDIENTE.lower(): 'pendiente',
            self.EN_PROCESO.lower(): 'proceso',
            self.RESUELTO.lower(): 'resuelto',
            self.RECHAZADO.lower(): 'rechazado',
        }.get(self.nombre_estado.lower(), 'pendiente')

    class Meta:
        db_table = 'estados'
        verbose_name = 'estado'
        verbose_name_plural = 'estados'
        ordering = ['id_estado']


class ReporteAmbiental(models.Model):
    id_reporte = models.AutoField(primary_key=True)
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField('descripción')
    ubicacion_direccion = models.CharField('ubicación', max_length=255)
    latitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitud = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    fecha_reporte = models.DateTimeField(auto_now_add=True)

    # Relaciones ForeignKey con otras tablas:
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario',
                                   related_name='reportes', verbose_name='usuario')
    id_categoria = models.ForeignKey(CategoriaProblema, on_delete=models.PROTECT, db_column='id_categoria',
                                     related_name='reportes', verbose_name='categoría')
    id_estado = models.ForeignKey(Estado, on_delete=models.PROTECT, db_column='id_estado',
                                  related_name='reportes', verbose_name='estado')

    def __str__(self):
        return self.titulo

    def get_absolute_url(self):
        return reverse('reportes:detalle', args=[self.pk])

    def clean(self):
        if (self.latitud is None) != (self.longitud is None):
            raise ValidationError('Indica la latitud y la longitud juntas, o deja ambas vacías.')

    def mostrar_informacion(self):
        """Devuelve un resumen legible del reporte."""
        return (
            f"Reporte #{self.pk}: {self.titulo} | Categoría: {self.id_categoria} | "
            f"Ubicación: {self.ubicacion_direccion} | Estado: {self.id_estado}"
        )

    def puede_editar(self, perfil):
        return perfil is not None and (perfil.es_administrador or perfil.pk == self.id_usuario_id)

    @transaction.atomic
    def cambiar_estado(self, nuevo_estado, responsable, comentario=''):
        """Cambia el estado del reporte y deja registro en el historial de seguimiento."""
        if nuevo_estado.pk == self.id_estado_id:
            raise ValidationError('El reporte ya se encuentra en ese estado.')
        seguimiento = Seguimiento.objects.create(
            id_reporte=self,
            id_usuario_responsable=responsable,
            id_estado_anterior=self.id_estado,
            id_estado_nuevo=nuevo_estado,
            comentario=comentario or None,
        )
        self.id_estado = nuevo_estado
        self.save(update_fields=['id_estado'])
        return seguimiento

    class Meta:
        db_table = 'reportes'
        verbose_name = 'reporte ambiental'
        verbose_name_plural = 'reportes ambientales'
        ordering = ['-fecha_reporte', '-id_reporte']


class Evidencia(models.Model):
    id_evidencia = models.AutoField(primary_key=True)
    id_reporte = models.ForeignKey(ReporteAmbiental, on_delete=models.CASCADE, db_column='id_reporte',
                                   related_name='evidencias', verbose_name='reporte')
    url_imagen = models.ImageField('imagen', upload_to='evidencias/%Y/%m/', max_length=500)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Evidencia #{self.id_evidencia}"

    class Meta:
        db_table = 'evidencias'
        verbose_name = 'evidencia'
        verbose_name_plural = 'evidencias'
        ordering = ['fecha_subida']


class Seguimiento(models.Model):
    id_seguimiento = models.AutoField(primary_key=True)
    id_reporte = models.ForeignKey(ReporteAmbiental, on_delete=models.CASCADE, db_column='id_reporte',
                                   related_name='seguimientos', verbose_name='reporte')
    id_usuario_responsable = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario_responsable',
                                               related_name='seguimientos_realizados', verbose_name='responsable')
    id_estado_anterior = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='seguimientos_anterior',
                                           db_column='id_estado_anterior', verbose_name='estado anterior')
    id_estado_nuevo = models.ForeignKey(Estado, on_delete=models.PROTECT, related_name='seguimientos_nuevo',
                                        db_column='id_estado_nuevo', verbose_name='estado nuevo')
    comentario = models.TextField(null=True, blank=True)
    fecha_cambio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Seguimiento #{self.id_seguimiento}"

    class Meta:
        db_table = 'seguimiento_reporte'
        verbose_name = 'seguimiento'
        verbose_name_plural = 'seguimientos'
        ordering = ['-fecha_cambio', '-id_seguimiento']

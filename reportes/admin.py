from django.contrib import admin

from .models import CategoriaProblema, Estado, Evidencia, ReporteAmbiental, Seguimiento


@admin.register(CategoriaProblema)
class CategoriaProblemaAdmin(admin.ModelAdmin):
    list_display = ('nombre_categoria', 'descripcion')
    search_fields = ('nombre_categoria',)


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ('nombre_estado', 'descripcion')


class EvidenciaInline(admin.TabularInline):
    model = Evidencia
    extra = 0
    readonly_fields = ('fecha_subida',)


class SeguimientoInline(admin.TabularInline):
    model = Seguimiento
    extra = 0
    fk_name = 'id_reporte'
    readonly_fields = ('fecha_cambio',)


@admin.register(ReporteAmbiental)
class ReporteAmbientalAdmin(admin.ModelAdmin):
    list_display = ('id_reporte', 'titulo', 'id_categoria', 'id_estado', 'id_usuario', 'fecha_reporte')
    list_filter = ('id_estado', 'id_categoria', 'fecha_reporte')
    search_fields = ('titulo', 'descripcion', 'ubicacion_direccion')
    date_hierarchy = 'fecha_reporte'
    readonly_fields = ('fecha_reporte',)
    inlines = [EvidenciaInline, SeguimientoInline]


@admin.register(Evidencia)
class EvidenciaAdmin(admin.ModelAdmin):
    list_display = ('id_evidencia', 'id_reporte', 'url_imagen', 'fecha_subida')


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ('id_reporte', 'id_estado_anterior', 'id_estado_nuevo', 'id_usuario_responsable', 'fecha_cambio')
    list_filter = ('id_estado_nuevo',)

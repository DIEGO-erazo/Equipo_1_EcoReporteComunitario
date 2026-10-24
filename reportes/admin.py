from django.contrib import admin
from .models import CategoriaProblema, Estado, ReporteAmbiental, Evidencia, Seguimiento

admin.site.register(CategoriaProblema)
admin.site.register(Estado)
admin.site.register(ReporteAmbiental)
admin.site.register(Evidencia)
admin.site.register(Seguimiento)
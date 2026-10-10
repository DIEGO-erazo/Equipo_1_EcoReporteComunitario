from django.contrib import admin
from .models import Usuario, Categoria, ReporteAmbiental, Seguimiento

# Registro de modelos en el panel de administración
admin.site.register(Usuario)
admin.site.register(Categoria)
admin.site.register(ReporteAmbiental)
admin.site.register(Seguimiento)
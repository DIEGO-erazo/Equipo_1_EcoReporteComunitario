from django.contrib import admin

from .models import Rol, Usuario


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre_rol', 'descripcion')
    search_fields = ('nombre_rol',)


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'correo', 'telefono', 'id_rol', 'fecha_registro')
    list_filter = ('id_rol',)
    search_fields = ('nombre', 'apellido', 'correo')
    readonly_fields = ('fecha_registro',)
    exclude = ('contrasena_hash',)
    raw_id_fields = ('cuenta',)

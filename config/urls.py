from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import RedirectView
from django.views.static import serve

from reportes import views as reportes_views
from usuarios.urls import sesion_urlpatterns

admin.site.site_header = 'EcoReporte Comunitario'
admin.site.site_title = 'EcoReporte'
admin.site.index_title = 'Administración'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', reportes_views.inicio, name='inicio'),
    path('reportes/', include('reportes.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('gestion/', include('gestion.urls')),
    *sesion_urlpatterns,
    # allauth trae sus propias páginas de ingreso y registro; se mandan a las del
    # proyecto para que solo haya una de cada una.
    path('cuentas/login/', RedirectView.as_view(pattern_name='login', query_string=True), name='account_login'),
    path('cuentas/signup/', RedirectView.as_view(pattern_name='usuarios:registro'), name='account_signup'),
    path('cuentas/logout/', RedirectView.as_view(pattern_name='logout'), name='account_logout'),
    path('cuentas/password/change/', RedirectView.as_view(pattern_name='usuarios:cambiar_contrasena'),
         name='account_change_password'),
    path('cuentas/password/reset/', RedirectView.as_view(pattern_name='usuarios:recuperar'),
         name='account_reset_password'),
    # Google, GitHub y Microsoft: /cuentas/<proveedor>/login/ y /cuentas/<proveedor>/login/callback/
    path('cuentas/', include('allauth.urls')),
    # Fotos de evidencia subidas por la comunidad.
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

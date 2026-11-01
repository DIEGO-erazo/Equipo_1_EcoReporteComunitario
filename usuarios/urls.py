from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import LoginForm

app_name = 'usuarios'

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('perfil/', views.perfil, name='perfil'),
    path('cambiar-contrasena/', auth_views.PasswordChangeView.as_view(
        template_name='usuarios/cambiar_contrasena.html',
        success_url='/usuarios/perfil/',
    ), name='cambiar_contrasena'),
]

# Rutas de sesión sin prefijo de app para que LOGIN_URL = 'login' funcione.
sesion_urlpatterns = [
    path('ingresar/', auth_views.LoginView.as_view(
        template_name='usuarios/login.html',
        authentication_form=LoginForm,
        redirect_authenticated_user=True,
    ), name='login'),
    path('salir/', auth_views.LogoutView.as_view(), name='logout'),
]

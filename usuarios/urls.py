from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

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

    # Recuperar la contraseña olvidada por correo.
    path('recuperar/', views.RecuperarContrasenaView.as_view(), name='recuperar'),
    path('recuperar/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='usuarios/recuperar_enviado.html',
    ), name='recuperar_enviado'),
    path('recuperar/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='usuarios/recuperar_nueva.html',
        success_url=reverse_lazy('usuarios:recuperar_listo'),
    ), name='recuperar_confirmar'),
    path('recuperar/listo/', auth_views.PasswordResetCompleteView.as_view(
        template_name='usuarios/recuperar_listo.html',
    ), name='recuperar_listo'),
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

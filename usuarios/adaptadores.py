"""Adaptadores de django-allauth para el inicio de sesión con Google, GitHub y Microsoft.

allauth se encarga de hablar con cada proveedor; aquí solo se ajusta la cuenta
creada para que siga las reglas del proyecto: el nombre de usuario es el correo
y toda cuenta tiene su perfil en la tabla ``usuarios``.
"""

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse

from .models import Usuario


class AdaptadorCuenta(DefaultAccountAdapter):
    def get_password_change_redirect_url(self, request):
        return reverse('usuarios:perfil')


class AdaptadorCuentaSocial(DefaultSocialAccountAdapter):
    @transaction.atomic
    def save_user(self, request, sociallogin, form=None):
        cuenta = super().save_user(request, sociallogin, form)
        correo = (cuenta.email or '').strip().lower()
        if correo and not get_user_model().objects.filter(username__iexact=correo).exclude(pk=cuenta.pk).exists():
            cuenta.username = correo
            cuenta.email = correo
            cuenta.save(update_fields=['username', 'email'])
        Usuario.para_cuenta(cuenta)
        return cuenta

import logging
import smtplib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import PerfilForm, RegistroForm
from .models import Usuario

logger = logging.getLogger(__name__)


def registro(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    form = RegistroForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        cuenta = form.save()
        login(request, cuenta, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, f'¡Bienvenido, {cuenta.first_name}! Tu cuenta fue creada.')
        return redirect('inicio')
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def perfil(request):
    perfil = Usuario.para_cuenta(request.user)
    form = PerfilForm(request.POST or None, instance=perfil)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Tus datos fueron actualizados.')
        return redirect('usuarios:perfil')
    return render(request, 'usuarios/perfil.html', {'form': form, 'mis_reportes': perfil.reportes.select_related('id_categoria', 'id_estado')})


class RecuperarContrasenaView(auth_views.PasswordResetView):
    """Envía al correo de la persona un enlace para crear una contraseña nueva.

    No dice si el correo está registrado, para no revelar quién tiene cuenta.
    """

    template_name = 'usuarios/recuperar.html'
    email_template_name = 'usuarios/correo_recuperar.txt'
    subject_template_name = 'usuarios/correo_recuperar_asunto.txt'
    success_url = reverse_lazy('usuarios:recuperar_enviado')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['correo_configurado'] = settings.CORREO_CONFIGURADO
        return contexto

    def form_valid(self, form):
        try:
            form.save(
                # En el servidor el sitio se abre siempre por https (el túnel lo pone),
                # aunque gunicorn reciba la conexión por http.
                use_https=self.request.is_secure() or not settings.DEBUG,
                token_generator=self.token_generator,
                from_email=self.from_email,
                email_template_name=self.email_template_name,
                subject_template_name=self.subject_template_name,
                request=self.request,
                html_email_template_name=self.html_email_template_name,
                extra_email_context=self.extra_email_context,
            )
        except (smtplib.SMTPException, OSError):
            logger.exception('No se pudo enviar el correo para recuperar la contraseña')
            messages.error(self.request, 'No pudimos enviar el correo en este momento. '
                                         'Intenta más tarde o pide ayuda a un administrador.')
            return redirect('usuarios:recuperar')
        return redirect(self.get_success_url())

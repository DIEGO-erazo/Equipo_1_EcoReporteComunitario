from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import PerfilForm, RegistroForm
from .models import Usuario


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

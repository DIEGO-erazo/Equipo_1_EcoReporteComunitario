from .models import Usuario


def perfil(request):
    """Pone el perfil del usuario conectado a disposición de todas las plantillas."""
    if request.user.is_authenticated:
        return {'perfil': Usuario.para_cuenta(request.user)}
    return {'perfil': None}

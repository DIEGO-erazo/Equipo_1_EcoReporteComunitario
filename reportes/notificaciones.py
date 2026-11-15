"""Correos que EcoReporte envía a quienes hicieron un reporte."""
import logging
import smtplib

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

# Correo que se inventa para cuentas sin correo real (ver Usuario.para_cuenta); no se le escribe.
DOMINIO_SIN_CORREO = '@ecoreporte.local'


def avisar_cambio_de_estado(seguimiento, request):
    """Avisa por correo al autor del reporte que su estado cambió.

    Devuelve True si el correo salió. Si falla el envío, el cambio de estado
    ya quedó guardado: solo se registra el error en el log.
    """
    reporte = seguimiento.id_reporte
    autor = reporte.id_usuario
    if autor.pk == seguimiento.id_usuario_responsable_id or autor.correo.endswith(DOMINIO_SIN_CORREO):
        return False

    # En el servidor el sitio se abre siempre por https (el túnel lo pone),
    # aunque gunicorn reciba la conexión por http.
    protocolo = 'https' if request.is_secure() or not settings.DEBUG else 'http'
    contexto = {
        'autor': autor,
        'reporte': reporte,
        'seguimiento': seguimiento,
        'enlace': f'{protocolo}://{request.get_host()}{reporte.get_absolute_url()}',
    }
    asunto = render_to_string('reportes/correo_estado_asunto.txt', contexto).strip()
    mensaje = render_to_string('reportes/correo_estado.txt', contexto)
    try:
        send_mail(asunto, mensaje, None, [autor.correo])
    except (smtplib.SMTPException, OSError):
        logger.exception('No se pudo avisar por correo el cambio de estado del reporte %s', reporte.pk)
        return False
    return True

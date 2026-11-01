from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from usuarios.models import Usuario

from . import exportar
from .forms import CambioEstadoForm, FiltroReportesForm, ReporteForm
from .models import Estado, Evidencia, ReporteAmbiental
from .notificaciones import avisar_cambio_de_estado

REPORTES_POR_PAGINA = 9


def _reportes():
    return ReporteAmbiental.objects.select_related('id_categoria', 'id_estado', 'id_usuario')


def inicio(request):
    por_estado = {e.nombre_estado.lower(): e.total for e in Estado.objects.annotate(total=Count('reportes'))}
    contexto = {
        'total_reportes': ReporteAmbiental.objects.count(),
        'total_pendientes': por_estado.get(Estado.PENDIENTE.lower(), 0),
        'total_en_proceso': por_estado.get(Estado.EN_PROCESO.lower(), 0),
        'total_resueltos': por_estado.get(Estado.RESUELTO.lower(), 0),
        'recientes': _reportes().prefetch_related('evidencias')[:6],
    }
    return render(request, 'reportes/inicio.html', contexto)


def _filtrar(request):
    """Aplica la búsqueda y los filtros de la URL; la usan la lista y el mapa."""
    filtro = FiltroReportesForm(request.GET or None)
    reportes = _reportes()
    if filtro.is_valid():
        q = filtro.cleaned_data['q']
        if q:
            reportes = reportes.filter(
                Q(titulo__icontains=q) | Q(descripcion__icontains=q) | Q(ubicacion_direccion__icontains=q)
            )
        if filtro.cleaned_data['categoria']:
            reportes = reportes.filter(id_categoria=filtro.cleaned_data['categoria'])
        if filtro.cleaned_data['estado']:
            reportes = reportes.filter(id_estado=filtro.cleaned_data['estado'])
    return filtro, reportes


def _parametros(request):
    """Los filtros actuales como texto de URL, sin el número de página."""
    parametros = request.GET.copy()
    parametros.pop('pagina', None)
    return parametros.urlencode()


def lista(request):
    filtro, reportes = _filtrar(request)
    pagina = Paginator(reportes.prefetch_related('evidencias'), REPORTES_POR_PAGINA).get_page(request.GET.get('pagina'))
    return render(request, 'reportes/lista.html', {
        'filtro': filtro,
        'pagina': pagina,
        'parametros': _parametros(request),
    })


FORMATOS_EXPORTAR = {
    'excel': (exportar.excel, 'xlsx', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
    'pdf': (exportar.pdf, 'pdf', 'application/pdf'),
}


@login_required
def exportar_reportes(request, formato):
    """Descarga los reportes de la lista, con los mismos filtros, en Excel o PDF."""
    if not Usuario.para_cuenta(request.user).es_administrador:
        raise PermissionDenied
    generar, extension, tipo = FORMATOS_EXPORTAR[formato]
    filtro, reportes = _filtrar(request)
    respuesta = HttpResponse(generar(reportes, filtro), content_type=tipo)
    nombre = f'reportes_ecoreporte_{timezone.localdate():%Y-%m-%d}.{extension}'
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre}"'
    return respuesta


def mapa(request):
    filtro, reportes = _filtrar(request)
    puntos = [
        {
            'titulo': reporte.titulo,
            'lat': float(reporte.latitud),
            'lng': float(reporte.longitud),
            'estado': reporte.id_estado.nombre_estado,
            'clase': reporte.id_estado.clase_css,
            'categoria': reporte.id_categoria.nombre_categoria,
            'url': reporte.get_absolute_url(),
        }
        for reporte in reportes.filter(latitud__isnull=False, longitud__isnull=False)
    ]
    return render(request, 'reportes/mapa.html', {
        'filtro': filtro,
        'puntos': puntos,
        'sin_coordenadas': reportes.count() - len(puntos),
        'mapa_config': {'centro': settings.MAPA_CENTRO, 'zoom': settings.MAPA_ZOOM},
        'parametros': _parametros(request),
    })


@login_required
def mis_reportes(request):
    perfil = Usuario.para_cuenta(request.user)
    reportes = _reportes().prefetch_related('evidencias').filter(id_usuario=perfil)
    pagina = Paginator(reportes, REPORTES_POR_PAGINA).get_page(request.GET.get('pagina'))
    return render(request, 'reportes/mis_reportes.html', {'pagina': pagina})


def detalle(request, pk):
    reporte = get_object_or_404(_reportes(), pk=pk)
    perfil = Usuario.para_cuenta(request.user) if request.user.is_authenticated else None
    contexto = {
        'reporte': reporte,
        'evidencias': reporte.evidencias.all(),
        'seguimientos': reporte.seguimientos.select_related(
            'id_usuario_responsable', 'id_estado_anterior', 'id_estado_nuevo'
        ),
        'puede_editar': reporte.puede_editar(perfil),
        'es_administrador': perfil is not None and perfil.es_administrador,
    }
    if contexto['es_administrador']:
        contexto['form_estado'] = CambioEstadoForm(
            initial={'nuevo_estado': reporte.id_estado},
        )
    return render(request, 'reportes/detalle.html', contexto)


def _config_elegir_punto():
    return {'centro': settings.MAPA_CENTRO, 'zoom': settings.MAPA_ZOOM}


def _guardar_fotos(reporte, fotos):
    for foto in fotos:
        Evidencia.objects.create(id_reporte=reporte, url_imagen=foto)


@login_required
def crear(request):
    perfil = Usuario.para_cuenta(request.user)
    form = ReporteForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            reporte = form.save(commit=False)
            reporte.id_usuario = perfil
            reporte.id_estado = Estado.inicial()
            reporte.save()
            _guardar_fotos(reporte, form.cleaned_data['fotos'])
        messages.success(request, '¡Gracias! Tu reporte fue registrado.')
        return redirect(reporte)
    return render(request, 'reportes/formulario.html', {
        'form': form, 'titulo_pagina': 'Nuevo reporte', 'mapa_config': _config_elegir_punto(),
    })


@login_required
def editar(request, pk):
    reporte = get_object_or_404(ReporteAmbiental, pk=pk)
    if not reporte.puede_editar(Usuario.para_cuenta(request.user)):
        raise PermissionDenied
    form = ReporteForm(request.POST or None, request.FILES or None, instance=reporte)
    if request.method == 'POST' and form.is_valid():
        with transaction.atomic():
            form.save()
            _guardar_fotos(reporte, form.cleaned_data['fotos'])
        messages.success(request, 'El reporte fue actualizado.')
        return redirect(reporte)
    return render(request, 'reportes/formulario.html', {
        'form': form, 'reporte': reporte, 'titulo_pagina': 'Editar reporte', 'mapa_config': _config_elegir_punto(),
    })


@login_required
def eliminar(request, pk):
    reporte = get_object_or_404(ReporteAmbiental, pk=pk)
    if not reporte.puede_editar(Usuario.para_cuenta(request.user)):
        raise PermissionDenied
    if request.method == 'POST':
        for evidencia in reporte.evidencias.all():
            evidencia.url_imagen.delete(save=False)
        reporte.delete()
        messages.success(request, 'El reporte fue eliminado.')
        return redirect('reportes:mis_reportes')
    return render(request, 'reportes/confirmar_eliminar.html', {'reporte': reporte})


@login_required
@require_POST
def eliminar_evidencia(request, pk):
    evidencia = get_object_or_404(Evidencia.objects.select_related('id_reporte'), pk=pk)
    reporte = evidencia.id_reporte
    if not reporte.puede_editar(Usuario.para_cuenta(request.user)):
        raise PermissionDenied
    evidencia.url_imagen.delete(save=False)
    evidencia.delete()
    messages.success(request, 'La foto fue eliminada.')
    return redirect('reportes:editar', pk=reporte.pk)


@login_required
@require_POST
def cambiar_estado(request, pk):
    perfil = Usuario.para_cuenta(request.user)
    if not perfil.es_administrador:
        raise PermissionDenied
    reporte = get_object_or_404(ReporteAmbiental, pk=pk)
    form = CambioEstadoForm(request.POST)
    if form.is_valid():
        try:
            seguimiento = reporte.cambiar_estado(form.cleaned_data['nuevo_estado'], perfil,
                                                 form.cleaned_data['comentario'])
        except ValidationError as error:
            messages.warning(request, error.messages[0])
        else:
            texto = f'Estado actualizado a «{reporte.id_estado}».'
            if avisar_cambio_de_estado(seguimiento, request):
                texto += f' Se avisó por correo a {reporte.id_usuario.nombre_completo}.'
            messages.success(request, texto)
    else:
        messages.error(request, 'Selecciona un estado válido.')
    return redirect(reporte)

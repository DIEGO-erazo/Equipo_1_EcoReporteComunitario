from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Count, ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from reportes.models import CategoriaProblema, Estado, Evidencia, ReporteAmbiental, Seguimiento
from usuarios.models import Rol, Usuario

from .forms import CategoriaForm, EstadoForm, UsuarioGestionForm


class SoloAdministradorMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Pide iniciar sesión y deja pasar solo a los administradores; al resto le responde 403."""

    def test_func(self):
        return Usuario.para_cuenta(self.request.user).es_administrador


class PanelView(SoloAdministradorMixin, TemplateView):
    template_name = 'gestion/panel.html'

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(
            total_reportes=ReporteAmbiental.objects.count(),
            total_usuarios=Usuario.objects.count(),
            total_categorias=CategoriaProblema.objects.count(),
            total_estados=Estado.objects.count(),
            por_estado=Estado.objects.annotate(total=Count('reportes')).order_by('id_estado'),
            por_categoria=CategoriaProblema.objects.annotate(total=Count('reportes')).order_by('-total', 'nombre_categoria'),
            ultimos_cambios=Seguimiento.objects.select_related(
                'id_reporte', 'id_usuario_responsable', 'id_estado_anterior', 'id_estado_nuevo'
            )[:8],
        )
        return contexto


# --- Categorías y estados -------------------------------------------------
# Las dos pantallas funcionan igual; cada clase concreta solo indica el modelo,
# el formulario y los textos.

class CatalogoMixin(SoloAdministradorMixin):
    nombre_singular = ''
    nombre_plural = ''
    titulo_nuevo = ''
    ruta = ''  # prefijo de los nombres de URL: 'categorias' -> gestion:categorias_editar

    def get_success_url(self):
        return reverse(f'gestion:{self.ruta}')

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(
            nombre_singular=self.nombre_singular,
            nombre_plural=self.nombre_plural,
            titulo_nuevo=self.titulo_nuevo,
            url_crear=f'gestion:{self.ruta}_crear',
            url_editar=f'gestion:{self.ruta}_editar',
            url_eliminar=f'gestion:{self.ruta}_eliminar',
            url_cancelar=self.get_success_url(),
        )
        return contexto


class ListaCatalogo(CatalogoMixin, ListView):
    template_name = 'gestion/catalogo_lista.html'

    def get_queryset(self):
        # Django no aplica Meta.ordering a las consultas con Count, por eso se repite aquí.
        return super().get_queryset().annotate(total_reportes=Count('reportes')).order_by(*self.model._meta.ordering)


class GuardarCatalogo(CatalogoMixin):
    template_name = 'gestion/formulario.html'
    # Se llama "formulario" y no "form_class" porque DeleteView también usa form_class.
    formulario = None

    def get_form_class(self):
        return self.formulario

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['titulo_pagina'] = f'Editar {self.nombre_singular}' if self.object else self.titulo_nuevo
        return contexto

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, f'Se guardó «{self.object}».')
        return respuesta


class EliminarCatalogo(CatalogoMixin, DeleteView):
    template_name = 'gestion/confirmar_eliminar.html'

    def motivo_bloqueo(self):
        """Texto que explica por qué no se puede eliminar, o None si sí se puede."""
        total = self.object.reportes.count()
        if total:
            if total == 1:
                return f'Hay 1 reporte con «{self.object}». Cámbialo de {self.nombre_singular} antes de eliminar.'
            return f'Hay {total} reportes con «{self.object}». Cámbialos de {self.nombre_singular} antes de eliminar.'
        return None

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto['motivo_bloqueo'] = self.motivo_bloqueo()
        return contexto

    def form_valid(self, form):
        motivo = self.motivo_bloqueo()
        if motivo:
            messages.error(self.request, motivo)
            return redirect(self.get_success_url())
        try:
            respuesta = super().form_valid(form)
        except ProtectedError:
            messages.error(self.request, f'«{self.object}» todavía se usa en otros registros.')
            return redirect(self.get_success_url())
        messages.success(self.request, f'Se eliminó «{self.object}».')
        return respuesta


class CategoriaMixin:
    model = CategoriaProblema
    formulario = CategoriaForm
    nombre_singular = 'categoría'
    nombre_plural = 'Categorías'
    titulo_nuevo = 'Nueva categoría'
    ruta = 'categorias'


class CategoriaLista(CategoriaMixin, ListaCatalogo):
    pass


class CategoriaCrear(CategoriaMixin, GuardarCatalogo, CreateView):
    pass


class CategoriaEditar(CategoriaMixin, GuardarCatalogo, UpdateView):
    pass


class CategoriaEliminar(CategoriaMixin, EliminarCatalogo):
    pass


class EstadoMixin:
    model = Estado
    formulario = EstadoForm
    nombre_singular = 'estado'
    nombre_plural = 'Estados'
    titulo_nuevo = 'Nuevo estado'
    ruta = 'estados'


class EstadoLista(EstadoMixin, ListaCatalogo):
    pass


class EstadoCrear(EstadoMixin, GuardarCatalogo, CreateView):
    pass


class EstadoEditar(EstadoMixin, GuardarCatalogo, UpdateView):
    pass


class EstadoEliminar(EstadoMixin, EliminarCatalogo):
    def motivo_bloqueo(self):
        if self.object.es_del_sistema:
            return f'«{self.object}» es un estado que usa el sistema y no se puede eliminar.'
        if self.object.seguimientos_anterior.exists() or self.object.seguimientos_nuevo.exists():
            return f'«{self.object}» aparece en el historial de seguimiento y no se puede eliminar.'
        return super().motivo_bloqueo()


# --- Usuarios --------------------------------------------------------------

class UsuarioLista(SoloAdministradorMixin, ListView):
    template_name = 'gestion/usuarios_lista.html'
    paginate_by = 15
    page_kwarg = 'pagina'

    def get_queryset(self):
        usuarios = (Usuario.objects.select_related('id_rol', 'cuenta')
                    .annotate(total_reportes=Count('reportes')).order_by('nombre', 'apellido', 'id_usuario'))
        q = self.request.GET.get('q', '').strip()
        if q:
            usuarios = usuarios.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(correo__icontains=q))
        rol = self.request.GET.get('rol', '')
        if rol.isdigit():
            usuarios = usuarios.filter(id_rol=rol)
        return usuarios

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        parametros = self.request.GET.copy()
        parametros.pop('pagina', None)
        contexto.update(
            pagina=contexto['page_obj'],
            parametros=parametros.urlencode(),
            roles=Rol.objects.all(),
            q=self.request.GET.get('q', ''),
            rol_elegido=self.request.GET.get('rol', ''),
        )
        return contexto


class UsuarioEditar(SoloAdministradorMixin, UpdateView):
    model = Usuario
    form_class = UsuarioGestionForm
    template_name = 'gestion/formulario.html'
    success_url = reverse_lazy('gestion:usuarios')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['editor'] = Usuario.para_cuenta(self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        contexto.update(
            titulo_pagina='Editar usuario',
            subtitulo=f'{self.object.correo} · registrado el {self.object.fecha_registro:%d/%m/%Y}',
            url_cancelar=self.success_url,
        )
        return contexto

    def form_valid(self, form):
        respuesta = super().form_valid(form)
        messages.success(self.request, f'Se guardaron los datos de {self.object.nombre_completo}.')
        return respuesta


class UsuarioEliminar(SoloAdministradorMixin, DeleteView):
    model = Usuario
    template_name = 'gestion/confirmar_eliminar.html'
    success_url = reverse_lazy('gestion:usuarios')

    def motivo_bloqueo(self):
        if self.object.pk == Usuario.para_cuenta(self.request.user).pk:
            return 'No puedes eliminar tu propia cuenta.'
        return None

    def get_context_data(self, **kwargs):
        contexto = super().get_context_data(**kwargs)
        total = self.object.reportes.count()
        contexto.update(
            nombre_singular='usuario',
            motivo_bloqueo=self.motivo_bloqueo(),
            aviso=f'También se eliminarán sus {total} reporte(s) con sus fotos, y su cuenta para iniciar sesión.',
            url_cancelar=self.success_url,
        )
        return contexto

    def form_valid(self, form):
        perfil = self.object
        motivo = self.motivo_bloqueo()
        if motivo:
            messages.error(self.request, motivo)
            return redirect(self.success_url)
        for evidencia in Evidencia.objects.filter(id_reporte__id_usuario=perfil):
            evidencia.url_imagen.delete(save=False)
        with transaction.atomic():
            # Borrar la cuenta de Django borra también el perfil (y sus reportes) en cascada.
            (perfil.cuenta or perfil).delete()
        messages.success(self.request, f'Se eliminó a {perfil.nombre_completo}.')
        return redirect(self.success_url)

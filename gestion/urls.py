from django.urls import path

from . import views

app_name = 'gestion'

urlpatterns = [
    path('', views.PanelView.as_view(), name='panel'),

    path('categorias/', views.CategoriaLista.as_view(), name='categorias'),
    path('categorias/nueva/', views.CategoriaCrear.as_view(), name='categorias_crear'),
    path('categorias/<int:pk>/editar/', views.CategoriaEditar.as_view(), name='categorias_editar'),
    path('categorias/<int:pk>/eliminar/', views.CategoriaEliminar.as_view(), name='categorias_eliminar'),

    path('estados/', views.EstadoLista.as_view(), name='estados'),
    path('estados/nuevo/', views.EstadoCrear.as_view(), name='estados_crear'),
    path('estados/<int:pk>/editar/', views.EstadoEditar.as_view(), name='estados_editar'),
    path('estados/<int:pk>/eliminar/', views.EstadoEliminar.as_view(), name='estados_eliminar'),

    path('usuarios/', views.UsuarioLista.as_view(), name='usuarios'),
    path('usuarios/<int:pk>/editar/', views.UsuarioEditar.as_view(), name='usuarios_editar'),
    path('usuarios/<int:pk>/eliminar/', views.UsuarioEliminar.as_view(), name='usuarios_eliminar'),
]

from django.urls import path

from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.lista, name='lista'),
    path('nuevo/', views.crear, name='crear'),
    path('mios/', views.mis_reportes, name='mis_reportes'),
    path('<int:pk>/', views.detalle, name='detalle'),
    path('<int:pk>/editar/', views.editar, name='editar'),
    path('<int:pk>/eliminar/', views.eliminar, name='eliminar'),
    path('<int:pk>/estado/', views.cambiar_estado, name='cambiar_estado'),
    path('evidencias/<int:pk>/eliminar/', views.eliminar_evidencia, name='eliminar_evidencia'),
]

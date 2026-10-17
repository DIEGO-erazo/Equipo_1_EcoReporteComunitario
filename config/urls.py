from django.contrib import admin
from django.urls import path
from reportes import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.inicio, name="inicio"),
]
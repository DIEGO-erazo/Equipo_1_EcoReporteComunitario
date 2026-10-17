from django.db import models


class ReporteAmbiental:
    def __init__(self, titulo, descripcion, ubicacion, tipo):
        self.titulo = titulo
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.tipo = tipo
        self.estado = "Pendiente"

    def mostrar_informacion(self):
        return (
            f"Reporte: {self.titulo} | "
            f"Tipo: {self.tipo} | "
            f"Ubicación: {self.ubicacion} | "
            f"Estado: {self.estado}"
        )

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
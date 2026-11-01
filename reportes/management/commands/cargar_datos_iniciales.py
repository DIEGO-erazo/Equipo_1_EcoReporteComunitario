from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from reportes.models import CategoriaProblema, Estado, ReporteAmbiental
from usuarios.models import Rol, Usuario

ROLES = [
    (Rol.CIUDADANO, 'Habitante que registra y consulta reportes.'),
    (Rol.ADMINISTRADOR, 'Responsable comunitario que da seguimiento a los reportes.'),
]

ESTADOS = [
    (Estado.PENDIENTE, 'Reporte recibido, aún sin atender.'),
    (Estado.EN_PROCESO, 'Se están realizando acciones para resolverlo.'),
    (Estado.RESUELTO, 'El problema fue solucionado.'),
    (Estado.RECHAZADO, 'El reporte no procede o está duplicado.'),
]

CATEGORIAS = [
    ('Botadero clandestino', 'Lugar no autorizado donde se tira basura.'),
    ('Acumulación de basura', 'Basura acumulada en calles, quebradas o espacios públicos.'),
    ('Recolección de residuos', 'Problemas con el tren de aseo o la recolección.'),
    ('Quema de basura', 'Quema de desechos que contamina el aire.'),
    ('Contaminación de agua', 'Ríos, quebradas o nacimientos contaminados.'),
    ('Otro', 'Otro problema ambiental de la comunidad.'),
]

REPORTES_DEMO = [
    ('Botadero junto a la quebrada', 'Botadero clandestino', 'Calle hacia el río, después del puente',
     'Desde hace dos semanas se tira basura a la orilla de la quebrada. Hay bolsas, llantas y plástico.'),
    ('Basura acumulada frente al Instituto', 'Acumulación de basura', 'Entrada del Instituto Nacional de San Rafael',
     'Los fines de semana se acumula basura en la entrada y los perros rompen las bolsas.'),
    ('El tren de aseo no pasó esta semana', 'Recolección de residuos', 'Barrio El Centro',
     'El camión recolector no pasó el martes ni el viernes. Las familias no tienen dónde dejar la basura.'),
]


class Command(BaseCommand):
    help = 'Crea roles, estados y categorías iniciales. Con --demo agrega usuarios y reportes de ejemplo.'

    def add_arguments(self, parser):
        parser.add_argument('--demo', action='store_true', help='Crea usuarios y reportes de ejemplo.')

    @transaction.atomic
    def handle(self, *args, **opciones):
        for nombre, descripcion in ROLES:
            Rol.objects.get_or_create(nombre_rol=nombre, defaults={'descripcion': descripcion})
        for nombre, descripcion in ESTADOS:
            Estado.objects.get_or_create(nombre_estado__iexact=nombre,
                                         defaults={'nombre_estado': nombre, 'descripcion': descripcion})
        for nombre, descripcion in CATEGORIAS:
            CategoriaProblema.objects.get_or_create(nombre_categoria__iexact=nombre,
                                                    defaults={'nombre_categoria': nombre, 'descripcion': descripcion})
        if opciones['verbosity']:
            self.stdout.write(self.style.SUCCESS('Roles, estados y categorías listos.'))

        if opciones['demo']:
            self._crear_demo()

    def _crear_cuenta(self, correo, nombre, apellido, contrasena, administrador=False):
        User = get_user_model()
        cuenta, creada = User.objects.get_or_create(
            username=correo,
            defaults={'email': correo, 'first_name': nombre, 'last_name': apellido,
                      'is_staff': administrador, 'is_superuser': administrador},
        )
        if creada:
            cuenta.set_password(contrasena)
            cuenta.save()
        return Usuario.para_cuenta(cuenta)

    def _crear_demo(self):
        admin = self._crear_cuenta('admin@ecoreporte.local', 'Administrador', 'EcoReporte', 'admin12345', True)
        vecina = self._crear_cuenta('vecina@ecoreporte.local', 'María', 'López', 'vecina12345')

        if not ReporteAmbiental.objects.exists():
            pendiente = Estado.inicial()
            for titulo, categoria, ubicacion, descripcion in REPORTES_DEMO:
                ReporteAmbiental.objects.create(
                    titulo=titulo, descripcion=descripcion, ubicacion_direccion=ubicacion,
                    id_categoria=CategoriaProblema.objects.get(nombre_categoria__iexact=categoria),
                    id_estado=pendiente, id_usuario=vecina,
                )
            primero = ReporteAmbiental.objects.order_by('id_reporte').first()
            primero.cambiar_estado(Estado.objects.get(nombre_estado__iexact=Estado.EN_PROCESO), admin,
                                   'Se notificó a la alcaldía para programar la limpieza.')

        self.stdout.write(self.style.SUCCESS(
            'Datos de ejemplo listos:\n'
            '  Administrador: admin@ecoreporte.local / admin12345\n'
            '  Ciudadana:     vecina@ecoreporte.local / vecina12345'
        ))

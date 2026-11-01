import shutil
import smtplib
import tempfile
from io import BytesIO
from unittest import mock

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from usuarios.models import Rol, Usuario

from .models import CategoriaProblema, Estado, Evidencia, ReporteAmbiental, Seguimiento

MEDIA_TEMPORAL = tempfile.mkdtemp()


def imagen_de_prueba(nombre='foto.png'):
    archivo = BytesIO()
    Image.new('RGB', (10, 10), 'green').save(archivo, 'PNG')
    return SimpleUploadedFile(nombre, archivo.getvalue(), content_type='image/png')


def crear_cuenta(correo, administrador=False):
    cuenta = get_user_model().objects.create_user(
        username=correo, email=correo, password='clave-segura-123', first_name='Ana', last_name='Pérez',
        is_staff=administrador,
    )
    return Usuario.para_cuenta(cuenta)


@override_settings(MEDIA_ROOT=MEDIA_TEMPORAL)
class BaseReportesTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos_iniciales', verbosity=0)
        cls.categoria = CategoriaProblema.objects.get(nombre_categoria='Botadero clandestino')
        cls.pendiente = Estado.objects.get(nombre_estado=Estado.PENDIENTE)
        cls.resuelto = Estado.objects.get(nombre_estado=Estado.RESUELTO)
        cls.vecino = crear_cuenta('vecino@test.com')
        cls.otro = crear_cuenta('otro@test.com')
        cls.admin = crear_cuenta('admin@test.com', administrador=True)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_TEMPORAL, ignore_errors=True)

    def crear_reporte(self, usuario=None, **campos):
        datos = {
            'titulo': 'Basura en la calle', 'descripcion': 'Hay bolsas acumuladas',
            'ubicacion_direccion': 'Barrio El Centro', 'id_categoria': self.categoria,
            'id_estado': self.pendiente, 'id_usuario': usuario or self.vecino,
        }
        datos.update(campos)
        return ReporteAmbiental.objects.create(**datos)

    def ingresar(self, perfil):
        self.client.force_login(perfil.cuenta)


class ModeloReporteTest(BaseReportesTest):
    def test_cambiar_estado_registra_seguimiento(self):
        reporte = self.crear_reporte()
        seguimiento = reporte.cambiar_estado(self.resuelto, self.admin, 'Limpieza realizada')

        reporte.refresh_from_db()
        self.assertEqual(reporte.id_estado, self.resuelto)
        self.assertEqual(seguimiento.id_estado_anterior, self.pendiente)
        self.assertEqual(seguimiento.id_estado_nuevo, self.resuelto)
        self.assertEqual(reporte.seguimientos.count(), 1)

    def test_cambiar_al_mismo_estado_falla(self):
        reporte = self.crear_reporte()
        with self.assertRaises(ValidationError):
            reporte.cambiar_estado(self.pendiente, self.admin)
        self.assertFalse(Seguimiento.objects.exists())

    def test_mostrar_informacion(self):
        reporte = self.crear_reporte()
        texto = reporte.mostrar_informacion()
        self.assertIn('Basura en la calle', texto)
        self.assertIn('Pendiente', texto)

    def test_coordenadas_incompletas_no_son_validas(self):
        reporte = self.crear_reporte(latitud=14.0)
        with self.assertRaises(ValidationError):
            reporte.full_clean()

    def test_carga_de_datos_es_idempotente(self):
        call_command('cargar_datos_iniciales', verbosity=0)
        self.assertEqual(Estado.objects.count(), 4)
        self.assertEqual(Rol.objects.count(), 2)


class VistasPublicasTest(BaseReportesTest):
    def test_inicio_muestra_estadisticas(self):
        self.crear_reporte()
        respuesta = self.client.get(reverse('inicio'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['total_reportes'], 1)
        self.assertEqual(respuesta.context['total_pendientes'], 1)

    def test_lista_filtra_por_texto_y_estado(self):
        self.crear_reporte(titulo='Quebrada contaminada')
        self.crear_reporte(titulo='Botadero en la escuela', id_estado=self.resuelto)

        respuesta = self.client.get(reverse('reportes:lista'), {'q': 'quebrada'})
        self.assertEqual([r.titulo for r in respuesta.context['pagina']], ['Quebrada contaminada'])

        respuesta = self.client.get(reverse('reportes:lista'), {'estado': self.resuelto.pk})
        self.assertEqual([r.titulo for r in respuesta.context['pagina']], ['Botadero en la escuela'])

    def test_detalle_publico(self):
        reporte = self.crear_reporte()
        respuesta = self.client.get(reporte.get_absolute_url())
        self.assertContains(respuesta, 'Basura en la calle')
        self.assertNotContains(respuesta, 'Actualizar estado')

    def test_crear_requiere_sesion(self):
        respuesta = self.client.get(reverse('reportes:crear'))
        self.assertRedirects(respuesta, f"{reverse('login')}?next={reverse('reportes:crear')}")

    def test_paginas_usan_bootstrap(self):
        respuesta = self.client.get(reverse('reportes:lista'))
        self.assertContains(respuesta, 'vendor/bootstrap/bootstrap.min.css')
        self.assertContains(respuesta, 'vendor/bootstrap/bootstrap.bundle.min.js')
        self.assertContains(respuesta, 'class="navbar ')
        self.assertContains(respuesta, 'class="form-select"', count=2)

    def test_formulario_marca_errores_con_bootstrap(self):
        self.ingresar(self.vecino)
        respuesta = self.client.post(reverse('reportes:crear'), {'titulo': ''})
        self.assertContains(respuesta, 'form-control is-invalid')
        self.assertContains(respuesta, 'invalid-feedback')


class CrudReportesTest(BaseReportesTest):
    def test_crear_reporte_con_fotos(self):
        self.ingresar(self.vecino)
        respuesta = self.client.post(reverse('reportes:crear'), {
            'titulo': 'Llantas abandonadas', 'id_categoria': self.categoria.pk,
            'descripcion': 'Junto al río', 'ubicacion_direccion': 'Puente principal',
            'fotos': [imagen_de_prueba('a.png'), imagen_de_prueba('b.png')],
        })
        reporte = ReporteAmbiental.objects.get(titulo='Llantas abandonadas')
        self.assertRedirects(respuesta, reporte.get_absolute_url())
        self.assertEqual(reporte.id_usuario, self.vecino)
        self.assertEqual(reporte.id_estado, self.pendiente)
        self.assertEqual(reporte.evidencias.count(), 2)

    def test_rechaza_archivo_que_no_es_imagen(self):
        self.ingresar(self.vecino)
        respuesta = self.client.post(reverse('reportes:crear'), {
            'titulo': 'X', 'id_categoria': self.categoria.pk, 'descripcion': 'X', 'ubicacion_direccion': 'X',
            'fotos': [SimpleUploadedFile('virus.png', b'no soy imagen', content_type='image/png')],
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertFalse(ReporteAmbiental.objects.exists())

    def test_solo_el_autor_puede_editar(self):
        reporte = self.crear_reporte()
        self.ingresar(self.otro)
        self.assertEqual(self.client.get(reverse('reportes:editar', args=[reporte.pk])).status_code, 403)
        self.ingresar(self.vecino)
        self.assertEqual(self.client.get(reverse('reportes:editar', args=[reporte.pk])).status_code, 200)

    def test_autor_elimina_su_reporte(self):
        reporte = self.crear_reporte()
        Evidencia.objects.create(id_reporte=reporte, url_imagen=imagen_de_prueba())
        self.ingresar(self.vecino)
        self.client.post(reverse('reportes:eliminar', args=[reporte.pk]))
        self.assertFalse(ReporteAmbiental.objects.exists())
        self.assertFalse(Evidencia.objects.exists())

    def test_mis_reportes_solo_muestra_los_propios(self):
        self.crear_reporte(titulo='Mío')
        self.crear_reporte(usuario=self.otro, titulo='Ajeno')
        self.ingresar(self.vecino)
        respuesta = self.client.get(reverse('reportes:mis_reportes'))
        self.assertEqual([r.titulo for r in respuesta.context['pagina']], ['Mío'])


class CambioEstadoTest(BaseReportesTest):
    def test_ciudadano_no_puede_cambiar_estado(self):
        reporte = self.crear_reporte()
        self.ingresar(self.vecino)
        respuesta = self.client.post(reverse('reportes:cambiar_estado', args=[reporte.pk]),
                                     {'nuevo_estado': self.resuelto.pk})
        self.assertEqual(respuesta.status_code, 403)

    def test_administrador_cambia_estado(self):
        reporte = self.crear_reporte()
        self.ingresar(self.admin)
        self.client.post(reverse('reportes:cambiar_estado', args=[reporte.pk]),
                         {'nuevo_estado': self.resuelto.pk, 'comentario': 'Listo'})
        reporte.refresh_from_db()
        self.assertEqual(reporte.id_estado, self.resuelto)
        self.assertEqual(reporte.seguimientos.get().comentario, 'Listo')


class MapaTest(BaseReportesTest):
    def test_mapa_muestra_solo_reportes_con_coordenadas(self):
        con_punto = self.crear_reporte(titulo='Con punto', latitud='14.133000', longitud='-89.033000')
        self.crear_reporte(titulo='Sin punto')
        respuesta = self.client.get(reverse('reportes:mapa'))
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.context['puntos'], [{
            'titulo': 'Con punto', 'lat': 14.133, 'lng': -89.033, 'estado': 'Pendiente',
            'clase': 'pendiente', 'categoria': 'Botadero clandestino', 'url': con_punto.get_absolute_url(),
        }])
        self.assertEqual(respuesta.context['sin_coordenadas'], 1)
        self.assertContains(respuesta, 'vendor/leaflet/leaflet.js')
        self.assertContains(respuesta, 'id="mapa-puntos"')

    def test_mapa_usa_los_mismos_filtros_que_la_lista(self):
        self.crear_reporte(titulo='Pendiente', latitud='14.1', longitud='-89.0')
        self.crear_reporte(titulo='Resuelto', latitud='14.2', longitud='-89.1', id_estado=self.resuelto)
        respuesta = self.client.get(reverse('reportes:mapa'), {'estado': self.resuelto.pk})
        self.assertEqual([p['titulo'] for p in respuesta.context['puntos']], ['Resuelto'])

    def test_detalle_muestra_el_punto_solo_si_tiene_coordenadas(self):
        reporte = self.crear_reporte(latitud='14.133000', longitud='-89.033000')
        self.assertContains(self.client.get(reporte.get_absolute_url()), 'data-mapa-punto')
        reporte = self.crear_reporte()
        respuesta = self.client.get(reporte.get_absolute_url())
        self.assertNotContains(respuesta, 'data-mapa-punto')
        self.assertNotContains(respuesta, 'leaflet.js')

    def test_formulario_trae_el_selector_de_ubicacion(self):
        self.ingresar(self.vecino)
        respuesta = self.client.get(reverse('reportes:crear'))
        self.assertContains(respuesta, 'id="mapa-elegir"')
        self.assertContains(respuesta, 'id="mapa-config"')


class AvisoPorCorreoTest(BaseReportesTest):
    def cambiar(self, reporte, comentario='Se coordinó la limpieza'):
        self.ingresar(self.admin)
        return self.client.post(reverse('reportes:cambiar_estado', args=[reporte.pk]),
                                {'nuevo_estado': self.resuelto.pk, 'comentario': comentario}, follow=True)

    def test_avisa_al_autor_cuando_cambia_el_estado(self):
        reporte = self.crear_reporte()
        respuesta = self.cambiar(reporte)
        self.assertEqual(len(mail.outbox), 1)
        correo = mail.outbox[0]
        self.assertEqual(correo.to, ['vecino@test.com'])
        self.assertEqual(correo.subject, 'Tu reporte «Basura en la calle» ahora está: Resuelto')
        self.assertIn('Antes: Pendiente', correo.body)
        self.assertIn('Ahora: Resuelto', correo.body)
        self.assertIn('Se coordinó la limpieza', correo.body)
        self.assertIn(f'https://testserver{reporte.get_absolute_url()}', correo.body)
        self.assertContains(respuesta, 'Se avisó por correo a Ana Pérez.')

    def test_no_avisa_si_el_administrador_cambia_su_propio_reporte(self):
        self.cambiar(self.crear_reporte(usuario=self.admin))
        self.assertEqual(len(mail.outbox), 0)

    def test_no_avisa_a_cuentas_sin_correo_real(self):
        sin_correo = Usuario.para_cuenta(get_user_model().objects.create_user(username='sincorreo', password='x'))
        self.cambiar(self.crear_reporte(usuario=sin_correo))
        self.assertEqual(len(mail.outbox), 0)

    def test_si_falla_el_correo_el_estado_igual_cambia(self):
        reporte = self.crear_reporte()
        with mock.patch('reportes.notificaciones.send_mail', side_effect=smtplib.SMTPException('caído')), \
                self.assertLogs('reportes.notificaciones', 'ERROR'):
            respuesta = self.cambiar(reporte)
        reporte.refresh_from_db()
        self.assertEqual(reporte.id_estado, self.resuelto)
        self.assertContains(respuesta, 'Estado actualizado a «Resuelto».')
        self.assertNotContains(respuesta, 'Se avisó por correo')

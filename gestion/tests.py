from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from reportes.models import CategoriaProblema, Estado, ReporteAmbiental
from reportes.tests import crear_cuenta
from usuarios.models import Rol, Usuario


class BaseGestionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('cargar_datos_iniciales', verbosity=0)
        cls.vecino = crear_cuenta('vecino@test.com')
        cls.admin = crear_cuenta('admin@test.com', administrador=True)
        cls.categoria = CategoriaProblema.objects.get(nombre_categoria='Botadero clandestino')
        cls.pendiente = Estado.objects.get(nombre_estado=Estado.PENDIENTE)

    def setUp(self):
        self.client.force_login(self.admin.cuenta)

    def crear_reporte(self, **campos):
        datos = {
            'titulo': 'Basura en la calle', 'descripcion': 'Bolsas acumuladas', 'ubicacion_direccion': 'Centro',
            'id_categoria': self.categoria, 'id_estado': self.pendiente, 'id_usuario': self.vecino,
        }
        datos.update(campos)
        return ReporteAmbiental.objects.create(**datos)


class PermisosTest(BaseGestionTest):
    RUTAS = ('gestion:panel', 'gestion:categorias', 'gestion:categorias_crear', 'gestion:estados', 'gestion:usuarios')

    def test_sin_sesion_pide_ingresar(self):
        self.client.logout()
        for ruta in self.RUTAS:
            respuesta = self.client.get(reverse(ruta))
            self.assertRedirects(respuesta, f"{reverse('login')}?next={reverse(ruta)}", fetch_redirect_response=False)

    def test_ciudadano_recibe_403(self):
        self.client.force_login(self.vecino.cuenta)
        for ruta in self.RUTAS:
            self.assertEqual(self.client.get(reverse(ruta)).status_code, 403, ruta)

    def test_administrador_entra_a_todas(self):
        for ruta in self.RUTAS:
            self.assertEqual(self.client.get(reverse(ruta)).status_code, 200, ruta)

    def test_menu_gestion_solo_para_administradores(self):
        self.assertContains(self.client.get(reverse('inicio')), reverse('gestion:panel'))
        self.client.force_login(self.vecino.cuenta)
        self.assertNotContains(self.client.get(reverse('inicio')), reverse('gestion:panel'))


class PanelTest(BaseGestionTest):
    def test_muestra_totales_y_ultimos_cambios(self):
        reporte = self.crear_reporte()
        reporte.cambiar_estado(Estado.objects.get(nombre_estado=Estado.RESUELTO), self.admin, 'Listo')
        respuesta = self.client.get(reverse('gestion:panel'))
        self.assertEqual(respuesta.context['total_reportes'], 1)
        self.assertEqual(respuesta.context['total_usuarios'], Usuario.objects.count())
        self.assertContains(respuesta, 'Últimos cambios de estado')
        self.assertContains(respuesta, reporte.get_absolute_url())


class CategoriasTest(BaseGestionTest):
    def test_crud_completo(self):
        respuesta = self.client.post(reverse('gestion:categorias_crear'),
                                     {'nombre_categoria': 'Tala de árboles', 'descripcion': 'Corte sin permiso'})
        self.assertRedirects(respuesta, reverse('gestion:categorias'))
        categoria = CategoriaProblema.objects.get(nombre_categoria='Tala de árboles')
        self.assertContains(self.client.get(reverse('gestion:categorias')), 'Tala de árboles')

        self.client.post(reverse('gestion:categorias_editar', args=[categoria.pk]),
                         {'nombre_categoria': 'Tala ilegal', 'descripcion': ''})
        categoria.refresh_from_db()
        self.assertEqual(categoria.nombre_categoria, 'Tala ilegal')

        self.client.post(reverse('gestion:categorias_eliminar', args=[categoria.pk]))
        self.assertFalse(CategoriaProblema.objects.filter(pk=categoria.pk).exists())

    def test_no_permite_nombre_repetido_aunque_cambien_mayusculas(self):
        respuesta = self.client.post(reverse('gestion:categorias_crear'), {'nombre_categoria': ' botadero CLANDESTINO '})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, 'Ya existe un registro con ese nombre.')
        self.assertContains(respuesta, 'is-invalid')

    def test_no_elimina_categoria_con_reportes(self):
        self.crear_reporte()
        respuesta = self.client.get(reverse('gestion:categorias_eliminar', args=[self.categoria.pk]))
        self.assertContains(respuesta, 'Cámbialo de categoría antes de eliminar.')
        self.client.post(reverse('gestion:categorias_eliminar', args=[self.categoria.pk]))
        self.assertTrue(CategoriaProblema.objects.filter(pk=self.categoria.pk).exists())


class EstadosTest(BaseGestionTest):
    def test_crear_y_eliminar_estado_nuevo(self):
        self.client.post(reverse('gestion:estados_crear'), {'nombre_estado': 'En revisión', 'descripcion': ''})
        estado = Estado.objects.get(nombre_estado='En revisión')
        self.client.post(reverse('gestion:estados_eliminar', args=[estado.pk]))
        self.assertFalse(Estado.objects.filter(pk=estado.pk).exists())

    def test_estado_del_sistema_no_se_renombra_ni_elimina(self):
        self.client.post(reverse('gestion:estados_editar', args=[self.pendiente.pk]),
                         {'nombre_estado': 'Otro nombre', 'descripcion': 'Nueva descripción'})
        self.pendiente.refresh_from_db()
        self.assertEqual(self.pendiente.nombre_estado, Estado.PENDIENTE)
        self.assertEqual(self.pendiente.descripcion, 'Nueva descripción')

        respuesta = self.client.post(reverse('gestion:estados_eliminar', args=[self.pendiente.pk]), follow=True)
        self.assertContains(respuesta, 'es un estado que usa el sistema')
        self.assertTrue(Estado.objects.filter(pk=self.pendiente.pk).exists())


class UsuariosTest(BaseGestionTest):
    def test_buscar_por_nombre_o_correo(self):
        respuesta = self.client.get(reverse('gestion:usuarios'), {'q': 'vecino@'})
        self.assertEqual(list(respuesta.context['object_list']), [self.vecino])

    def test_cambiar_rol_y_desactivar_cuenta(self):
        rol_admin = Rol.objects.get(nombre_rol=Rol.ADMINISTRADOR)
        self.client.post(reverse('gestion:usuarios_editar', args=[self.vecino.pk]), {
            'nombre': 'Ana María', 'apellido': 'Pérez', 'telefono': '', 'id_rol': rol_admin.pk,
        })
        self.vecino.refresh_from_db()
        self.vecino.cuenta.refresh_from_db()
        self.assertEqual(self.vecino.id_rol, rol_admin)
        self.assertEqual(self.vecino.cuenta.first_name, 'Ana María')
        self.assertFalse(self.vecino.cuenta.is_active)

    def test_no_puede_quitarse_el_acceso_ni_eliminarse(self):
        rol_ciudadano = Rol.objects.get(nombre_rol=Rol.CIUDADANO)
        self.client.post(reverse('gestion:usuarios_editar', args=[self.admin.pk]), {
            'nombre': 'Ana', 'apellido': 'Pérez', 'telefono': '', 'id_rol': rol_ciudadano.pk,
        })
        self.admin.refresh_from_db()
        self.admin.cuenta.refresh_from_db()
        self.assertEqual(self.admin.id_rol.nombre_rol, Rol.ADMINISTRADOR)
        self.assertTrue(self.admin.cuenta.is_active)

        self.client.post(reverse('gestion:usuarios_eliminar', args=[self.admin.pk]))
        self.assertTrue(Usuario.objects.filter(pk=self.admin.pk).exists())

    def test_eliminar_usuario_borra_su_cuenta_y_sus_reportes(self):
        self.crear_reporte()
        cuenta_id = self.vecino.cuenta_id
        respuesta = self.client.post(reverse('gestion:usuarios_eliminar', args=[self.vecino.pk]))
        self.assertRedirects(respuesta, reverse('gestion:usuarios'))
        self.assertFalse(Usuario.objects.filter(pk=self.vecino.pk).exists())
        self.assertFalse(type(self.admin.cuenta).objects.filter(pk=cuenta_id).exists())
        self.assertFalse(ReporteAmbiental.objects.exists())

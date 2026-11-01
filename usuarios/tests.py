from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Rol, Usuario


class RegistroTest(TestCase):
    def setUp(self):
        call_command('cargar_datos_iniciales', verbosity=0)

    def datos(self, **extra):
        datos = {
            'nombre': 'Carlos', 'apellido': 'Hernández', 'correo': 'Carlos@Correo.com',
            'telefono': '7777-7777', 'password1': 'unaClaveSegura2026', 'password2': 'unaClaveSegura2026',
        }
        datos.update(extra)
        return datos

    def test_registro_crea_cuenta_y_perfil(self):
        respuesta = self.client.post(reverse('usuarios:registro'), self.datos())
        self.assertRedirects(respuesta, reverse('inicio'))
        perfil = Usuario.objects.get(correo='carlos@correo.com')
        self.assertEqual(perfil.cuenta.username, 'carlos@correo.com')
        self.assertEqual(perfil.id_rol.nombre_rol, Rol.CIUDADANO)
        self.assertFalse(perfil.es_administrador)

    def test_no_permite_correo_repetido(self):
        self.client.post(reverse('usuarios:registro'), self.datos())
        self.client.logout()
        respuesta = self.client.post(reverse('usuarios:registro'), self.datos(correo='carlos@correo.com'))
        self.assertContains(respuesta, 'Ya existe una cuenta con este correo.')

    def test_login_con_correo(self):
        self.client.post(reverse('usuarios:registro'), self.datos())
        self.client.logout()
        respuesta = self.client.post(reverse('login'), {'username': 'CARLOS@correo.com', 'password': 'unaClaveSegura2026'})
        self.assertRedirects(respuesta, reverse('inicio'))

    def test_superusuario_recibe_perfil_de_administrador(self):
        cuenta = get_user_model().objects.create_superuser('jefe', 'jefe@test.com', 'clave-segura-123')
        perfil = Usuario.para_cuenta(cuenta)
        self.assertEqual(perfil.id_rol.nombre_rol, Rol.ADMINISTRADOR)
        self.assertTrue(perfil.es_administrador)

    def test_editar_perfil(self):
        self.client.post(reverse('usuarios:registro'), self.datos())
        self.client.post(reverse('usuarios:perfil'), {'nombre': 'Carlitos', 'apellido': 'H', 'telefono': ''})
        perfil = Usuario.objects.get(correo='carlos@correo.com')
        self.assertEqual(perfil.nombre, 'Carlitos')
        self.assertEqual(perfil.cuenta.first_name, 'Carlitos')


PROVEEDOR_GOOGLE = {'google': {'APPS': [{'client_id': 'id-de-prueba', 'secret': 'clave-de-prueba'}]}}


class InicioSesionSocialTest(TestCase):
    def setUp(self):
        call_command('cargar_datos_iniciales', verbosity=0)

    def entrar_con_google(self, correo, nombre='Ana', apellido='Martínez'):
        """Simula que Google respondió con esta persona y allauth guarda la cuenta."""
        from allauth.socialaccount.adapter import get_adapter
        from allauth.socialaccount.models import SocialAccount, SocialLogin
        from django.contrib.sessions.middleware import SessionMiddleware
        from django.test import RequestFactory

        request = RequestFactory().get('/')
        SessionMiddleware(lambda r: None).process_request(request)
        cuenta = get_user_model()(email=correo, first_name=nombre, last_name=apellido)
        login_social = SocialLogin(user=cuenta, account=SocialAccount(provider='google', uid='12345'))
        return get_adapter(request).save_user(request, login_social)

    def test_sin_credenciales_no_hay_botones(self):
        with self.settings(SOCIALACCOUNT_PROVIDERS={}):
            respuesta = self.client.get(reverse('login'))
        self.assertNotContains(respuesta, 'Continuar con')

    def test_boton_aparece_al_configurar_el_proveedor(self):
        with self.settings(SOCIALACCOUNT_PROVIDERS=PROVEEDOR_GOOGLE):
            for pagina in ('login', 'usuarios:registro'):
                respuesta = self.client.get(reverse(pagina))
                self.assertContains(respuesta, 'Continuar con Google')
                self.assertContains(respuesta, reverse('google_login'))

    def test_boton_lleva_a_google(self):
        with self.settings(SOCIALACCOUNT_PROVIDERS=PROVEEDOR_GOOGLE):
            respuesta = self.client.post(reverse('google_login'))
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(respuesta['Location'].startswith('https://accounts.google.com/'))
        self.assertIn('client_id=id-de-prueba', respuesta['Location'])

    def test_cuenta_nueva_usa_el_correo_y_recibe_perfil(self):
        cuenta = self.entrar_con_google('Ana@Gmail.com')
        self.assertEqual(cuenta.username, 'ana@gmail.com')
        perfil = Usuario.objects.get(cuenta=cuenta)
        self.assertEqual((perfil.nombre, perfil.apellido, perfil.correo), ('Ana', 'Martínez', 'ana@gmail.com'))
        self.assertEqual(perfil.id_rol.nombre_rol, Rol.CIUDADANO)
        self.assertFalse(cuenta.has_usable_password())

    def test_perfil_ofrece_crear_contrasena_a_cuentas_sociales(self):
        self.client.force_login(self.entrar_con_google('ana@gmail.com'))
        respuesta = self.client.get(reverse('usuarios:perfil'))
        self.assertContains(respuesta, 'Crear contraseña')
        self.assertContains(respuesta, 'Cuentas conectadas')

    def test_paginas_de_allauth_redirigen_a_las_del_proyecto(self):
        self.assertRedirects(self.client.get('/cuentas/login/'), reverse('login'))
        self.assertRedirects(self.client.get('/cuentas/signup/'), reverse('usuarios:registro'))

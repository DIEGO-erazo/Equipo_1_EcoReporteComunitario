from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.db import transaction

from .models import Rol, Usuario

User = get_user_model()


class RegistroForm(UserCreationForm):
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    correo = forms.EmailField(max_length=150, label='Correo electrónico')
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono (opcional)')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('nombre', 'apellido', 'correo', 'telefono')

    def clean_correo(self):
        correo = self.cleaned_data['correo'].lower()
        if User.objects.filter(username__iexact=correo).exists() or Usuario.objects.filter(correo__iexact=correo).exists():
            raise forms.ValidationError('Ya existe una cuenta con este correo.')
        return correo

    def _post_clean(self):
        # El correo es el nombre de usuario; se asigna antes de validar la contraseña
        # para que el validador de similitud lo tome en cuenta.
        if 'correo' in self.cleaned_data:
            self.instance.username = self.cleaned_data['correo']
            self.instance.email = self.cleaned_data['correo']
        super()._post_clean()

    @transaction.atomic
    def save(self, commit=True):
        cuenta = super().save(commit=False)
        cuenta.first_name = self.cleaned_data['nombre']
        cuenta.last_name = self.cleaned_data['apellido']
        cuenta.save()
        rol, _ = Rol.objects.get_or_create(nombre_rol=Rol.CIUDADANO)
        Usuario.objects.create(
            cuenta=cuenta,
            nombre=self.cleaned_data['nombre'],
            apellido=self.cleaned_data['apellido'],
            correo=self.cleaned_data['correo'],
            telefono=self.cleaned_data['telefono'] or None,
            id_rol=rol,
        )
        return cuenta


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Correo electrónico', widget=forms.TextInput(attrs={'autofocus': True}))

    def clean(self):
        if self.cleaned_data.get('username'):
            self.cleaned_data['username'] = self.cleaned_data['username'].strip().lower()
        return super().clean()


class PerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ('nombre', 'apellido', 'telefono')

    @transaction.atomic
    def save(self, commit=True):
        perfil = super().save(commit)
        if perfil.cuenta_id:
            perfil.cuenta.first_name = perfil.nombre
            perfil.cuenta.last_name = perfil.apellido
            perfil.cuenta.save(update_fields=['first_name', 'last_name'])
        return perfil

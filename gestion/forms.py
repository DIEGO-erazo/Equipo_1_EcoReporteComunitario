from django import forms
from django.db import transaction

from reportes.models import CategoriaProblema, Estado
from usuarios.models import Usuario


def _nombre_unico(form, campo):
    """Evita nombres repetidos aunque cambien mayúsculas o espacios ("Basura" y " basura")."""
    nombre = form.cleaned_data[campo].strip()
    repetidos = form._meta.model.objects.filter(**{f'{campo}__iexact': nombre}).exclude(pk=form.instance.pk)
    if repetidos.exists():
        raise forms.ValidationError('Ya existe un registro con ese nombre.')
    return nombre


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = CategoriaProblema
        fields = ('nombre_categoria', 'descripcion')
        labels = {'nombre_categoria': 'Nombre', 'descripcion': 'Descripción'}
        widgets = {
            'nombre_categoria': forms.TextInput(attrs={'placeholder': 'Ej.: Quema de basura'}),
            'descripcion': forms.TextInput(attrs={'placeholder': 'Opcional'}),
        }

    def clean_nombre_categoria(self):
        return _nombre_unico(self, 'nombre_categoria')


class EstadoForm(forms.ModelForm):
    class Meta:
        model = Estado
        fields = ('nombre_estado', 'descripcion')
        labels = {'nombre_estado': 'Nombre', 'descripcion': 'Descripción'}
        widgets = {
            'nombre_estado': forms.TextInput(attrs={'placeholder': 'Ej.: En revisión'}),
            'descripcion': forms.TextInput(attrs={'placeholder': 'Opcional'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.es_del_sistema:
            self.fields['nombre_estado'].disabled = True
            self.fields['nombre_estado'].help_text = 'El sistema usa este estado; solo puedes cambiar su descripción.'

    def clean_nombre_estado(self):
        return _nombre_unico(self, 'nombre_estado')


class UsuarioGestionForm(forms.ModelForm):
    activo = forms.BooleanField(label='Cuenta activa', required=False,
                                help_text='Una cuenta inactiva no puede iniciar sesión.')

    class Meta:
        model = Usuario
        fields = ('nombre', 'apellido', 'telefono', 'id_rol')
        labels = {'telefono': 'Teléfono', 'id_rol': 'Rol'}

    def __init__(self, *args, editor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['id_rol'].empty_label = None
        self.fields['id_rol'].help_text = 'Los administradores cambian el estado de los reportes y entran a Gestión.'
        cuenta = self.instance.cuenta
        if cuenta is None:
            del self.fields['activo']
        else:
            self.fields['activo'].initial = cuenta.is_active
        if editor is not None and editor.pk == self.instance.pk:
            # Así nadie se queda fuera por accidente quitándose su propio acceso.
            for campo in ('id_rol', 'activo'):
                if campo in self.fields:
                    self.fields[campo].disabled = True
                    self.fields[campo].help_text = 'No puedes cambiar esto en tu propia cuenta.'

    @transaction.atomic
    def save(self, commit=True):
        perfil = super().save(commit)
        if perfil.cuenta_id:
            cuenta = perfil.cuenta
            cuenta.first_name = perfil.nombre
            cuenta.last_name = perfil.apellido
            cuenta.is_active = self.cleaned_data['activo']
            cuenta.save(update_fields=['first_name', 'last_name', 'is_active'])
        return perfil

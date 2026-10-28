from django import forms
from django.conf import settings

from .models import CategoriaProblema, Estado, ReporteAmbiental


class VariasFotosInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class VariasFotosField(forms.ImageField):
    """Campo que acepta varias imágenes y devuelve una lista ya validada."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', VariasFotosInput(attrs={'accept': 'image/*'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        archivos = [f for f in (data if isinstance(data, (list, tuple)) else [data]) if f]
        if not archivos and self.required:
            raise forms.ValidationError(self.error_messages['required'], code='required')
        limpias = []
        for archivo in archivos:
            imagen = super().clean(archivo, initial)
            if imagen.size > settings.MAX_TAMANO_EVIDENCIA:
                raise forms.ValidationError(f'La foto «{imagen.name}» supera los 5 MB.')
            limpias.append(imagen)
        return limpias


class ReporteForm(forms.ModelForm):
    fotos = VariasFotosField(
        label='Fotos de evidencia',
        required=False,
        help_text='Puedes adjuntar varias fotos (máximo 5 MB cada una).',
    )

    class Meta:
        model = ReporteAmbiental
        fields = ('titulo', 'id_categoria', 'descripcion', 'ubicacion_direccion', 'latitud', 'longitud')
        labels = {
            'titulo': 'Título',
            'id_categoria': 'Categoría',
            'ubicacion_direccion': 'Ubicación o referencia',
        }
        widgets = {
            'titulo': forms.TextInput(attrs={'placeholder': 'Ej.: Basura acumulada frente a la escuela'}),
            'descripcion': forms.Textarea(attrs={'rows': 5, 'placeholder': '¿Qué está pasando? ¿Desde cuándo?'}),
            'ubicacion_direccion': forms.TextInput(attrs={'placeholder': 'Ej.: Barrio El Centro, calle principal'}),
            'latitud': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Opcional'}),
            'longitud': forms.NumberInput(attrs={'step': 'any', 'placeholder': 'Opcional'}),
        }


class CambioEstadoForm(forms.Form):
    nuevo_estado = forms.ModelChoiceField(queryset=Estado.objects.all(), label='Nuevo estado', empty_label=None)
    comentario = forms.CharField(
        label='Comentario', required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ej.: Se coordinó la limpieza con la alcaldía.'}),
    )


class FiltroReportesForm(forms.Form):
    q = forms.CharField(label='Buscar', required=False,
                        widget=forms.TextInput(attrs={'placeholder': 'Título, descripción o lugar'}))
    categoria = forms.ModelChoiceField(queryset=CategoriaProblema.objects.all(), required=False,
                                       empty_label='Todas las categorías')
    estado = forms.ModelChoiceField(queryset=Estado.objects.all(), required=False,
                                    empty_label='Todos los estados')

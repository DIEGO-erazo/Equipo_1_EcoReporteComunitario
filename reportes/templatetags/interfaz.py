from django import forms, template

register = template.Library()


@register.filter
def bootstrap(campo):
    """Dibuja el campo de un formulario con las clases de Bootstrap que le corresponden."""
    widget = campo.field.widget
    if isinstance(widget, forms.CheckboxInput):
        clase = 'form-check-input'
    elif isinstance(widget, forms.Select):
        clase = 'form-select'
    else:
        clase = 'form-control'
    if campo.errors:
        clase += ' is-invalid'
    existentes = widget.attrs.get('class', '')
    return campo.as_widget(attrs={'class': f'{existentes} {clase}'.strip()})


@register.filter
def es_casilla(campo):
    return isinstance(campo.field.widget, forms.CheckboxInput)

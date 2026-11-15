"""Archivos Excel y PDF con la lista de reportes, para los administradores."""
from io import BytesIO
from xml.sax.saxutils import escape

from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

VERDE = '2F7D4F'
VERDE_CLARO = 'E6F4EA'


def describir_filtros(filtro):
    """Texto con los filtros usados, para que el archivo diga qué contiene."""
    if not filtro.is_valid():
        return 'Todos los reportes'
    partes = []
    if filtro.cleaned_data['q']:
        partes.append(f"Búsqueda: «{filtro.cleaned_data['q']}»")
    if filtro.cleaned_data['categoria']:
        partes.append(f"Categoría: {filtro.cleaned_data['categoria']}")
    if filtro.cleaned_data['estado']:
        partes.append(f"Estado: {filtro.cleaned_data['estado']}")
    return ' · '.join(partes) or 'Todos los reportes'


def _fecha(reporte):
    return timezone.localtime(reporte.fecha_reporte)


# --- Excel ---------------------------------------------------------------

COLUMNAS_EXCEL = [
    ('N.º', 8), ('Título', 38), ('Categoría', 24), ('Estado', 14), ('Descripción', 60),
    ('Ubicación', 36), ('Latitud', 12), ('Longitud', 12), ('Reportado por', 26), ('Correo', 30), ('Fecha', 17),
]


def excel(reportes, filtro):
    libro = Workbook()
    hoja = libro.active
    hoja.title = 'Reportes'
    hoja.append(['Reportes ambientales — EcoReporte Comunitario'])
    hoja.append([f'{describir_filtros(filtro)} · Generado el {timezone.localtime():%d/%m/%Y %H:%M}'])
    hoja.append([])
    hoja.append([nombre for nombre, _ in COLUMNAS_EXCEL])
    hoja['A1'].font = Font(bold=True, size=14, color=VERDE)
    for celda in hoja[4]:
        celda.font = Font(bold=True, color='FFFFFF')
        celda.fill = PatternFill('solid', fgColor=VERDE)

    for reporte in reportes:
        hoja.append([
            reporte.pk, reporte.titulo, str(reporte.id_categoria), str(reporte.id_estado), reporte.descripcion,
            reporte.ubicacion_direccion,
            float(reporte.latitud) if reporte.latitud is not None else None,
            float(reporte.longitud) if reporte.longitud is not None else None,
            reporte.id_usuario.nombre_completo, reporte.id_usuario.correo,
            _fecha(reporte).replace(tzinfo=None),  # Excel no guarda zonas horarias.
        ])
        for celda in hoja[hoja.max_row]:
            # Un texto que empieza con "=" es texto, no una fórmula de Excel.
            if isinstance(celda.value, str) and celda.value.startswith('='):
                celda.data_type = 's'
            celda.alignment = Alignment(vertical='top', wrap_text=True)
        hoja.cell(hoja.max_row, len(COLUMNAS_EXCEL)).number_format = 'dd/mm/yyyy hh:mm'

    for numero, (_, ancho) in enumerate(COLUMNAS_EXCEL, start=1):
        hoja.column_dimensions[get_column_letter(numero)].width = ancho
    hoja.freeze_panes = 'A5'
    hoja.auto_filter.ref = f'A4:{get_column_letter(len(COLUMNAS_EXCEL))}{hoja.max_row}'

    archivo = BytesIO()
    libro.save(archivo)
    return archivo.getvalue()


# --- PDF -----------------------------------------------------------------

COLUMNAS_PDF = [
    ('N.º', 1.2), ('Título', 6.5), ('Categoría', 4.0), ('Estado', 2.6),
    ('Ubicación', 6.0), ('Reportado por', 4.0), ('Fecha', 2.4),
]


def _numero_de_pagina(lienzo, documento):
    lienzo.saveState()
    lienzo.setFont('Helvetica', 8)
    lienzo.setFillColor(colors.HexColor('#5B6B61'))
    lienzo.drawString(1.5 * cm, 1 * cm, 'EcoReporte Comunitario · San Rafael, Chalatenango')
    lienzo.drawRightString(documento.pagesize[0] - 1.5 * cm, 1 * cm, f'Página {documento.page}')
    lienzo.restoreState()


def pdf(reportes, filtro):
    archivo = BytesIO()
    documento = SimpleDocTemplate(
        archivo, pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.8 * cm,
        title='Reportes ambientales — EcoReporte Comunitario', author='EcoReporte Comunitario',
    )
    estilos = getSampleStyleSheet()
    titulo = ParagraphStyle('titulo', parent=estilos['Title'], alignment=0, textColor=colors.HexColor('#' + VERDE))
    celda = ParagraphStyle('celda', parent=estilos['BodyText'], fontSize=8.5, leading=10.5)
    encabezado = ParagraphStyle('encabezado', parent=celda, fontName='Helvetica-Bold', textColor=colors.white)

    reportes = list(reportes)
    contenido = [
        Paragraph('Reportes ambientales — EcoReporte Comunitario', titulo),
        Paragraph(escape(f'{describir_filtros(filtro)} · {len(reportes)} reporte{"s" if len(reportes) != 1 else ""}'
                         f' · Generado el {timezone.localtime():%d/%m/%Y %H:%M}'), estilos['Normal']),
        Spacer(1, 0.4 * cm),
    ]
    if not reportes:
        contenido.append(Paragraph('No hay reportes con esos filtros.', estilos['Italic']))
        documento.build(contenido, onFirstPage=_numero_de_pagina, onLaterPages=_numero_de_pagina)
        return archivo.getvalue()

    filas = [[Paragraph(nombre, encabezado) for nombre, _ in COLUMNAS_PDF]]
    for reporte in reportes:
        valores = [
            reporte.pk, reporte.titulo, reporte.id_categoria, reporte.id_estado, reporte.ubicacion_direccion,
            reporte.id_usuario.nombre_completo, f'{_fecha(reporte):%d/%m/%Y}',
        ]
        filas.append([Paragraph(escape(str(valor)), celda) for valor in valores])

    tabla = Table(filas, colWidths=[ancho * cm for _, ancho in COLUMNAS_PDF], repeatRows=1)
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#' + VERDE)),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#' + VERDE_CLARO)]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#C9D3CC')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    contenido.append(tabla)
    documento.build(contenido, onFirstPage=_numero_de_pagina, onLaterPages=_numero_de_pagina)
    return archivo.getvalue()

from django.http import HttpResponse


def inicio(request):
    contenido = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EcoReporte Comunitario</title>
    </head>
    <body>
        <h1>EcoReporte Comunitario</h1>
        <h2>Bienvenido a nuestra plataforma ambiental</h2>
        <p>Reporta problemas ambientales de tu comunidad.</p>
        <p>Juntos podemos construir un entorno más limpio y saludable.</p>
    </body>
    </html>
    """
    return HttpResponse(contenido)
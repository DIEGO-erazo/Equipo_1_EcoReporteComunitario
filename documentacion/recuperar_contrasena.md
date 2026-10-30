# Recuperar la contraseña por correo

En la página **Ingresar** hay un enlace **"¿Olvidaste tu contraseña?"**. La persona escribe su
correo y le llega un enlace para crear una contraseña nueva. El enlace sirve una sola vez y
vence en 24 horas. La página no dice si el correo está registrado, para no revelar quién
tiene cuenta.

Para que los correos se envíen de verdad, el servidor necesita una cuenta de correo.
Sin ella, el sitio funciona igual, pero los correos solo se muestran en la consola del
servidor, y la página avisa que por ahora no se pueden enviar.

## Conectar una cuenta de Gmail

1. **Usa una cuenta de Gmail del proyecto**, no una personal (por ejemplo,
   `ecoreporte.sanrafael@gmail.com`). Los correos saldrán con esa dirección.
2. En esa cuenta, activa la **verificación en dos pasos**:
   <https://myaccount.google.com/security>
3. Crea una **contraseña de aplicación** en <https://myaccount.google.com/apppasswords>.
   Ponle de nombre `EcoReporte` y copia las 16 letras que muestra Google.
   (No es la contraseña normal de la cuenta; si la borras ahí, el sitio deja de enviar correos.)
4. En la laptop del servidor, abre una terminal en la carpeta del proyecto y ejecuta:
   ```bash
   bash servidor/configurar_correo.sh
   ```
   Te pide el correo y las 16 letras (no se ven al escribirlas), prueba que Gmail los acepte,
   los guarda en el `.env` y reinicia la página. Si Gmail los rechaza, no cambia nada.
5. Si prefieres hacerlo a mano: agrega al final del `.env` del proyecto
   `CORREO_USUARIO=tucorreo@gmail.com` y `CORREO_CONTRASENA=las 16 letras`, y luego
   ejecuta `sudo systemctl restart ecoreporte`.
6. Prueba: abre la página → **Ingresar** → **¿Olvidaste tu contraseña?** y escribe tu correo.

El `.env` no se sube a GitHub, así que la contraseña de aplicación queda solo en el servidor.

## Si el correo no llega

- Revisa la carpeta de **spam** o correo no deseado.
- Si la página dice *"No pudimos enviar el correo en este momento"*, revisa el error con:
  ```bash
  journalctl -u ecoreporte -n 50
  ```
  Lo más común es una contraseña de aplicación mal copiada o la verificación en dos pasos desactivada.
- Las cuentas que entran con **Google, GitHub o Microsoft** no tienen contraseña, así que no reciben
  enlace: deben usar ese botón para ingresar (y desde su perfil pueden crear una contraseña).
- Gmail permite unos 500 correos por día, más que suficiente para el proyecto.

## Otro proveedor de correo

Si no es Gmail, agrega también el servidor SMTP y su puerto (con TLS):
```
CORREO_SERVIDOR=smtp.office365.com
CORREO_PUERTO=587
```

## En una computadora de desarrollo

Sin `CORREO_USUARIO` en el `.env`, el correo con el enlace aparece en la terminal donde
corre `python manage.py runserver`; se puede copiar el enlace de ahí para probar.

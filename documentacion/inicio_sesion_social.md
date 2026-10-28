# Iniciar sesión con Google, GitHub y Microsoft

Además del correo y la contraseña, EcoReporte permite entrar con una cuenta de **Google**,
**GitHub** o **Microsoft** (Outlook, Hotmail o cuentas de escuela y trabajo). Lo maneja la
librería [django-allauth](https://docs.allauth.org/).

- Cada botón aparece **solo** cuando su proveedor tiene credenciales en el `.env`. Puedes
  activar uno, dos o los tres.
- La primera vez que alguien entra con un proveedor se le crea su cuenta y su perfil de
  ciudadano. Si su correo ya estaba registrado en EcoReporte, entra a esa misma cuenta.
- Quien entró con un proveedor puede crear una contraseña desde **Mi perfil → Crear contraseña**
  y ver o quitar sus proveedores en **Mi perfil → Cuentas conectadas**.

## Antes de empezar: la dirección de la página

Cada proveedor pide la **dirección de regreso** (callback) a la que manda a la persona después
de iniciar sesión, y solo acepta las que registres. Esa dirección debe ser **fija**:

| Dónde corre | Dirección de regreso (cambia `google` por `github` o `microsoft`) |
|---|---|
| Tu computadora, para probar | `http://localhost:8000/cuentas/google/login/callback/` |
| El servidor, con dominio propio | `https://tudominio.com/cuentas/google/login/callback/` |

> La dirección gratuita `*.trycloudflare.com` cambia cada vez que se reinicia el servidor, así que
> no sirve para esto. Para usar el inicio de sesión social en internet hace falta un dominio propio
> conectado a Cloudflare.

Después de poner las credenciales en el `.env`, reinicia la app: en tu computadora, detén y vuelve a
iniciar `runserver`; en el servidor, `sudo systemctl restart ecoreporte`.

## Google

1. Entra a <https://console.cloud.google.com/> y crea un proyecto (por ejemplo, "EcoReporte").
2. Ve a **APIs y servicios → Pantalla de consentimiento de OAuth**. Elige **Externo**, escribe el
   nombre de la app y tu correo de soporte, y guarda. No hace falta agregar permisos extra.
3. En **Público** (o "Usuarios de prueba"), pulsa **Publicar app**. Mientras esté en modo de
   prueba, solo pueden entrar los correos que agregues como usuarios de prueba.
4. Ve a **APIs y servicios → Credenciales → Crear credenciales → ID de cliente de OAuth**.
   - Tipo de aplicación: **Aplicación web**.
   - **URI de redireccionamiento autorizados**: agrega la de pruebas y la de tu dominio (tabla de arriba).
5. Copia el **ID de cliente** y el **Secreto del cliente** al `.env`:
   ```
   GOOGLE_CLIENT_ID=1234567890-abc.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=GOCSPX-...
   ```

## GitHub

1. Entra a <https://github.com/settings/developers> → **OAuth Apps → New OAuth App**.
2. Llena los datos:
   - **Homepage URL**: la dirección de la página (`http://localhost:8000` para probar).
   - **Authorization callback URL**: la dirección de regreso de la tabla, con `github`.
3. Pulsa **Register application** y luego **Generate a new client secret**.
4. Copia los valores al `.env`:
   ```
   GITHUB_CLIENT_ID=Ov23li...
   GITHUB_CLIENT_SECRET=...
   ```

> GitHub solo permite **una** dirección de regreso por app. Crea una app para probar en tu
> computadora y otra para el servidor.

## Microsoft

1. Entra a <https://entra.microsoft.com/> → **Aplicaciones → Registros de aplicaciones → Nuevo registro**.
   Sirve cualquier cuenta de Microsoft (Outlook o Hotmail).
2. En **Tipos de cuenta compatibles**, elige *Cuentas de cualquier directorio organizativo y cuentas
   personales de Microsoft*.
3. En **URI de redirección**, elige **Web** y escribe la dirección de regreso con `microsoft`.
   Para probar usa `localhost`, no `127.0.0.1`.
4. Pulsa **Registrar** y copia el **Id. de aplicación (cliente)**.
5. Ve a **Certificados y secretos → Nuevo secreto de cliente** y copia el **Valor** (no el Id. del secreto).
6. Pon los valores en el `.env`:
   ```
   MICROSOFT_CLIENT_ID=00000000-0000-0000-0000-000000000000
   MICROSOFT_CLIENT_SECRET=...
   ```

> El secreto de Microsoft vence (máximo a los 24 meses). Anota la fecha y crea uno nuevo antes de
> que venza, o el botón dejará de funcionar.

## Si algo falla

| Mensaje | Causa probable |
|---|---|
| `redirect_uri_mismatch` (Google) o *"The redirect_uri is not associated"* (GitHub) | La dirección de regreso registrada no coincide letra por letra con la de la página. Revisa `http`/`https`, el dominio y la `/` final. |
| *"Falló la autenticación de terceros"* | El ID o el secreto están mal copiados en el `.env`, o no reiniciaste la app después de cambiarlo. |
| Google dice que la app no está verificada o que no tienes acceso | La pantalla de consentimiento sigue en modo de prueba (paso 3 de Google). |
| El botón no aparece | Falta el `_CLIENT_ID` o el `_CLIENT_SECRET` de ese proveedor, o no se reinició la app. |

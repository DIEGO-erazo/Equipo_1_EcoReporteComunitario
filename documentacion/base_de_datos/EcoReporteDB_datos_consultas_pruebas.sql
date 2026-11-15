/* =====================================================================
   EcoReporte Comunitario · EcoReporteDB · Datos, consultas y pruebas
   Equipo N.º 1 · Diseño de Base de Datos · Ciclo 02-2026

   Parte 1: datos de prueba (3 usuarios, 6 reportes, 4 seguimientos y
            3 evidencias).
   Parte 2: consultas C1 a C9.
   Parte 3: pruebas de integridad I1 a I6. Cada una intenta romper una
            regla de la base; el mensaje de error es la evidencia.

   Requisito: una base EcoReporteDB con las tablas y los catálogos ya
   creados (EcoReporteDB_estructura.sql, o  python manage.py migrate
   seguido de  python manage.py cargar_datos_iniciales) y sin reportes.

   Uso: SQL Server Management Studio o Azure Data Studio, o
       sqlcmd -S <servidor> -U <usuario> -C -f 65001 -i EcoReporteDB_datos_consultas_pruebas.sql
   Los usuarios de prueba no tienen cuenta de acceso (cuenta_id NULL): sirven
   para las consultas, no para iniciar sesión en la página.
   ===================================================================== */

USE EcoReporteDB;
GO
SET NOCOUNT ON;
-- Necesarias para escribir en tablas con índices únicos filtrados (usuarios.cuenta_id);
-- SSMS ya las trae encendidas, sqlcmd no.
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

/* =====================================================================
   PARTE 1 · Datos de prueba
   ===================================================================== */
IF EXISTS (SELECT 1 FROM reportes)
BEGIN
    PRINT N'La base ya tiene reportes: la Parte 1 se omite para no duplicar datos.';
    SET NOEXEC ON;
END
GO

DECLARE @ciudadano int = (SELECT id_rol FROM roles WHERE nombre_rol = N'Ciudadano');
DECLARE @administrador int = (SELECT id_rol FROM roles WHERE nombre_rol = N'Administrador');
DECLARE @pendiente int = (SELECT id_estado FROM estados WHERE nombre_estado = N'Pendiente');
DECLARE @en_proceso int = (SELECT id_estado FROM estados WHERE nombre_estado = N'En proceso');
DECLARE @resuelto int = (SELECT id_estado FROM estados WHERE nombre_estado = N'Resuelto');
DECLARE @rechazado int = (SELECT id_estado FROM estados WHERE nombre_estado = N'Rechazado');
DECLARE @ahora datetimeoffset = SYSDATETIMEOFFSET();

-- Usuarios
INSERT INTO usuarios (nombre, apellido, correo, contrasena_hash, telefono, fecha_registro, id_rol) VALUES
    (N'Administrador', N'EcoReporte', N'admin@ecoreporte.local', N'', NULL, @ahora, @administrador),
    (N'María', N'López', N'vecina@ecoreporte.local', N'', N'7000-0001', @ahora, @ciudadano),
    (N'Carlos', N'Rivas', N'carlos.rivas@ecoreporte.local', N'', NULL, @ahora, @ciudadano);

DECLARE @admin int = (SELECT id_usuario FROM usuarios WHERE correo = N'admin@ecoreporte.local');
DECLARE @maria int = (SELECT id_usuario FROM usuarios WHERE correo = N'vecina@ecoreporte.local');
DECLARE @carlos int = (SELECT id_usuario FROM usuarios WHERE correo = N'carlos.rivas@ecoreporte.local');

-- Reportes: todos empiezan en Pendiente, como en la aplicación.
INSERT INTO reportes (titulo, descripcion, ubicacion_direccion, latitud, longitud, fecha_reporte,
                      id_usuario, id_categoria, id_estado) VALUES
    (N'Botadero junto a la quebrada',
     N'Desde hace dos semanas se tira basura a la orilla de la quebrada. Hay bolsas, llantas y plástico.',
     N'Calle hacia el río, después del puente', 14.133000, -89.032200, DATEADD(MINUTE, -60, @ahora), @maria,
     (SELECT id_categoria FROM categorias WHERE nombre_categoria = N'Botadero clandestino'), @pendiente),
    (N'Basura acumulada frente al Instituto',
     N'Los fines de semana se acumula basura en la entrada y los perros rompen las bolsas.',
     N'Entrada del Instituto Nacional de San Rafael', 14.133800, -89.028800, DATEADD(MINUTE, -55, @ahora), @maria,
     (SELECT id_categoria FROM categorias WHERE nombre_categoria = N'Acumulación de basura'), @pendiente),
    (N'El tren de aseo no pasó esta semana',
     N'El camión recolector no pasó el martes ni el viernes. Las familias no tienen dónde dejar la basura.',
     N'Barrio El Centro', 14.134700, -89.029600, DATEADD(MINUTE, -50, @ahora), @maria,
     (SELECT id_categoria FROM categorias WHERE nombre_categoria = N'Recolección de residuos'), @pendiente),
    (N'Quema de basura en solar baldío',
     N'Cada tarde queman bolsas de desechos y el humo llega a las casas vecinas.',
     N'Solar baldío detrás del mercado', NULL, NULL, DATEADD(MINUTE, -45, @ahora), @carlos,
     (SELECT id_categoria FROM categorias WHERE nombre_categoria = N'Quema de basura'), @pendiente),
    (N'Desechos en el nacimiento de agua',
     N'Hay plásticos y latas dentro del nacimiento que abastece a varias familias.',
     N'Nacimiento de agua al norte del pueblo', NULL, NULL, DATEADD(MINUTE, -40, @ahora), @carlos,
     (SELECT id_categoria FROM categorias WHERE nombre_categoria = N'Contaminación de agua'), @pendiente),
    (N'Basura frente a la cancha',
     N'Después de los partidos quedan bolsas y botellas en la entrada de la cancha.',
     N'Cancha municipal', NULL, NULL, DATEADD(MINUTE, -35, @ahora), @maria,
     (SELECT id_categoria FROM categorias WHERE nombre_categoria = N'Acumulación de basura'), @pendiente);

DECLARE @r1 int = (SELECT id_reporte FROM reportes WHERE titulo = N'Botadero junto a la quebrada');
DECLARE @r4 int = (SELECT id_reporte FROM reportes WHERE titulo = N'Quema de basura en solar baldío');
DECLARE @r5 int = (SELECT id_reporte FROM reportes WHERE titulo = N'Desechos en el nacimiento de agua');
DECLARE @r6 int = (SELECT id_reporte FROM reportes WHERE titulo = N'Basura frente a la cancha');

-- Seguimiento: cada cambio de estado deja su fila y actualiza el reporte en la misma
-- transacción, igual que ReporteAmbiental.cambiar_estado() en la aplicación.
BEGIN TRANSACTION;
    INSERT INTO seguimiento_reporte (id_reporte, id_usuario_responsable, id_estado_anterior, id_estado_nuevo,
                                     comentario, fecha_cambio)
    VALUES (@r1, @admin, @pendiente, @en_proceso, N'Se notificó a la alcaldía para programar la limpieza.',
            DATEADD(MINUTE, -30, @ahora));
    UPDATE reportes SET id_estado = @en_proceso WHERE id_reporte = @r1;
COMMIT;

BEGIN TRANSACTION;
    INSERT INTO seguimiento_reporte (id_reporte, id_usuario_responsable, id_estado_anterior, id_estado_nuevo,
                                     comentario, fecha_cambio)
    VALUES (@r5, @admin, @pendiente, @en_proceso,
            N'Se coordinó una jornada de limpieza con estudiantes del Instituto.', DATEADD(MINUTE, -25, @ahora));
    UPDATE reportes SET id_estado = @en_proceso WHERE id_reporte = @r5;
COMMIT;

BEGIN TRANSACTION;
    INSERT INTO seguimiento_reporte (id_reporte, id_usuario_responsable, id_estado_anterior, id_estado_nuevo,
                                     comentario, fecha_cambio)
    VALUES (@r5, @admin, @en_proceso, @resuelto, N'Jornada realizada; se retiraron 12 sacos de desechos.',
            DATEADD(MINUTE, -20, @ahora));
    UPDATE reportes SET id_estado = @resuelto WHERE id_reporte = @r5;
COMMIT;

BEGIN TRANSACTION;
    INSERT INTO seguimiento_reporte (id_reporte, id_usuario_responsable, id_estado_anterior, id_estado_nuevo,
                                     comentario, fecha_cambio)
    VALUES (@r6, @admin, @pendiente, @rechazado, N'En la visita el lugar ya estaba limpio.',
            DATEADD(MINUTE, -15, @ahora));
    UPDATE reportes SET id_estado = @rechazado WHERE id_reporte = @r6;
COMMIT;

-- Evidencias: la tabla guarda la ruta del archivo dentro de la carpeta media/.
INSERT INTO evidencias (id_reporte, url_imagen, fecha_subida) VALUES
    (@r4, N'evidencias/2026/11/quema_solar_1.jpg', DATEADD(MINUTE, -44, @ahora)),
    (@r4, N'evidencias/2026/11/quema_solar_2.jpg', DATEADD(MINUTE, -44, @ahora)),
    (@r5, N'evidencias/2026/11/nacimiento_agua_1.jpg', DATEADD(MINUTE, -39, @ahora));

PRINT N'Parte 1 lista: 3 usuarios, 6 reportes, 4 seguimientos y 3 evidencias.';
GO
SET NOEXEC OFF;
GO

/* =====================================================================
   PARTE 2 · Consultas
   ===================================================================== */

PRINT N'C1. Reportes con su categoría, estado y autor';
SELECT r.id_reporte, r.titulo, c.nombre_categoria AS categoria, e.nombre_estado AS estado,
       u.nombre + N' ' + u.apellido AS autor
FROM reportes AS r
INNER JOIN categorias AS c ON c.id_categoria = r.id_categoria
INNER JOIN estados    AS e ON e.id_estado    = r.id_estado
INNER JOIN usuarios   AS u ON u.id_usuario   = r.id_usuario
ORDER BY r.id_reporte;

PRINT N'C2. Reportes por estado';
SELECT e.nombre_estado AS estado, COUNT(r.id_reporte) AS total
FROM estados AS e
LEFT JOIN reportes AS r ON r.id_estado = e.id_estado
GROUP BY e.id_estado, e.nombre_estado
ORDER BY e.id_estado;

PRINT N'C3. Reportes por categoría y su porcentaje del total';
SELECT c.nombre_categoria AS categoria, COUNT(r.id_reporte) AS total,
       CAST(100.0 * COUNT(r.id_reporte) / (SELECT COUNT(*) FROM reportes) AS DECIMAL(5, 1)) AS porcentaje
FROM categorias AS c
LEFT JOIN reportes AS r ON r.id_categoria = c.id_categoria
GROUP BY c.id_categoria, c.nombre_categoria
ORDER BY total DESC, categoria;

PRINT N'C4. Historial de un reporte';
SELECT s.fecha_cambio, ea.nombre_estado AS estado_anterior, en.nombre_estado AS estado_nuevo,
       u.nombre + N' ' + u.apellido AS responsable, s.comentario
FROM seguimiento_reporte AS s
INNER JOIN reportes AS r  ON r.id_reporte = s.id_reporte
INNER JOIN estados  AS ea ON ea.id_estado = s.id_estado_anterior
INNER JOIN estados  AS en ON en.id_estado = s.id_estado_nuevo
INNER JOIN usuarios AS u  ON u.id_usuario = s.id_usuario_responsable
WHERE r.titulo = N'Desechos en el nacimiento de agua'
ORDER BY s.fecha_cambio, s.id_seguimiento;

PRINT N'C5. Reportes sin fotografías';
SELECT r.id_reporte, r.titulo
FROM reportes AS r
WHERE NOT EXISTS (SELECT 1 FROM evidencias AS ev WHERE ev.id_reporte = r.id_reporte)
ORDER BY r.id_reporte;

PRINT N'C6. Participación de cada usuario';
SELECT u.nombre + N' ' + u.apellido AS usuario, ro.nombre_rol AS rol, COUNT(r.id_reporte) AS reportes
FROM usuarios AS u
INNER JOIN roles AS ro ON ro.id_rol = u.id_rol
LEFT JOIN reportes AS r ON r.id_usuario = u.id_usuario
GROUP BY u.id_usuario, u.nombre, u.apellido, ro.nombre_rol
ORDER BY reportes DESC, usuario;

PRINT N'C7. Reportes abiertos y días sin resolverse';
SELECT r.id_reporte, r.titulo, e.nombre_estado AS estado,
       DATEDIFF(DAY, r.fecha_reporte, SYSDATETIMEOFFSET()) AS dias_abierto
FROM reportes AS r
INNER JOIN estados AS e ON e.id_estado = r.id_estado
WHERE e.nombre_estado IN (N'Pendiente', N'En proceso')
ORDER BY r.fecha_reporte, r.id_reporte;

PRINT N'C8. Búsqueda por texto y estado';
SELECT r.id_reporte, r.titulo, e.nombre_estado AS estado
FROM reportes AS r
INNER JOIN estados AS e ON e.id_estado = r.id_estado
WHERE (r.titulo LIKE N'%basura%' OR r.descripcion LIKE N'%basura%' OR r.ubicacion_direccion LIKE N'%basura%')
  AND e.nombre_estado = N'Pendiente'
ORDER BY r.id_reporte;

PRINT N'C9. Reportes con fotografías';
SELECT r.id_reporte, r.titulo, COUNT(ev.id_evidencia) AS fotos
FROM reportes AS r
LEFT JOIN evidencias AS ev ON ev.id_reporte = r.id_reporte
GROUP BY r.id_reporte, r.titulo
HAVING COUNT(ev.id_evidencia) > 0
ORDER BY fotos DESC;
GO

/* =====================================================================
   PARTE 3 · Pruebas de integridad
   Todas deben fallar. Cada una imprime el número y el mensaje de error
   de SQL Server; si alguna no falla, lo dice.
   ===================================================================== */

PRINT N'I1. Reporte con una categoría que no existe (id_categoria = 999)';
BEGIN TRY
    INSERT INTO reportes (titulo, descripcion, ubicacion_direccion, fecha_reporte, id_usuario, id_categoria, id_estado)
    VALUES (N'Prueba I1', N'Prueba', N'Prueba', SYSDATETIMEOFFSET(),
            (SELECT MIN(id_usuario) FROM usuarios), 999,
            (SELECT id_estado FROM estados WHERE nombre_estado = N'Pendiente'));
    PRINT N'   NO falló: revisar la clave foránea.';
END TRY
BEGIN CATCH
    PRINT CONCAT(N'   Rechazada · Error ', ERROR_NUMBER(), N': ', ERROR_MESSAGE());
END CATCH;

PRINT N'I2. Categoría repetida («Quema de basura»)';
BEGIN TRY
    INSERT INTO categorias (nombre_categoria, descripcion) VALUES (N'Quema de basura', N'Repetida');
    PRINT N'   NO falló: revisar la restricción UNIQUE.';
END TRY
BEGIN CATCH
    PRINT CONCAT(N'   Rechazada · Error ', ERROR_NUMBER(), N': ', ERROR_MESSAGE());
END CATCH;

PRINT N'I3. Usuario con un correo ya registrado';
BEGIN TRY
    INSERT INTO usuarios (nombre, apellido, correo, contrasena_hash, fecha_registro, id_rol)
    VALUES (N'Otra', N'Persona', N'vecina@ecoreporte.local', N'', SYSDATETIMEOFFSET(),
            (SELECT id_rol FROM roles WHERE nombre_rol = N'Ciudadano'));
    PRINT N'   NO falló: revisar la restricción UNIQUE.';
END TRY
BEGIN CATCH
    PRINT CONCAT(N'   Rechazada · Error ', ERROR_NUMBER(), N': ', ERROR_MESSAGE());
END CATCH;

PRINT N'I4. Eliminar el estado Pendiente, que usan varios reportes';
BEGIN TRY
    DELETE FROM estados WHERE nombre_estado = N'Pendiente';
    PRINT N'   NO falló: revisar la clave foránea.';
END TRY
BEGIN CATCH
    PRINT CONCAT(N'   Rechazada · Error ', ERROR_NUMBER(), N': ', ERROR_MESSAGE());
END CATCH;

PRINT N'I5. Reporte sin título (NULL)';
BEGIN TRY
    INSERT INTO reportes (titulo, descripcion, ubicacion_direccion, fecha_reporte, id_usuario, id_categoria, id_estado)
    VALUES (NULL, N'Prueba', N'Prueba', SYSDATETIMEOFFSET(),
            (SELECT MIN(id_usuario) FROM usuarios), (SELECT MIN(id_categoria) FROM categorias),
            (SELECT id_estado FROM estados WHERE nombre_estado = N'Pendiente'));
    PRINT N'   NO falló: revisar NOT NULL.';
END TRY
BEGIN CATCH
    PRINT CONCAT(N'   Rechazada · Error ', ERROR_NUMBER(), N': ', ERROR_MESSAGE());
END CATCH;

PRINT N'I6. Cambio de estado con un responsable que no existe, dentro de una transacción';
DECLARE @r2 int = (SELECT id_reporte FROM reportes WHERE titulo = N'Basura acumulada frente al Instituto');
BEGIN TRY
    BEGIN TRANSACTION;
        UPDATE reportes SET id_estado = (SELECT id_estado FROM estados WHERE nombre_estado = N'En proceso')
        WHERE id_reporte = @r2;
        INSERT INTO seguimiento_reporte (id_reporte, id_usuario_responsable, id_estado_anterior, id_estado_nuevo,
                                         comentario, fecha_cambio)
        VALUES (@r2, 999,
                (SELECT id_estado FROM estados WHERE nombre_estado = N'Pendiente'),
                (SELECT id_estado FROM estados WHERE nombre_estado = N'En proceso'),
                N'Prueba I6', SYSDATETIMEOFFSET());
    COMMIT;
    PRINT N'   NO falló: revisar la clave foránea.';
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK;
    PRINT CONCAT(N'   Rechazada · Error ', ERROR_NUMBER(), N': ', ERROR_MESSAGE());
END CATCH;
DECLARE @estado_final nvarchar(50) = (SELECT e.nombre_estado FROM reportes AS r
                                      JOIN estados AS e ON e.id_estado = r.id_estado WHERE r.id_reporte = @r2);
PRINT CONCAT(N'   Después del ROLLBACK, el reporte sigue en: ', @estado_final);
GO

PRINT N'Filas por tabla después de las pruebas (ninguna prueba dejó datos a medias)';
SELECT N'roles' AS tabla, COUNT(*) AS filas FROM roles
UNION ALL SELECT N'usuarios', COUNT(*) FROM usuarios
UNION ALL SELECT N'categorias', COUNT(*) FROM categorias
UNION ALL SELECT N'estados', COUNT(*) FROM estados
UNION ALL SELECT N'reportes', COUNT(*) FROM reportes
UNION ALL SELECT N'evidencias', COUNT(*) FROM evidencias
UNION ALL SELECT N'seguimiento_reporte', COUNT(*) FROM seguimiento_reporte;
GO

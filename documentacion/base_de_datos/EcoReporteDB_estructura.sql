/* =====================================================================
   EcoReporte Comunitario · EcoReporteDB · Estructura de la base de datos
   Equipo N.º 1 · Diseño de Base de Datos · Ciclo 02-2026

   Crea la base EcoReporteDB con 21 tablas (7 del proyecto y 14 de
   Django y allauth), 24 claves foráneas (10 entre las tablas del proyecto),
   sus restricciones UNIQUE, sus índices y los catálogos iniciales
   (2 roles, 4 estados y 6 categorías).

   Se generó leyendo el catálogo de una base EcoReporteDB creada con
   python manage.py migrate  en SQL Server 2022, así que describe
   exactamente la estructura que usa la aplicación. Falta solo la tabla
   django_migrations, que Django crea para anotar qué migraciones aplicó;
   con ella, una base hecha con migrate tiene 22 tablas.

   Uso: abrir en SQL Server Management Studio o Azure Data Studio y
   ejecutar, o desde la terminal:
       sqlcmd -S <servidor> -U <usuario> -C -f 65001 -i EcoReporteDB_estructura.sql
   Si después se quiere usar esta base con la aplicación, ejecutar una vez
       python manage.py migrate --fake
   para que Django la reconozca sin volver a crear las tablas.
   ===================================================================== */

IF DB_ID(N'EcoReporteDB') IS NULL
    CREATE DATABASE EcoReporteDB;
GO
USE EcoReporteDB;
GO
-- Los índices únicos filtrados (WHERE ... IS NOT NULL) necesitan estas opciones;
-- SSMS ya las trae encendidas, sqlcmd no.
SET QUOTED_IDENTIFIER ON;
SET ANSI_NULLS ON;
GO

-- ===================== Tablas del proyecto =====================
CREATE TABLE [roles] (
    [id_rol] int NOT NULL IDENTITY (1, 1),
    [nombre_rol] nvarchar(50) NOT NULL,
    [descripcion] nvarchar(255) NULL,
    CONSTRAINT [PK_roles] PRIMARY KEY ([id_rol])
);
ALTER TABLE [roles] ADD CONSTRAINT [UQ_roles_nombre_rol] UNIQUE ([nombre_rol]);

CREATE TABLE [usuarios] (
    [id_usuario] int NOT NULL IDENTITY (1, 1),
    [nombre] nvarchar(100) NOT NULL,
    [apellido] nvarchar(100) NOT NULL,
    [correo] nvarchar(150) NOT NULL,
    [contrasena_hash] nvarchar(256) NOT NULL,
    [telefono] nvarchar(15) NULL,
    [fecha_registro] datetimeoffset NOT NULL,
    [id_rol] int NOT NULL,
    [cuenta_id] int NULL,
    CONSTRAINT [PK_usuarios] PRIMARY KEY ([id_usuario])
);
ALTER TABLE [usuarios] ADD CONSTRAINT [UQ_usuarios_correo] UNIQUE ([correo]);
CREATE UNIQUE INDEX [usuarios_cuenta_id_0e26d031_uniq] ON [usuarios] ([cuenta_id]) WHERE ([cuenta_id] IS NOT NULL);
CREATE INDEX [usuarios_id_rol_af950121] ON [usuarios] ([id_rol]);

CREATE TABLE [categorias] (
    [id_categoria] int NOT NULL IDENTITY (1, 1),
    [nombre_categoria] nvarchar(100) NOT NULL,
    [descripcion] nvarchar(255) NULL,
    CONSTRAINT [PK_categorias] PRIMARY KEY ([id_categoria])
);
ALTER TABLE [categorias] ADD CONSTRAINT [UQ_categorias_nombre_categoria] UNIQUE ([nombre_categoria]);

CREATE TABLE [estados] (
    [id_estado] int NOT NULL IDENTITY (1, 1),
    [nombre_estado] nvarchar(50) NOT NULL,
    [descripcion] nvarchar(255) NULL,
    CONSTRAINT [PK_estados] PRIMARY KEY ([id_estado])
);
ALTER TABLE [estados] ADD CONSTRAINT [UQ_estados_nombre_estado] UNIQUE ([nombre_estado]);

CREATE TABLE [reportes] (
    [id_reporte] int NOT NULL IDENTITY (1, 1),
    [titulo] nvarchar(150) NOT NULL,
    [descripcion] nvarchar(max) NOT NULL,
    [ubicacion_direccion] nvarchar(255) NOT NULL,
    [latitud] numeric(9, 6) NULL,
    [longitud] numeric(9, 6) NULL,
    [fecha_reporte] datetimeoffset NOT NULL,
    [id_categoria] int NOT NULL,
    [id_estado] int NOT NULL,
    [id_usuario] int NOT NULL,
    CONSTRAINT [PK_reportes] PRIMARY KEY ([id_reporte])
);
CREATE INDEX [reportes_id_categoria_a85b0aaf] ON [reportes] ([id_categoria]);
CREATE INDEX [reportes_id_estado_76e51b58] ON [reportes] ([id_estado]);
CREATE INDEX [reportes_id_usuario_72e03538] ON [reportes] ([id_usuario]);

CREATE TABLE [evidencias] (
    [id_evidencia] int NOT NULL IDENTITY (1, 1),
    [url_imagen] nvarchar(500) NOT NULL,
    [fecha_subida] datetimeoffset NOT NULL,
    [id_reporte] int NOT NULL,
    CONSTRAINT [PK_evidencias] PRIMARY KEY ([id_evidencia])
);
CREATE INDEX [evidencias_id_reporte_7c91f3e4] ON [evidencias] ([id_reporte]);

CREATE TABLE [seguimiento_reporte] (
    [id_seguimiento] int NOT NULL IDENTITY (1, 1),
    [comentario] nvarchar(max) NULL,
    [fecha_cambio] datetimeoffset NOT NULL,
    [id_estado_anterior] int NOT NULL,
    [id_estado_nuevo] int NOT NULL,
    [id_reporte] int NOT NULL,
    [id_usuario_responsable] int NOT NULL,
    CONSTRAINT [PK_seguimiento_reporte] PRIMARY KEY ([id_seguimiento])
);
CREATE INDEX [seguimiento_reporte_id_estado_anterior_8e5a5e3c] ON [seguimiento_reporte] ([id_estado_anterior]);
CREATE INDEX [seguimiento_reporte_id_estado_nuevo_3f2478e1] ON [seguimiento_reporte] ([id_estado_nuevo]);
CREATE INDEX [seguimiento_reporte_id_reporte_b3a6c9a6] ON [seguimiento_reporte] ([id_reporte]);
CREATE INDEX [seguimiento_reporte_id_usuario_responsable_75ef8f66] ON [seguimiento_reporte] ([id_usuario_responsable]);

-- ============ Tablas de Django y de allauth (inicio de sesión) ============
CREATE TABLE [account_emailaddress] (
    [id] int NOT NULL IDENTITY (1, 1),
    [email] nvarchar(254) NOT NULL,
    [verified] bit NOT NULL,
    [primary] bit NOT NULL,
    [user_id] int NOT NULL,
    CONSTRAINT [PK_account_emailaddress] PRIMARY KEY ([id])
);
CREATE INDEX [account_emailaddress_email_03be32b2] ON [account_emailaddress] ([email]);
CREATE INDEX [account_emailaddress_user_id_2c513194] ON [account_emailaddress] ([user_id]);
CREATE UNIQUE INDEX [account_emailaddress_user_id_email_987c8728_uniq] ON [account_emailaddress] ([user_id], [email]) WHERE ([user_id] IS NOT NULL AND [email] IS NOT NULL);
CREATE UNIQUE INDEX [unique_primary_email] ON [account_emailaddress] ([user_id], [primary]) WHERE ([primary]=(1));

CREATE TABLE [account_emailconfirmation] (
    [id] int NOT NULL IDENTITY (1, 1),
    [created] datetimeoffset NOT NULL,
    [sent] datetimeoffset NULL,
    [key] nvarchar(64) NOT NULL,
    [email_address_id] int NOT NULL,
    CONSTRAINT [PK_account_emailconfirmation] PRIMARY KEY ([id])
);
CREATE INDEX [account_emailconfirmation_email_address_id_5b7f8c58] ON [account_emailconfirmation] ([email_address_id]);
ALTER TABLE [account_emailconfirmation] ADD CONSTRAINT [UQ_account_emailconfirmation_key] UNIQUE ([key]);

CREATE TABLE [auth_group] (
    [id] int NOT NULL IDENTITY (1, 1),
    [name] nvarchar(150) NOT NULL,
    CONSTRAINT [PK_auth_group] PRIMARY KEY ([id])
);
ALTER TABLE [auth_group] ADD CONSTRAINT [auth_group_name_a6ea08ec_uniq] UNIQUE ([name]);

CREATE TABLE [auth_group_permissions] (
    [id] bigint NOT NULL IDENTITY (1, 1),
    [group_id] int NOT NULL,
    [permission_id] int NOT NULL,
    CONSTRAINT [PK_auth_group_permissions] PRIMARY KEY ([id])
);
CREATE INDEX [auth_group_permissions_group_id_b120cbf9] ON [auth_group_permissions] ([group_id]);
CREATE UNIQUE INDEX [auth_group_permissions_group_id_permission_id_0cd325b0_uniq] ON [auth_group_permissions] ([group_id], [permission_id]) WHERE ([group_id] IS NOT NULL AND [permission_id] IS NOT NULL);
CREATE INDEX [auth_group_permissions_permission_id_84c5c92e] ON [auth_group_permissions] ([permission_id]);

CREATE TABLE [auth_permission] (
    [id] int NOT NULL IDENTITY (1, 1),
    [name] nvarchar(255) NOT NULL,
    [content_type_id] int NOT NULL,
    [codename] nvarchar(100) NOT NULL,
    CONSTRAINT [PK_auth_permission] PRIMARY KEY ([id])
);
CREATE INDEX [auth_permission_content_type_id_2f476e4b] ON [auth_permission] ([content_type_id]);
CREATE UNIQUE INDEX [auth_permission_content_type_id_codename_01ab375a_uniq] ON [auth_permission] ([content_type_id], [codename]) WHERE ([content_type_id] IS NOT NULL AND [codename] IS NOT NULL);

CREATE TABLE [auth_user] (
    [id] int NOT NULL IDENTITY (1, 1),
    [password] nvarchar(128) NOT NULL,
    [last_login] datetimeoffset NULL,
    [is_superuser] bit NOT NULL,
    [username] nvarchar(150) NOT NULL,
    [first_name] nvarchar(150) NOT NULL,
    [last_name] nvarchar(150) NOT NULL,
    [email] nvarchar(254) NOT NULL,
    [is_staff] bit NOT NULL,
    [is_active] bit NOT NULL,
    [date_joined] datetimeoffset NOT NULL,
    CONSTRAINT [PK_auth_user] PRIMARY KEY ([id])
);
ALTER TABLE [auth_user] ADD CONSTRAINT [auth_user_username_6821ab7c_uniq] UNIQUE ([username]);

CREATE TABLE [auth_user_groups] (
    [id] bigint NOT NULL IDENTITY (1, 1),
    [user_id] int NOT NULL,
    [group_id] int NOT NULL,
    CONSTRAINT [PK_auth_user_groups] PRIMARY KEY ([id])
);
CREATE INDEX [auth_user_groups_group_id_97559544] ON [auth_user_groups] ([group_id]);
CREATE INDEX [auth_user_groups_user_id_6a12ed8b] ON [auth_user_groups] ([user_id]);
CREATE UNIQUE INDEX [auth_user_groups_user_id_group_id_94350c0c_uniq] ON [auth_user_groups] ([user_id], [group_id]) WHERE ([user_id] IS NOT NULL AND [group_id] IS NOT NULL);

CREATE TABLE [auth_user_user_permissions] (
    [id] bigint NOT NULL IDENTITY (1, 1),
    [user_id] int NOT NULL,
    [permission_id] int NOT NULL,
    CONSTRAINT [PK_auth_user_user_permissions] PRIMARY KEY ([id])
);
CREATE INDEX [auth_user_user_permissions_permission_id_1fbb5f2c] ON [auth_user_user_permissions] ([permission_id]);
CREATE INDEX [auth_user_user_permissions_user_id_a95ead1b] ON [auth_user_user_permissions] ([user_id]);
CREATE UNIQUE INDEX [auth_user_user_permissions_user_id_permission_id_14a6b632_uniq] ON [auth_user_user_permissions] ([user_id], [permission_id]) WHERE ([user_id] IS NOT NULL AND [permission_id] IS NOT NULL);

CREATE TABLE [django_admin_log] (
    [id] int NOT NULL IDENTITY (1, 1),
    [action_time] datetimeoffset NOT NULL,
    [object_id] nvarchar(max) NULL,
    [object_repr] nvarchar(200) NOT NULL,
    [action_flag] smallint NOT NULL,
    [change_message] nvarchar(max) NOT NULL,
    [content_type_id] int NULL,
    [user_id] int NOT NULL,
    CONSTRAINT [PK_django_admin_log] PRIMARY KEY ([id])
);
CREATE INDEX [django_admin_log_content_type_id_c4bce8eb] ON [django_admin_log] ([content_type_id]);
CREATE INDEX [django_admin_log_user_id_c564eba6] ON [django_admin_log] ([user_id]);
ALTER TABLE [django_admin_log] ADD CONSTRAINT [django_admin_log_action_flag_a8637d59_check] CHECK ([action_flag]>=(0));

CREATE TABLE [django_content_type] (
    [id] int NOT NULL IDENTITY (1, 1),
    [app_label] nvarchar(100) NOT NULL,
    [model] nvarchar(100) NOT NULL,
    CONSTRAINT [PK_django_content_type] PRIMARY KEY ([id])
);
CREATE UNIQUE INDEX [django_content_type_app_label_model_76bd3d3b_uniq] ON [django_content_type] ([app_label], [model]) WHERE ([app_label] IS NOT NULL AND [model] IS NOT NULL);

CREATE TABLE [django_session] (
    [session_key] nvarchar(40) NOT NULL,
    [session_data] nvarchar(max) NOT NULL,
    [expire_date] datetimeoffset NOT NULL,
    CONSTRAINT [PK_django_session] PRIMARY KEY ([session_key])
);
CREATE INDEX [django_session_expire_date_a5c62663] ON [django_session] ([expire_date]);

CREATE TABLE [socialaccount_socialaccount] (
    [id] int NOT NULL IDENTITY (1, 1),
    [provider] nvarchar(200) NOT NULL,
    [uid] nvarchar(191) NOT NULL,
    [last_login] datetimeoffset NOT NULL,
    [date_joined] datetimeoffset NOT NULL,
    [extra_data] nvarchar(max) NOT NULL,
    [user_id] int NOT NULL,
    CONSTRAINT [PK_socialaccount_socialaccount] PRIMARY KEY ([id])
);
CREATE UNIQUE INDEX [socialaccount_socialaccount_provider_uid_fc810c6e_uniq] ON [socialaccount_socialaccount] ([provider], [uid]) WHERE ([provider] IS NOT NULL AND [uid] IS NOT NULL);
CREATE INDEX [socialaccount_socialaccount_user_id_8146e70c] ON [socialaccount_socialaccount] ([user_id]);
ALTER TABLE [socialaccount_socialaccount] ADD CONSTRAINT [socialaccount_socialaccount_extra_data_234cdc64_check] CHECK (isjson([extra_data])=(1));

CREATE TABLE [socialaccount_socialapp] (
    [id] int NOT NULL IDENTITY (1, 1),
    [provider] nvarchar(30) NOT NULL,
    [name] nvarchar(40) NOT NULL,
    [client_id] nvarchar(191) NOT NULL,
    [secret] nvarchar(191) NOT NULL,
    [key] nvarchar(191) NOT NULL,
    [provider_id] nvarchar(200) NOT NULL,
    [settings] nvarchar(max) NOT NULL,
    CONSTRAINT [PK_socialaccount_socialapp] PRIMARY KEY ([id])
);
ALTER TABLE [socialaccount_socialapp] ADD CONSTRAINT [CK__socialacc__setti__03F0984C] CHECK (isjson([settings])=(1));

CREATE TABLE [socialaccount_socialtoken] (
    [id] int NOT NULL IDENTITY (1, 1),
    [token] nvarchar(max) NOT NULL,
    [token_secret] nvarchar(max) NOT NULL,
    [expires_at] datetimeoffset NULL,
    [account_id] int NOT NULL,
    [app_id] int NULL,
    CONSTRAINT [PK_socialaccount_socialtoken] PRIMARY KEY ([id])
);
CREATE INDEX [socialaccount_socialtoken_account_id_951f210e] ON [socialaccount_socialtoken] ([account_id]);
CREATE INDEX [socialaccount_socialtoken_app_id_636a42d7] ON [socialaccount_socialtoken] ([app_id]);
CREATE UNIQUE INDEX [socialaccount_socialtoken_app_id_account_id_fca4e0ac_uniq] ON [socialaccount_socialtoken] ([app_id], [account_id]) WHERE ([app_id] IS NOT NULL AND [account_id] IS NOT NULL);

-- ===================== Claves foráneas =====================
-- Se crean sin acción en cascada (NO ACTION): PROTECT y CASCADE los aplica Django.
ALTER TABLE [usuarios] ADD CONSTRAINT [usuarios_cuenta_id_0e26d031_fk_auth_user_id]
    FOREIGN KEY ([cuenta_id]) REFERENCES [auth_user] ([id]);
ALTER TABLE [usuarios] ADD CONSTRAINT [usuarios_id_rol_af950121_fk_roles_id_rol]
    FOREIGN KEY ([id_rol]) REFERENCES [roles] ([id_rol]);
ALTER TABLE [reportes] ADD CONSTRAINT [reportes_id_categoria_a85b0aaf_fk_categorias_id_categoria]
    FOREIGN KEY ([id_categoria]) REFERENCES [categorias] ([id_categoria]);
ALTER TABLE [reportes] ADD CONSTRAINT [reportes_id_estado_76e51b58_fk_estados_id_estado]
    FOREIGN KEY ([id_estado]) REFERENCES [estados] ([id_estado]);
ALTER TABLE [reportes] ADD CONSTRAINT [reportes_id_usuario_72e03538_fk_usuarios_id_usuario]
    FOREIGN KEY ([id_usuario]) REFERENCES [usuarios] ([id_usuario]);
ALTER TABLE [evidencias] ADD CONSTRAINT [evidencias_id_reporte_7c91f3e4_fk_reportes_id_reporte]
    FOREIGN KEY ([id_reporte]) REFERENCES [reportes] ([id_reporte]);
ALTER TABLE [seguimiento_reporte] ADD CONSTRAINT [seguimiento_reporte_id_estado_anterior_8e5a5e3c_fk_estados_id_estado]
    FOREIGN KEY ([id_estado_anterior]) REFERENCES [estados] ([id_estado]);
ALTER TABLE [seguimiento_reporte] ADD CONSTRAINT [seguimiento_reporte_id_estado_nuevo_3f2478e1_fk_estados_id_estado]
    FOREIGN KEY ([id_estado_nuevo]) REFERENCES [estados] ([id_estado]);
ALTER TABLE [seguimiento_reporte] ADD CONSTRAINT [seguimiento_reporte_id_reporte_b3a6c9a6_fk_reportes_id_reporte]
    FOREIGN KEY ([id_reporte]) REFERENCES [reportes] ([id_reporte]);
ALTER TABLE [seguimiento_reporte] ADD CONSTRAINT [seguimiento_reporte_id_usuario_responsable_75ef8f66_fk_usuarios_id_usuario]
    FOREIGN KEY ([id_usuario_responsable]) REFERENCES [usuarios] ([id_usuario]);
ALTER TABLE [account_emailaddress] ADD CONSTRAINT [account_emailaddress_user_id_2c513194_fk_auth_user_id]
    FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
ALTER TABLE [account_emailconfirmation] ADD CONSTRAINT [account_emailconfirmation_email_address_id_5b7f8c58_fk_account_emailaddress_id]
    FOREIGN KEY ([email_address_id]) REFERENCES [account_emailaddress] ([id]);
ALTER TABLE [auth_group_permissions] ADD CONSTRAINT [auth_group_permissions_group_id_b120cbf9_fk_auth_group_id]
    FOREIGN KEY ([group_id]) REFERENCES [auth_group] ([id]);
ALTER TABLE [auth_group_permissions] ADD CONSTRAINT [auth_group_permissions_permission_id_84c5c92e_fk_auth_permission_id]
    FOREIGN KEY ([permission_id]) REFERENCES [auth_permission] ([id]);
ALTER TABLE [auth_permission] ADD CONSTRAINT [auth_permission_content_type_id_2f476e4b_fk_django_content_type_id]
    FOREIGN KEY ([content_type_id]) REFERENCES [django_content_type] ([id]);
ALTER TABLE [auth_user_groups] ADD CONSTRAINT [auth_user_groups_group_id_97559544_fk_auth_group_id]
    FOREIGN KEY ([group_id]) REFERENCES [auth_group] ([id]);
ALTER TABLE [auth_user_groups] ADD CONSTRAINT [auth_user_groups_user_id_6a12ed8b_fk_auth_user_id]
    FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
ALTER TABLE [auth_user_user_permissions] ADD CONSTRAINT [auth_user_user_permissions_permission_id_1fbb5f2c_fk_auth_permission_id]
    FOREIGN KEY ([permission_id]) REFERENCES [auth_permission] ([id]);
ALTER TABLE [auth_user_user_permissions] ADD CONSTRAINT [auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id]
    FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
ALTER TABLE [django_admin_log] ADD CONSTRAINT [django_admin_log_content_type_id_c4bce8eb_fk_django_content_type_id]
    FOREIGN KEY ([content_type_id]) REFERENCES [django_content_type] ([id]);
ALTER TABLE [django_admin_log] ADD CONSTRAINT [django_admin_log_user_id_c564eba6_fk_auth_user_id]
    FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
ALTER TABLE [socialaccount_socialaccount] ADD CONSTRAINT [socialaccount_socialaccount_user_id_8146e70c_fk_auth_user_id]
    FOREIGN KEY ([user_id]) REFERENCES [auth_user] ([id]);
ALTER TABLE [socialaccount_socialtoken] ADD CONSTRAINT [socialaccount_socialtoken_account_id_951f210e_fk_socialaccount_socialaccount_id]
    FOREIGN KEY ([account_id]) REFERENCES [socialaccount_socialaccount] ([id]);
ALTER TABLE [socialaccount_socialtoken] ADD CONSTRAINT [socialaccount_socialtoken_app_id_636a42d7_fk_socialaccount_socialapp_id]
    FOREIGN KEY ([app_id]) REFERENCES [socialaccount_socialapp] ([id]);
GO

-- ===================== Catálogos iniciales =====================
-- Equivalen a  python manage.py cargar_datos_iniciales
INSERT INTO [roles] ([nombre_rol], [descripcion]) VALUES (N'Ciudadano', N'Habitante que registra y consulta reportes.');
INSERT INTO [roles] ([nombre_rol], [descripcion]) VALUES (N'Administrador', N'Responsable comunitario que da seguimiento a los reportes.');

INSERT INTO [estados] ([nombre_estado], [descripcion]) VALUES (N'Pendiente', N'Reporte recibido, aún sin atender.');
INSERT INTO [estados] ([nombre_estado], [descripcion]) VALUES (N'En proceso', N'Se están realizando acciones para resolverlo.');
INSERT INTO [estados] ([nombre_estado], [descripcion]) VALUES (N'Resuelto', N'El problema fue solucionado.');
INSERT INTO [estados] ([nombre_estado], [descripcion]) VALUES (N'Rechazado', N'El reporte no procede o está duplicado.');

INSERT INTO [categorias] ([nombre_categoria], [descripcion]) VALUES (N'Botadero clandestino', N'Lugar no autorizado donde se tira basura.');
INSERT INTO [categorias] ([nombre_categoria], [descripcion]) VALUES (N'Acumulación de basura', N'Basura acumulada en calles, quebradas o espacios públicos.');
INSERT INTO [categorias] ([nombre_categoria], [descripcion]) VALUES (N'Recolección de residuos', N'Problemas con el tren de aseo o la recolección.');
INSERT INTO [categorias] ([nombre_categoria], [descripcion]) VALUES (N'Quema de basura', N'Quema de desechos que contamina el aire.');
INSERT INTO [categorias] ([nombre_categoria], [descripcion]) VALUES (N'Contaminación de agua', N'Ríos, quebradas o nacimientos contaminados.');
INSERT INTO [categorias] ([nombre_categoria], [descripcion]) VALUES (N'Otro', N'Otro problema ambiental de la comunidad.');
GO

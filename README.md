# 🍃 EcoReporte Comunitario

**Universidad Dr. Andrés Bello**  
**Carrera:** Ingeniería en Sistemas y Computación  
**Asignatura:** Programación Orientada a Objetos (POO)  
**Proyecto de Proyección Social** | Ciclo 02-2026  
**Ubicación:** Comunidad de San Rafael e Instituto Nacional de San Rafael, Distrito de San Rafael, Chalatenango  

---

## 📌 Descripción del Proyecto
EcoReporte Comunitario es una plataforma web desarrollada con **Django** y **SQL Server** para registrar, organizar y dar seguimiento en tiempo real a problemáticas ambientales (botaderos clandestinos, acumulación de basura y fallas en la recolección) en la Comunidad de San Rafael. Funciona como un canal digital centralizado entre los habitantes, instituciones educativas y las autoridades municipales o gestores comunitarios.

---

## 👥 Integrantes y Roles

| Nombre Completo | Carnet | Rol Principal | Responsabilidad / Enfoque |
| :--- | :---: | :--- | :--- |
| **Patrick Alejandro Alvarenga Cardoza** | ac0473032026 | Líder de Proyecto / Project Manager | Coordinación general, recolección de campo e instrumentos. |
| **Jefersson Javier Galdámez Mejía** | gm1366032026 | Analista de Requerimientos | Definición de usuarios, matriz de permisos y Requisitos Funcionales. |
| **Diego Fabricio Erazo Deras** | ed0921032026 | Líder Técnico / Administrador Git | Gestión del repositorio GitHub, tablero Kanban y arquitectura base. |
| **Victor Angel Rivas Torres** | rt0234032026 | Diseñador UX/UI y Frontend | Requisitos No Funcionales, diseño responsive y adaptabilidad. |
| **Geovany Enmanuel Alas Orellana** | ao0922032026 | Desarrollador Backend / QA | Redacción del diagnóstico, Fuentes Consultadas y maquetación de informes. |

---

## 👤 Tipos de Usuarios y Permisos

1. **Ciudadano / Reportante:**
   - **Función:** Reportar problemas ambientales de la comunidad y darles seguimiento.
   - **Permisos:** Registrarse, iniciar sesión, crear reportes con fotos, editar o eliminar reportes propios, consultar el catálogo público y filtrar casos.
2. **Personal Municipal / Gestor:**
   - **Función:** Atender reportes comunitarios y actualizar el avance de los casos.
   - **Permisos:** Ver todos los reportes, cambiar estados (*Pendiente*, *En proceso*, *Resuelto*), agregar comentarios de avance y filtrar por zonas o categorías.
3. **Administrador del Sistema:**
   - **Función:** Moderar la plataforma, gestionar usuarios y supervisar estadísticas.
   - **Permisos:** Control total del sistema, asignación de roles, moderación de contenidos y gestión de categorías.

---

## 📋 Requisitos Funcionales (RF)

| Código | Nombre | Descripción |
| :---: | :--- | :--- |
| **RF-01** | Registro de usuarios | Permite a los usuarios registrarse con nombre, correo electrónico y contraseña. |
| **RF-02** | Autenticación | Permite iniciar y cerrar sesión adaptando la interfaz según el rol del usuario. |
| **RF-03** | Registro de reportes | Permite crear reportes indicando título, descripción, categoría y ubicación del problema. |
| **RF-04** | Consulta de reportes | Muestra el catálogo de reportes y el detalle completo de cada caso. |
| **RF-05** | Modificación de reportes | Permite al autor editar sus reportes mientras no estén resueltos. |
| **RF-06** | Eliminación de reportes | Permite al autor o al administrador eliminar publicaciones. |
| **RF-07** | Evidencias fotográficas | Permite adjuntar imágenes (.jpg, .jpeg, .png) al reporte. |
| **RF-08** | Búsqueda y filtrado | Búsqueda por palabras clave y filtros por categoría, estado y fecha. |
| **RF-09** | Actualización de estado | Permite al personal municipal cambiar el estado del reporte (*Pendiente*, *En proceso*, *Resuelto*). |
| **RF-10** | Seguimiento de avances | Muestra el historial de cambios de estado y comentarios oficiales. |
| **RF-11** | Gestión de usuarios y roles | Permite al administrador gestionar cuentas y asignar permisos. |

---

## ⚙️ Requisitos No Funcionales (RNF)

| Código | Categoría | Descripción |
| :---: | :--- | :--- |
| **RNF-01** | Adaptabilidad y Usabilidad | Interfaz responsive adaptada a móviles, tabletas y computadoras con Bootstrap. |
| **RNF-02** | Arquitectura Tecnológica | Backend en Django (MVT) con base de datos relacional SQL Server. |
| **RNF-03** | Integridad de Datos | Validación de formularios en cliente y servidor junto a restricciones de archivos. |
| **RNF-04** | Seguridad y Privacidad | Cifrado de contraseñas (PBKDF2), protección CSRF y control de acceso basado en roles (RBAC). |
| **RNF-05** | Rendimiento | Carga de vistas principales en un tiempo medio no mayor a 3 segundos. |

---

## 🛠️ Especificaciones Técnicas y Arquitectura
* **Backend Framework:** Python / Django (Patrón MVT).
* **Base de Datos:** SQL Server (Conexión mediante `mssql-django` / ODBC).
* **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5.
* **Control de Versiones & Gestión:** Git, GitHub, Tablero Kanban.
* **Seguridad:** Tokens CSRF, Hashing PBKDF2 / SHA256 y anonimización opcional de datos de contacto.

---

## 📚 Fuentes Confiables Consultadas

1. **Ministerio de Medio Ambiente y Recursos Naturales (MARN) - El Salvador (2022):** *Diagnóstico Nacional de Residuos*. Sustenta la urgencia de erradicar botaderos clandestinos y mejorar el control local.
2. **Fundación Empresarial para la Acción Social (FUNDEMAS) (2024/2025):** *Guía para alcaldías sobre la gestión integral de residuos con énfasis en reciclaje*. Confirma que los canales digitales de reporte ciudadano disminuyen riesgos sanitarios.

---
---

## 📂 Estado del Proyecto
* **Semana 1:** [✓] Organización del equipo y selección de la problemática ambiental.
* **Semana 2:** [✓] Diagnóstico de campo en San Rafael, levantamiento de encuestas y registros fotográficos[cite: 11].
* **Semana 3:** [✓] Documentación del README.md en GitHub, matriz de perfiles de usuario, 11 Requisitos Funcionales, 5 No Funcionales y fuentes oficiales.
* **Semana 4 (Próxima):** [ ] Configuración del entorno Django, conexión con SQL Server y creación de los modelos en `models.py`.

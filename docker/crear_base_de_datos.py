"""Espera a que SQL Server esté listo y crea la base de datos si no existe."""

import os
import sys
import time

import mssql_python

nombre = os.environ.get("DB_NAME", "EcoReporteDB")
cadena = (
    f"Server={os.environ.get('DB_HOST', 'localhost')},{os.environ.get('DB_PORT') or 1433};"
    f"UID={os.environ['DB_USER']};PWD={os.environ['DB_PASSWORD']};"
    "Database=master;Encrypt=yes;TrustServerCertificate=yes;"
)

for intento in range(1, 61):
    try:
        conexion = mssql_python.connect(cadena, autocommit=True)
        break
    except mssql_python.Error as error:
        print(f"Esperando a SQL Server ({intento}/60): {str(error)[:100]}")
        time.sleep(2)
else:
    sys.exit("No fue posible conectarse a SQL Server.")

cursor = conexion.cursor()
cursor.execute(f"IF DB_ID(N'{nombre}') IS NULL CREATE DATABASE [{nombre}]")
conexion.close()
print(f"Base de datos {nombre} lista.")

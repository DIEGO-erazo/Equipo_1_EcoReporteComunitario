FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# libodbc2 lo necesita pyodbc al importarse y libgssapi-krb5-2 el driver de SQL Server.
# La conexión usa mssql-python, que ya incluye el ODBC Driver 18 de Microsoft.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libodbc2 libltdl7 libgssapi-krb5-2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn==23.0.0

COPY . .
RUN chmod +x docker/entrypoint.sh && python manage.py collectstatic --noinput

EXPOSE 8000
ENTRYPOINT ["docker/entrypoint.sh"]
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]

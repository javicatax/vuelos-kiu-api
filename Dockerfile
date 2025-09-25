# Usa una imagen base de Python. Puedes especificar una versión si es necesario.
FROM python:3.12

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de requerimientos primero para aprovechar el caché de Docker
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación al directorio de trabajo
COPY . .

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Define el comando para ejecutar la aplicación
# Usa gunicorn para un despliegue en producción
# Instala gunicorn en tu requirements.txt para que funcione
CMD ["gunicorn", "flight_search_project.wsgi:application", "--bind", "0.0.0.0:8000"]
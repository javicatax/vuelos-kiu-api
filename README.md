# Proyecto vuelos

Una API REST construida con Django REST Framework para gestionar viajes.

## Características

- API REST completa
- Panel de administración Django
- Documentación automática
- Base de datos PostgreSQL


Persistencia de Datos: Utiliza PostgreSQL para almacenar los eventos de vuelo.

Dockerización: El proyecto está configurado para ejecutarse fácilmente en un entorno Docker, facilitando el desarrollo y el despliegue.

Tests Automatizados: Incluye pruebas unitarias y de integración para garantizar la fiabilidad del servicio y su lógica de negocio.

Tecnologías Utilizadas
Backend: Django, Django REST Framework

Base de Datos: PostgreSQL

Contenedores: Docker, Docker Compose

Pruebas: unittest, Coverage.py

Requisitos
Docker y Docker Compose instalados.

## Guía de Uso
1. Clonar el Repositorio

```bash
git clone clone https://github.com/javicatax/vuelos-kiu-api.git
cd vuelos_kiu_api
```

2. Configurar Variables de Entorno
Crea un archivo .env en la raíz del proyecto, con la siguiente estructura:
```bash
# Variables de la base de datos
POSTGRES_DB=flight_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Variables de Django
SECRET_KEY=your_incredibly_long_and_secure_key
DEBUG=True

# Variables de la base de datos
POSTGRES_DB=flight_db
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# Variables de Django
SECRET_KEY=your_incredibly_long_and_secure_key
DEBUG=True
```

3. Ejecutar el Proyecto con Docker Compose
Levanta los contenedores de la aplicación y la base de datos. La opción --build asegura que las imágenes se construyan con los últimos cambios.

```bash
docker-compose up --build
```
4. Realizar Migraciones de la Base de Datos
Una vez que los contenedores estén en funcionamiento, aplica las migraciones de Django:

```bash
docker-compose exec web python manage.py migrate
```

5. Consumir y Cargar Eventos de Vuelo
Para poblar la base de datos con los eventos de vuelo, puedes usar el comando de gestión personalizado:

Este comando consume el mock de la API externa y guarda los datos en la base de datos local.
```bash
docker-compose exec web python manage.py fetch_flight_events
```

6. Usar la API
El endpoint de búsqueda de vuelos está disponible en http://localhost:8000/journeys/search/. Puedes realizar una petición GET con los siguientes parámetros de consulta:

Parámetro	Ejemplo	Descripción
date	2024-09-12	Fecha de salida del primer vuelo (formato YYYY-MM-DD).
from	BUE	Código de ciudad de origen (tres letras).
to	PMO	Código de ciudad de destino (tres letras).

Exportar a Hojas de cálculo
Ejemplo de Petición:

http://localhost:8000/journeys/search/?date=2021-12-31&from=MAD&to=BUE

Ejecución de Tests y Cobertura
Para ejecutar las pruebas y generar un reporte de cobertura, usa el siguiente comando dentro de tu contenedor web:


```bash
docker-compose exec web coverage run --source='.' manage.py test
docker-compose exec web coverage html
```

El reporte HTML estará disponible en la carpeta htmlcov/ de tu proyecto.

Autor:
Javier Castillo

Email: javicatax@hotmail.com

¡La API estará disponible en `http://localhost:8000`!
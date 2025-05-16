# VitalPaw - Backend (Django)
Proyecto backend del sistema VitalPaw, una aplicación enfocada en el monitoreo de salud de mascotas mediante dispositivos IoT.

# Descripción
Este es el inicio del desarrollo del backend para la aplicación VitalPaw, hecho en Django. Con el objetivo de cumplir con el primer sprint. Al momento solo se agregó:
Registro de usuarios
Registro de mascotas
Cálculo automático de edad a partir de fecha de nacimiento
Subida y redimensionamiento automático de la foto de la mascota a 1X1

# Librerías utilizadas
Python 3.13.2
Django 5.2.1
Django REST Framework
Pillow

# Estructura del proyecto
backend/
├── manage.py
├── vitalpawdj/              # Configuración general del proyecto
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── usuarios/                # App para gestión de usuarios
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── mascotas/                # App para gestión de mascotas
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
└── db.sqlite3               # Base de datos SQLite por defecto

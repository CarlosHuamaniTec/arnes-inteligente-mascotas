# Arnés Inteligente para Mascotas - Backend

## Información del Proyecto

Backend desarrollado en Django + Django REST Framework (DRF) para el proyecto académico "Arnés Inteligente para Mascotas".

Este backend ofrece funcionalidades de registro, inicio de sesión y confirmación de correo electrónico con generación de token, preparado para escalar a notificaciones push y alertas médicas.

---

## Historias de Usuario Implementadas

HU01 - Registro de usuario con email único
HU02 - Inicio de sesión con email y contraseña
HU10 - Confirmación de correo tras registro
HU11 - Recuperación de contraseña (en desarrollo)

---

## Tecnologías Utilizadas

- Python 3.13.0
- Django 5.2.1
- Django REST Framework
- Token Authentication
- SMTP con Gmail
- SQLite (en desarrollo)
- decouple – Para variables de entorno
- unittest.mock – Pruebas unitarias de caja blanca

---

## Funcionalidades Actuales

### 1. Registro de Usuarios

Permite crear usuarios con:
- email (único)
- first_name (obligatorio)
- password
- Campos opcionales: last_name, phone, city

El usuario se crea con is_active=False hasta que confirme su correo.

Ejemplo de solicitud:

{
  "email": "juan@api.com",
  "first_name": "Juan",
  "password": "mipassword123"
}

Respuesta exitosa:

{
  "message": "Usuario creado exitosamente"
}

---

### 2. Inicio de Sesión

Autentica al usuario y devuelve un token para llamadas posteriores.

Ejemplo de solicitud:

{
  "email": "juan@api.com",
  "password": "mipassword123"
}

Respuesta exitosa:

{
  "message": "Inicio de sesión exitoso",
  "token": "9876543210abcdef1234567890abcdef12345678",
  "user_email": "juan@api.com",
  "user_id": 1
}

---

### 3. Confirmación de Correo Electrónico (HU10)

Al registrar un usuario:
- Se genera un token único.
- Se envía un correo de verificación.
- El usuario debe usar el token para activar su cuenta.

Correo contiene mensaje con token para validación.

---

### 4. Recuperación de Contraseña (HU11)

En desarrollo. Ya está la estructura preparada para enviar correos con tokens temporales.

---

## Pruebas Unitarias y de Integración

Se han aplicado pruebas unitarias de tipo caja blanca basadas en CFG (Control Flow Graph) para cubrir todas las rutas lógicas posibles.

### Cobertura actual:

- Modelo CustomUser
- Serializadores RegisterSerializer y LoginSerializer
- Funciones de envío de correo
- Vistas API

### Tipos de cobertura aplicados:

- Cobertura de nodos – Cada línea ejecutada al menos una vez
- Cobertura de condiciones – Todos los if/else probados
- Cobertura de rutas – Ruta principal y alternativas

---

## Arquitectura Modular

Estructura pensada para ser escalable y mantener buenas prácticas:

- Uso de carpeta utils para funciones reutilizables
- Separación clara de responsabilidades: modelos, serializadores, vistas, pruebas
- Listo para integrar Celery (tareas asíncronas)
- Soporte modular para múltiples proveedores SMTP (Gmail, Mailtrap, etc.)

---

## Requisitos Técnicos

Asegúrate de tener instalado:

pip install -r requirements.txt

Variables de Entorno (.env):

EMAIL_HOST_USER=vitalpaw.devtester007@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_aqui
DJANGO_DEBUG=True

Migraciones:

python manage.py migrate

Ejecutar servidor local:

python manage.py runserver

---

## Estructura del Proyecto (actual)

users/
├── models.py          # Definición del modelo CustomUser
├── serializers.py     # RegisterSerializer, LoginSerializer
├── views.py           # Vistas API
├── urls.py            # Rutas de autenticación
└── utils/
    └── email.py      # Funciones reutilizables de envío de correo

tests_users/
└── unitarias/
    ├── test_users.py         # Pruebas del modelo de usuario
    ├── test_serializers.py  # Validación de campos y errores
    └── test_email_cfg.py   # Pruebas de flujo de control para correo

---

## Flujo de Control Probado (CFG)

Pruebas unitarias de tipo caja blanca aplicadas para validar flujos completos.

### Ejemplo: LoginSerializer.validate()

Rutas probadas:
- Usuario existe → Contraseña correcta → Usuario activo → Devuelve token
- Usuario no existe → Levanta error
- Contraseña incorrecta → Levanta error
- Usuario inactivo → Levanta error

Todas estas rutas fueron probadas con unittest.mock y assertRaises.

---

## Estilo de Documentación

Todo el código incluye docstrings entre triple comilla siguiendo estilo Google/Sphinx.

Ejemplo:

def validate(self, data):
    """
    Valida que el usuario exista y la contraseña sea correcta.

    Args:
        data (dict): Datos de entrada (correo y contraseña).

    Raises:
        ValidationError: Si credenciales son inválidas.

    Returns:
        dict: Datos validados si todo es correcto.
    """

---

## Configuración de Correo (SMTP)

Actualmente se usa Gmail SMTP con App Passwords.

### settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)

---

## Próximos Pasos Planificados

- Crear endpoint /verify-email/
- Agregar campo verification_token al modelo CustomUser
- Integrar Celery para envío de correo en background
- Empezar desarrollo de app mascotas (Pet, SensorData, Alert)
- Preparar estructura para notificaciones push futuras

---

## Contacto

Carlos Huamani  
Correo institucional: carlos.huamani@unmsm.edu.pe  
Universidad Nacional Mayor de San Marcos  
Ingeniería de Software - Proyecto Académico
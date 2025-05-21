# VitalPaw - Backend (Arnés Inteligente para Mascotas)

## Introducción

VitalPaw es una aplicación empresarial diseñada para dueños de mascotas que desean monitorear la salud y el bienestar de sus animales a través de un arnés inteligente. Este repositorio contiene el **backend** de la plataforma, implementado con Django y Django REST Framework. El backend soporta autenticación de usuarios, registro de mascotas, monitoreo en tiempo real de datos biométricos (pulso cardíaco, temperatura, movimiento), y notificaciones push para alertas de salud. Los datos biométricos son recibidos desde un ESP32 vía MQTT, procesados en tiempo real, y enviados a una API Gateway para la aplicación móvil, sin almacenamiento en base de datos.

El proyecto está en desarrollo como parte del **Sprint 1**, cubriendo las siguientes historias de usuario:
- **HU01**: Registro de usuarios con email, nombre, contraseña, y username opcional.
- **HU02**: Login con email y contraseña, devolviendo un token.
- **HU10**: Verificación de email mediante enlace.
- **HU11**: Recuperación de contraseña vía email.
- **HU12**: Registro de nuevas mascotas.
- **HU03, HU04**: Monitoreo en tiempo real de pulso cardíaco y temperatura.
- **HU05-HU09**: Notificaciones push para fiebre, hipotermia, taquicardia, bradicardia, caída, y letargo.

## Tecnologías

- **Backend**: Django 4.x, Django REST Framework, Python 3.10+
- **Autenticación**: Django Token Authentication (`rest_framework.authtoken`)
- **Procesamiento en tiempo real**: MQTT (Mosquitto), Celery, Redis
- **Notificaciones**: Firebase Cloud Messaging (FCM)
- **Base de datos**: SQLite (desarrollo), preparado para PostgreSQL (producción)
- **Infraestructura**: VM local con FRP, API Gateway en AWS EC2

## Estructura del Proyecto

```
backend/
├── arnes_api/          # Configuración principal de Django
├── users/              # App para gestión de usuarios
│   ├── models.py       # CustomUser
│   ├── serializers.py  # RegisterSerializer, LoginSerializer, PasswordResetRequestSerializer
│   ├── views.py        # Vistas para autenticación y verificación
│   ├── urls.py         # Rutas de la app users
│   └── utils/email.py  # Utilidades para envío de correos
├── pets/               # App para gestión de mascotas y datos biométricos
│   ├── models.py       # Pet, BreedThresholds
│   ├── serializers.py  # PetSerializer, BiometricDataSerializer
│   ├── views.py        # Vistas para mascotas y datos biométricos
│   ├── urls.py         # Rutas de la app pets
│   ├── tasks.py        # Tareas Celery para procesar datos biométricos
│   └── mqtt_client.py  # Cliente MQTT para recibir datos del ESP32
├── .env                # Variables de entorno (no versionado)
├── requirements.txt    # Dependencias del proyecto
└── firebase-adminsdk.json  # Credenciales de Firebase (no versionado)
```

## Prerrequisitos

- Python 3.10+
- Redis (`redis-server`)
- Mosquitto MQTT Broker
- Cuenta en Firebase para notificaciones push
- (Opcional) FRP y AWS EC2 para API Gateway

## Instalación

1. **Clona el repositorio**:
   ```bash
   git clone https://github.com/CarlosHuamaniTec/arnes-inteligente-mascotas.git
   cd arnes-inteligente-mascotas/backend
   ```

2. **Crea un entorno virtual e instala dependencias**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configura las variables de entorno**:
   - Crea un archivo `.env` en `backend/` con el siguiente contenido:
     ```
     EMAIL_HOST_USER=
     EMAIL_HOST_PASSWORD=
     DEFAULT_FROM_EMAIL=
     SECRET_KEY=
     DEBUG=True
     ALLOWED_HOSTS=
     USE_POSTGRES=
     REDIS_URL=
     FRONTEND_VERIFY_URL=
     ```
   - Asegúrate de que `EMAIL_HOST_PASSWORD` sea una contraseña de aplicación de Gmail.

4. **Configura Firebase**:
   - Crea un proyecto en [Firebase Console](https://console.firebase.google.com/) con el nombre `VitalPaw-ArnesInteligente`.
   - Descarga `firebase-adminsdk.json` desde **Configuración del proyecto > Cuentas de servicio > Generar nueva clave privada**.
   - Coloca `firebase-adminsdk.json` en `backend/`.
   - Instala el SDK de Firebase:
     ```bash
     pip install firebase-admin
     ```

5. **Aplica migraciones**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Crea un superusuario** (opcional):
   ```bash
   python manage.py createsuperuser
   ```

## Ejecución

1. **Inicia Redis y Mosquitto**:
   ```bash
   redis-server
   mosquitto
   ```

2. **Inicia el worker de Celery**:
   ```bash
   celery -A arnes_api worker --loglevel=info
   ```

3. **Inicia el cliente MQTT**:
   ```bash
   python pets/mqtt_client.py
   ```

4. **Inicia el servidor Django**:
   ```bash
   python manage.py runserver
   ```

5. **Configura FRP** (si usas API Gateway en AWS EC2):
   - En la VM de AWS, configura `frps.ini`:
     ```ini
     [common]
     bind_port = 7000
     ```
     Inicia:
     ```bash
     ./frps -c frps.ini
     ```
   - En la VM local, configura `frpc.ini`:
     ```ini
     [common]
     server_addr = <IP_EC2>
     server_port = 7000

     [django_api]
     type = tcp
     local_ip = 127.0.0.1
     local_port = 8000
     remote_port = 8000
     ```
     Inicia:
     ```bash
     ./frpc -c frpc.ini
     ```

## Endpoints Principales

- **Autenticación**:
  - `POST /api/users/register/`: Registra un nuevo usuario.
  - `POST /api/users/login/`: Autentica y devuelve un token.
  - `GET /api/users/verify-email/?token=<token>`: Verifica el correo.
  - `POST /api/users/password/reset/`: Solicita restablecimiento de contraseña.
  - `POST /api/users/device-token/`: Actualiza el token de dispositivo para notificaciones.

- **Mascotas**:
  - `POST /api/pets/create/`: Registra una nueva mascota (requiere autenticación).
  - `GET /api/pets/<pet_id>/biometrics/`: Obtiene datos biométricos en tiempo real (requiere autenticación).

## Procesamiento de Datos Biométricos

- **Recepción**: Los datos del ESP32 (pulso, temperatura, movimiento en ejes X, Y, Z) llegan vía MQTT al tema `pet/biometric/<pet_id>`.
- **Procesamiento**: Celery evalúa los datos contra umbrales por raza (`BreedThresholds`) para detectar fiebre, hipotermia, taquicardia, bradicardia, caída, o letargo.
- **Almacenamiento temporal**: Los datos se guardan en Redis por 60 segundos.
- **Envío**: Los datos procesados se envían a la API Gateway para la app móvil.
- **Notificaciones**: Alertas se envían vía Firebase Cloud Messaging (FCM) si se detectan condiciones críticas.

## Configuración de Firebase

1. Crea un proyecto en [Firebase Console](https://console.firebase.google.com/) con el nombre `VitalPaw-ArnesInteligente`.
2. Registra tu app Android con el ID de paquete (e.g., `com.carlosHuamani.vitalpaw`).
3. Descarga `google-services.json` para la app móvil y colócalo en `android/app/`.
4. Descarga `firebase-adminsdk.json` y colócalo en `backend/`.
5. Asegúrate de que el modelo `CustomUser` tenga un campo `device_token` para almacenar tokens de dispositivos.

## Pruebas

Ejecuta las pruebas unitarias para validar la funcionalidad:
```bash
python manage.py test
```

Los tests cubren:
- Registro con correos duplicados (`test_registro_correo_repetido_lanza_error`).
- Normalización de emails en login (`test_login_email_normalizado`).
- Presencia del campo `username` (`test_username_field_present`).
- Verificación de email (`VerifyEmailViewCFGTest`).
- Creación de superusuarios (`test_create_superuser_error_is_superuser_false`).

## Notas para Producción

- Cambia `USE_POSTGRES=True` en `.env` y configura las variables de PostgreSQL (`DB_NAME`, `DB_USER`, etc.).
- Asegúrate de que `DEBUG=False` y actualiza `ALLOWED_HOSTS`.
- Configura la API Gateway en AWS EC2 para reenviar tráfico a los endpoints de Django.
- Usa una contraseña de aplicación de Gmail para `EMAIL_HOST_PASSWORD` si encuentras problemas con el envío de correos.

## Contribuciones

Este proyecto está en desarrollo activo. Para contribuir:
1. Crea un fork del repositorio.
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m "Añade nueva funcionalidad"`).
4. Envía un pull request a la rama `sprint-1`.

## Contacto

Para dudas o reportes de errores, contacta a [Carlos Huamani](mailto:carlos.huamani@example.com).

---

© 2025 VitalPaw Team

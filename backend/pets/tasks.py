import firebase_admin
import os
import json
from celery import shared_task
from pets.models import Pet, BreedThresholds
from django_redis import get_redis_connection
from .models import CustomUser
from firebase_admin import messaging, credentials
from django.conf import settings



# Inicializar Firebase
cred = credentials.Certificate(os.path.join(settings.BASE_DIR, 'firebase-adminsdk.json'))
firebase_admin.initialize_app(cred)

@shared_task
def process_biometric_data(pet_id, data):
    try:
        pet = Pet.objects.get(id=pet_id)
        heart_rate = data.get('heart_rate')
        temperature = data.get('temperature')
        movement_x = data.get('movement_x', 0.0)
        movement_y = data.get('movement_y', 0.0)
        movement_z = data.get('movement_z', 0.0)

        # Obtener umbrales por raza
        thresholds = BreedThresholds.objects.filter(breed=pet.breed).first()
        if not thresholds:
            # Umbrales por defecto si no hay específicos
            thresholds = type('Thresholds', (), {
                'min_heart_rate': 60,
                'max_heart_rate': 120,
                'min_temperature': 37.0,
                'max_temperature': 39.0
            })()

        # Evaluar alertas
        alerts = []
        if temperature > thresholds.max_temperature:
            alerts.append("Fiebre detectada")
        if temperature < thresholds.min_temperature:
            alerts.append("Hipotermia detectada")
        if heart_rate > thresholds.max_heart_rate:
            alerts.append("Taquicardia detectada")
        if heart_rate < thresholds.min_heart_rate:
            alerts.append("Bradicardia detectada")

        # Detectar caída (variación grande en Y)
        redis_conn = get_redis_connection("default")
        prev_y = redis_conn.get(f"movement_y:{pet_id}")
        if prev_y:
            prev_y = float(prev_y)
            if abs(movement_y - prev_y) > 10.0:  # Umbral de caída (ajustar)
                alerts.append("Caída detectada")

        # Detectar letargo (movimiento bajo en todos los ejes)
        total_movement = abs(movement_x) + abs(movement_y) + abs(movement_z)
        if total_movement < 0.1:  # Umbral de letargo (ajustar)
            # Verificar duración para evitar falsos positivos (e.g., durmiendo)
            count = redis_conn.incr(f"low_movement_count:{pet_id}")
            if count >= 30:  # 3 segundos a 0.1s por mensaje
                alerts.append("Letargo detectado")
                redis_conn.delete(f"low_movement_count:{pet_id}")
        else:
            redis_conn.delete(f"low_movement_count:{pet_id}")

        # Guardar datos en Redis para consulta
        biometric_data = {
            'pet_id': pet_id,
            'heart_rate': heart_rate,
            'temperature': temperature,
            'movement_x': movement_x,
            'movement_y': movement_y,
            'movement_z': movement_z,
            'alerts': alerts
        }
        redis_conn.set(f"biometric:{pet_id}", json.dumps(biometric_data), ex=60)  # Expira en 60s
        redis_conn.set(f"movement_y:{pet_id}", movement_y, ex=60)

        # Enviar notificaciones push si hay alertas
        if alerts:
            send_push_notification.delay(pet.owner.id, alerts)

        # Enviar datos a la API Gateway (placeholder)
        # Aquí iría una llamada HTTP a la API Gateway en AWS EC2
        print(f"Enviando datos a API Gateway: {biometric_data}")

        return {"status": "success", "pet_id": pet_id}
    except Pet.DoesNotExist:
        return {"status": "error", "message": "Mascota no encontrada"}

@shared_task
def send_push_notification(user_id, alerts):
    try:
        user = CustomUser.objects.get(id=user_id)
        # Asumimos que el usuario tiene un device_token (añadir al modelo si necesario)
        message = messaging.Message(
            notification=messaging.Notification(
                title="Alerta de salud",
                body=", ".join(alerts)
            ),
            token=user.device_token  # Placeholder
        )
        messaging.send(message)
    except Exception as e:
        print(f"Error enviando notificación: {e}")
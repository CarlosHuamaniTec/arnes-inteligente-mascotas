# users/utils/email.py
from django.core.mail import send_mail
from django.conf import settings

def enviar_correo_confirmacion(email, token):
    verification_url = f"{settings.FRONTEND_VERIFY_URL}?token={token}"
    send_mail(
        subject="Verifica tu correo electrónico",
        message=f"Por favor, haz clic en el enlace para verificar tu correo: {verification_url}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )
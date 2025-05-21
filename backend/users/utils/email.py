"""
Módulo de utilidades para envío de correos electrónicos.

Este módulo contiene funciones reutilizables para enviar correos desde el sistema,
como confirmación de correo electrónico, recuperación de contraseña, etc.
"""

from django.core.mail import send_mail
from django.conf import settings


def enviar_correo_confirmacion(destinatario, token):
    """
    Envía un correo de confirmación al usuario recién registrado.

    Args:
        destinatario (str): Dirección de correo del destinatario.
        token (str): Token único para verificar el correo.

    Returns:
        None
    """
    asunto = "Confirma tu correo electrónico"
    mensaje = f"""
    Gracias por registrarte. Usa el siguiente token para confirmar tu correo:

    {token}

    Atentamente,
    Equipo de Vital Paw
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    send_mail(
        subject=asunto,
        message=mensaje,
        from_email=from_email,
        recipient_list=[destinatario],
        fail_silently=False
    )
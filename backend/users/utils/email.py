"""
Módulo de utilidades para envío de correos electrónicos.

Este módulo contiene funciones reutilizables para enviar correos desde el sistema,
como confirmación de correo electrónico, recuperación de contraseña, etc.
"""
# users/utils/email.py

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def enviar_correo_confirmacion(destinatario, token):
    """
    Envía un correo de confirmación al usuario recién registrado.

    Args:
        destinatario (str): Dirección de correo del destinatario.
        token (str): Token único para verificar el correo.

    Returns:
        None

    Raises:
        Exception: Si falla el envío del correo.
    """
    subject = "Confirma tu correo electrónico"
    from_email = settings.DEFAULT_FROM_EMAIL

    # Cargar plantilla HTML
    context = {"token": token}
    html_message = render_to_string("emails/confirm_email.html", context)
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[destinatario],
            html_message=html_message,
            fail_silently=False
        )
    except Exception as e:
        raise Exception(f"Error al enviar correo: {e}")
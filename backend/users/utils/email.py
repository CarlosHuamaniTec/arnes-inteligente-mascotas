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
    """

    subject = "Confirma tu correo electrónico"
    from_email = settings.DEFAULT_FROM_EMAIL

    # Contexto dinámico sin FRONTEND_VERIFY_URL
    context = {
        "token": token,
        "confirmation_link": f"https://tuapp.com/verify-email/?token= {token}",  # URL provisional
    }

    html_message = render_to_string("emails/confirm_email.html", context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=from_email,
        recipient_list=[destinatario],
        html_message=html_message,
        fail_silently=False
    )
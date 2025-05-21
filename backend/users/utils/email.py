# backend/users/utils/email.py

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def enviar_correo_confirmacion(destinatario, token):
    subject = "Confirma tu correo electrónico"
    from_email = settings.DEFAULT_FROM_EMAIL

    confirmation_link = f"{settings.FRONTEND_VERIFY_URL}?token={token}"

    context = {
        "token": token,
        "confirmation_link": confirmation_link,
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

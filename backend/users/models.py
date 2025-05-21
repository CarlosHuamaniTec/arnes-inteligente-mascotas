from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import secrets
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, password=None, username=None, **extra_fields):
        if not email:
            raise ValueError("Debe ingresar el correo")
        if not first_name:
            raise ValueError("Debe ingresar el nombre")

        email = self.normalize_email(email)
        # Generar username si no se proporciona (basado en email o aleatorio)
        if not username:
            username = email.split('@')[0][:30]  # Primeros 30 caracteres del email antes de @
            # Asegurar unicidad
            base_username = username
            counter = 1
            while CustomUser.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

        user = self.model(email=email, first_name=first_name, username=username, **extra_fields)
        user.verification_token = secrets.token_urlsafe(40)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password=None, username=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields['is_staff'] or not extra_fields['is_superuser']:
            raise ValueError('Superuser debe tener is_staff=True y is_superuser=True')

        return self.create_user(email, first_name, password, username, **extra_fields)

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    first_name = models.CharField("Nombre", max_length=150)
    last_name = models.CharField("Apellido", max_length=150, blank=True, null=True)
    phone = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True)
    verification_token = models.CharField(
        "Token de verificación",
        max_length=100,
        null=True,
        blank=True,
        help_text="Token generado para verificar el correo"
    )
    is_verified = models.BooleanField(
        "Correo verificado",
        default=False,
        help_text="Si el correo fue verificado"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
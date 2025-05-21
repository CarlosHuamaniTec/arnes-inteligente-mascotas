from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import secrets


class CustomUserManager(BaseUserManager):
    """
    Manager para el modelo CustomUser basado en email.
    """

    def create_user(self, email, first_name, password=None, **extra_fields):
        """
        Crea un usuario con email, nombre y contraseña.
        """
        if not email:
            raise ValueError("Debe ingresar el correo")
        if not first_name:
            raise ValueError("Debe ingresar el nombre")

        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **extra_fields)

        if not getattr(user, 'verification_token', None):
            user.verification_token = secrets.token_urlsafe(40)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password=None, **extra_fields):
        """
        Crea un superusuario con permisos de administrador.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser debe tener is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser debe tener is_superuser=True')

        return self.create_user(email, first_name, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Modelo de usuario con email como identificador y sin username.
    """

    username = None
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

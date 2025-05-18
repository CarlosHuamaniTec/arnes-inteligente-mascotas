from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    """Manejador personalizado para CustomUser
    Permite crear usuarios y superusuarios sin el campo username"""

    def create_user(self, email, first_name, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el correo y contraseña

        Args:
            email (string): Correo electrónico del usuario
            first_name (string): Nombre del usuario
            password (string, optional): Contraseña del usuario. Por defecto en None.
            extra_fields (dictionary): Campos adicionales como 'last_name' (apellidos), 'phone' (teléfono) y 'city'

        Raises:
            ValueError: Si no se proporciona un correo electrónico

        Returns:
            Custom_User: Usuario creado y guardado
        """
        if not email:
            raise ValueError("Debe ingresar el correo")
        if not first_name:
            raise ValueError("Debe ingresar el nombre")
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, password=None, **extra_fields):
        """
        Crea y guarda un superusuario con correo y contraseña.

        Args:
            email (string): Correo electrónico del superusuario
            first_name (string): Nombre del superusuario
            password (string, optional): Contraseña del superusuario. Por defecto en None.
            extra_fields (dictionary): Campos adicionales como is_staff o is_superuser

        Returns:
            CustomUser: Superusuario creado y guardado
        
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
    Modelo personalizado de usuario para la aplicación móvil.
    
    Se usa como usuario de autenticación (AUTH_USER_MODEL) en lugar del modelo usuario predeterminado de Django.
    No usa el campo 'username', sino 'email' como identificador único.
    """
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField("Nombre", max_length=150)
    last_name = models.CharField("Apellido", max_length=150, blank=True, null=True)
    phone = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
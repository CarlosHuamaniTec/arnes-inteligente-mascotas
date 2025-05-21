from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    Manejador personalizado para el modelo CustomUser
    
    Este manager permite la creación de usuarios y superusuarios sin usar el campo 'username',
    empleando únicamente el correo electrónico como identificador único.
    
    Métodos:
        create_user: Crea un usuario común con validaciones básicas
        create_superuser: Crea un superusuario con permisos adicionales
    """

    def create_user(self, email, first_name, password=None, **extra_fields):
        """
        Crea y guarda un usuario con el correo y contraseña
        
        Flujo de control:
            - Verifica que se proporcione correo y nombre
            - Normaliza el correo (lowercase)
            - Encripta la contraseña
            - Guarda el usuario en la base de datos
            
        Args:
            email (str): Correo electrónico del usuario. Requerido.
            first_name (str): Nombre del usuario. Requerido.
            password (str, optional): Contraseña del usuario. Por defecto es None.
            extra_fields (dict): Campos adicionales como last_name, phone, city, verification_token, is_verified

        Raises:
            ValueError: Si no se proporciona email o first_name
            
        Returns:
            CustomUser: Usuario creado y guardado en la base de datos
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
        
        Este método asegura que:
            - El usuario tenga is_staff=True
            - El usuario tenga is_superuser=True
            
        Args:
            email (str): Correo electrónico del superusuario
            first_name (str): Nombre del superusuario
            password (str, optional): Contraseña del superusuario. Por defecto es None.
            extra_fields (dict): Campos adicionales como is_staff, is_superuser, etc.

        Raises:
            ValueError: Si is_staff o is_superuser son False
            
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
    
    Extiende de Django's AbstractUser y reemplaza el campo username por email,
    usando este último como identificador único de sesión y verificación.
    
    Atributos principales:
        email (EmailField): Identificador único del usuario
        first_name (CharField): Nombre del usuario
        last_name (CharField, opcional): Apellido del usuario
        phone (CharField, opcional): Teléfono del usuario
        city (CharField, opcional): Ciudad donde reside el usuario
        verification_token (CharField, opcional): Token único para validar el correo
        is_verified (BooleanField): Indica si el correo fue verificado

    Flujo de Registro:
        1. Se crea usuario con is_active=False
        2. Se envía token de verificación al correo
        3. Al hacer clic en enlace → is_active = True, is_verified = True

    Notas:
        - Este modelo no incluye username
        - La autenticación se realiza vía correo + contraseña
        - Para producción, se espera integrar JWT Auth o Token Auth
    """
    
    # Campos de identificación y autenticación
    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField("Nombre", max_length=150)
    last_name = models.CharField("Apellido", max_length=150, blank=True, null=True)
    
    # Datos adicionales
    phone = models.CharField("Teléfono", max_length=20, blank=True, null=True)
    city = models.CharField("Ciudad", max_length=100, blank=True, null=True)

    # Confirmación de correo
    verification_token = models.CharField(
        "Token de verificación",
        max_length=100,
        null=True,
        blank=True,
        help_text="Token único generado durante el registro para verificar el correo"
    )
    is_verified = models.BooleanField(
        "Correo verificado",
        default=False,
        help_text="Indica si el correo fue confirmado mediante token"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email
# users/serializers.py
from rest_framework import serializers
from users.models import CustomUser
from django.utils.crypto import get_random_string
from users.utils.email import enviar_correo_confirmacion
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings

class RegisterSerializer(serializers.ModelSerializer):
    """
    Registra un nuevo usuario con correo, nombre, contraseña y username opcional.
    """
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'first_name', 'last_name', 'phone', 'city', 'password']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': False},
            'phone': {'required': False},
            'city': {'required': False},
        }

    def validate_email(self, value):
        """Valida que el email no esté registrado y lo normaliza."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Ya existe usuario con este email.")
        return value.lower().strip()

    def validate_username(self, value):
        """Valida que el username, si se proporciona, sea único."""
        if value and CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def create(self, validated_data):
        """Crea un usuario inactivo con token de verificación y envía correo."""
        validated_data.pop('verification_token', None)
        token = get_random_string(40)
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data.get('username'),  # Will be auto-generated if None
            first_name=validated_data['first_name'],
            password=validated_data['password'],
            last_name=validated_data.get('last_name'),
            phone=validated_data.get('phone'),
            city=validated_data.get('city'),
            verification_token=token,
            is_active=False
        )
        enviar_correo_confirmacion(user.email, token)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Autentica usuario con email y contraseña, y devuelve un token y detalles del usuario.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Verifica credenciales, estado del usuario y verificación de correo."""
        email = data.get('email').lower().strip()
        password = data.get('password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado.")

        if not user.check_password(password):
            raise serializers.ValidationError("Contraseña incorrecta.")

        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo.")

        if not user.is_verified:
            raise serializers.ValidationError("Correo no verificado.")

        token, _ = Token.objects.get_or_create(user=user)

        return {
            'token': token.key,
            'user': {
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone,
                'city': user.city
            }
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Solicita un enlace de restablecimiento de contraseña para un email dado.
    """
    email = serializers.EmailField()

    def validate_email(self, value):
        """Valida que el email esté registrado."""
        if not CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("No existe usuario con este email.")
        return value.lower().strip()

    def save(self):
        """Envía un correo con el enlace de restablecimiento."""
        email = self.validated_data['email']
        user = CustomUser.objects.get(email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_url = f"{settings.FRONTEND_VERIFY_URL}reset/{uid}/{token}/"
        send_mail(
            subject="Restablecer contraseña",
            message=f"Haz clic en el enlace para restablecer tu contraseña: {reset_url}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
from rest_framework import serializers
from users.models import CustomUser
from rest_framework.authtoken.models import Token


class RegisterSerializer(serializers.ModelSerializer):
    """
    Registra un nuevo usuario con correo, nombre y contraseña.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'city', 'password']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True}
        }

    def validate_email(self, value):
        """Valida que el email no esté registrado."""
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value.lower().strip()

    def create(self, validated_data):
        """Crea un usuario inactivo con token de verificación y envía correo."""
        validated_data.pop('verification_token', None)

        from django.utils.crypto import get_random_string
        token = get_random_string(40)

        user = CustomUser.objects.create_user(**validated_data, verification_token=token, is_active=False)

        from users.utils.email import enviar_correo_confirmacion
        enviar_correo_confirmacion(user.email, token)

        return user


class LoginSerializer(serializers.Serializer):
    """
    Autentica usuario con email y contraseña, y devuelve un token.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """Verifica credenciales y estado del usuario."""
        email = data.get('email')
        password = data.get('password')

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado.")

        if not user.check_password(password):
            raise serializers.ValidationError("Contraseña incorrecta.")

        if not user.is_active:
            raise serializers.ValidationError("Usuario inactivo.")

        token, _ = Token.objects.get_or_create(user=user)

        return {
            'user': user,
            'token': token.key
        }

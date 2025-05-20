from rest_framework import serializers
from users.models import CustomUser
from rest_framework.authtoken.models import Token

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de nuevos usuarios.

    Valida que:
    - El correo sea único.
    - El nombre no esté vacío.
    - Se pueda incluir campos adicionales como apellido, teléfono y ciudad.

    Atributos:
        email (str): Correo electrónico del usuario.
        first_name (str): Nombre del usuario (obligatorio).
        last_name (str, opcional): Apellido del usuario.
        phone (str, opcional): Número de teléfono.
        city (str, opcional): Ciudad donde reside el usuario.
        password (str): Contraseña del usuario (escribible pero no leíble desde la API).
    """

    password = serializers.CharField(
        write_only=True,
        help_text="Contraseña del usuario. No se devuelve en respuestas."
    )

    class Meta:
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'phone', 'city', 'password']
        extra_kwargs = {
            'email': {'required': True},
            'first_name': {'required': True}
        }

    def validate_email(self, value):
        """
        Valida que el correo no esté ya registrado.

        Args:
            value (str): Email proporcionado.

        Raises:
            serializers.ValidationError: Si el correo ya está en uso.

        Returns:
            str: Email válido.
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def create(self, validated_data):
        """
        Crea un nuevo usuario con los datos validados.

        Args:
            validated_data (dict): Datos validados por el serializador.

        Returns:
            CustomUser: Usuario creado.
        """
        user = CustomUser.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializador para autenticar usuarios mediante correo y contraseña.

    Campos:
        email (str): Correo del usuario.
        password (str): Contraseña del usuario (solo escritura).
    """

    email = serializers.EmailField(
        help_text="Correo electrónico del usuario."
    )
    password = serializers.CharField(
        write_only=True,
        help_text="Contraseña del usuario. No se devuelve en respuestas."
    )

    def validate(self, data):
        """
        Valida que el usuario exista y la contraseña sea correcta.

        Args:
            data (dict): Datos de entrada (correo y contraseña).

        Raises:
            serializers.ValidationError: Si el correo o la contraseña son inválidos.

        Returns:
            dict: Datos validados si todo es correcto.
        """
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

        # Crear o recuperar token
        token, created = Token.objects.get_or_create(user=user)

        return {
            'user': user,
            'token': token.key
        }
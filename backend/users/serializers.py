from rest_framework import serializers
from users.models import CustomUser
from rest_framework.authtoken.models import Token


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializador para el registro de nuevos usuarios.
    
    Este serializador permite crear usuarios con correo electrónico único, nombre obligatorio,
    y campos adicionales opcionales como apellido, teléfono y ciudad. Incluye validación de correo duplicado
    y genera un usuario inactivo hasta que confirme su correo.
    
    Flujo de Control:
        [Inicio]
           ↓
        validar_email() → email válido y no registrado
           ↓
         create() → crea usuario con is_active=False e is_verified=False
           ↓
        [Fin] Devuelve usuario creado
    
    Cobertura de prueba:
        - Camino principal: Registro exitoso con datos válidos
        - Condición 1: Falta email → ValidationError
        - Condición 2: Email ya existe → ValidationError
        - Camino secundario: Registro con campos extra ignorados
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
            value (str): Correo proporcionado por el usuario
            
        Ruta del CFG probada:
            [Entrada] → ¿Existe el correo? → Sí → Levantar error
                                           ↘ No → Salida: correo válido
        
        Raises:
            serializers.ValidationError: Si el correo ya está en uso.

        Returns:
            str: El correo validado
        """
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def create(self, validated_data):
        """
        Crea un nuevo usuario con los datos validados.

        Args:
            validated_data (dict): Datos validados por el serializador.

        Flujo de control:
            [Entrada]
               ↓
            Se eliminan los campos relacionados al token (si existen)
               ↓
            Se genera un verification_token único
               ↓
            Se crea el usuario con is_active=False e is_verified=False
               ↓
            Se retorna el usuario creado

        Returns:
            CustomUser: Usuario creado con estado inactivo y token de verificación
        """
        # Extraer datos sensibles
        validated_data.pop('verification_token', None)

        # Generar token único
        from django.utils.crypto import get_random_string
        token = get_random_string(40)

        # Crear usuario con is_active=False
        user = CustomUser.objects.create_user(**validated_data, verification_token=token, is_active=False)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializador para autenticar usuarios mediante correo y contraseña.

    Flujo de validación:
        [Entrada]
           ↓
        Buscar usuario por correo
           ↓
        ¿Usuario existe? → No → Error
                          ↘ Sí → Validar contraseña
                                 ↓
                             ¿Contraseña correcta? → No → Error
                                                    ↘ Sí → Verificar si es activo
                                                           ↓
                                                       ¿Es activo? → No → Error
                                                                         ↘ Sí → Generar token
                                                                                   ↓
                                                                               Devolver datos + token

    Cobertura de prueba:
        - Camino principal: Usuario válido → Contraseña válida → Activo → Token devuelto
        - Camino alternativo 1: Usuario no existe → Error lanzado
        - Camino alternativo 2: Contraseña incorrecta → Error lanzado
        - Camino alternativo 3: Usuario inactivo → Error lanzado
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
        Valida las credenciales del usuario y genera token si pasa todas las condiciones.

        Args:
            data (dict): Datos de entrada (correo y contraseña).

        Raises:
            serializers.ValidationError: Si el correo no existe, la contraseña es incorrecta o el usuario está inactivo.

        Returns:
            dict: Diccionario con usuario y token asociado.
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
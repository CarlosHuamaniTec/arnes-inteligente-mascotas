from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import RegisterSerializer, LoginSerializer
from users.models import CustomUser


class RegisterAPIView(APIView):
    """
    Vista para registrar nuevos usuarios.

    Permite crear un nuevo usuario con correo, nombre y contraseña.
    Campos adicionales como apellido, teléfono y ciudad son opcionales.
    
    Flujo de Control:
        [Entrada]
           ↓
        Validar datos → ¿Datos válidos? → Sí → Crear usuario e inactivar
                                           ↘ No → Devolver errores
        [Salida] Mensaje de éxito o error
        
    Cobertura:
        - Camino principal: Registro exitoso
        - Condición 1: Falta email → Error
        - Condición 2: Email ya usado → Error
        - Camino secundario: Datos extra se ignoran
    """

    def post(self, request):
        """
        Registra un nuevo usuario desde solicitud POST.

        Args:
            request (Request): Datos del cliente (correo, nombre, etc.)

        Returns:
            Response: HTTP 201_CREATED si es válido
                      HTTP 400_BAD_REQUEST si hay errores
        """
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Usuario creado exitosamente"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """
    Vista para autenticar usuarios.

    Valida credenciales mediante correo y contraseña.
    Si todo es correcto, devuelve token y datos básicos del usuario.
    
    Flujo de Control:
        [Entrada]
           ↓
        Validar correo → ¿Existe?
                             ↘ No → Error
                               ↓
                        Validar contraseña → ¿Correcta?
                                          ↘ No → Error
                                            ↓
                                        ¿Usuario activo?
                                          ↘ No → Error
                                            ↓
                                         Generar token
                                            ↓
                                       Devolver respuesta
    """

    def post(self, request):
        """
        Autentica al usuario y devuelve token.

        Args:
            request (Request): Datos del cliente (correo y contraseña)

        Returns:
            Response: Token + detalles si válido
                      Errores si no pasa validaciones
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.validated_data['token']
            return Response({
                "message": "Inicio de sesión exitoso",
                "token": token,
                "user_email": user.email,
                "user_id": user.id
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """
    Vista para validar el correo del usuario mediante un token enviado por email.

    Este endpoint permite:
    - Validar token desde URL
    - Activar cuenta del usuario
    - Limpiar token después de uso
    - Devolver mensaje HTML amigable o redirigir a app móvil

    Flujo de Control:
        [Entrada]
           ↓
        ¿Token presente? → No → Error
                            ↘ Sí → Buscar usuario
                                    ↘ Encontrado → Activar cuenta
                                                    ↓
                                                  Guardar cambios
                                                    ↓
                                                 Devolver éxito
                                                   ↗ No encontrado → Error

    Cobertura:
        - Camino principal: Token válido → Usuario activado
        - Condición 1: Token no proporcionado → Error lanzado
        - Condición 2: Token inválido → Error lanzado
        - Camino final: Respuesta HTML amigable
    """

    def get(self, request):
        """
        Activa la cuenta del usuario usando un token desde el navegador o app móvil.

        Args:
            request (Request): Debe contener parámetro 'token' en query params

        Returns:
            Response: Mensaje HTML o JSON indicando éxito o fallo
        """
        token = request.query_params.get('token')

        if not token:
            return Response(
                "<h1>Error</h1><p>No se proporcionó un token.</p>",
                status=status.HTTP_400_BAD_REQUEST,
                content_type="text/html"
            )

        try:
            user = CustomUser.objects.get(verification_token=token)
        except CustomUser.DoesNotExist:
            return Response(
                "<h1>Error</h1><p>Token inválido o expirado.</p>",
                status=status.HTTP_400_BAD_REQUEST,
                content_type="text/html"
            )

        # Activar usuario y limpiar token
        user.is_active = True
        user.is_verified = True
        user.verification_token = None
        user.save()

        return Response(
            "<h1>Correo Confirmado</h1><p>Ahora puedes iniciar sesión.</p>",
            status=status.HTTP_200_OK,
            content_type="text/html"
        )
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from users.serializers import RegisterSerializer, LoginSerializer


class RegisterAPIView(APIView):
    """
    Vista para registrar nuevos usuarios.

    Permite crear un nuevo usuario con correo, nombre y contraseña.
    Campos adicionales como apellido, teléfono y ciudad son opcionales.
    """

    def post(self, request):
        """
        Registra un nuevo usuario.

        Args:
            request (Request): Datos de entrada del cliente.

        Returns:
            Response: Respuesta HTTP con estado y datos del usuario creado o errores.
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

    Valida las credenciales del usuario y devuelve un token.
    """

    def post(self, request):
        """
        Autentica al usuario y devuelve un token.

        Args:
            request (Request): Datos de entrada del cliente.

        Returns:
            Response: Respuesta HTTP con token o errores.
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
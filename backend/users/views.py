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

    Valida las credenciales del usuario y devuelve una respuesta simple.
    En versiones futuras puede devolver un token JWT o Token Auth.
    """

    def post(self, request):
        """
        Autentica al usuario mediante correo y contraseña.

        Args:
            request (Request): Datos de entrada del cliente.

        Returns:
            Response: Respuesta HTTP con mensaje de éxito o errores.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(
                {"message": "Inicio de sesión exitoso"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
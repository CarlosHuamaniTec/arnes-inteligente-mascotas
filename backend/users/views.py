from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from users.serializers import RegisterSerializer, LoginSerializer
from users.models import CustomUser
from django.http import HttpResponse


class RegisterAPIView(APIView):
    """Registra nuevos usuarios."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Usuario creado exitosamente"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """Autentica usuario y devuelve token."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token = serializer.validated_data['token']
            return Response({
                "message": "Inicio de sesión exitoso",
                "token": token,
                "user": {
                    "id": user.id,
                    "email": user.email
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    """Activa cuenta mediante token enviado por correo."""

    def get(self, request):
        token = request.query_params.get('token')

        if not token:
            return self._render_error("No se proporcionó un token.")

        try:
            user = CustomUser.objects.get(verification_token=token)
        except CustomUser.DoesNotExist:
            return self._render_error("Token inválido o expirado.")

        user.is_active = True
        user.is_verified = True
        user.verification_token = None
        user.save()

        return HttpResponse("""
        <html>
        <head><title>Correo Verificado</title></head>
        <body style="font-family: Arial; text-align: center; padding: 40px;">
            <h1 style="color: green;">✅ Correo verificado exitosamente</h1>
            <p>Ahora puedes iniciar sesión desde tu aplicación móvil.</p>
            <br>
            <a href="#" onclick="window.close()" style="text-decoration: none; color: #007bff;">Cerrar ventana</a>
        </body>
        </html>
        """)

    def _render_error(self, message):
        return HttpResponse(f"""
        <html>
        <body style="font-family: Arial; text-align: center; padding: 40px;">
            <h1 style="color: red;">❌ Error</h1>
            <p>{message}</p>
            <br>
            <a href="#" onclick="window.close()" style="text-decoration: none; color: #007bff;">Volver</a>
        </body>
        </html>
        """, status=400)
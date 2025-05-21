from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer
from .serializers import LoginSerializer
from .serializers import PasswordResetRequestSerializer
from .models import CustomUser

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({"message": "Usuario registrado. Revisa tu correo para verificar."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import LoginSerializer

class LoginAPIView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VerifyEmailView(APIView):
    def get(self, request):
        token = request.GET.get('token')
        if not token:
            return Response({"error": "No se proporcionó un token."}, status=400)
        try:
            user = CustomUser.objects.get(verification_token=token)
            user.is_verified = True
            user.is_active = True
            user.verification_token = None
            user.save()
            return Response({"message": "Correo verificado exitosamente"})
        except CustomUser.DoesNotExist:
            return Response({"error": "Token inválido o expirado."}, status=400)
        

class PasswordResetRequestView(APIView):
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Correo de restablecimiento enviado."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
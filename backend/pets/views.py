from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import PetSerializer
from .models import Pet

class PetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class PetCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PetSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# pets/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import BiometricDataSerializer
from django_redis import get_redis_connection

class BiometricDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pet_id):
        try:
            pet = request.user.pets.get(id=pet_id)
            # Obtener datos más recientes desde Redis
            redis_conn = get_redis_connection("default")
            data = redis_conn.get(f"biometric:{pet_id}")
            if data:
                import json
                biometric_data = json.loads(data)
                serializer = BiometricDataSerializer(data=biometric_data)
                serializer.is_valid(raise_exception=True)
                return Response(serializer.validated_data)
            return Response({"message": "No hay datos disponibles"}, status=404)
        except Pet.DoesNotExist:
            return Response({"error": "Mascota no encontrada"}, status=404)
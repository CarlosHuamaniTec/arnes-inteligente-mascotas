from rest_framework import serializers
from pets.models import Pet

class PetSerializer(serializers.ModelSerializer):
    """
    Registra una nueva mascota para un usuario autenticado.
    """
    class Meta:
        model = Pet
        fields = ['id', 'name', 'species', 'breed', 'birth_date']
        extra_kwargs = {
            'name': {'required': True},
            'species': {'required': True},
            'breed': {'required': False},
            'birth_date': {'required': False},
        }

    def create(self, validated_data):
        """Asocia la mascota al usuario autenticado."""
        validated_data['owner'] = self.context['request'].user
        return Pet.objects.create(**validated_data)
    

class BiometricDataSerializer(serializers.Serializer):
    """
    Serializa datos biométricos en tiempo real para enviar a la app móvil.
    """
    pet_id = serializers.IntegerField()
    heart_rate = serializers.FloatField()
    temperature = serializers.FloatField()
    movement_x = serializers.FloatField()
    movement_y = serializers.FloatField()
    movement_z = serializers.FloatField()
    alerts = serializers.ListField(child=serializers.CharField(), required=False)
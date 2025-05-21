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
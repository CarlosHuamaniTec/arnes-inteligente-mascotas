# pets/models.py
from django.db import models
from users.models import CustomUser

class Pet(models.Model):
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=50)  # e.g., "Perro", "Gato"
    breed = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner.email})"

    class Meta:
        verbose_name = "Mascota"
        verbose_name_plural = "Mascotas"
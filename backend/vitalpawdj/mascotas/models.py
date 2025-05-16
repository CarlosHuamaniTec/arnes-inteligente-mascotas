from django.db import models
from django.contrib.auth import get_user_model
from datetime import date
from PIL import Image
import os

User = get_user_model()

class Mascota(models.Model):
    nombre = models.CharField(max_length=100)
    raza = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    foto = models.ImageField(upload_to='fotos_mascotas/', null=True, blank=True)
    propietario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def calcular_edad(self):
        #Calcula la edad en años y meses
        hoy = date.today()
        nacimiento = self.fecha_nacimiento
        total_meses = (hoy.year - nacimiento.year) * 12 + (hoy.month - nacimiento.month)
        if hoy.day < nacimiento.day:
            total_meses -= 1
        return {
            'años': total_meses // 12,
            'meses': total_meses % 12,
        }

    @property
    def edad_años(self):
        return self.calcular_edad()['años']

    @property
    def edad_meses(self):
        return self.calcular_edad()['meses']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Si hay foto, redimensionar a 1x1
        if self.foto:
            img_path = self.foto.path
            try:
                with Image.open(img_path) as image:
                    image.thumbnail((1, 1), Image.LANCZOS)
                    image.save(img_path)
            except Exception as e:
                print(f"Error al procesar imagen: {e}")

    def __str__(self):
        return f"{self.nombre} ({self.raza})"
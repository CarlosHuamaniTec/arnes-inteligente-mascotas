# pets/urls.py
from django.urls import path
from .views import PetCreateAPIView, BiometricDataAPIView

urlpatterns = [
    path('create/', PetCreateAPIView.as_view(), name='pet-create'),
    path('<int:pet_id>/biometrics/', BiometricDataAPIView.as_view(), name='pet-biometrics'),
]
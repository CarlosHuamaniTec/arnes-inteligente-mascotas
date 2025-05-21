# backend/users/tests_user/unitarias/test_register_api_viewcfg.py

from django.test import TestCase, RequestFactory
from rest_framework.test import APIRequestFactory
from rest_framework import status
from users.views import RegisterAPIView
from users.models import CustomUser


class RegisterAPIViewCFGTest(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.view = RegisterAPIView.as_view()
        self.valid_data = {
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "city": "Lima",
            "password": "pass1234"
        }

    def test_post_valido_crea_usuario(self):
        """
        Flujo principal: datos válidos → usuario creado → status 201
        """
        request = self.factory.post('/register/', self.valid_data, format='json')
        response = self.view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data.get("message"), "Usuario creado exitosamente")
        self.assertTrue(CustomUser.objects.filter(email=self.valid_data["email"]).exists())

    def test_post_email_repetido_retorna_error(self):
        """
        Email repetido → status 400 con error
        """
        # Crear usuario previo con email repetido
        CustomUser.objects.create_user(
            email=self.valid_data["email"],
            first_name="Existing",
            password="pass1234"
        )

        request = self.factory.post('/register/', self.valid_data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_post_sin_email_retorna_error(self):
        """
        Sin email → status 400 con error
        """
        data = self.valid_data.copy()
        data.pop("email")

        request = self.factory.post('/register/', data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_post_sin_nombre_retorna_error(self):
        """
        Sin first_name → status 400 con error
        """
        data = self.valid_data.copy()
        data.pop("first_name")

        request = self.factory.post('/register/', data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)

    def test_post_con_campos_extra_ignora(self):
        """
        Campos extras no definidos → son ignorados y usuario creado correctamente
        """
        data = self.valid_data.copy()
        data["extra_field"] = "ignored"

        request = self.factory.post('/register/', data, format='json')
        response = self.view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse("extra_field" in response.data)  # No aparece en response
        self.assertTrue(CustomUser.objects.filter(email=data["email"]).exists())

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser


class UserRegistrationAPITest(TestCase):
    """Pruebas de integración para la vista de registro de usuarios"""

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.valid_payload = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "city": "Lima",
            "password": "pass1234"
        }

    def test_registro_usuario_exitoso(self):
        """Verifica que un usuario pueda registrarse con datos válidos"""
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(CustomUser.objects.filter(email=self.valid_payload['email']).exists())

    def test_registro_sin_correo_falla(self):
        """Verifica que falte el correo lance un error 400"""
        payload = self.valid_payload.copy()
        payload.pop('email')
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registro_sin_nombre_falla(self):
        """Verifica que falte el nombre lance un error 400"""
        payload = self.valid_payload.copy()
        payload.pop('first_name')
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('first_name', response.data)

    def test_registro_con_correo_duplicado_falla(self):
        """Verifica que no se permita duplicar correos"""
        CustomUser.objects.create_user(**self.valid_payload)
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registro_no_devuelve_password(self):
        """Verifica que la contraseña no esté en la respuesta"""
        response = self.client.post(self.register_url, self.valid_payload, format='json')
        self.assertNotIn('password', response.data)


class UserLoginAPITest(TestCase):
    """Pruebas de integración para la vista de inicio de sesión"""

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.user = CustomUser.objects.create_user(
            email="login@example.com",
            first_name="Login",
            password="correctpassword"
        )

    def test_login_exitoso(self):
        """Verifica que el inicio de sesión sea exitoso con credenciales correctas"""
        payload = {
            "email": "login@example.com",
            "password": "correctpassword"
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], "Inicio de sesión exitoso")

    def test_login_con_correo_incorrecto(self):
        """Verifica que se lance un error si el correo es inválido"""
        payload = {
            "email": "invalid@example.com",
            "password": "correctpassword"
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("Usuario no encontrado.", response.data["non_field_errors"])

    def test_login_con_password_incorrecto(self):
        """Verifica que se lance un error si la contraseña es incorrecta"""
        payload = {
            "email": "login@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("Contraseña incorrecta.", response.data["non_field_errors"])

    def test_login_usuario_inactivo(self):
        """Verifica que un usuario inactivo no pueda iniciar sesión"""
        self.user.is_active = False
        self.user.save()

        payload = {
            "email": "login@example.com",
            "password": "correctpassword"
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)
        self.assertIn("Usuario inactivo.", response.data["non_field_errors"])
# backend/users/tests_user/unitarias/test_login_api_viewcfg.py

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from users.models import CustomUser
from rest_framework.authtoken.models import Token


class LoginAPIViewCFGTest(APITestCase):
    """
    Pruebas unitarias de caja blanca (CFG) para LoginAPIView POST /login/.

    Cobertura:
    - Datos correctos → login exitoso → token y user devueltos.
    - Datos inválidos → errores de serializador.
    - Usuario no existe.
    - Password incorrecta.
    - Usuario inactivo.
    """

    def setUp(self):
        self.url = reverse("login-api")  # Ajusta según tu urls.py, ejemplo: path('login/', LoginAPIView.as_view(), name='login-api')
        self.password = "testpass123"
        self.active_user = CustomUser.objects.create_user(
            email="active@example.com",
            first_name="Active",
            password=self.password,
            is_active=True
        )
        self.inactive_user = CustomUser.objects.create_user(
            email="inactive@example.com",
            first_name="Inactive",
            password=self.password,
            is_active=False
        )

    def test_login_exitoso(self):
        """
        [Caja Blanca - CFG] Camino principal: login correcto.
        """
        data = {"email": self.active_user.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertIn("user", response.data)
        self.assertEqual(response.data["user"]["email"], self.active_user.email)
        # Verificar token válido en DB
        token = Token.objects.filter(user=self.active_user).first()
        self.assertIsNotNone(token)
        self.assertEqual(response.data["token"], token.key)

    def test_login_usuario_no_existe(self):
        """
        [CFG] Usuario no existe → error 400 con mensaje.
        """
        data = {"email": "noexiste@example.com", "password": "any"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Usuario no encontrado.", str(response.data))

    def test_login_password_incorrecta(self):
        """
        [CFG] Password incorrecta → error 400 con mensaje.
        """
        data = {"email": self.active_user.email, "password": "wrongpass"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Contraseña incorrecta.", str(response.data))

    def test_login_usuario_inactivo(self):
        """
        [CFG] Usuario inactivo → error 400 con mensaje.
        """
        data = {"email": self.inactive_user.email, "password": self.password}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Usuario inactivo.", str(response.data))

    def test_login_faltan_campos_requeridos(self):
        """
        [CFG] Falta email o password → error 400 y detalles.
        """
        # Sin email
        data = {"password": self.password}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

        # Sin password
        data = {"email": self.active_user.email}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_login_email_con_mayusculas(self):
        """
        [CFG] Email con mayúsculas → login exitoso (normalización).
        """
        data = {"email": self.active_user.email.upper(), "password": self.password}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["user"]["email"], self.active_user.email)
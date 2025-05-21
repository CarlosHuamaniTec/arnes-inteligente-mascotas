# users/tests_users/unitarias/LoginAPIViewTestCFG.py

from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from users.views import LoginAPIView
from users.models import CustomUser
from rest_framework.authtoken.models import Token


class LoginAPIViewCFGTest(TestCase):
    """
    Prueba unitaria de caja blanca para LoginAPIView.
    
    Flujo de Control del método POST:
    
        [Entrada]
           ↓
        Validar datos → ¿Correo existe?
                             ↘ No → Error
                               ↓
                        ¿Contraseña correcta? → No → Error
                                               ↓
                                      ¿Usuario activo? → No → Error
                                                            ↓
                                                 Generar token → Devolver éxito
        
    Aplica estos criterios de cobertura:
        - Cobertura de instrucciones/nodos
        - Cobertura de condiciones/decisiones
        - Cobertura de ruta completa
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

        # Datos de prueba
        self.user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "password": "correctpassword"
        }

        # Crear usuario
        self.user = CustomUser.objects.create_user(**self.user_data)
        self.user.is_active = True
        self.user.save()

    def test_login_usuario_valido_activo(self):
        """
        [Caja Blanca - CFG] Camino principal completo

        Camino:
        Datos válidos → Usuario existe → Contraseña correcta → Activo → Token devuelto

        Cobertura:
        - Todos los nodos ejecutados
        - Todos los if pasan (True)
        """
        view = LoginAPIView.as_view()
        request = self.factory.post("/api/auth/login/", self.user_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user_email"], self.user_data["email"])

        # Verificar que el token se haya creado
        token = Token.objects.get(user=self.user)
        self.assertEqual(response.data["token"], token.key)

    def test_login_con_correo_incorrecto(self):
        """
        [Caja Blanca - CFG] Condición 1: correo no existe

        Camino:
        email == None → Levanta error
            
        Cobertura:
        - Nodo decisión: usuario no encontrado
        - Excepción lanzada
        """
        invalid_data = {
            "email": "invalid@example.com",
            "password": "any_password"
        }
        view = LoginAPIView.as_view()
        request = self.factory.post("/api/auth/login/", invalid_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Usuario no encontrado.")

    def test_login_con_password_incorrecto(self):
        """
        [Caja Blanca - CFG] Condición 2: contraseña incorrecta

        Camino:
        Usuario existe → Contraseña != correcta → Error
            
        Cobertura:
        - Nodo decisión: contraseña incorrecta
        - Excepción lanzada
        """
        wrong_data = {
            "email": self.user_data["email"],
            "password": "wrongpassword"
        }
        view = LoginAPIView.as_view()
        request = self.factory.post("/api/auth/login/", wrong_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Contraseña incorrecta.")

    def test_login_usuario_inactivo(self):
        """
        [Caja Blanca - CFG] Condición 3: usuario inactivo

        Camino:
        Usuario existe → Contraseña correcta → is_active == False → Error
            
        Cobertura:
        - Nodo decisión: usuario inactivo
        - Excepción lanzada
        """
        self.user.is_active = False
        self.user.save()

        inactive_data = {
            "email": self.user.email,
            "password": self.user_data["password"]
        }

        view = LoginAPIView.as_view()
        request = self.factory.post("/api/auth/login/", inactive_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["non_field_errors"][0], "Usuario inactivo.")

    def test_login_no_devuelve_password(self):
        """
        [Caja Blanca - CFG] Camino secundario: seguridad en respuesta

        Camino:
        Inicio de sesión válido → Respuesta sin password
            
        Cobertura:
        - Ruta básica con seguridad
        """
        view = LoginAPIView.as_view()
        request = self.factory.post("/api/auth/login/", self.user_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("password", response.data)

    def test_login_datos_minimos_requeridos(self):
        """
        [Caja Blanca - CFG] Datos mínimos necesarios

        Camino:
        Solo email y password → Se valida correctamente
            
        Cobertura:
        - Camino básico con envío mínimo de campos
        """
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        view = LoginAPIView.as_view()
        request = self.factory.post("/api/auth/login/", data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
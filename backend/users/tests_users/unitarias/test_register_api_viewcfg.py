# users/tests_users/unitarias/RegisterAPIViewTestCFG.py

from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from users.views import RegisterAPIView
from users.models import CustomUser
from rest_framework.test import APIClient


class RegisterAPIViewCFGTest(TestCase):
    """
    Prueba unitaria de caja blanca para la vista RegisterAPIView.
    
    Flujo de Control del método POST:
    
        [Entrada]
           ↓
        ¿Datos válidos? → Sí → Guardar usuario con is_active=False
                             ↓
                        Enviar correo de confirmación (mockeado)
                             ↓
                      Devolver mensaje de éxito
                            ↗ No → Devolver errores
        
    Se aplican criterios de cobertura:
        - Cobertura de instrucciones/nodos
        - Cobertura de condiciones/decisiones
        - Cobertura de ruta completa
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

    def test_registro_usuario_datos_validos(self):
        """
        [Caja Blanca - Flujo de Control] Camino principal completo
        
        Camino:
        Datos válidos → Serializador válido → Usuario creado con is_active=False
        
        Cobertura:
        - Nodo inicial y final
        - Todos los if pasan (True)
        """
        request_data = {
            "email": "valid@example.com",
            "first_name": "Valid",
            "last_name": "User",
            "phone": "+1234567890",
            "city": "Lima",
            "password": "pass1234"
        }

        view = RegisterAPIView.as_view()
        request = self.factory.post("/api/auth/register/", request_data, format="json")
        response = view(request)

        # Verificar respuesta HTTP
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["message"], "Usuario creado exitosamente")

        # Verificar datos del usuario
        user = CustomUser.objects.get(email=request_data["email"])
        self.assertEqual(user.first_name, request_data["first_name"])
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)
        self.assertIsNotNone(user.verification_token)

    def test_registro_sin_correo_falla(self):
        """
        [Caja Blanca - Flujo de Control] Condición 1: email == None
        
        Camino:
        Sin correo → Serializador inválido → Error devuelto
        
        Cobertura:
        - Decisión 1: falta email
        - Ruta alternativa: validación fallida
        """
        request_data = {
            "first_name": "MissingEmail",
            "password": "pass1234"
        }

        view = RegisterAPIView.as_view()
        request = self.factory.post("/api/auth/register/", request_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registro_sin_nombre_falla(self):
        """
        [Caja Blanca - Flujo de Control] Condición 2: first_name == None
        
        Camino:
        Sin nombre → Serializador inválido → Error devuelto
        
        Cobertura:
        - Decisión 2: falta first_name
        - Ruta alternativa: validación fallida
        """
        request_data = {
            "email": "no-name@example.com",
            "password": "pass1234"
        }

        view = RegisterAPIView.as_view()
        request = self.factory.post("/api/auth/register/", request_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("first_name", response.data)

    def test_registro_con_campos_extra_ignorados(self):
        """
        [Caja Blanca - Flujo de Control] Campos no definidos se ignoran
        
        Camino:
        Datos con campo adicional → serializador los ignora
            
        Cobertura:
        - Camino secundario con campos extras
        """
        request_data = {
            "email": "extra@example.com",
            "first_name": "Extra",
            "password": "pass1234",
            "invalid_field": "should_be_ignored"
        }

        view = RegisterAPIView.as_view()
        request = self.factory.post("/api/auth/register/", request_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = CustomUser.objects.get(email=request_data["email"])
        self.assertNotIn("invalid_field", user.__dict__)
        self.assertNotIn("invalid_field", user.to_dict())  # Si tienes un método to_dict() o similar

    def test_registro_con_correo_repetido_falla(self):
        """
        [Caja Blanca - Flujo de Control] Correo ya usado
        
        Camino:
        Email existente → ValidationError → Error devuelto
        
        Cobertura:
        - Decisión 3: correo ya existe
        - Ruta alternativa: validación fallida
        """
        existing_user = CustomUser.objects.create_user(
            email="duplicate@example.com",
            first_name="Existing",
            password="pass1234"
        )
        request_data = {
            "email": "duplicate@example.com",
            "first_name": "John",
            "password": "pass1234"
        }

        view = RegisterAPIView.as_view()
        request = self.factory.post("/api/auth/register/", request_data, format="json")
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_registro_no_devuelve_password_en_respuesta(self):
        """
        [Caja Blanca - Flujo de Control] Contraseña no devuelta
        
        Camino:
        Registro exitoso → Respuesta sin contraseña
            
        Cobertura:
        - Camino básico con seguridad
        """
        data = {
            "email": "secure@example.com",
            "first_name": "Secure",
            "password": "pass1234"
        }

        view = RegisterAPIView.as_view()
        client = APIClient()
        response = client.post("/api/auth/register/", data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertNotIn("password", response.data)
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from users.models import CustomUser
from django.urls import reverse


class VistaModeloIntegracionTest(TestCase):
    """
    Prueba de integración entre vistas y modelos
    
    Flujo probado:
        1. Registro desde API → Crea usuario inactivo
        2. Confirmación por token → Activa al usuario
        3. Inicio de sesión → Devuelve token si está activo
        
    Cobertura:
        - Interacción completa entre vistas y modelos
        - Validación de estado persistente del usuario
        - Comprobación de tokens y mensajes de éxito/error
    """

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.verify_email_url = reverse('verify-email')

        self.user_data = {
            "email": "integ@example.com",
            "first_name": "Integration",
            "last_name": "Test",
            "phone": "+51987654321",
            "city": "Lima",
            "password": "pass1234"
        }

    def test_registro_usuario_y_estado_inicial(self):
        """
        [Caja Gris] Verifica que el registro crea usuario inactivo
        
        Camino:
        POST /api/auth/register/ → Usuario creado → is_active=False
            
        Cobertura:
        - Vista + Modelo trabajando juntos
        - Validación de estado inicial
        """
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = CustomUser.objects.get(email=self.user_data["email"])
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)
        self.assertIsNotNone(user.verification_token)

    def test_registro_y_confirmacion_correo_desde_api(self):
        """
        [Caja Gris] Ruta completa: registro → verificación → login
        
        Camino:
        POST /register/ → usuario inactivo
        GET /verify-email/ → usuario activado
        POST /login/ → devuelve token
        
        Cobertura:
        - Integración entre tres vistas
        - Cambio de estado persistido en modelo
        """
        # Paso 1: Registrar usuario
        register_response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        user = CustomUser.objects.get(email=self.user_data["email"])
        token = user.verification_token

        # Paso 2: Confirmar correo
        verify_response = self.client.get(f"{self.verify_email_url}?token={token}")
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_verified)
        self.assertIsNone(user.verification_token)

        # Paso 3: Iniciar sesión
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("token", login_response.data)

    def test_inicio_sesion_sin_verificar_correo_falla(self):
        """
        [Caja Gris] Login falla si no se verificó el correo
        
        Camino:
        POST /register/ → usuario inactivo
        POST /login/ → debe fallar
            
        Cobertura:
        - Validación de estado antes de verificación
        """
        # Paso 1: Registrar usuario
        register_response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # Paso 2: Intentar iniciar sesión sin verificar correo
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", login_response.data)

    def test_confirmar_correo_invalido_lanza_error(self):
        """
        [Caja Gris] Token inválido → error en confirmación
        
        Camino:
        GET /verify-email/?token=invalid → Levanta error
            
        Cobertura:
        - Vista y modelo reaccionan correctamente a token inválido
        """
        # Registrar usuario
        self.client.post(self.register_url, self.user_data, format='json')

        # Usar token inválido
        invalid_token = "invalid123456"
        verify_response = self.client.get(f"{self.verify_email_url}?token={invalid_token}")
        self.assertEqual(verify_response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_flujo_completo_con_datos_opcionales(self):
        """
        [Caja Gris] Campos adicionales como apellido, teléfono y ciudad son guardados
        
        Camino:
        Registro con campos extra → Guardar correctamente
            
        Cobertura:
        - Campos opcionales funcionan correctamente
        """
        optional_data = {
            "email": "optional@example.com",
            "first_name": "Optional",
            "password": "pass1234",
            "last_name": "Apellido",
            "phone": "+1234567890",
            "city": "Madrid"
        }

        # Paso 1: Registro con campos adicionales
        register_response = self.client.post(self.register_url, optional_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        user = CustomUser.objects.get(email=optional_data["email"])

        # Paso 2: Verificar correo
        verify_response = self.client.get(f"{self.verify_email_url}?token={user.verification_token}")
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        for field in ["last_name", "phone", "city"]:
            with self.subTest(field=field):
                self.assertEqual(getattr(user, field), optional_data[field])

        # Paso 3: Iniciar sesión
        login_data = {
            "email": optional_data["email"],
            "password": optional_data["password"]
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
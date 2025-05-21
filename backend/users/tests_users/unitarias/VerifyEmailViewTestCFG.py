# users/tests_users/unitarias/VerifyEmailViewTestCFG.py

from django.test import TestCase
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from users.views import VerifyEmailView
from users.models import CustomUser


class VerifyEmailViewCFGTest(TestCase):
    """
    Prueba unitaria de caja blanca para VerifyEmailView.
    
    Flujo de Control del método GET:
    
        [Entrada]
           ↓
        ¿Token presente? → No → Devolver error HTML
                            ↘ Sí → Buscar usuario
                                        ↘ Encontrado → Activar cuenta
                                                        ↓
                                                      Limpiar token
                                                        ↓
                                                    Guardar cambios
                                                        ↓
                                                  Devolver éxito HTML
                                                   ↗ No encontrado → Error HTML
        
    Aplica los siguientes criterios de cobertura:
        - Cobertura de instrucciones/nodos
        - Cobertura de condiciones/decisiones
        - Cobertura de ruta completa
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

        # Datos de usuario de prueba
        self.user_data = {
            "email": "verify@example.com",
            "first_name": "Verify",
            "password": "pass1234"
        }

        # Crear usuario con token de verificación
        self.user = CustomUser.objects.create_user(**self.user_data, is_active=False)
        self.verification_token = self.user.verification_token

    def test_verificar_correo_con_token_valido(self):
        """
        [Caja Blanca - CFG] Camino principal completo
        
        Camino:
        token != None → Usuario encontrado → Cuenta activada → Token limpiado
            
        Cobertura:
        - Todos los nodos ejecutados
        - Condición 1: token válido → éxito
        """
        url = f"/api/auth/verify-email/?token={self.verification_token}"
        request = self.factory.get(url)
        view = VerifyEmailView.as_view()
        response = view(request)

        # Verificar respuesta HTTP
        self.assertEqual(response.status_code, status.HTTP_200_OK)
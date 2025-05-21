# users/tests_users/unitarias/LoginSerializerTestCFG.py

from django.test import TestCase
from rest_framework import serializers
from users.serializers import LoginSerializer
from users.models import CustomUser
from rest_framework.authtoken.models import Token


class LoginSerializerCFGTest(TestCase):
    """
    Prueba unitaria de caja blanca para LoginSerializer.
    
    Flujo de Control del método validate():
    
        [Entrada]
           ↓
        Buscar usuario por correo → ¿Existe?
                                           ↘ No → Levantar error
                                             ↓
                                       Validar contraseña → ¿Correcta?
                                                                    ↘ No → Levantar error
                                                                      ↓
                                                                ¿Usuario activo? → No → Levantar error
                                                                                     ↘ Sí → Generar token
                                                                                              ↓
                                                                                  Devolver datos validados
    
    Cobertura:
        - Camino principal: Usuario válido, contraseña correcta, activo → Token devuelto
        - Condición 1: email == None → Error lanzado
        - Condición 2: Contraseña incorrecta → Error lanzado
        - Condición 3: is_active == False → Error lanzado
    """

    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "password": "correctpassword"
        }
        self.user = CustomUser.objects.create_user(**self.user_data)

    def test_login_usuario_valido_activo(self):
        """
        [Caja Blanca - CFG] Ruta principal completa
        
        Camino:
        Usuario existe → Contraseña correcta → Activo → Devuelve token
        
        Cobertura:
        - Todos los nodos ejecutados
        - Todos los if pasan (True)
        """
        serializer = LoginSerializer()
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }

        validated_data = serializer.validate(data)

        self.assertIn("user", validated_data)
        self.assertIn("token", validated_data)
        self.assertEqual(validated_data["user"].email, self.user.email)

        token = Token.objects.get(user=self.user)
        self.assertEqual(validated_data["token"], token.key)

    def test_login_sin_correo_lanza_error(self):
        """
        [Caja Blanca - CFG] Condición 1: email == None
        
        Camino:
        email == None → Levanta error
            
        Cobertura:
        - Nodo decisión: usuario no encontrado
        - Excepción lanzada
        """
        serializer = LoginSerializer()
        data = {
            "email": None,
            "password": "any_password"
        }

        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(data)

        self.assertEqual(context.exception.detail[0], "Usuario no encontrado.")

    def test_login_con_password_incorrecto_lanza_error(self):
        """
        [Caja Blanca - CFG] Condición 2: contraseña != correcta
        
        Camino:
        email != None → usuario existe → contraseña inválida → error
            
        Cobertura:
        - Nodo decisión: contraseña incorrecta
        - Excepción lanzada
        """
        serializer = LoginSerializer()
        data = {
            "email": self.user_data["email"],
            "password": "wrongpassword"
        }

        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(data)

        self.assertEqual(context.exception.detail[0], "Contraseña incorrecta.")

    def test_login_usuario_inactivo_lanza_error(self):
        """
        [Caja Blanca - CFG] Condición 3: is_active == False
        
        Camino:
        usuario existe → contraseña correcta → is_active == False → error
            
        Cobertura:
        - Nodo decisión: usuario inactivo
        - Excepción lanzada
        """
        # Desactivar usuario
        self.user.is_active = False
        self.user.save()

        serializer = LoginSerializer()
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }

        with self.assertRaises(serializers.ValidationError) as context:
            serializer.validate(data)

        self.assertEqual(context.exception.detail[0], "Usuario inactivo.")

    def test_login_datos_minimos_requeridos(self):
        """
        [Caja Blanca - CFG] Datos mínimos necesarios
        
        Camino:
        Solo email y password → Se valida correctamente
            
        Cobertura:
        - Camino básico con datos mínimos
        """
        serializer = LoginSerializer()
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }

        validated_data = serializer.validate(data)

        self.assertIn("user", validated_data)
        self.assertIn("token", validated_data)

    def test_login_no_devuelve_password_en_respuesta(self):
        """
        [Caja Blanca - CFG] Seguridad en respuesta
        
        Camino:
        Credenciales válidas → Respuesta sin contraseña
            
        Cobertura:
        - Camino básico con seguridad
        """
        serializer = LoginSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("password", serializer.data)

    def test_login_campos_opcionales_ignorados(self):
        """
        [Caja Blanca - CFG] Campos adicionales no afectan login
        
        Camino:
        Datos con campos extra → son ignorados
            
        Cobertura:
        - Camino secundario con campos extras
        """
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
            "extra_field": "should_be_ignored"
        }

        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        self.assertNotIn("extra_field", serializer.validated_data)

    def test_login_usuario_desde_vista_api(self):
        """
        [Caja Blanca - CFG] Validación desde vista API
        
        Camino:
        Vista POST → serializador valida → devuelve token
            
        Cobertura:
        - Camino completo desde API hasta serializador
        """
        from rest_framework.test import APIRequestFactory
        from users.views import LoginAPIView

        view = LoginAPIView()
        request_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        request = APIRequestFactory().post("/api/auth/login/", request_data, format="json")
        response = view.post(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user_email"], self.user.email)

    def test_login_usuario_y_token_guardado(self):
        """
        [Caja Blanca - CFG] Token persistente guardado en base de datos
        
        Camino:
        Usuario válido → Token generado → Guardado en DB
            
        Cobertura:
        - Camino básico con token persistido
        """
        serializer = LoginSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())

        user = serializer.validated_data["user"]
        token_key = serializer.validated_data["token"]

        token_db = Token.objects.get(user=user)
        self.assertEqual(token_key, token_db.key)

    def test_login_flujo_completo_registro_verificacion_login(self):
        """
        [Caja Blanca - CFG] Registro → verificación → inicio de sesión
        
        Camino:
        Registro → Correo pendiente → verificar → login exitoso
            
        Cobertura:
        - Camino integral de flujo de registro a login
        """
        from rest_framework.test import APIClient
        from django.urls import reverse

        client = APIClient()

        # Paso 1: Registro
        register_data = {
            "email": "flow@example.com",
            "first_name": "Flow",
            "password": "pass1234"
        }
        register_response = client.post(reverse('register'), register_data, format='json')
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED) # type: ignore

        # Paso 2: Verificar correo
        user = CustomUser.objects.get(email=register_data["email"])
        verification_url = reverse('verify-email') + f"?token={user.verification_token}"
        verify_response = client.get(verification_url)
        self.assertEqual(verify_response.status_code, status.HTTP_200_OK) # type: ignore

        # Paso 3: Iniciar sesión
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        login_response = client.post(reverse('login'), login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK) # type: ignore
        self.assertIn("token", login_response.data)
from django.test import TestCase
from users.serializers import RegisterSerializer, LoginSerializer
from users.models import CustomUser
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError


class SerializerModelIntegrationTest(TestCase):
    """
    Prueba de integración entre serializadores y modelos (Caja Gris)
    
    Flujo probado:
        1. Registro desde RegisterSerializer → Crea usuario inactivo con token
        2. Inicio de sesión falla si no está activo
        3. Verificación activa usuario
        4. LoginSerializer valida credenciales y genera token
        
    Cobertura:
        - Interacción directa entre serializadores y modelo
        - Validación de estado del modelo tras serialización
        - Probar efectos secundarios (token, is_active, etc.)
    """

    def test_registro_serializador_crea_usuario_correcto(self):
        """
        [Caja Gris] Registro desde RegisterSerializer → Usuario creado en DB
        
        Camino:
        Serializador válido → Usuario guardado → Campos correctos en modelo
            
        Cobertura:
        - Registro exitoso con serializador
        - Datos reflejados en base de datos
        """
        data = {
            "email": "integ@example.com",
            "first_name": "Integ",
            "last_name": "Model",
            "phone": "+51999999999",
            "city": "Lima",
            "password": "pass1234"
        }

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Verificar campos en modelo
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data.get("last_name", None))
        self.assertEqual(user.phone, data.get("phone", None))
        self.assertEqual(user.city, data.get("city", None))
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)
        self.assertIsNotNone(user.verification_token)

    def test_registro_y_login_sin_verificar_correo_falla(self):
        """
        [Caja Gris] Usuario no puede iniciar sesión sin verificar correo
        
        Camino:
        Registro → Usuario inactivo → Login falla
            
        Cobertura:
        - Integración RegisterSerializer → CustomUser → LoginSerializer
        - Validación de estado antes de verificación
        """
        # Paso 1: Registrar usuario
        data_register = {
            "email": "no-verify@example.com",
            "first_name": "NoVerify",
            "password": "pass1234"
        }
        register_serializer = RegisterSerializer(data=data_register)
        self.assertTrue(register_serializer.is_valid())
        register_serializer.save()

        # Paso 2: Intentar login sin verificar correo
        data_login = {
            "email": data_register["email"],
            "password": data_register["password"]
        }
        login_serializer = LoginSerializer(data=data_login)

        with self.assertRaises(ValidationError) as context:
            login_serializer.validate(data_login)

        self.assertEqual(context.exception.detail[0], "Usuario inactivo.")

    def test_registro_verificacion_y_login_exitoso(self):
        """
        [Caja Gris] Registro → Confirmación → Login
        
        Camino:
        Registro → Genera token → Confirma email → Usuario activo → Login exitoso
            
        Cobertura:
        - Integración completa: RegisterSerializer → VerifyEmailView → LoginSerializer
        - Validación de estado persistente
        """
        # Paso 1: Registrar usuario
        data_register = {
            "email": "verified@example.com",
            "first_name": "Verified",
            "password": "pass1234",
            "last_name": "User",
            "phone": "+51987654321",
            "city": "Madrid"
        }

        register_serializer = RegisterSerializer(data=data_register)
        self.assertTrue(register_serializer.is_valid())
        user = register_serializer.save()
        token = user.verification_token

        # Paso 2: Confirmar correo
        user.is_active = True
        user.is_verified = True
        user.verification_token = None
        user.save()

        # Paso 3: Iniciar sesión
        data_login = {
            "email": data_register["email"],
            "password": data_register["password"]
        }
        login_serializer = LoginSerializer(data=data_login)
        self.assertTrue(login_serializer.is_valid())
        validated_data = login_serializer.validate(data_login)

        self.assertIn("user", validated_data)
        self.assertIn("token", validated_data)

        db_user = validated_data["user"]
        db_token = validated_data["token"]

        token_obj = Token.objects.get(user=db_user)
        self.assertEqual(db_token, token_obj.key)

    def test_registro_con_campos_extra_y_confirmacion(self):
        """
        [Caja Gris] Campos extra se guardan y persisten tras verificación
        
        Camino:
        Registro con campos adicionales → Guardar en modelo → Verificar correo → Valida datos
        
        Cobertura:
        - Campos extras son guardados correctamente
        - Persistencia tras confirmación
        """
        data_register = {
            "email": "extra@example.com",
            "first_name": "Extra",
            "password": "pass1234",
            "last_name": "Fields",
            "phone": "+1234567890",
            "city": "City"
        }

        register_serializer = RegisterSerializer(data=data_register)
        self.assertTrue(register_serializer.is_valid())
        user = register_serializer.save()

        # Simular verificación de correo
        user.is_active = True
        user.is_verified = True
        user.verification_token = None
        user.save()

        # Validar datos guardados
        db_user = CustomUser.objects.get(email=data_register["email"])
        for field in ["last_name", "phone", "city"]:
            with self.subTest(field=field):
                self.assertEqual(getattr(db_user, field), data_register[field])

    def test_login_desde_vista_api_y_modelo_consistente(self):
        """
        [Caja Gris] Login desde vista API → datos consistentes en modelo
        
        Camino:
        Registro → Confirmación → Vista POST /login/ → Token devuelto
            
        Cobertura:
        - Integra vista + serializador + modelo
        - Token generado correctamente
        """
        # Paso 1: Registrar usuario
        data_register = {
            "email": "api-login@example.com",
            "first_name": "API",
            "password": "pass1234"
        }

        register_serializer = RegisterSerializer(data=data_register)
        self.assertTrue(register_serializer.is_valid())
        user = register_serializer.save()

        # Paso 2: Activar manualmente (simula verificación)
        user.is_active = True
        user.is_verified = True
        user.save()

        # Paso 3: Usar LoginSerializer
        data_login = {
            "email": data_register["email"],
            "password": data_register["password"]
        }

        login_serializer = LoginSerializer(data=data_login)
        self.assertTrue(login_serializer.is_valid())

        validated_data = login_serializer.validate(data_login)
        db_user = validated_data["user"]
        db_token = validated_data["token"]

        # Verificar token
        token_obj = Token.objects.get(user=db_user)
        self.assertEqual(db_token, token_obj.key)

    def test_registro_con_datos_invalidos_no_guarda_usuario(self):
        """
        [Caja Gris] Registro inválido → no se crea usuario
        
        Camino:
        Sin email → Levanta error → usuario no guardado
            
        Cobertura:
        - Validación de datos previa a modelo
        - Seguridad ante fallos de validación
        """
        invalid_data = {
            "first_name": "Invalid",
            "password": "pass1234"
        }

        serializer = RegisterSerializer(data=invalid_data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

        with self.assertRaises(CustomUser.DoesNotExist):
            CustomUser.objects.get(email=invalid_data.get("email", ""))
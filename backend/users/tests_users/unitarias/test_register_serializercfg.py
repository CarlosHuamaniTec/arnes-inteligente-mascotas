# users/tests_users/unitarias/RegisterSerializerTestCFG.py

from django.test import TestCase
from rest_framework import serializers
from users.serializers import RegisterSerializer


class RegisterSerializerCFGTest(TestCase):
    """
    Prueba unitaria de caja blanca para RegisterSerializer.
    
    Este test cubre el gráfico de flujo de control (CFG) del serializador:
    
        [Entrada]
           ↓
        validar_email() → ¿Correo único?
                                ↘ No → Levantar ValidationError
                                  ↓
                             create() → ¿Datos válidos? → Sí → Guardar usuario
                                                              ↓
                                                           Devolver datos
                                                    
    Criterios de cobertura aplicados:
        - Cobertura de instrucción/nodo: cada línea ejecutada al menos una vez
        - Cobertura de condición: todos los if pasan por True/False
        - Cobertura de ruta completa: desde inicio hasta fin
    """

    def setUp(self):
        self.valid_data = {
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "city": "Lima",
            "password": "pass1234"
        }

    def test_registro_usuario_datos_completos(self):
        """
        [Caja Blanca - Flujo de Control] Camino principal
        
        Camino:
        email != None → Único → first_name != None → Contraseña hasheada → Usuario guardado
        
        Cobertura:
        - Todos los nodos ejecutados
        - Valores esperados verificados
        """
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        # Validar campos principales
        self.assertEqual(user.email, self.valid_data["email"])
        self.assertEqual(user.first_name, self.valid_data["first_name"])
        self.assertTrue(user.check_password(self.valid_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_registro_sin_correo_lanza_error(self):
        """
        [Caja Blanca - Flujo de Control] Condición 1: correo == None
        
        Camino:
        email == None → Levanta error
            
        Cobertura:
        - Nodo decisión: correo es obligatorio
        - Excepción lanzada
        """
        invalid_data = self.valid_data.copy()
        invalid_data.pop("email")

        with self.assertRaises(serializers.ValidationError) as context:
            serializer = RegisterSerializer(data=invalid_data)
            serializer.is_valid(raise_exception=True)

        self.assertIn("email", context.exception.detail)

    def test_registro_con_correo_repetido_lanza_error(self):
        """
        [Caja Blanca - Flujo de Control] Condición 2: correo ya usado
        
        Camino:
        Correo ya existe → Levanta error
            
        Cobertura:
        - Nodo decisión: correo único
        - Excepción lanzada
        """
        from users.models import CustomUser

        # Registrar primer usuario
        CustomUser.objects.create_user(
            email="duplicate@example.com",
            first_name="Existing",
            password="pass1234"
        )

        # Intentar registrar otro con mismo correo
        duplicate_data = self.valid_data.copy()
        duplicate_data["email"] = "duplicate@example.com"

        with self.assertRaises(serializers.ValidationError) as context:
            serializer = RegisterSerializer(data=duplicate_data)
            serializer.is_valid(raise_exception=True)

        self.assertIn("email", context.exception.detail)

    def test_registro_sin_nombre_lanza_error(self):
        """
        [Caja Blanca - Flujo de Control] Condición 3: first_name == None
        
        Camino:
        first_name == None → Levanta error
            
        Cobertura:
        - Nodo decisión: nombre es obligatorio
        - Excepción lanzada
        """
        invalid_data = self.valid_data.copy()
        invalid_data.pop("first_name")

        with self.assertRaises(serializers.ValidationError) as context:
            serializer = RegisterSerializer(data=invalid_data)
            serializer.is_valid(raise_exception=True)

        self.assertIn("first_name", context.exception.detail)

    def test_registro_con_campos_extra_ignorados(self):
        """
        [Caja Blanca - Flujo de Control] Campos no definidos se ignoran
        
        Camino:
        Datos con campo adicional → serializador lo ignora
            
        Cobertura:
        - Ruta secundaria con campos extras
        """
        extra_data = {
            "extra_field": "should_be_ignored"
        }
        data = {**self.valid_data, **extra_data}

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Asegurarse que el campo extra no está en validated_data
        self.assertNotIn("extra_field", serializer.validated_data)

    def test_registro_usuario_y_verification_token_generado(self):
        """
        [Caja Blanca - Flujo de Control] Token generado al crear usuario
        
        Camino:
        Registro exitoso → verification_token != None
            
        Cobertura:
        - Camino básico con token generado
        """
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertIsNotNone(user.verification_token)
        self.assertEqual(len(user.verification_token), 40)  # Longitud del token generado

    def test_registro_usuario_y_estado_inicial_inactivo(self):
        """
        [Caja Blanca - Flujo de Control] Usuario creado inactivo
        
        Camino:
        Registro exitoso → is_active == False
            
        Cobertura:
        - Camino básico con estado inicial inactivo
        """
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)

    def test_registro_no_devuelve_password(self):
        """
        [Caja Blanca - Flujo de Control] Contraseña no devuelta en respuesta
        
        Camino:
        Registro exitoso → Respuesta sin contraseña
            
        Cobertura:
        - Camino básico con seguridad
        """
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("password", serializer.data)

    def test_registro_datos_opcionales(self):
        """
        [Caja Blanca - Flujo de Control] Campos adicionales como apellido, teléfono y ciudad
        
        Camino:
        Campos adicionales dados → Se guardan correctamente
            
        Cobertura:
        - Ruta alternativa con campos opcionales
        """
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        for field in ["last_name", "phone", "city"]:
            with self.subTest(field=field):
                self.assertEqual(getattr(user, field), self.valid_data[field])

    def test_registro_datos_minimos_necesarios(self):
        """
        [Caja Blanca - Flujo de Control] Solo campos requeridos
        
        Camino:
        Solo email y first_name → Se crea usuario
            
        Cobertura:
        - Camino mínimo: sin campos extra
        """
        minimal_data = {
            "email": "minimal@example.com",
            "first_name": "Minimal",
            "password": "pass1234"
        }

        serializer = RegisterSerializer(data=minimal_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertEqual(user.email, minimal_data["email"])
        self.assertEqual(user.first_name, minimal_data["first_name"])
        self.assertIsNone(user.last_name)
        self.assertIsNone(user.phone)
        self.assertIsNone(user.city)
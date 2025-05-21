from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

User = get_user_model()


class CustomUserModelCFGTest(TestCase):
    """
    Prueba unitaria de caja blanca para el modelo CustomUser.
    
    Esta prueba está diseñada siguiendo criterios de flujo de control:
        - Cobertura de instrucciones/nodos
        - Cobertura de condiciones/decisiones
        - Cobertura de rutas completas
        
    CFG del modelo CustomUser durante la creación:
    
        [Entrada]
           ↓
        ¿Correo proporcionado?
           ├── Sí → ¿Es único?
           │          ├── Sí → ¿Nombre proporcionado?
           │                      ├── Sí → Guardar usuario
           │                      └── No → Levantar ValueError
           └── No → Levantar ValueError
    
    Se han creado casos de prueba que recorren todas las rutas posibles.
    """

    def test_ruta_registro_exitoso_datos_completos(self):
        """
        [Caja Blanca - Flujo de Control] Ruta principal completa
        
        Camino:
        email != None → Único → first_name != None → Contraseña hasheada → Usuario guardado
        
        Cobertura:
        - Inicio y fin del flujo
        - Todos los nodos ejecutados
        """
        user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            password="password123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.is_verified)
        self.assertFalse(user.is_active)

    def test_camino_registro_sin_correo_lanza_error(self):
        """
        [Caja Blanca - Flujo de Control] Correo no proporcionado
        
        Camino:
        email == None → Levanta ValueError
        
        Cobertura:
        - Nodo decisión 1: correo no proporcionado
        - Excepción lanzada
        """
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email=None, first_name="John", password="pass1234")

        self.assertEqual(str(context.exception), "Debe ingresar el correo")

    def test_camino_registro_con_correo_repetido_lanza_error(self):
        """
        [Caja Blanca - Flujo de Control] Correo duplicado
        
        Camino:
        email != None → Ya existe → Levanta ValidationError
        
        Cobertura:
        - Nodo decisión 2: correo ya usado
        - Excepción lanzada
        """
        # Primer registro exitoso
        User.objects.create_user(email="duplicate@example.com", first_name="First", password="pass1234")

        # Segundo registro con mismo correo → debe fallar
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(email="duplicate@example.com", first_name="Second", password="pass1234")

        self.assertEqual(str(context.exception), "Este correo ya está registrado.")

    def test_camino_registro_sin_nombre_lanza_error(self):
        """
        [Caja Blanca - Flujo de Control] Nombre no proporcionado
        
        Camino:
        email != None → Único → first_name == None → Levanta error
        
        Cobertura:
        - Nodo decisión 3: nombre no proporcionado
        - Excepción lanzada
        """
        with self.assertRaises(ValueError) as context:
            User.objects.create_user(
                email="test@example.com",
                first_name=None,
                password="password123"
            )

        self.assertEqual(str(context.exception), "Debe ingresar el nombre")

    def test_camino_registro_datos_opcionales_ignorados(self):
        """
        [Caja Blanca - Flujo de Control] Registro con campos extra no definidos
        
        Camino:
        Campos adicionales como 'last_name', 'phone' o 'city' se pasan → son ignorados si no están definidos en el modelo
        
        Cobertura:
        - Camino secundario con campos opcionales
        """
        data = {
            "email": "optional@example.com",
            "first_name": "Optional",
            "password": "pass1234",
            "last_name": "Ignored",
            "phone": "+1234567890",
            "city": "Lima"
        }

        user = User.objects.create_user(**data)
        for field in ['last_name', 'phone', 'city']:
            with self.subTest(field=field):
                self.assertEqual(getattr(user, field), data[field])

    def test_registro_usuario_y_normalizacion_email(self):
        """
        [Caja Blanca - Flujo de Control] Email normalizado al registrar
        
        Camino:
        email contiene mayúsculas → se pasa a minúsculas
        
        Cobertura:
        - Ruta básica con normalización de correo
        """
        email = "TEST@EXAMPLE.COM"
        user = User.objects.create_user(email=email, first_name="Test", password="pass1234")
        self.assertEqual(user.email, email.lower())

    def test_creacion_superuser_campos_obligatorios(self):
        """
        [Caja Blanca - Flujo de Control] Superusuario válido
        
        Camino:
        is_staff == True → is_superuser == True
        
        Cobertura:
        - Camino principal con superusuario
        """
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            password="password123"
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_creacion_superuser_condiciones_obligatorias(self):
        """
        [Caja Blanca - Flujo de Control] Validación de condiciones en superusuario
        
        Camino:
        is_staff == False → Levanta error
        is_superuser == False → Levanta error
        
        Cobertura:
        - Condición 1: is_staff == False → Error
        - Condición 2: is_superuser == False → Error
        """
        # Caso 1: is_staff=False
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                password="password123",
                is_staff=False,
                is_superuser=True
            )
        self.assertEqual(str(context.exception), "Superuser debe tener is_staff=True")

        # Caso 2: is_superuser=False
        with self.assertRaises(ValueError) as context:
            User.objects.create_superuser(
                email="admin2@example.com",
                first_name="Admin",
                password="password123",
                is_staff=True,
                is_superuser=False
            )
        self.assertEqual(str(context.exception), "Superuser debe tener is_superuser=True")

    def test_registro_usuario_campos_nulos_por_defecto(self):
        """
        [Caja Blanca - Flujo de Control] Campos por defecto nulos
        
        Camino:
        Campos como last_name, phone y city → Si no se dan → Son None
        
        Cobertura:
        - Camino básico sin campos adicionales
        """
        user = User.objects.create_user(
            email="default@example.com",
            first_name="Default",
            password="password123"
        )
        self.assertIsNone(user.last_name)
        self.assertIsNone(user.phone)
        self.assertIsNone(user.city)

    def test_registro_usuario_string_representation(self):
        """
        [Caja Blanca - Flujo de Control] Método __str__ devuelve email
        
        Camino:
        Se llama a str(usuario) → Devuelve email
        
        Cobertura:
        - Camino básico del método __str__
        """
        user = User.objects.create_user(
            email="str@example.com",
            first_name="String",
            password="password123"
        )
        self.assertEqual(str(user), user.email)
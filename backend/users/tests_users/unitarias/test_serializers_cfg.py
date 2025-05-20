from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import CustomUser


class CustomUserModelWhiteBoxTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "password": "password123"
        }

    def test_registro_usuario_valido(self):
        """
        [Caja Blanca - Flujo de Control] Registro exitoso
        
        Camino:
        Campos obligatorios presentes → Se crea usuario → No es staff ni superusuario
        
        Cobertura:
        - Nodo inicial y final
        - Instrucciones básicas ejecutadas
        - Valores esperados verificados
        """
        user = self.User.objects.create_user(**self.user_data)
        self.assertEqual(user.email, self.user_data["email"])
        self.assertEqual(user.first_name, self.user_data["first_name"])
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_registro_con_campos_opcionales(self):
        """
        [Caja Blanca - Flujo de Control] Registro con campos adicionales
        
        Camino:
        Campos opcionales incluidos → Se guardan correctamente
        
        Cobertura:
        - Ruta alternativa con last_name, phone, city
        """
        extra_data = {
            "last_name": "Doe",
            "phone": "+51999999999",
            "city": "Lima"
        }
        data = {**self.user_data, **extra_data}
        user = self.User.objects.create_user(**data)

        for field, value in extra_data.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(user, field), value)

    def test_registro_sin_correo_lanza_error(self):
        """
        [Caja Blanca - Flujo de Control] Falta correo
        
        Camino:
        email == None → Levanta ValueError
        
        Cobertura:
        - Condición 1 falsa (email no proporcionado)
        """
        with self.assertRaises(ValueError):
            self.User.objects.create_user(email=None, first_name="John", password="pass1234")

    def test_registro_sin_nombre_lanza_error(self):
        """
        [Caja Blanca - Flujo de Control] Falta nombre
        
        Camino:
        first_name == None → Levanta ValueError
        
        Cobertura:
        - Condición 1 falsa (nombre no proporcionado)
        """
        with self.assertRaises(ValueError):
            self.User.objects.create_user(email="john@example.com", first_name=None, password="pass1234")

    def test_creacion_superuser(self):
        """
        [Caja Blanca - Flujo de Control] Creación de superusuario
        
        Camino:
        Campos válidos → is_staff e is_superuser True
        
        Cobertura:
        - Camino principal
        - Todos los campos son asignados
        """
        admin_user = self.User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            password="password123"
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_creacion_superuser_con_extra_fields(self):
        """
        [Caja Blanca - Flujo de Control] Superusuario con campos adicionales
        
        Camino:
        Campos extra incluidos → Se guardan correctamente
        
        Cobertura:
        - Camino secundario con campos adicionales
        """
        extra_data = {
            "last_name": "User",
            "phone": "+51999999999",
            "city": "Lima"
        }
        data = {**self.user_data, **extra_data, "is_superuser": True, "is_staff": True}

        admin_user = self.User.objects.create_superuser(**data)

        for field, value in extra_data.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(admin_user, field), value)

    def test_creacion_superuser_invalid_is_staff(self):
        """
        [Caja Blanca - Flujo de Control] Error si is_staff es False
        
        Camino:
        is_staff == False → Levanta error
        
        Cobertura:
        - Decisión condicional fallida
        """
        with self.assertRaises(ValueError):
            self.User.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                password="password123",
                is_staff=False,
                is_superuser=True
            )

    def test_creacion_superuser_invalid_is_superuser(self):
        """
        [Caja Blanca - Flujo de Control] Error si is_superuser es False
        
        Camino:
        is_superuser == False → Levanta error
        
        Cobertura:
        - Decisión condicional fallida
        """
        with self.assertRaises(ValueError):
            self.User.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                password="password123",
                is_staff=True,
                is_superuser=False
            )

    def test_campos_opcionales_por_defecto_nulos(self):
        """
        [Caja Blanca - Flujo de Control] Campos opcional nulos por defecto
        
        Camino:
        Usuario creado sin campos adicionales → Son None
        
        Cobertura:
        - Camino básico
        - Valores predeterminados verificados
        """
        user = self.User.objects.create_user(
            email="optional@example.com",
            first_name="Optional",
            password="password123"
        )
        self.assertIsNone(user.last_name)
        self.assertIsNone(user.phone)
        self.assertIsNone(user.city)
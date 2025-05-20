from django.test import TestCase
from users.serializers import RegisterSerializer
from users.models import CustomUser


class RegisterSerializerTest(TestCase):
    def test_registro_usuario_valido(self):
        """Verifica que se cree un usuario con datos válidos"""
        data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
            "city": "Lima",
            "password": "pass1234"
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.first_name, data["first_name"])
        self.assertEqual(user.last_name, data["last_name"])
        self.assertEqual(user.phone, data["phone"])
        self.assertEqual(user.city, data["city"])
        self.assertTrue(user.check_password(data["password"]))

    def test_registro_sin_correo_falla(self):
        """Verifica que falta de correo lance ValidationError"""
        data = {
            "first_name": "John",
            "password": "pass1234"
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_registro_sin_nombre_falla(self):
        """Verifica que falta de nombre lance ValidationError"""
        data = {
            "email": "test@example.com",
            "password": "pass1234"
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("first_name", serializer.errors)

    def test_registro_con_correo_repetido_falla(self):
        """Verifica que no se acepte un correo ya usado"""
        CustomUser.objects.create_user(
            email="duplicate@example.com",
            first_name="Existing",
            password="pass1234"
        )
        data = {
            "email": "duplicate@example.com",
            "first_name": "John",
            "password": "pass1234"
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_registro_con_campos_extra_ignorados(self):
        """Verifica que campos no definidos sean ignorados"""
        data = {
            "email": "extra@example.com",
            "first_name": "John",
            "password": "pass1234",
            "invalid_field": "no_debe_guardarse"
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        
        self.assertNotIn("invalid_field", serializer.validated_data)

        user = serializer.save()
        self.assertEqual(user.email, data["email"])
        self.assertEqual(user.first_name, data["first_name"])

    def test_registro_no_devuelve_password(self):
        """Verifica que la contraseña no aparezca en los datos serializados"""
        user = CustomUser.objects.create_user(
            email="secure@example.com",
            first_name="Pass",
            password="safe1234"
        )
        serializer = RegisterSerializer(user)
        self.assertNotIn("password", serializer.data)
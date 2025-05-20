from django.test import TestCase
from users.serializers import RegisterSerializer
from users.serializers import LoginSerializer
from users.models import CustomUser
from rest_framework import serializers
from rest_framework.authtoken.models import Token


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

class LoginSerializerCFGTest(TestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "password": "correctpassword"
        }
        self.user = CustomUser.objects.create_user(**self.user_data)
        self.serializer = LoginSerializer()

    def test_ruta_principal_usuario_valido_activo(self):
        """Verifica validación exitosa con usuario válido, contraseña correcta y activo"""
        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        validated_data = self.serializer.validate(data)

        self.assertIn("user", validated_data)
        self.assertIn("token", validated_data)
        self.assertEqual(validated_data["user"].email, self.user.email)

        token = Token.objects.get(user=self.user)
        self.assertEqual(validated_data["token"], token.key)

    def test_usuario_no_existe(self):
        """Verifica error cuando el correo no corresponde a ningún usuario"""
        data = {
            "email": "invalid@example.com",
            "password": "any_password"
        }
        with self.assertRaises(serializers.ValidationError) as context:
            self.serializer.validate(data)
        self.assertEqual(context.exception.detail[0], "Usuario no encontrado.")

    def test_contrasena_incorrecta(self):
        """Verifica error cuando la contraseña es incorrecta"""
        data = {
            "email": self.user_data["email"],
            "password": "wrongpassword"
        }
        with self.assertRaises(serializers.ValidationError) as context:
            self.serializer.validate(data)
        self.assertEqual(context.exception.detail[0], "Contraseña incorrecta.")

    def test_usuario_inactivo(self):
        """Verifica error cuando el usuario está inactivo"""
        self.user.is_active = False
        self.user.save()

        data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"]
        }
        with self.assertRaises(serializers.ValidationError) as context:
            self.serializer.validate(data)
        self.assertEqual(context.exception.detail[0], "Usuario inactivo.")
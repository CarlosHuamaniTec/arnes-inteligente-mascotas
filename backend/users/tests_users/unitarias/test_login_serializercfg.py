# backend/users/tests_user/unitarias/test_login_serializercfg.py

from django.test import TestCase
from rest_framework import serializers
from users.serializers import LoginSerializer
from users.models import CustomUser
from rest_framework.authtoken.models import Token


class LoginSerializerCFGTest(TestCase):
    """
    Pruebas unitarias caja blanca (CFG) para LoginSerializer.

    Cobertura:
    - Validar que email y password estén presentes.
    - Usuario existe / no existe.
    - Password correcta / incorrecta.
    - Usuario activo / inactivo.
    - Creación o recuperación de token.
    """

    def setUp(self):
        self.password = "correctpass123"
        self.user = CustomUser.objects.create_user(
            email="activeuser@example.com",
            first_name="Active",
            password=self.password,
            is_active=True
        )
        self.inactive_user = CustomUser.objects.create_user(
            email="inactiveuser@example.com",
            first_name="Inactive",
            password=self.password,
            is_active=False
        )

    def test_login_exito_con_usuario_activo(self):
        data = {
            "email": self.user.email,
            "password": self.password
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        validated_data = serializer.validated_data
        self.assertEqual(validated_data["user"], self.user)
        self.assertIsInstance(validated_data["token"], str)
        # Verificar token existe en DB
        token_obj = Token.objects.filter(user=self.user).first()
        self.assertIsNotNone(token_obj)
        self.assertEqual(token_obj.key, validated_data["token"])

    def test_login_usuario_no_encontrado(self):
        data = {
            "email": "nonexistent@example.com",
            "password": "any"
        }
        serializer = LoginSerializer(data=data)
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Usuario no encontrado.", str(context.exception))

    def test_login_password_incorrecta(self):
        data = {
            "email": self.user.email,
            "password": "wrongpassword"
        }
        serializer = LoginSerializer(data=data)
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Contraseña incorrecta.", str(context.exception))

    def test_login_usuario_inactivo(self):
        data = {
            "email": self.inactive_user.email,
            "password": self.password
        }
        serializer = LoginSerializer(data=data)
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("Usuario inactivo.", str(context.exception))

    def test_login_token_existente_reutilizado(self):
        # Crear token manualmente para usuario
        token_obj, created = Token.objects.get_or_create(user=self.user)
        data = {
            "email": self.user.email,
            "password": self.password
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["token"], token_obj.key)

    def test_login_campos_requeridos(self):
        # Sin email
        data = {"password": "pass"}
        serializer = LoginSerializer(data=data)
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("email", context.exception.detail)

        # Sin password
        data = {"email": "someone@example.com"}
        serializer = LoginSerializer(data=data)
        with self.assertRaises(serializers.ValidationError) as context:
            serializer.is_valid(raise_exception=True)
        self.assertIn("password", context.exception.detail)

    def test_login_email_normalizado(self):
        data = {
            "email": self.user.email.upper(),
            "password": self.password
        }
        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], self.user)
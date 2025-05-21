# backend/users/tests_user/unitarias/test_register_serializercfg.py

from django.test import TestCase
from rest_framework import serializers
from users.serializers import RegisterSerializer
from users.models import CustomUser
from unittest.mock import patch


class RegisterSerializerCFGTest(TestCase):
    """
    Pruebas unitarias caja blanca (CFG) para RegisterSerializer.

    Cobertura:
    - Validación de email (único, formato)
    - Campos requeridos y opcionales
    - Creación de usuario (token, is_active, is_verified)
    - Campos extra ignorados
    - No devolución de password en respuesta
    - Normalización de email
    - Llamada a función de envío de correo (mock)
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
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()

        self.assertEqual(user.email, self.valid_data["email"].lower())
        self.assertEqual(user.first_name, self.valid_data["first_name"])
        self.assertEqual(user.last_name, self.valid_data["last_name"])
        self.assertEqual(user.phone, self.valid_data["phone"])
        self.assertEqual(user.city, self.valid_data["city"])
        self.assertTrue(user.check_password(self.valid_data["password"]))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_registro_sin_correo_lanza_error(self):
        invalid_data = self.valid_data.copy()
        invalid_data.pop("email")

        with self.assertRaises(serializers.ValidationError) as context:
            serializer = RegisterSerializer(data=invalid_data)
            serializer.is_valid(raise_exception=True)
        self.assertIn("email", context.exception.detail)

    def test_registro_correo_repetido_lanza_error(self):
        CustomUser.objects.create_user(
            email="duplicate@example.com",
            first_name="Exist",
            password="pass1234"
        )
        duplicate_data = self.valid_data.copy()
        duplicate_data["email"] = "duplicate@example.com"

        with self.assertRaises(serializers.ValidationError) as context:
            serializer = RegisterSerializer(data=duplicate_data)
            serializer.is_valid(raise_exception=True)
        self.assertIn("email", context.exception.detail)
        self.assertIn("Este correo ya está registrado.", context.exception.detail["email"])

    def test_registro_sin_nombre_lanza_error(self):
        invalid_data = self.valid_data.copy()
        invalid_data.pop("first_name")

        with self.assertRaises(serializers.ValidationError) as context:
            serializer = RegisterSerializer(data=invalid_data)
            serializer.is_valid(raise_exception=True)
        self.assertIn("first_name", context.exception.detail)

    def test_registro_con_campos_extra_ignorados(self):
        extra_data = {
            "extra_field": "ignored"
        }
        data = {**self.valid_data, **extra_data}

        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("extra_field", serializer.validated_data)

    def test_registro_email_normalizado(self):
        data = self.valid_data.copy()
        data["email"] = "  MiXeDCase@Example.COM  "
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["email"], "mixedcase@example.com")

    @patch("users.serializers.enviar_correo_confirmacion")
    def test_registro_usuario_y_verification_token_generado(self, mock_send_email):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()

        self.assertIsNotNone(user.verification_token)
        self.assertEqual(len(user.verification_token), 40)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)

        mock_send_email.assert_called_once_with(user.email, user.verification_token)

    def test_registro_no_devuelve_password(self):
        serializer = RegisterSerializer(data=self.valid_data)
        self.assertTrue(serializer.is_valid())
        serializer.save()
        self.assertNotIn("password", serializer.data)

    def test_registro_datos_minimos_necesarios(self):
        minimal_data = {
            "email": "minimal@example.com",
            "first_name": "Minimal",
            "password": "pass1234"
        }
        serializer = RegisterSerializer(data=minimal_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, minimal_data["email"].lower())
        self.assertEqual(user.first_name, minimal_data["first_name"])
        self.assertIsNone(user.last_name)
        self.assertIsNone(user.phone)
        self.assertIsNone(user.city)
from django.test import TestCase
from users.models import CustomUser
from django.core.exceptions import ValidationError


class CustomUserManagerTest(TestCase):
    def test_create_user_successfully(self):
        """Crea un usuario común y verifica sus atributos básicos"""
        user = CustomUser.objects.create_user(
            email="user@example.com",
            first_name="John",
            password="password123"
        )
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.first_name, "John")
        self.assertTrue(user.check_password("password123"))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_user_missing_email_raises_error(self):
        """Si no se provee email, debe lanzar ValueError"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email=None, first_name="John", password="password123")

    def test_create_user_missing_first_name_raises_error(self):
        """Si no se provee first_name, debe lanzar ValueError"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(email="user@example.com", first_name=None, password="password123")

    def test_create_user_optional_fields(self):
        """Verifica que los campos adicionales se guarden correctamente"""
        user = CustomUser.objects.create_user(
            email="user@example.com",
            first_name="John",
            last_name="Doe",
            phone="1234567890",
            city="Springfield"
        )
        self.assertEqual(user.last_name, "Doe")
        self.assertEqual(user.phone, "1234567890")
        self.assertEqual(user.city, "Springfield")

    def test_create_superuser_successfully(self):
        """Crea un superusuario y verifica sus atributos"""
        admin_user = CustomUser.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            password="password123"
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_superuser_missing_is_staff_raises_error(self):
        """Si se pasa is_staff=False en superusuario, debe lanzar error"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                password="password123",
                is_staff=False,
                is_superuser=True
            )

    def test_create_superuser_missing_is_superuser_raises_error(self):
        """Si se pasa is_superuser=False en superusuario, debe lanzar error"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                password="password123",
                is_staff=True,
                is_superuser=False
            )

    def test_create_superuser_missing_both_flags_raises_error(self):
        """Si se pasan is_staff=False e is_superuser=False, debe lanzar error"""
        with self.assertRaises(ValueError):
            CustomUser.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                password="password123",
                is_staff=False,
                is_superuser=False
            )
from django.test import TestCase
from django.contrib.auth import get_user_model
from users.models import CustomUser

User = get_user_model()


class CustomUserModelTest(TestCase):
    def test_create_user_with_email_success(self):
        """Verifica que se pueda crear un usuario con email y nombre"""
        email = "test@example.com"
        first_name = "Test"
        password = "password123"

        user = User.objects.create_user(
            email=email,
            first_name=first_name,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_new_user_email_normalized(self):
        """Verifica que el email sea normalizado al crear un usuario"""
        email = "test@EXAMPLE.COM"
        user = User.objects.create_user(email=email, first_name="Test", password="password123")

        self.assertEqual(user.email, email.lower())

    def test_create_user_missing_email_raises_error(self):
        """Verifica que se lance un ValueError si no se proporciona email"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, first_name="Test", password="password123")

    def test_create_user_missing_first_name_raises_error(self):
        """Verifica que se lance un ValueError si no se proporciona first_name"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="test@example.com", first_name=None, password="password123")

    def test_create_superuser(self):
        """Verifica que se pueda crear un superusuario"""
        email = "admin@example.com"
        first_name = "Admin"
        password = "password123"

        admin_user = User.objects.create_superuser(
            email=email,
            first_name=first_name,
            password=password
        )

        self.assertEqual(admin_user.email, email)
        self.assertEqual(admin_user.first_name, first_name)
        self.assertTrue(admin_user.check_password(password))
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_create_superuser_with_extra_fields(self):
        """Verifica que se puedan incluir campos extra al crear un superusuario"""
        user = User.objects.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            password="password123",
            last_name="User",
            phone="1234567890",
            city="Example City"
        )

        self.assertEqual(user.last_name, "User")
        self.assertEqual(user.phone, "1234567890")
        self.assertEqual(user.city, "Example City")

    def test_create_superuser_invalid_is_staff(self):
        """Verifica que se lance un error si is_staff es False en superusuario"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                password="password123",
                is_staff=False,
                is_superuser=True
            )

    def test_create_superuser_invalid_is_superuser(self):
        """Verifica que se lance un error si is_superuser es False en superusuario"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                first_name="Admin",
                password="password123",
                is_staff=True,
                is_superuser=False
            )

    def test_user_has_optional_fields(self):
        """Verifica que los campos opcionales pueden ser nulos"""
        user = User.objects.create_user(
            email="optional@example.com",
            first_name="Optional",
            password="password123"
        )

        self.assertIsNone(user.last_name)
        self.assertIsNone(user.phone)
        self.assertIsNone(user.city)

    def test_user_string_representation(self):
        """Verifica que __str__ devuelva el email"""
        user = User.objects.create_user(
            email="str@example.com",
            first_name="String",
            password="password123"
        )

        self.assertEqual(str(user), user.email)
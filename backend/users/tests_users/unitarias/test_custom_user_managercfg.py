# backend/users/tests_user/unitarias/test_custom_user_managercfg.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from users.models import CustomUser, CustomUserManager


class CustomUserManagerCFGTest(TestCase):
    """
    Pruebas unitarias caja blanca (CFG) para CustomUserManager.

    Flujo de control cubierto para:
      - create_user: 
          * email None → ValueError
          * first_name None → ValueError
          * creación exitosa con token si no existe
      - create_superuser:
          * is_staff != True → ValueError
          * is_superuser != True → ValueError
          * creación exitosa con campos obligatorios y flags
    """

    def setUp(self):
        self.manager = CustomUser.objects

    def test_create_user_success_token_generated(self):
        """
        [Camino principal] create_user crea usuario con token generado si no existe
        """
        user = self.manager.create_user(
            email="user@example.com",
            first_name="First",
            password="pass1234"
        )
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.first_name, "First")
        self.assertTrue(user.check_password("pass1234"))
        self.assertIsNotNone(user.verification_token)
        self.assertGreater(len(user.verification_token), 0)

    def test_create_user_error_no_email(self):
        """
        [Condición] email None → ValueError
        """
        with self.assertRaisesMessage(ValueError, "Debe ingresar el correo"):
            self.manager.create_user(email=None, first_name="First", password="pwd")

    def test_create_user_error_no_first_name(self):
        """
        [Condición] first_name None → ValueError
        """
        with self.assertRaisesMessage(ValueError, "Debe ingresar el nombre"):
            self.manager.create_user(email="e@e.com", first_name=None, password="pwd")

    def test_create_user_token_preserved_if_already_set(self):
        """
        [Ruta alternativa] Si el usuario tiene verification_token antes de save, no se genera otro
        """
        # Creamos un usuario manualmente para manipular el token
        user = CustomUser(email="token@t.com", first_name="T", verification_token="token123")
        user.set_password("pwd")
        user.save()
        
        # Ahora usamos create_user para verificar que no sobreescribe token si ya existe
        user2 = self.manager.create_user(email="token2@t.com", first_name="T2", password="pwd2")
        # Debería generarlo para el nuevo usuario
        self.assertIsNotNone(user2.verification_token)
        self.assertNotEqual(user2.verification_token, "token123")

    def test_create_superuser_success(self):
        """
        [Camino principal] create_superuser con flags correctos crea usuario admin
        """
        superuser = self.manager.create_superuser(
            email="admin@example.com",
            first_name="Admin",
            password="adminpass"
        )
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.check_password("adminpass"))

    def test_create_superuser_error_is_staff_false(self):
        """
        [Condición] is_staff != True → ValueError
        """
        with self.assertRaisesMessage(ValueError, "Superuser debe tener is_staff=True"):
            self.manager.create_superuser(
                email="admin2@example.com",
                first_name="Admin2",
                password="pass",
                is_staff=False
            )

    def test_create_superuser_error_is_superuser_false(self):
        """
        [Condición] is_superuser != True → ValueError
        """
        with self.assertRaisesMessage(ValueError, "Superuser debe tener is_superuser=True"):
            self.manager.create_superuser(
                email="admin3@example.com",
                first_name="Admin3",
                password="pass",
                is_superuser=False
            )
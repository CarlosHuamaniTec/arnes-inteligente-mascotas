# backend/users/tests_user/unitarias/test_custom_usercfg.py

from django.test import TestCase
from django.db import IntegrityError
from users.models import CustomUser


class CustomUserModelCFGTest(TestCase):
    """
    Pruebas unitarias caja blanca (CFG) para el modelo CustomUser.

    Flujo de control y criterios de cobertura:
      - Nodo de creación de instancia (constructor + save)
      - Valores por defecto (verification_token, is_verified)
      - Campos opcionales (blank/null) con rutas null y no-null
      - Restricción de unicidad de email
      - Método __str__
    """

    def setUp(self):
        self.base_data = {
            "email": "user@example.com",
            "first_name": "FirstName",
            "password": "irrelevant"  # no se usará set_password aquí
        }

    def test_str_returns_email(self):
        """
        [Nodo] __str__ debe devolver el email
        """
        u = CustomUser(email="a@b.com", first_name="Name")
        self.assertEqual(str(u), "a@b.com")

    def test_default_values_after_manual_save(self):
        """
        [Nodo decisión] Campos con default:
          - verification_token: None
          - is_verified: False
        """
        u = CustomUser(email="d@d.com", first_name="DName")
        u.set_password("pwd")
        u.save()
        self.assertIsNone(u.verification_token)
        self.assertFalse(u.is_verified)

    def test_optional_fields_null_paths(self):
        """
        [Ruta] Campos opcionales pueden ser None:
          last_name, phone, city = None
        """
        u = CustomUser(email="x@y.com", first_name="XName")
        u.set_password("pwd")
        u.save()
        for field in ["last_name", "phone", "city"]:
            with self.subTest(field=field):
                self.assertIsNone(getattr(u, field))

    def test_optional_fields_non_null_paths(self):
        """
        [Ruta] Campos opcionales asignados correctamente:
          last_name, phone, city con valores string
        """
        data = {
            "email": "p@q.com",
            "first_name": "PName",
            "last_name": "Last",
            "phone": "12345",
            "city": "TestCity"
        }
        u = CustomUser(**data)
        u.set_password("pwd")
        u.save()
        for field in ["last_name", "phone", "city"]:
            with self.subTest(field=field):
                self.assertEqual(getattr(u, field), data[field])

    def test_email_unique_constraint(self):
        """
        [Nodo fusión] No se permiten duplicados de email:
          Crear dos usuarios con mismo email → IntegrityError
        """
        CustomUser.objects.create_user(email="dup@dup.com", first_name="Dup", password="pwd")
        with self.assertRaises(IntegrityError):
            # bypass manager para simular conflicto en DB
            u = CustomUser(email="dup@dup.com", first_name="Dup2")
            u.set_password("pwd2")
            u.save()

    def test_username_field_removed(self):
        """
        [Condición] username no existe en el modelo
        """
        self.assertFalse(hasattr(CustomUser, "username"))

    def test_manual_verification_token_path(self):
        """
        [Ruta alternativa] Si se asigna verification_token antes de save, persiste:
        """
        token = "manualtoken123"
        u = CustomUser(email="m@a.com", first_name="MName", verification_token=token)
        u.set_password("pwd")
        u.save()
        self.assertEqual(u.verification_token, token)

    def test_model_creation_via_manager_strips_username(self):
        """
        [Cobertura de ruta] Al crear con manager, username permanece None
        """
        u = CustomUser.objects.create_user(email="mgr@mgr.com", first_name="Mgr", password="pwd")
        self.assertFalse(hasattr(u, "username") or u.username is None)
